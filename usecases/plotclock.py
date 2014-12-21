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
    pivot_shaft_dia = 7.3 + 0.4
    pivot_tip_dia = 4.3
    length = 19.5 + 0.5
    height = 4.23
    arm_height = 1.5
    arm_long_width = 5.45 + .05
    arm_short_width = 4.2 + .1

    def scad(self):
        x_offset = self.length - (self.pivot_shaft_dia / 2.0 + self.pivot_tip_dia / 2.0)
        points = [[1, self.arm_long_width / 2.0], [x_offset, self.arm_short_width / 2.0], [x_offset, self.arm_short_width / -2.0], [1, self.arm_long_width / -2.0]]
        middle = Polygon(points=points)
        middle = LinearExtrude(h=self.arm_height, center=True)(middle)
        pivot = Pipe(iD=self.pivot_shaft_inner_dia, oD=self.pivot_shaft_dia, h=self.height, center=True)
        pivot = Translate(z=(self.height / -2.0) + self.arm_height)(pivot)
        tip = Cylinder(dia=self.pivot_tip_dia, h=self.arm_height, center=True)
        tip = Translate(x=x_offset)(tip)
        middle = Translate(z=self.arm_height / 2.0)(middle, tip)
        arm = Union()(pivot, middle)
        return arm

class Arm(SCAD_Object):
    linkage_width = 7
    linkage_height = ServoArm.arm_height + 1
    #
    pivot_inner_dia = 3.2
    pivot_dia = pivot_inner_dia + 5
    pivot_height = linkage_height

    def linkage(self, length):
        linkage = Cube(y=self.linkage_width, z=self.linkage_height, x=length, center=True)
        return linkage

    def pivot(self):
        pivot = Pipe(iD=self.pivot_inner_dia, oD=self.pivot_dia, h=self.pivot_height, center=True)
        return pivot

class AftArm(Arm):
    linkage_length = 35
    shaft_pivot_height = Servo.shaft_height
    shaft_pivot_inner_dia = Servo.shaft_inner_dia
    shaft_pivot_dia = ServoArm.pivot_shaft_dia + 4

    def scad(self):
        linkage = self.linkage(self.linkage_length)
        z_offset = self.linkage_height / 2.0
        x_offset = (self.linkage_length + self.shaft_pivot_inner_dia) / 2.0
        linkage = Translate(x=x_offset, z=z_offset)(linkage)
        pivot = self.pivot()
        pivot_offset = self.linkage_length + (self.shaft_pivot_inner_dia + self.pivot_inner_dia) / 2.0
        pivot = Translate(x=pivot_offset, z=z_offset)(pivot)
        # servo shaft binding
        shaft_offset_x = self.linkage_length / 2.0 + self.shaft_pivot_inner_dia / 2.0
        shaft_pivot = Pipe(iD=self.shaft_pivot_inner_dia, oD=self.shaft_pivot_dia, h=self.linkage_height, center=True)
        shaft_pivot = Translate(z=z_offset)(shaft_pivot)
        shaft_pivot_offset_z = (self.shaft_pivot_height - self.linkage_height) / -2.0
        servo_arm = ServoArm()
        aftarm = Difference()(Union()(linkage, shaft_pivot, pivot), servo_arm)
        #aftarm = Difference()(Union()(linkage, shaft_pivot), servo_arm)
        return aftarm

class LiftArm(AftArm):
    linkage_length = 8

class ForeArm(Arm):
    linkage_length = 45

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

class PenCup(SCAD_Object):
    cup_height = 6
    cup_thickness = 4
    cup_lower_inner_dia = 9.65 + 0.5
    cup_upper_inner_dia = 9.88 + 0.5
    cup_dia = cup_lower_inner_dia + cup_thickness
    set_screw_dia = 2.5

    def scad(self):
        cup = Pipe(id1=self.cup_lower_inner_dia, od1=self.cup_dia, id2=self.cup_upper_inner_dia, od2=self.cup_dia, h=self.cup_height, center=True)
        set_screw = Cylinder(d=self.set_screw_dia, h=self.cup_thickness + 1, center=True)
        set_screw = Rotate(y=90)(set_screw)
        x_offset = self.cup_dia / 2.0
        set_screw = Translate(x=x_offset)(set_screw)
        #cup = Difference()(cup, set_screw)
        return cup

class ForeArmPen(ForeArm):
    linkage_pen_length = 13
    linkage_rotation = 45

    def scad(self):
        _forearm = super(ForeArmPen, self).scad()
        # pivots
        cup = PenCup()
        x_offset = (PenCup.cup_lower_inner_dia + self.linkage_pen_length) / 2.0
        z_offset = (PenCup.cup_height - self.linkage_height) / 2.0
        cup = Translate(x=x_offset, z=z_offset)(cup)
        linkage = self.linkage(self.linkage_pen_length)
        linkage = Union()(linkage, cup)
        linkage = Translate(x=self.linkage_pen_length / 2.0)(linkage)
        linkage = Rotate(z=self.linkage_rotation)(linkage)
        offset = (self.linkage_length + self.pivot_inner_dia) / 2.0
        linkage = Translate(x=offset)(linkage)
        x_offset = math.cos(math.radians(self.linkage_rotation)) * (self.pivot_inner_dia / 2.0)
        y_offset = math.sin(math.radians(self.linkage_rotation)) * (self.pivot_inner_dia / 2.0)
        linkage = Translate(x=x_offset, y=y_offset)(linkage)
        forearm = Union()(linkage, _forearm)
        return forearm

