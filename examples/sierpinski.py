#!/usr/bin/env python

import math
from scad import *

def simple(size, level=0):
    if level == 0:
        ret = union()(
            pyramid("top", size, center=True),
            translate([-size / 2.0, -size / 2.0, -size])( pyramid("b1", size, center=True) ),
            translate([size / 2.0, -size / 2.0, -size])( pyramid("b1", size, center=True) ),
            translate([-size / 2.0, size / 2.0, -size])( pyramid("b1", size, center=True) ),
            translate([size / 2.0, size / 2.0, -size])( pyramid("b1", size, center=True) ),
        )
    else:
        ret = union()(
            pyramid("top", size, center=True),
            translate([-size / 2.0, -size / 2.0, -size])( unit(size, level-1) ),
            translate([size / 2.0, -size / 2.0, -size])( unit(size, level-1) ),
            translate([-size / 2.0, size / 2.0, -size])( unit(size, level-1) ),
            translate([size / 2.0, size / 2.0, -size])( unit(size, level-1) ),
        )
    return ret

class SierpinskiTriangle(SCAD_Object):
    Defaults = {
        "iterations": {"type": int, "default": 4},
        "height": {"type": int, "default": 10},
    }

    def build(self, level=0, height=None):
        height = height or self.height
        edge = height / math.sqrt(2.0 / 3.0)

        if level == self.iterations:
            return None
        if level == 0:
            #return rotate([180, 0, 0])( self.build(level=level + 1, height=height / 2.0) )
            return union()(
                translate([0, 0, height / 2.0])( tetrahedron(height=height, center=True) ),
                rotate([0, 0, -30])( self.build(level=level + 1, height=height / 2.0) )
            )
        if level + 1 == self.iterations:
            return translate([0, 0, -height / 2.0])( octohedron(edge=height, center=True) )
        else:
            next_edge = (height / 2.0) / math.sqrt(2.0 / 3.0)
            radius = (math.sqrt(3.0) / 2.0 * edge / 2.0) / 3.0 + (math.sqrt(3.0) / 2.0 * next_edge) - (math.sqrt(3.0) / 2.0 * next_edge) / 3.0
            return union()(
                translate([0, 0, -height / 2.0])( octohedron(edge=height * 2, center=True) ),
                translate([math.cos(math.radians(45)) * radius, math.sin(math.radians(45)) * radius, 0])( self.build(level=level + 1, height=height / 2.0) ),
                translate([math.cos(math.radians(165)) * radius, math.sin(math.radians(165)) * radius, 0])( self.build(level=level + 1, height=height / 2.0) ),
                translate([math.cos(math.radians(285)) * radius, math.sin(math.radians(285)) * radius, 0])( self.build(level=level + 1, height=height / 2.0) ),
                translate([0, 0, -height])( self.build(level=level + 1, height=height / 2.0) ),
            )

    def octohedron_edge(self, idx, height):
        height = 10
        edge = height / (math.sqrt(3.0) / 2.0)
        eq_height = edge * (math.sqrt(3.0) / 2.0)
        octoedge = (height / 2.0) / math.sqrt(2.0 / 3.0)
        # top is offset from bottom by -(eq_height / 3.0)

    def render_scad(self):
        height = 10
        edge = height / (math.sqrt(3.0) / 2.0)
        return self.build().render_scad()
        return union()(
            Octohedron(height=height),
            translate( [-edge / 2.0,0,0] )( cube([1, 1, height], center=True )),
            translate( [-edge / 2.0,0,0] )( rotate([-33 -2/3.0,0,0])( cube([1, 1, height], center=True ))),
            translate( [-edge / 4.0,8,0] )( cube([1, 1, height], center=True )),
            ).render_scad()
        return difference()(
            translate([0,0,0])( tetrahedron(height=height, center=True) ),
            translate([0,0,-height / 4.0])( 
            rotate([0,0,0])(
                octohedron(height=height / 2.0, edge=octoedge + .1, center=True) ),
            )
        )
        #return tetrahedron(10)

st = SierpinskiTriangle()
st.render("striangle.scad")
