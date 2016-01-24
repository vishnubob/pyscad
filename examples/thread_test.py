from scad import *
import os

body = Threads(pitch=1, diameter=6, height=10, fn=20)
head = Cylinder(h=3, radius=4, center=True, fn=6)
screw = Union()(body, head)
screw.render("helix.scad")
if not os.path.exists("helix.stl"):
    screw.render("helix.stl")
