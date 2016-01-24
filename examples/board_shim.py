#!/usr/bin/env python

from scad import *

class BoardShim(SCAD_Object):
    small_width = 21.5
    small_depth = 39
    large_width = 40.5
    large_depth = 65.5
    thickness = 2
    margin = 10
    small_screw_radius = 1.5
    large_screw_radius = 1.5

    def corners(self, xy):
        xy = [xy[0] / 2.0, xy[1] / 2.0]
        yield {'x': xy[0], 'y': xy[1]}
        yield {'x': -xy[0], 'y': xy[1]}
        yield {'x': xy[0], 'y': -xy[1]}
        yield {'x': -xy[0], 'y': -xy[1]}

    def scad(self):
        x = self.large_width + self.margin
        y = self.large_depth + self.margin
        shim = Cube(x=x, y=y, z=self.thickness, center=True)
        ss = Cylinder(r=self.small_screw_radius, h=self.thickness + 1, center=True, fn=20)
        ls = Cylinder(r=self.large_screw_radius, h=self.thickness + 1, center=True, fn=20)
        small_holes = [Translate(**kw)(ss) for kw in self.corners((self.small_width, self.small_depth))]
        large_holes = [Translate(**kw)(ls) for kw in self.corners((self.large_width, self.large_depth))]
        holes = Union()(small_holes + large_holes)
        shim = Difference()(shim, holes)
        return shim

shim = BoardShim()
shim.render("board.scad")
shim.render("board.stl")
