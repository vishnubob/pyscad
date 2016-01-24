import math
from scad import *

gear1 = Gear(center=True)
gear1.gear.number_of_teeth = 20
gear1.gear.module = 2
gear1.gear.pressure_angle = math.radians(20)
gear1.height = 5

gear2 = Gear(center=True)
gear2.gear.number_of_teeth = 10
gear2.gear.module = 2
gear2.gear.pressure_angle = math.radians(20)
gear2.height = 5

x_offset = (gear1.gear.pitch_radius + gear2.gear.pitch_radius)
bore = Cylinder(dia=5, h=6, center=True, fn=20)
gear1 = Difference()(gear1, bore)
gear2 = Difference()(gear2, bore)
gear2 = rotate(z=33)(gear2)
gear2 = Translate(x=x_offset)(gear2)

gears = Union()(gear1, gear2)
gears.render("gear.scad")
