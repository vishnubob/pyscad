#!/usr/bin/env python

import math
from scad import *

"""
union() {
    intersection() {
        translate([0, 0, 25.4 / 2]) { cube([28, 28, 25.4], center=true); }
        translate([0, 0, -1]) { thread_in_pitch(26.99,30,2.2); }
    }
    difference() {
        cylinder(d=30, h=25.4);
        cylinder(d=26.99, h=25.5);
    }
};
"""


def hexagon(edge=1):
    for angle_idx in xrange(6):
        angle = math.radians(60 * angle_idx)
        x = math.cos(angle) * edge
        y = math.sin(angle) * edge
        yield {'x': x, 'y': y}

def x_clip(x):
    return x > 20

def y_clip(y):
    return y > 20

def circle_clip(r):
    def inner_circle_clip(x, y):
        return ((x - r) ** 2 + (y - r) ** 2) > (r ** 2) 
    return inner_circle_clip

def circle_pack(clip, radius=1):
    def next_xy(x, y):
        while 1:
            if not clip(x, y):
                return (x, y)
            x += (radius * 2)
    (x, y) = next_xy(0, 0)
    yield {'x': x, 'y': y}
    angle = math.radians(60)
    xoff = math.cos(angle) * (radius * 2)
    yoff = math.sin(angle) * (radius * 2)
    offset = 0
    while 1:
        x += radius * 2
        if clip(x, y):
            y += yoff
            if clip(0, y):
                break
            x = 0
            offset += 1
            if (offset % 2):
                x += xoff
            x = next_xy(x, y)
        yield {'x': x, 'y': y}

class LaminarJet(SCAD_Object):
    body_length = 50
    body_radius = 50
    body_thickness = 2
    body_inner_radius = body_radius - body_thickness
    # inlet
    inlet_length = 20
    inlet_thickness = body_thickness
    #inlet_inner_radius = 26.99 / 2.0
    #inlet_radius = inlet_inner_radius + inlet_thickness
    inlet_radius = 23.10
    inlet_inner_radius = inlet_radius - inlet_thickness
    # washer block
    washer_block_length = 2
    washer_block_inner_rad = 6
    washer_block_thickness = 2
    washer_block_offset = 4
    # threads
    thread_length = 15

    def body_transform(self, body):
        body = Translate(z=self.body_thickness)( body )
        return body
    
    def inlet_transform(self, inlet):
        inlet = Rotate(x=90)( inlet )
        inlet = Translate(x=self.body_radius - self.inlet_radius, z=self.inlet_radius)( inlet )
        #inlet = self.body_transform(inlet)
        return inlet

    def thread_transform(self, threads):
        threads = self.inlet_transform(threads)
        threads = Translate(y=-self.inlet_length + self.thread_length + 1.3)(threads)
        return threads

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
        inlet = Pipe(h=self.inlet_length, iR=self.inlet_inner_radius - 3, oR=self.inlet_radius - 3)
        inlet = self.inlet_transform(inlet)
        return inlet
    
    @property
    def endcap(self):
        endcap = Cylinder(h=self.body_thickness, r=self.body_radius)
        return endcap
    
    @property
    def washer_block(self):
        washer_block = Pipe(h=self.washer_block_length, ir=self.washer_block_inner_rad, oR=self.inlet_radius)
        washer_block = self.thread_transform(washer_block)
        washer_block = Translate(y=self.washer_block_offset)( washer_block )
        return washer_block

    @property
    def body(self):
        body = Pipe(h=self.body_length, ir=self.body_inner_radius, oR=self.body_radius)
        body = self.body_transform(body)
        return body

    @property
    def outer_body(self):
        body = Cylinder(h=self.body_length, r=self.body_radius)
        return body

    @property
    def inner_body(self):
        body = Cylinder(h=self.body_length, r=self.body_inner_radius)
        return body

    @property
    def threads(self):
        scad = "thread_out_pitch(%s,%s,2.2,100);" % (self.inlet_inner_radius * 2.0, self.thread_length)
        threads = Inline(code=scad)
        threads = self.thread_transform(threads)
        return threads
    
    @property
    def straws(self):
        body = Cylinder(h=2, d=7, fn=20, center=True)
        straw = Cylinder(h=10, d=2, fn=20)
        straws = [Translate(**coords)(straw) for coords in circle_pack(circle_clip(self.body_inner_radius), 1)]
        return Union()( *straws )

    def render_scad(self, *args, **kw):
        body = Difference()(self.body, self.inlet_outer)
        inlet = Difference()(self.inlet, self.inner_body)
        jet = Union()( body, self.endcap, inlet, self.threads, self.washer_block, self.straws )
        jet = Union()( self.threads, self.inlet )
        jet = Include(filename="ISOThread.scad")( jet )
        return jet.render_scad()


#scene = Difference() (body, *straws)
jet = LaminarJet()
scene = jet
#threads = english_thread(1.0625, 11.5, 1, internal=True)
#scene = Difference() (Cylinder(d=inch2mm(1.2), h=inch2mm(.9)), threads)
scene.render("ljet.scad")
