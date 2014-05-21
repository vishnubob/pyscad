#!/usr/bin/env python

from sctk import *

def unit(size, level=0):
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

class ST(Part):
    def render_scad(self):
        return difference()(
            tetrahedron(10, center=True),
            translate([0,0,-2.5])( rotate([180,0,-30])( tetrahedron(6, center=True) )),
        )

r = RootObject()
part = ST(r)
scad = part.render_scad()
save_scad(scad, "st.scad", lazy=False)
