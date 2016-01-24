#!/usr/bin/env python

from scad import *

class CalibrationTest(SCAD_Object):
    Defaults = {
        "thickness": {"type": float, "default": 0.4}
    }

class CubeTest(CalibrationTest):
    Defaults = {
        "outer": {"type": cube},
        "_inner": {"type": cube, "default": None},
        "bottom_width": {"type": float, "default": 0.0},
        "x": {"type": float, "default": 1.0},
        "y": {"type": float, "default": 1.0},
        "z": {"type": float, "default": 1.0},
    }

    @property
    def inner(self):
        icube = Cube(x=self.x - self.thickness * 2, y=self.y - self.thickness * 2, z=self.z, center=True)
        icube = Translate(z=self.bottom_width)(icube)
        return icube

    def render_scad(self):
        self.outer = Cube(x=self.x, y=self.y, z=self.z, center=True)
        cube = Difference()(self.outer, self.inner)
        return cube.render_scad()

class CylinderTest(CalibrationTest):
    Defaults = {
        "cylinder": {"type": cylinder},
    }

    @property
    def inner(self):
        icube = Cube(x=self.x - self.thickness * 2, y=self.y - self.thickness * 2, z=self.z, center=True)
        icube = Translate(z=self.bottom_width)(icube)
        return icube

    def render_scad(self):
        self.outer = Cube(x=self.x, y=self.y, z=self.z, center=True)
        cube = Difference()(self.outer, self.inner)
        return cube.render_scad()

sizes = [1, 5, 10, 20]
for sz in sizes:
    c = CubeTest(x=sz, y=sz, z=sz, thickness=0.4)
    fn = "cube_test_%d" % sz
    c.render(fn + ".scad")
    c.render(fn + ".stl")
