#!/usr/bin/env python
import os
from scad import *

class LimitSwitchMount(SCAD_Object):
    mount_x = 10
    mount_y = 25
    mount_z = 2
    offset_z = 3.10
    base_x = 10
    base_y = 12
    base_z = mount_z + offset_z

    def scad(self):
        base = Cube(x=self.base_x, y=self.base_y, z=self.base_z, center=True)
        screw_hole = Cube(x=4.5, y=self.base_x - 3, z=self.base_z + 2, center=True)
        base = Difference()(base, screw_hole)
        #
        mount = Cube(x=self.mount_x, y=self.mount_y, z=self.mount_z, center=True)
        screw_hole = Cube(x=3.5, y=self.mount_y - 3, z=self.mount_z + 2, center=True)
        mount = Difference()(mount, screw_hole)
        mount = Translate(y=(self.base_y + self.mount_y) / -2.0, z=(self.base_z - self.mount_z) / 2.0)(mount)
        #
        body = Union()(mount, base)
        body = SCAD_Globals(fn=40)(body)
        return body

d = LimitSwitchMount()
d.render("limit_switch.scad")
if not os.path.exists("limit_switch.stl"):
    d.render("limit_switch.stl")
