#!/usr/bin/env python

from scad import *
import os

class HalfSphere(SCAD_Object):
    size = inch2mm(1)

    def scad(self):
        ball = Sphere(d=self.size, center=True, fn=50)
        box = Cube(x=self.size, y=self.size, z=self.size, center=True)
        box = Translate(z=self.size / -2.0)(box)
        body = Difference()(ball, box)
        return body

hs = HalfSphere()
hs.render("half_sphere.scad")
if not os.path.exists("half_sphere.stl"):
    hs.render("half_sphere.stl")
