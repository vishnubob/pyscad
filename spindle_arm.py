#!/usr/bin/env python
from scad import *
import os

class SpindleArm(SCAD_Object):
    shaft_dia = inch2mm(1/8.0)
    dialind_dia = inch2mm(3/8.0)
    margin = inch2mm(1/8.0) * 1.1
    width = inch2mm(2.5) * 1.1
    depth = dialind_dia + margin
    height = inch2mm(.25)
    corner_dia = inch2mm(1/4.0)
    #
    tap_dia = 2.5
    tap_height = margin + 8

    def scad(self):
        body = Cube(x=self.width, y=self.depth, z=self.height / 2.0, center=True)
        corner = Sphere(dia=self.height / 2.0, center=True, fn=10)
        body = Minkowski()(body, corner)
        shaft_hole = Cylinder(dia=self.shaft_dia, h=self.height + 1, center = True)
        x_offset = (self.width - self.shaft_dia) / 2.0 - self.margin
        shaft_hole = Translate(x=x_offset)(shaft_hole)
        dialind_hole = Cylinder(dia=self.dialind_dia, h=self.height + 1, center = True)
        x_offset = (self.width - self.dialind_dia) / -2.0 + self.margin
        dialind_hole = Translate(x=x_offset)(dialind_hole)
        # tap holes
        tap = Cylinder(dia=self.tap_dia, h=self.tap_height, center=True)
        tap = Rotate(y=90)(tap)
        x_offset = (self.width + self.tap_height) / 2.0 - self.margin - 1
        tap1 = Translate(x=x_offset)(tap)
        x_offset = (self.width + self.tap_height) / -2.0 + self.margin + 1
        tap2 = Translate(x=x_offset)(tap)
        arm = Difference()(body, shaft_hole, dialind_hole, tap1, tap2)
        return arm

arm = SpindleArm()
arm = SCAD_Globals(fn=40)(arm)
arm.render("spindle_arm.scad")
if not os.path.exists("spindle_arm.stl"):
    arm.render("spindle_arm.stl")
