#!/usr/bin/env python

from scad import *
import math

class Servo(SCAD_Object):
    shaft_dia = 4.6
    shaft_inner_dia = 1.7
    shaft_height = 3.2
    #
    servo_width = 22.9
    servo_depth = 12.20
    servo_height = 22.7
    #
    ears_width = 32.5
    ears_depth = servo_depth
    ears_height = 2.3
    ears_offset = 15
    #
    ear_hole_dia = 2.1
    ear_hole_offset = 1
    #
    pedestal_dia = servo_depth
    pedestal_ext_dia = 4.8
    pedestal_width = 14.2
    pedestal_ext_offset = pedestal_width - pedestal_dia
    pedestal_height = 4

    def shaft(self):
        shaft = Pipe(iD=self.shaft_inner_dia, oD=self.shaft_dia, h=self.shaft_height, center=True)
        return shaft

    def pedestal(self):
        pedestal = Cylinder(dia=self.pedestal_dia, h=self.pedestal_height, center=True)
        pedestal_ext = Cylinder(dia=self.pedestal_ext_dia, h=self.pedestal_height, center=True)
        ext_offset = (self.pedestal_ext_dia + self.pedestal_dia) / -2.0 + self.pedestal_ext_offset
        pedestal_ext = Translate(x=ext_offset)(pedestal_ext)
        pedestal = Union()(pedestal, pedestal_ext)
        return pedestal
    
    def ears(self):
        ears = Cube(x=self.ears_width, y=self.ears_depth, z=self.ears_height, center=True)
        hole = Cylinder(dia=self.ear_hole_dia, h=self.ears_height, center=True)
        hole_offset = (self.ears_width / 2.0) - (self.ear_hole_dia / 2.0) - 1
        hole1 = Translate(x=hole_offset)(hole)
        hole2 = Translate(x=-hole_offset)(hole)
        ears = Difference()(ears, hole1, hole2)
        ears = Render()(ears)
        return ears

    def servo_body(self):
        body = Cube(x=self.servo_width, y=self.servo_depth, z=self.servo_height, center=True)
        return body

    def servo(self):
        body = self.servo_body()
        # ears
        ears = self.ears()
        ears_offset = self.ears_offset - (self.servo_height / 2.0) - (self.ears_height / 2.0)
        ears = Translate(z=ears_offset)(ears)
        # pedestal
        pedestal = self.pedestal()
        pedestal_offset_z = (self.servo_height + self.pedestal_height) / 2.0 
        pedestal_offset_x = (self.servo_width - self.pedestal_dia) / 2.0 
        pedestal = Translate(x=pedestal_offset_x, z=pedestal_offset_z)(pedestal)
        # shaft
        shaft = self.shaft()
        shaft_offset_z = (self.servo_height + self.shaft_height) / 2.0 + self.pedestal_height
        shaft_offset_x = (self.servo_width - self.pedestal_dia) / 2.0
        shaft = Translate(x=shaft_offset_x, z=shaft_offset_z)(shaft)
        # colors
        body = Color(colorname="blue")(body)
        ears = Color(colorname="blue")(ears)
        pedestal = Color(colorname="lightblue")(pedestal)
        shaft = Color(colorname="white")(shaft)
        # complete servo
        servo = Union()(body, ears, pedestal, shaft)
        return servo

    def scad(self):
        return self.servo()

class ServoArm(SCAD_Object):
    pivot_shaft_inner_dia = Servo.shaft_inner_dia
    pivot_shaft_dia = 7.3
    pivot_tip_dia = 4.2
    length = 19.5
    height = 4.23
    arm_height = 1.5

    def scad(self):
        x_offset = self.length - (self.pivot_shaft_dia / 2.0 + self.pivot_tip_dia / 2.0)
        points = [[1, 5.45 / 2.0], [x_offset, 4.2 / 2.0], [x_offset, 4.2 / -2.0], [1, 5.45 / -2.0]]
        middle = Polygon(points=points)
        middle = LinearExtrude(h=self.arm_height, center=True)(middle)
        pivot = Pipe(iD=self.pivot_shaft_inner_dia, oD=self.pivot_shaft_dia, h=self.height, center=True)
        tip = Cylinder(dia=self.pivot_tip_dia, h=self.arm_height, center=True)
        tip = Translate(x=x_offset)(tip)
        middle = Translate(z=(self.height - self.arm_height) / 2)(middle, tip)
        arm = Union()(pivot, middle)
        return arm