class BasePlate(SCAD_Object):
    plate_length = 80
    plate_width = 80
    plate_thickness = Arm.linkage_height
    # plate pivot
    pivot_plate_length = plate_thickness * 3 + 0.2
    pivot_plate_width = 20
    pivot_plate_thickness = Arm.linkage_height
    # pillars
    pillar_inner_dia = 2.5
    pillar_dia = pillar_inner_dia + 3
    pillar_x_spread = (plate_width - pillar_dia) / 2.0 - 1
    pillar_y_spread = (plate_length - pillar_dia) / 2.0 - 1
    pillar_height = 40
    # pivot
    pivot_inner_dia = Arm.pivot_inner_dia
    pivot_dia = pivot_inner_dia + 5
    pivot_height = Arm.linkage_height
    # servo mount
    screw_offset = Servo.servo_width / 2.0 + 2.4
    screw_dia = 1.9
    servo_mount_width = Servo.servo_width + 10
    servo_mount_height = Servo.servo_depth - 0.01
    servo_mount_thickness = plate_thickness
    draw_servo = True

    def scad(self):
        plate = Cube(x=self.plate_length, y=self.plate_width, z=self.plate_thickness, center=True)
        # servo hole
        servo = Servo()
        if self.draw_servo:
            servo_body = servo.servo()
        else:
            servo_body = servo.servo_body()
        servo_body = Rotate(z=90, x=90)(servo_body)
        z_offset = (servo.servo_depth + self.plate_thickness) / 2.0
        x_offset = -(self.servo_mount_thickness + Servo.ears_height)
        servo_body = Translate(z=z_offset, x=x_offset)(servo_body)
        servo_mount = Cube(y=self.servo_mount_width, x=self.servo_mount_thickness, z=self.servo_mount_height, center=True)
        z_offset = (self.servo_mount_height + self.plate_thickness) / 2.0
        servo_mount = Translate(z=z_offset)(servo_mount)
        if self.draw_servo:
            servo_mount = Union()(servo_mount, servo_body)
        else:
            servo_mount = Difference()(servo_mount, servo_body)
        screw_hole = Cylinder(d=self.screw_dia, h=self.servo_mount_thickness + 2, center=True)
        screw_hole = Rotate(y=90)(screw_hole)
        z_offset = (self.plate_thickness + Servo.servo_depth) / 2.0
        y_offset = self.screw_offset
        screw_hole1 = Translate(z=z_offset, y=y_offset)(screw_hole)
        screw_hole2 = Translate(z=z_offset, y=-y_offset)(screw_hole)
        servo_mount = Difference()(servo_mount, screw_hole1, screw_hole2)
        plate = Union()(servo_mount, plate)
        # pillars
        pillar = Pipe(iD=self.pillar_inner_dia, oD=self.pillar_dia, h=self.pillar_height, center=True)
        z_offset = (self.pillar_height + self.plate_thickness) / 2.0
        pillar = Translate(z=z_offset)(pillar)
        pillar1 = Translate(x=self.pillar_x_spread, y=self.pillar_y_spread)(pillar)
        pillar2 = Translate(x=-self.pillar_x_spread, y=self.pillar_y_spread)(pillar)
        pillar3 = Translate(x=self.pillar_x_spread, y=-self.pillar_y_spread)(pillar)
        pillar4 = Translate(x=-self.pillar_x_spread, y=-self.pillar_y_spread)(pillar)
        pillars = Union()(pillar1, pillar2, pillar3, pillar4)
        # pivot plate
        pivot = Cube(x=self.pivot_dia, y=self.pivot_dia, z=self.pivot_height, center=True)
        pivot_hole = Cylinder(d=self.pivot_inner_dia, h=self.pivot_height + 2, center=True)
        pivot = Difference()(pivot, pivot_hole)
        pivot = Rotate(y=90)(pivot)
        z_offset = (self.pivot_height + self.pivot_dia) / 2.0
        y_offset = (self.pivot_plate_width - self.pivot_dia) / 2.0
        x_offset = (self.pivot_plate_length - self.pivot_plate_thickness) /  2.0
        pivot1 = Translate(z=z_offset, x=x_offset, y=y_offset)(pivot)
        pivot2 = Translate(z=z_offset, x=-x_offset, y=y_offset)(pivot)
        pivot_plate = Cube(x=self.pivot_plate_length, y=self.pivot_plate_width, z=self.pivot_plate_thickness, center=True)
        pivot_plate = Union()(pivot1, pivot2, pivot_plate)
        y_offset = (self.plate_width + self.pivot_plate_width) / 2.0
        pivot_plate = Translate(y=y_offset)(pivot_plate)
        plate = Union()(plate, pivot_plate, pillars)
        return plate

