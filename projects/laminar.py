#!/usr/bin/env python

import math
from scad import *

class LaminarJetObject(SCAD_Object):
    body_length = 50
    body_radius = 50
    body_thickness = 2
    body_inner_radius = body_radius - body_thickness
    # threads
    thread_pitch = 2.2
    # inlet hose thread length
    body_thread_length = 10

    ##
    ## Body
    def body_transform(self, body):
        return body
    
    def body_out_thread_transform(self, body_threads):
        body_threads = Translate(z=self.body_length - self.body_thread_length + 2)(body_threads)
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
        body = Cylinder(h=self.body_length, r=self.body_inner_radius, fn=50)
        return body

    @property
    def body_out_threads(self):
        scad = "thread_out_pitch(%s, %s, %s, 200);" % (self.body_radius * 2.0 + 2, self.body_thread_length, self.thread_pitch)
        body_threads = Inline(code=scad)
        body_threads = self.body_out_thread_transform(body_threads)
        return body_threads

    @property
    def body_in_threads(self):
        scad = "thread_in_pitch(%s, %s, %s, 200);" % (self.body_radius * 2.0 + 2, self.body_thread_length, self.thread_pitch)
        body_threads = Inline(code=scad)
        body_threads = self.body_in_thread_transform(body_threads)
        return body_threads

class LaminarJetMiddle(LaminarJetObject):
    straw_radius = 4
    body_length = 10
    collar_length = 12
    collar_inner_radius = LaminarJetObject.body_radius + 1
    collar_radius = collar_inner_radius + LaminarJetObject.body_thickness

    def body_transform(self, body):
        body = Translate(z=self.body_thread_length)( body )
        return body

    def circle_pack(self, clip_radius, circle_radius):
        def is_clipped(x, y):
            return \
                ((x - clip_radius + circle_radius) ** 2 + (y - clip_radius - circle_radius) ** 2) > (clip_radius ** 2) or \
                ((x - clip_radius - circle_radius) ** 2 + (y - clip_radius + circle_radius) ** 2) > (clip_radius ** 2) or \
                ((x - clip_radius + circle_radius) ** 2 + (y - clip_radius + circle_radius) ** 2) > (clip_radius ** 2) or \
                ((x - clip_radius - circle_radius) ** 2 + (y - clip_radius - circle_radius) ** 2) > (clip_radius ** 2) 
        angle = math.radians(60)
        yoff = math.sin(angle) * (circle_radius * 2)
        xoff = math.cos(angle) * (circle_radius * 2)
        offset = 0
        x = y = 0
        while 1:
            if y > (clip_radius * 2):
                raise StopIteration
            x += circle_radius * 2
            if x > (clip_radius * 2):
                y += yoff
                x = 0
                offset += 1
                if (offset % 2):
                    x += xoff
            if is_clipped(x, y):
                continue
            yield {'x': x - clip_radius, 'y': y - clip_radius}

    @property
    def collar(self):
        collar1 = Pipe(h=self.body_thread_length, ir=self.collar_inner_radius, oR=self.collar_radius, ifn=200, ofn=200)
        collar2 = Pipe(h=2, ir=self.body_inner_radius, oR=self.collar_radius, oR2=self.body_radius, ifn=200, ofn=200)
        collar2 = Translate(z=self.body_thread_length)( collar2 )
        collar = Union()(collar1, collar2)
        return collar

    @property
    def straws(self):
        straw = Cylinder(h=20, r=self.straw_radius, fn=20)
        straws = [Translate(**coords)(straw) for coords in self.circle_pack(self.body_inner_radius, self.straw_radius + 0.2)]
        straw_count = len(straws)
        straws = Translate(z=-1)(straws)
        print "generated %d straws" % straw_count
        return straws

    def render_scad(self, *args, **kw):
        straws = Union()( self.inner_body, self.straws )
        straws = Difference()( self.inner_body, self.straws )
        jet = Union()( self.body, self.body_in_threads, self.collar, straws )
        jet = straws
        jet = Include(filename="ISOThread.scad")( jet )
        return jet.render_scad()

class LaminarJetBase(LaminarJetObject):
    # inlet
    inlet_length = 60
    #inlet_inner_radius = 26.99 / 2.0
    inlet_inner_radius = 27.99 / 2.0
    inlet_thickness = LaminarJetObject.body_thickness
    inlet_radius = inlet_inner_radius + inlet_thickness
    # washer block
    washer_block_length = 2
    washer_block_inner_rad = 6
    washer_block_thickness = 2
    washer_block_offset = 4
    # inlet inlet thread length
    inlet_thread_length = 10

    ##
    ## Body
    def body_transform(self, body):
        body = Translate(z=self.body_thickness)( body )
        return body
    
    def body_thread_transform(self, body_threads):
        body_threads = Translate(z=self.body_length - self.inlet_thread_length + 2)(body_threads)
        return body_threads

    ##
    ## Inlet
    def inlet_transform(self, inlet):
        inlet = Rotate(x=90)( inlet )
        inlet = Translate(x=self.body_radius - self.inlet_radius, z=self.inlet_radius)( inlet )
        #inlet = self.body_transform(inlet)
        return inlet

    def inlet_thread_transform(self, inlet_threads):
        inlet_threads = self.inlet_transform(inlet_threads)
        inlet_threads = Translate(y=-self.inlet_length + self.inlet_thread_length - 1.3)(inlet_threads)
        return inlet_threads

    @property
    def inlet_outer(self):
        inlet = Cylinder(h=self.inlet_length, r=self.inlet_radius)
        inlet = self.inlet_transform(inlet)
        return inlet

    @property
    def inlet_outer(self):
        inlet = Cylinder(h=self.inlet_length, r=self.inlet_radius)
        inlet = self.inlet_transform(inlet)
        return inlet

    @property
    def inlet(self):
        inlet = Pipe(h=self.inlet_length, iR=self.inlet_inner_radius, oR=self.inlet_radius, ifn=200, ofn=200)
        inlet = self.inlet_transform(inlet)
        return inlet
    
    @property
    def endcap(self):
        endcap = Cylinder(h=self.body_thickness, r=self.body_radius, fn=200)
        return endcap
    
    @property
    def washer_block(self):
        washer_block = Pipe(h=self.washer_block_length, ir=self.washer_block_inner_rad, oR=self.inlet_radius)
        washer_block = self.inlet_thread_transform(washer_block)
        washer_block = Translate(y=self.washer_block_offset)( washer_block )
        return washer_block

    @property
    def inlet_threads(self):
        scad = "thread_in_pitch(%s, %s, %s, 200);" % (self.inlet_inner_radius * 2.0, self.inlet_thread_length, self.thread_pitch)
        inlet_threads = Inline(code=scad)
        inlet_threads = self.inlet_thread_transform(inlet_threads)
        return inlet_threads
    
    def render_scad(self, *args, **kw):
        body = Difference()(self.body, self.inlet_outer)
        inlet = Difference()(self.inlet, self.inner_body)
        jet = Union()( body, self.endcap, inlet, self.inlet_threads, self.washer_block, self.body_out_threads )
        jet = Include(filename="ISOThread.scad")( jet )
        return jet.render_scad()

base = LaminarJetBase()
base.render("laminar_jet_base.scad")
middle = LaminarJetMiddle()
middle.render("laminar_jet_middle2.scad")
