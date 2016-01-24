#!/usr/bin/env python
from scad import *

nail_rad = 1.5
mold_rad = 6
mold_height = 50
ttcnt = 8

class TestTube(SCAD_Object):
    Defaults = {
        "radius": {"type": float, "default": 1.0},
        "center": {"type": bool, "default": False},
        "resolution": {"type": RadialResolution, "default": lambda: RadialResolution()},
        "height": {"type": float, "default": 1.0},
    }

    def get_diamater(self):
        return self.radius * 2
    def set_diamater(self, dia):
        self.radius = dia / 2.0
    diameter = property(get_diamater, set_diamater)
    
    def render_scad(self, *args, **kw):
        tube = Cylinder(h=self.height - self.radius, r=self.radius, center=self.center, fn=40)
        endcap = Difference()(
            Sphere(r=self.radius, center=self.center, fn=40), 
            Translate(z=self.radius)( Cube([self.diameter, self.diameter, self.diameter], center=True)))
        tt = Union()( tube, endcap,)
        return tt.render_scad()


tt = TestTube(radius=mold_rad, height=mold_height)
padding = 4
step = mold_rad * 2 + padding

ttrow = Union()(*[Translate(y=step * idx)(tt) for idx in range(ttcnt)])
mold = Difference() (
        Translate(y=-mold_rad - padding  / 2.0, z=-mold_rad - 1)( 
            Cube(x=10, z=mold_height + 1, y=(step * ttcnt))),
        ttrow)

box = Difference() (
        Translate(y=-mold_rad - padding  / 2.0 - 1, z=-mold_rad - 2, x=-1)( Cube(x=12, z=mold_height + 2, y=(step * ttcnt) + 2)),
        Translate(y=-mold_rad - padding  / 2.0, z=-mold_rad - 1, x=-3)( Cube(x=13, z=mold_height + 1, y=(step * ttcnt)))
        )


bitemark = Union()(
    # main
    Cylinder(h=8, r=nail_rad, fn=40),
    Translate(y=nail_rad * 3)(
        Cylinder(h=8, r=nail_rad, fn=40),
    )
)

biterow = Union()(*[Translate(y=step * idx)(bitemark) for idx in range(ttcnt)])

lid = Difference() (
    Translate(y=-mold_rad - padding  / 2.0 - 2, z=mold_height - mold_rad - 2, x=-12)( Cube( x = 24, y = (step * ttcnt) + 4, z = 4)),
    Translate(y=-mold_rad - padding  / 2.0, z=-mold_rad - 1, x=-10)( Cube(x=20, z=mold_height + 1, y=(step * ttcnt))),
    box,
    Translate(z=mold_height - mold_rad - 4, y=-2.5)(biterow)
)

scene = Union()(Rotate(y=90)(mold))
scene = Union()(Rotate(y=90)(mold, box))
scene = Union()(lid, box, mold)
scene = Union()(lid)
scene.render("mold.scad")
scene.render("mold.stl")