class Arm(SCAD_Object):
    linkage_width = 3
    linkage_height = 2
    #
    pivot_inner_dia = 3.3
    pivot_dia = pivot_inner_dia + 3
    pivot_height = linkage_height

    def linkage(self, length):
        linkage = Cube(y=self.linkage_width, z=self.linkage_height, x=length, center=True)
        return linkage

    def pivot(self):
        pivot = Pipe(iD=self.pivot_inner_dia, oD=self.pivot_dia, h=self.pivot_height, center=True)
        return pivot

class AftArm(Arm):
    linkage_length = 15
    shaft_pivot_height = Servo.shaft_height
    shaft_pivot_inner_dia = Servo.shaft_dia + 1.2
    shaft_pivot_dia = shaft_pivot_inner_dia + 2
    shaft_pivot_top_inner_dia = Servo.shaft_inner_dia
    shaft_pivot_top_height = 1
    dimple_count = 20
    dimple_radius = .8

    def dimples(self):
        dimple = Cube(x=self.dimple_radius, y=self.dimple_radius, z=self.shaft_pivot_height, center=True)
        step = 2 * math.pi / self.dimple_count
        radius = self.shaft_pivot_inner_dia / 2.0
        dimples = []
        for cnt in range(self.dimple_count):
            x = math.cos(step * cnt) * radius
            y = math.sin(step * cnt) * radius
            _dimple = Rotate(z=math.degrees(step*cnt) + 45)(dimple)
            _dimple = Translate(x=x, y=y)(_dimple)
            dimples.append(_dimple)
        return Union()(*dimples)

    def scad(self):
        linkage = self.linkage(self.linkage_length)
        pivot = self.pivot()
        #pivot_offset = self.linkage_length / 2.0 + (self.pivot_radius - self.pivot_inner_radius)
        pivot_offset = self.linkage_length / 2.0 + self.pivot_inner_dia / 2.0
        pivot = Translate(x=pivot_offset)(pivot)
        # servo shaft binding
        shaft_offset_x = self.linkage_length / 2.0 + self.shaft_pivot_inner_dia / 2.0
        shaft_pivot = Pipe(iD=self.shaft_pivot_inner_dia, oD=self.shaft_pivot_dia, h=self.shaft_pivot_height, center=True)
        dimples = self.dimples()
        shaft_pivot = Union()(shaft_pivot, dimples)
        shaft_pivot_top = Pipe(iD=self.shaft_pivot_top_inner_dia, oD=self.shaft_pivot_dia, h=self.shaft_pivot_top_height, center=True)
        shaft_pivot_top_offset_z = (self.shaft_pivot_height - self.shaft_pivot_top_height) / 2.0
        shaft_pivot_top = Translate(z=shaft_pivot_top_offset_z)(shaft_pivot_top)
        shaft_pivot = Union()(shaft_pivot, shaft_pivot_top)
        shaft_pivot_offset_z = (self.shaft_pivot_height - self.linkage_height) / -2.0
        shaft_pivot = Translate(x=-shaft_offset_x, z=shaft_pivot_offset_z)(shaft_pivot)
        aftarm = Union()(linkage, pivot, shaft_pivot)
        return aftarm

class ForeArm(Arm):
    linkage_length = 12

    def scad(self):
        # pivots
        pivot = self.pivot()
        pivot_offset = self.linkage_length / 2.0 + self.pivot_inner_dia / 2.0
        pivot1 = Translate(x=pivot_offset)(pivot)
        pivot2 = Translate(x=-pivot_offset)(pivot)
        # linkage
        linkage = self.linkage(self.linkage_length)
        forearm = Union()(linkage, pivot1, pivot2)
        return forearm

class Plotter(SCAD_Object):
    def scad(self):
        servo = Servo()
        x_offset = 20
        servo1 = Translate(x=-x_offset)(servo)
        servo2 = Translate(x=x_offset)(Rotate(z=180)(servo))
        #
        aftarm = AftArm()
        aftarm = Rotate(z=90)(aftarm)
        aftarm = Translate(z=20, x=15, y=7)(aftarm)
        #
        plotter = Union()(servo1, servo2, aftarm)
        return plotter

def render(obj, fn):
    _fn = fn + '.scad'
    _obj = SCAD_Globals(fn=20)(obj)
    _obj.render(_fn)
    _fn = fn + '.stl'
    if not os.path.exists(_fn):
        _obj = SCAD_Globals(fn=50)(obj)
        _obj.render(_fn)

servoarm = ServoArm()
render(servoarm, "servo_arm")
forearm = ForeArm()
render(forearm, "fore_arm")
aft_arm = AftArm()
render(aft_arm, "aft_arm")
servo = Servo()
render(servo, "servo")
plotter = Plotter()
render(plotter, "plotter")
