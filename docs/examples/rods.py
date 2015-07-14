from scad import *
import math

rod = Cylinder(diameter=2, height=20, fn=20, center=True)
rod = Rotate(x=90)(rod)
rods = []
for index in range(30):
    _rod = Rotate(z=(360.0 / 30) * index)(rod)
    _rod = Translate(z=index * 1)(_rod)
    rods.append(_rod)
rods = Union()(*rods)
rods.render("rods.scad")
rods.render("rods.png")
rods.render("rods.stl")
