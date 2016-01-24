#!/usr/bin/env python

from scad import *

class MotorMount(SCAD_Object):
    height = 15
    depth = 25
    thickness = 2
    plate_height = 40
    motor_mount_screw_dia = 3.5
    motor_mount_slide_length = 10
    nema17_bolt_distance = 31
    nema17_center_hole_dia = 25
    mount_bolt_distance = 55
    mount_bolt_dia = 4
    mount_bolt_height_offset = 0
    motor_dugout = 42
    width = mount_bolt_distance + mount_bolt_dia + thickness + 4
    pully_bolt_dia = 3.5

    def motor_holes(self):
        hdis = self.nema17_bolt_distance / 2.0
        h1 = Cylinder(dia=self.motor_mount_screw_dia, h=self.height * 2, center=True)
        h2 = Translate(y=self.motor_mount_slide_length)(h1)
        hole = Hull()(h1, h2)
        holes = []
        for x_offset in [hdis, -hdis]:
            for y_offset in [hdis, -hdis]:
                holes.append(Translate(x=x_offset, y=y_offset)(hole))
        center_hole_1 = Cylinder(dia=self.nema17_center_hole_dia, h=self.height * 2, center=True)
        center_hole_2 = Translate(y=self.motor_mount_slide_length)(center_hole_1)
        center_hole = Hull()(center_hole_1, center_hole_2)
        holes.append(center_hole)
        holes = Union()(*holes)
        return holes

    def pully_hole(self):
        hdis = self.pully_bolt_dia / 2.0
        h1 = Cylinder(dia=self.motor_mount_screw_dia, h=self.height * 2, center=True)
        h2 = Translate(y=self.motor_mount_slide_length)(h1)
        hole = Hull()(h1, h2)
        return hole

    def scad(self):
        mount = Cube(x=self.width, y=self.depth, z=self.height, center=True)
        # dugout
        dugout = Cube(x=self.motor_dugout, y=self.depth, z=self.height - self.thickness, center=True)
        dugout = Translate(z=-self.thickness, y=-self.thickness)(dugout)
        mount = Difference()(mount, dugout)
        mount = Translate(y=self.depth / -2.0)(mount)
        #holes = self.motor_holes()
        holes = self.pully_hole()
        holes = Translate(y=-19)(holes)
        mount = Difference()(mount, holes)
        mount = Translate(z=self.height / -2.0)(mount)
        # mount bolts
        bolt = Cylinder(dia=self.mount_bolt_dia, h=50, center=True)
        bolt = Rotate(x=90)(bolt)
        bolt = Union()(bolt)
        bolt = Translate(z=self.motor_mount_screw_dia / -2.0 - self.thickness)(bolt)
        _side = 8.5
        bolt_shroud = Cube(x=_side + 2,  y=self.depth, z=self.height, center=True)
        bolt_shroud_1 = Translate(y=self.depth / -2.0 - self.thickness - 1, x=-(self.width - _side) / 2.0, z=self.height / -2.0)(bolt_shroud)
        bolt_shroud_2 = Translate(y=self.depth / -2.0 - self.thickness - 1, x=(self.width - _side) / 2.0, z=self.height / -2.0)(bolt_shroud)

        bolt1 = Translate(x=self.mount_bolt_distance / 2.0)(bolt)
        bolt2 = Translate(x=self.mount_bolt_distance / -2.0)(bolt)
        bolts = Union()(bolt1, bolt2)
        bolts = Translate(z=self.mount_bolt_height_offset - 1)(bolts)
        bolts = Union()(bolts, bolt_shroud_1, bolt_shroud_2)
        body = Difference()(mount, bolts)
        return body

mm = MotorMount()
mm.render("motor_mount.scad")
mm = SCAD_Globals(fn=20)(mm)
mm.render("motor_mount.stl")
