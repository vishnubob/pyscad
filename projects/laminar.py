#!/usr/bin/env python

import math
from scad import *

def from_polar(radius, angle):
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)
    return (x, y)

def to_polar(x, y):
    radius = math.sqrt(x ** 2 + y ** 2)
    angle = math.atan2(y, x)
    return (radius, angle)

class LaminarJetObject(SCAD_Object):
    body_length = 50
    body_radius = inch2mm(3.5 - 0.1) / 2.0 - 1
    body_thread_radius = inch2mm(3.5) / 2.0 - 1
    body_thickness = inch2mm(0.216)
    body_inner_radius = body_radius - body_thickness
    # threads
    hose_thread_pitch = 2.2
    # inlet hose thread length
    body_thread_pitch = inch2mm(1/8.0)
    body_thread_length = 20
    # collar
    collar_length = 12
    collar_inner_radius = body_radius + 1
    collar_radius = collar_inner_radius + body_thickness

    ##
    ## Body
    def body_transform(self, body):
        return body
    
    def body_out_thread_transform(self, body_threads):
        body_threads = self.body_transform(body_threads)
        body_threads = Translate(z=self.body_length - self.body_thread_length)(body_threads)
        return body_threads

    def body_in_thread_transform(self, body_threads):
        #body_threads = Translate(z=self.body_length - self.body_thread_length + 2)(body_threads)
        return body_threads

    @property
    def body(self):
        body = Pipe(h=self.body_length, ir=self.body_inner_radius, oR=self.body_radius, ifn=200, ofn=200)
        body = self.body_transform(body)
        return body

    @property
    def outer_body(self):
        body = Cylinder(h=self.body_length, r=self.body_radius, fn=200)
        return body

    @property
    def inner_body(self):
        body = Cylinder(h=self.body_length, r=self.body_inner_radius, fn=200)
        return body

    @property
    def body_out_threads(self):
        scad = "thread_out_pitch(%s, %s, %s, 100);" % (self.body_thread_radius * 2.0, self.body_thread_length, self.body_thread_pitch)
        body_threads = Inline(code=scad)
        body_threads = self.body_out_thread_transform(body_threads)
        return body_threads

    @property
    def body_in_threads(self):
        scad = "thread_in_pitch(%s, %s, %s, 200);" % (self.body_radius * 2.0 + 2, self.body_thread_length, self.body_thread_pitch)
        body_threads = Inline(code=scad)
        body_threads = self.body_in_thread_transform(body_threads)
        return body_threads

    @property
    def collar(self):
        collar1 = Pipe(h=self.body_thread_length, ir=self.collar_inner_radius, oR=self.collar_radius, ifn=200, ofn=200)
        collar2 = Pipe(h=2, ir=self.body_inner_radius, oR=self.collar_radius, oR2=self.body_radius, ifn=200, ofn=200)
        collar2 = Translate(z=self.body_thread_length)( collar2 )
        collar = Union()(collar1, collar2)
        return collar

class LaminarJetNozzle(LaminarJetObject):
    body_length = 10
    nozzle_radius = 9.55 / 2.0

    def body_transform(self, body):
        body = Translate(z=self.body_thread_length)( body )
        return body

    def frontcap_transform(self, frontcap):
        frontcap = self.body_transform(frontcap)
        frontcap = Translate(z=self.body_length)(frontcap)
        return frontcap

    @property
    def nozzle(self):
        nozzle = Cylinder(h=self.body_thickness + 0.1, r1=self.nozzle_radius, r2=self.nozzle_radius * 1.6, fn=200)
        nozzle = self.frontcap_transform(nozzle)
        nozzle = Translate(z=-.05)(nozzle)
        return nozzle

    @property
    def frontcap(self):
        frontcap = Cylinder(h=self.body_thickness, r=self.body_radius, fn=200)
        frontcap = self.frontcap_transform(frontcap)
        frontcap = Difference()( frontcap, self.nozzle )
        return frontcap

    def render_scad(self, *args, **kw):
        nozzle = Union()( self.body, self.body_in_threads, self.collar, self.frontcap )
        nozzle = Rotate(y=180)(nozzle)
        nozzle = Include(filename="ISOThread.scad")( nozzle )
        return nozzle.render_scad()

