#!/usr/bin/env python
from scad import *
import os

class Squiggly(SCAD_Object):
    def scad(self):

sq = Squiggly()
sq = SCAD_Globals(fn=100)(dpa)
sq.render("squiggly.scad")
if not os.path.exists("squiggly.stl"):
    sq.render("squiggly.stl")