class ServoPlate(SCAD_Object):
    plate_length = 80
    plate_width = 20
    plate_thickness = Arm.linkage_height
    servo_spread = 20
    screw_offset = Servo.servo_width / 2.0 + 2.4
    screw_dia = 1.9
    #
    divider_height = 32
    divider_width = 2
    divider_depth = plate_width
    #
    hinge_dia = Arm.pivot_dia
    hinge_inner_dia = Arm.pivot_inner_dia
    hinge_height = divider_width
    #
    pivot_dia = Arm.pivot_dia
    pivot_inner_dia = Arm.pivot_inner_dia
    pivot_height = divider_width
    #
    height = divider_height + plate_thickness

    def scad(self):
        # servo holes
        servo = Servo()
        servo_body = servo.servo_body()
        x_offset = (servo.servo_width + self.servo_spread) / 2.0
        servo_body1 = Translate(x=x_offset)(servo_body)
        servo_body2 = Translate(x=-x_offset)(servo_body)
        # screw holes
        screw_hole = Cylinder(dia=self.screw_dia, h=self.plate_thickness + 1, center=True)
        screw_hole1 = Translate(x=x_offset + self.screw_offset)(screw_hole)
        screw_hole2 = Translate(x=x_offset - self.screw_offset)(screw_hole)
        screw_hole3 = Translate(x=-x_offset + self.screw_offset)(screw_hole)
        screw_hole4 = Translate(x=-x_offset - self.screw_offset)(screw_hole)
        screw_holes = Union()(screw_hole1, screw_hole2, screw_hole3, screw_hole4)
        plate = Cube(x=self.plate_length, y=self.plate_width, z=self.plate_thickness, center=True)
        plate = Difference()(plate, servo_body1, servo_body2, screw_holes)
        # divider
        divider = Cube(x=self.divider_width, y=self.divider_depth, z=self.divider_height, center=True)
        # divider : corner
        corner = Cube(x=self.divider_width + 2, y=self.hinge_dia / 2.0 + 0.1, z=self.hinge_dia / 2.0 + 0.1, center=True)
        z_offset = (self.divider_height - self.hinge_dia / 2.0) / 2.0
        y_offset = (self.divider_depth - self.hinge_dia / 2.0) / 2.0
        corner = Translate(z=z_offset, y=y_offset)(corner)
        divider = Difference()(divider, corner)
        # diver : hinge
        divider_hinge = Cylinder(dia=self.hinge_dia, h=self.hinge_height, center=True)
        divider_hinge_inner = Cylinder(dia=self.hinge_inner_dia, h=self.divider_width + 1, center=True)
        divider_hinge = Rotate(y=90)(divider_hinge)
        divider_hinge_inner = Rotate(y=90)(divider_hinge_inner)
        z_offset = (self.divider_height - self.hinge_dia) / 2.0
        y_offset = (self.divider_depth - self.hinge_dia) / 2.0
        divider_hinge = Translate(z=z_offset, y=y_offset)(divider_hinge)
        divider_hinge_inner = Translate(z=z_offset, y=y_offset)(divider_hinge_inner)
        divider = Union()(divider, divider_hinge)
        # divider : pivot
        divider_pivot = Cylinder(d=self.pivot_inner_dia, h=self.pivot_height + 1, center=True)
        divider_pivot = Rotate(y=90)(divider_pivot)
        z_offset = 0
        y_offset = (self.divider_depth - self.pivot_dia) / -2.0
        divider_pivot = Translate(z=z_offset, y=y_offset)(divider_pivot)
        # divider : translation
        divider = Difference()(divider, divider_pivot, divider_hinge_inner)
        y_offset = (self.divider_depth + self.plate_width) / 2.0 - self.divider_depth
        z_offset = self.divider_height / 2.0
        divider = Translate(y=y_offset, z=z_offset)(divider)
        plate = Union()(divider, plate)
        return plate

class Plotter(SCAD_Object):
    def scad(self):
        base_plate = BasePlate()
        servo_plate = ServoPlate()
        z_offset = servo_plate.height
        y_offset = (base_plate.plate_width + servo_plate.plate_width) / 2.0
        servo_plate = Translate(z=-z_offset, y=y_offset)(servo_plate)
        servo_plate = Rotate(x=180, z=180)(servo_plate)
        lift_arm = LiftArm()
        lift_arm = Rotate(y=-90, z=180)(lift_arm)
        y_offset = (Servo.servo_width - Servo.pedestal_dia) / 2.0
        x_offset = 12
        z_offset = (BasePlate.plate_thickness + Servo.servo_depth) / 2.0
        lift_arm = Translate(x=x_offset, y=y_offset, z=z_offset)(lift_arm)
        plotter = Union()(lift_arm, base_plate, servo_plate)
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
forearmpen = ForeArmPen()
render(forearmpen, "fore_arm_pen")
pencup = PenCup()
render(pencup, "pencup")
servo_plate = ServoPlate()
render(servo_plate, "servo_plate")
base_plate = BasePlate()
render(base_plate, "base_plate")
lift_arm = LiftArm()
render(lift_arm, "lift_arm")