class LaminarJetMiddle(LaminarJetObject):
    straw_radius = 2.0
    body_length = 10
    body_thread_length = 10
    body_inner_radius = LaminarJetObject.body_radius - 2
    center_shaft_radius = 9.55 / 2.0

    def body_transform(self, body):
        body = Translate(z=self.body_thread_length)( body )
        return body

    def pack_straws(self):
        def is_clipped(x, y, r):
            return (x ** 2 + y ** 2) > (r ** 2)
        idx = 0
        constant = self.straw_radius * 1.5
        while 1:
            radius = constant * math.sqrt(idx)
            angle = idx * math.radians(137.5)
            idx += 1
            (x, y) = from_polar(radius, angle)
            if not is_clipped(x, y, self.center_shaft_radius + self.straw_radius * 1.2):
                continue
            if is_clipped(x, y, self.body_inner_radius - self.straw_radius - self.body_thickness):
                break
            yield {'x': x, 'y': y}

    @property
    def straws(self):
        straw = Cylinder(h=self.body_length + 2, r=self.straw_radius, fn=20)
        center_shaft = Cylinder(h=self.body_length + 2, r=self.center_shaft_radius, fn=100)
        straws = [center_shaft]
        straws += [Translate(**coords)(straw) for coords in self.pack_straws()]
        straw_count = len(straws)
        straws = Translate(z=-1)(straws)
        print "generated %d straws" % straw_count
        return straws

    """
    @property
    def outer_body(self):
        body = Cylinder(h=self.body_length - self.body_thread_length, r=self.body_radius, fn=200)
        return body
    """

    def render_scad(self, *args, **kw):
        #straws = Union()( self.inner_body, self.straws )
        #straws = Difference()( self.outer_body, self.straws )
        #straws = self.body_transform(straws)
        #jet = Union()( self.body, self.body_in_threads, self.collar, straws, self.body_out_threads )
        #jet = Union()( self.body, self.body_in_threads, self.collar, self.body_out_threads )
        jet = Union()( self.body, self.body_out_threads )
        jet = Include(filename="ISOThread.scad")( jet )
        return jet.render_scad()

class LaminarJetBase(LaminarJetObject):
    # inlet
    inlet_length = 43
    #inlet_inner_radius = 26.99 / 2.0
    inlet_inner_radius = 27.99 / 2.0
    inlet_thickness = 2
    endcap_thickness = 4
    inlet_radius = inlet_inner_radius + inlet_thickness
    # washer block
    washer_block_length = inlet_length - 4
    washer_block_inner_rad = 10
    washer_block_thickness = 2
    washer_block_offset = washer_block_length + 4
    # inlet inlet thread length
    inlet_thread_length = 10

    ##
    ## Body
    def body_transform(self, body):
        body = Translate(z=self.endcap_thickness)( body )
        return body
    
    def body_thread_transform(self, body_threads):
        body_threads = Translate(z=self.body_length - self.inlet_thread_length + 2)(body_threads)
        return body_threads

    ##
    ## Inlet
    def inlet_transform(self, inlet):
        inlet = Rotate(x=90)( inlet )
        inlet = Translate(x=self.body_radius - self.inlet_radius - 1, z=self.inlet_radius, y=-9)( inlet )
        #inlet = self.body_transform(inlet)
        return inlet

    def inlet_thread_transform(self, inlet_threads):
        inlet_threads = self.inlet_transform(inlet_threads)
        inlet_threads = Translate(y=-self.inlet_length + self.inlet_thread_length - 1.3)(inlet_threads)
        return inlet_threads

    @property
    def inlet_outer(self):
        inlet = Cylinder(h=self.inlet_length, r=self.inlet_radius, fn=200)
        inlet = self.inlet_transform(inlet)
        return inlet

    @property
    def inlet(self):
        inlet = Pipe(h=self.inlet_length, iR=self.inlet_inner_radius, oR=self.inlet_radius, ifn=200, ofn=200)
        inlet = self.inlet_transform(inlet)
        return inlet
    
    @property
    def endcap(self):
        endcap = Cylinder(h=self.endcap_thickness, r=self.body_radius, fn=200)
        return endcap
    
    @property
    def washer_block(self):
        washer_block = Pipe(h=self.washer_block_length, ir=self.washer_block_inner_rad, oR=self.inlet_radius, ifn=200, ofn=200)
        washer_block = self.inlet_thread_transform(washer_block)
        washer_block = Translate(y=self.washer_block_offset)( washer_block )
        return washer_block

    @property
    def inlet_threads(self):
        scad = "thread_in_pitch(%s, %s, %s, 200);" % (self.inlet_inner_radius * 2.0, self.inlet_thread_length, self.hose_thread_pitch)
        inlet_threads = Inline(code=scad)
        inlet_threads = self.inlet_thread_transform(inlet_threads)
        return inlet_threads
    
    def render_scad(self, *args, **kw):
        body = Difference()(self.body, self.inlet_outer)
        inlet = Difference()(Union()(self.inlet, self.washer_block), self.inner_body)
        jet = Union()( body, self.endcap, inlet, self.inlet_threads, self.body_out_threads )
        jet = Include(filename="ISOThread.scad")( jet )
        return jet.render_scad()

base = LaminarJetBase()
base.render("laminar_jet_base.scad")
middle = LaminarJetMiddle()
middle.render("laminar_jet_middle.scad")
nozzle = LaminarJetNozzle()
nozzle.render("laminar_jet_nozzle.scad")
