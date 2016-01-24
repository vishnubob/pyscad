#!/usr/bin/env python

from scad import *
import os

class WasteBoard(SCAD_Object):
    height = 13
    width = 500
    depth = 500
    flange_height = 1.3
    flange_dia = 12
    insert_height = height
    insert_dia = 9
    x_count = 10
    y_count = 10

    def insert(self):
        flange = Cylinder(d=self.flange_dia, h=self.flange_height)
        flange = Translate(z=(self.insert_height - self.flange_height + .05))(flange)
        insert = Cylinder(d=self.insert_dia, h=self.insert_height + self.flange_height)
        insert = Translate(z=-.05)(insert)
        insert = Union()(flange, insert)
        return insert

    def scad(self):
        board = Cube(width=self.width, depth=self.depth, height=self.height)
        insert = self.insert()
        inserts = []
        x_spacing = float(self.width) / self.x_count
        x_margin = (self.width - (x_spacing * (self.x_count - 1))) / 2.0
        y_spacing = float(self.depth) / self.y_count
        y_margin = (self.depth - (y_spacing * (self.y_count - 1))) / 2.0
        print "x spacing: %02fmm, y spacing %02fmm" % (x_spacing, y_spacing)
        for x in range(self.x_count):
            for y in range(self.y_count):
                _x = x * x_spacing + x_margin
                _y = y * y_spacing + y_margin
                _insert = translate(x=_x, y=_y)(insert)
                inserts.append(_insert)
        inserts = Union()(*inserts)
        board = Difference()(board, inserts)
        board = SCAD_Globals(fn=40)(board)
        return board

class QuarterWasteBoard(WasteBoard):
    width = 250
    depth = 250
    x_count = 5
    y_count = 5

#wb = WasteBoard()
#wb.render("wasteboard.scad")

qwb = QuarterWasteBoard()
qwb.render("wasteboard.scad")
if not os.path.exists("wasteboard.stl"):
    qwb.render("wasteboard.stl")
