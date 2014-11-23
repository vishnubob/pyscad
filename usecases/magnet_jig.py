#!/usr/bin/env python

from scad import *

class MagnetJig(SCAD_Object):
    inner_radius = 9.525 
    outer_radius = 15
    thickness = 1

    def scad(self):
        jig = Pipe(oR=self.outer_radius, iR=self.inner_radius, h=self.thickness)
        return jig

MagnetJig = MagnetJig()
MagnetJig.render("magnet_jig.scad")
MagnetJig.render("magnet_jig.stl")
