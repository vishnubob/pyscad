#!/usr/bin/env python

from scad import *
import math

# white board marker dia: 17.8mm
# stepper motor height: 46.9mm
# stepper motor width: 42mm
# stepper motor depth: 42mm

class StepperMotor(SCAD_Object):
    stepper_height = 47
    stepper_width = 42.3 + .2
    stepper_depth = 42.3 + .2
    stepper_bodycut = 54
    center_standoff_dia = 22
    center_standoff_height = 5
    stepper_screw_offset = 31 / 2.0
    stepper_screw_length = 5
    stepper_screw_dia = 3.1 + .3

    def scad(self):
        body = Cube(x=self.stepper_width, y=self.stepper_depth, z=self.stepper_height, center=True)
        body_cut = Cube(x=self.stepper_bodycut, y=self.stepper_bodycut, z=self.stepper_height, center=True)
        body_cut = Rotate(z=45)(body_cut)
        # standoff
        center_standoff = Cylinder(dia=self.center_standoff_dia, h=self.center_standoff_height, center=True)
        center_standoff = Translate(z=(self.stepper_height + self.center_standoff_height) / 2.0)(center_standoff)
        # screw posts
        screw_post = Cylinder(dia=self.stepper_screw_dia, h=self.stepper_screw_length, center=True)
        screw_post = Translate(z=(self.stepper_screw_length + self.stepper_height) / 2.0)(screw_post)
        post1 = Translate(x=self.stepper_screw_offset, y=self.stepper_screw_offset)(screw_post)
        post2 = Translate(x=-self.stepper_screw_offset, y=self.stepper_screw_offset)(screw_post)
        post3 = Translate(x=-self.stepper_screw_offset, y=-self.stepper_screw_offset)(screw_post)
        post4 = Translate(x=self.stepper_screw_offset, y=-self.stepper_screw_offset)(screw_post)
        stepper = Intersection()(body, body_cut)
        stepper = Union()(stepper, center_standoff, post1, post2, post3, post4)
        return stepper

class StepperMotorChassis(StepperMotor):
    #chassis_height = StepperMotor.stepper_height + 2
    chassis_height = 4
    chassis_width = StepperMotor.stepper_width + 2
    chassis_depth = StepperMotor.stepper_depth + 2

    def scad(self):
        stepper = super(StepperMotorChassis, self).scad()
        body = Cube(x=self.chassis_width, y=self.chassis_depth, z=self.chassis_height, center=True)
        if self.chassis_height > self.stepper_height:
            zoffset = 2 - (self.chassis_height - self.stepper_height) / 2.0
        else:
            zoffset = (self.stepper_height - self.chassis_height) / 2.0 + 2
        body = Translate(z=(zoffset))(body)
        cut1 = Cube(x=self.chassis_width + 2, y=self.chassis_depth - 13, z=self.chassis_height - 4, center=True)
        cut2 = Cube(x=self.chassis_width - 13, y=self.chassis_depth + 2, z=self.chassis_height - 4, center=True)
        cut = Translate(z=-4)(cut1, cut2)
        chassis = Difference()(body, stepper, cut)
        return chassis

class Pulley(SCAD_Object):
    shaft_radius = 2.6
    collar_radius = shaft_radius * 2
    collar_thickness = 4
    ball_dia = 2.4
    ball_spacing = .3
    ball_spacing_thickness = 0.5
    ball_count = 20
    pulley_circ = ball_count * ball_dia + ball_count * ball_spacing
    pulley_radius = pulley_circ / (2 * math.pi)
    pulley_thickness = 6
    screw_dia = 2.5

    def get_balls(self):
        balls = []
        ball = Sphere(dia=self.ball_dia * 1.05)
        for ballidx in range(self.ball_count):
            angle = ballidx * (2 * math.pi / self.ball_count)
            x = math.cos(angle) * (self.pulley_radius)
            y = math.sin(angle) * (self.pulley_radius)
            obj = Translate(x=x, y=y)(ball)
            balls.append(obj)
        balls = Union()(*balls)
        return balls

    def pulley_top(self):
        pulley_top = Cylinder(R1=self.pulley_radius, R2=self.pulley_radius + 1, h=self.pulley_thickness / 2.0, center=True, padding=1.2)
        pulley_top = Translate(z=self.pulley_thickness / 4.0)(pulley_top)
        center_shaft = Cylinder(r=self.shaft_radius, h=self.pulley_thickness * 2, center=True)()
        key = Cube(x=2, y=2, z=1, center=True)()
        key1 = Translate(x=(2 * self.shaft_radius + 1) / 2.0, z=-.5)(key)
        key2 = Translate(x=(2 * self.shaft_radius + 1) / -2.0, z=-.5)(key)
        pulley_top = Union()(pulley_top, key1, key2)
        pulley_top = Difference()(pulley_top, center_shaft)
        return pulley_top

    def pulley_bottom(self):
        pulley_bottom = Pipe(oR1=self.pulley_radius + 1, iR1=self.shaft_radius, oR2=self.pulley_radius, iR2=self.shaft_radius, h=self.pulley_thickness / 2.0, center=True, padding=1.2)
        pulley_bottom = Translate(z=self.pulley_thickness / -4.0)(pulley_bottom)
        key = Cube(x=2, y=2, z=1.1, center=True)()
        key1 = Translate(x=(2 * self.shaft_radius + 1) / 2.0, z=-.5)(key)
        key2 = Translate(x=(2 * self.shaft_radius + 1) / -2.0, z=-.5)(key)
        key3 = Translate(y=(2 * self.shaft_radius + 1) / 2.0, z=-2.55)(key)
        key4 = Translate(y=(2 * self.shaft_radius + 1) / -2.0, z=-2.55)(key)
        pulley_bottom = Difference()(pulley_bottom, key1, key2, key3, key4)
        return pulley_bottom

    def pulley_full(self):
        pulley_top = self.pulley_top()
        pulley_bottom = self.pulley_bottom()
        pulley = Union()(pulley_bottom, pulley_top)
        return pulley

    def pulley(self, mode="full"):
        func = "pulley_" + mode
        func = getattr(self, func)
        pulley = func()
        balls = self.get_balls()
        pulley = Difference()(pulley, balls)
        return pulley

    def collar(self):
        collar = Pipe(oR=self.collar_radius, iR=self.shaft_radius, h=self.collar_thickness, center=True, padding=1.2)
        collar = Translate(z=(self.collar_thickness + self.pulley_thickness) / 2.0)(collar)
        collar_screw = Cylinder(dia=self.screw_dia, h=self.collar_thickness * 2)
        cs1 = Rotate(x=90)(collar_screw)
        cs2 = Rotate(y=90)(collar_screw)
        collar_screws = Translate(z=(self.collar_thickness + self.pulley_thickness) / 2.0)(cs1, cs2)
        collar = Difference()(collar, collar_screws)
        return collar

    def scad(self):
        return self.pulley()

def render(obj, fn):
    _fn = fn + '.scad'
    _obj = SCAD_Globals(fn=20)(obj)
    _obj.render(_fn)
    _fn = fn + '.stl'
    if not os.path.exists(_fn):
        _obj = SCAD_Globals(fn=50)(obj)
        _obj.render(_fn)

pulley = Pulley()
render(pulley, "pulley")
render(pulley.pulley("top"), "pulley_top")
render(pulley.pulley("bottom"), "pulley_bottom")
#
stepper = StepperMotor()
render(stepper, "stepper")
#
chassis = StepperMotorChassis()
render(chassis, "chassis")
