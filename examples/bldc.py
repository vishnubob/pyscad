from scad import *
import math
import os

class SpindleBaseHD(SCAD_Object):
    top_cyl_dia = 14.5 + 0.3
    top_cyl_height = 3.7
    mid_cyl_dia = 25 + 0.3
    mid_cyl_height = 5.0
    bot_cyl_dia = 30.2
    bot_cyl_height = 2.1
    spindle_height = top_cyl_height + mid_cyl_height - 1
    screw_count = 6
    screw_dia = 2.7
    screw_offset = (mid_cyl_dia / 2.0) - (screw_dia / 2.0) - 1.0 - 0.2
    screw_head_height = 1.5
    screw_head_dia = 3.9
    screw_height = spindle_height - screw_head_dia
    magnet_size = (1/8.0) * 25.4 + 0.2

    def base(self):
        top_cyl = Cylinder(d=self.top_cyl_dia, h=self.top_cyl_height, center=True)
        top_cyl = Translate(z=(self.top_cyl_height + self.mid_cyl_height) / 2.0)(top_cyl)
        mid_cyl = Cylinder(d=self.mid_cyl_dia, h=self.mid_cyl_height, center=True)
        radstep = (2 * math.pi) / self.screw_count
        screws = []
        for screw_idx in range(self.screw_count):
            screw = Cylinder(d=self.screw_dia, h=self.screw_height, center=True)
            screw_head = Cylinder(d1=self.screw_dia, d2=self.screw_head_dia, h=self.screw_head_height, center=True)
            z_offset = (self.screw_head_height + self.screw_height) / 2.0
            screw_head = Translate(z=z_offset)(screw_head)
            screw = Union()(screw, screw_head)
            x_offset = math.cos(radstep * screw_idx) * self.screw_offset
            y_offset = math.sin(radstep * screw_idx) * self.screw_offset
            z_offset = self.screw_height / 2.0
            screw = Translate(x=x_offset, y=y_offset, z=z_offset)(screw)
            screws.append(screw)
        screws = Union()(*screws)
        cyl = Union()(top_cyl, mid_cyl, screws)
        cyl = Translate(z=self.mid_cyl_height / 2.0)(cyl)
        return cyl

    def neck_post(self):
        self.neck_post_dia = 26
        self.neck_post_len = 20
        dia = self.screw_dia * 2.5
        escs = []
        radstep = (2 * math.pi) / self.screw_count
        for screw_idx in range(self.screw_count):
            esc = Cylinder(d1=dia, h=self.neck_post_len / 2.0, center=True)
            x_offset = math.cos(radstep * screw_idx) * (self.screw_offset + 1)
            y_offset = math.sin(radstep * screw_idx) * (self.screw_offset + 1)
            z_offset = self.neck_post_len / -4.0
            esc = Translate(x=x_offset, y=y_offset, z=z_offset)(esc)
            escs.append(esc)
        escs = Union()(*escs)
        neck_post = Cylinder(d1=self.neck_post_dia + 1, d2=self.neck_post_dia - 1, h=self.neck_post_len, center=True)
        neck_post = Difference()(neck_post, escs)
        return neck_post

    def magnet(self):
        magnet = Cube(x=self.magnet_size, y=self.magnet_size, z=self.magnet_size, center=True)
        return magnet
    
    def scad(self):
        base = self.base()
        spindle = Cylinder(d=self.mid_cyl_dia + 10, h=self.spindle_height)
        magnet = self.magnet()
        x_offset = (self.mid_cyl_dia + 10) / 2.0 - (self.magnet_size / 2.0) + 0.2
        z_offset = (self.magnet_size + self.mid_cyl_height) / 2.0
        magnet = Translate(x=x_offset, z=z_offset)(magnet)
        spindle = Difference()(spindle, base, magnet)
        neck_post = self.neck_post()
        z_offset = (self.neck_post_len / 2.0) + self.spindle_height
        neck_post = Translate(z=z_offset)(neck_post)
        spindle = Union()(spindle, neck_post)
        #spindle = Union()(spindle, base)
        spindle = SCAD_Globals(fn=50)(spindle)
        return spindle

class SpindleBase(SCAD_Object):
    top_cyl_dia = 14.5 + 0.3
    top_cyl_height = 3.7
    mid_cyl_dia = 25 + 0.3
    mid_cyl_height = 5.0
    bot_cyl_dia = 30.2
    bot_cyl_height = 2.1
    spindle_height = top_cyl_height + mid_cyl_height - 1
    screw_count = 6
    screw_dia = 2.7
    screw_offset = (mid_cyl_dia / 2.0) - (screw_dia / 2.0) - 1.0 - 0.2
    screw_head_height = 1.5
    screw_head_dia = 3.9
    screw_height = spindle_height - screw_head_dia
    magnet_size = (1/8.0) * 25.4 + 0.2

    def base(self):
        top_cyl = Cylinder(d=self.top_cyl_dia, h=self.top_cyl_height, center=True)
        top_cyl = Translate(z=(self.top_cyl_height + self.mid_cyl_height) / 2.0)(top_cyl)
        mid_cyl = Cylinder(d=self.mid_cyl_dia, h=self.mid_cyl_height, center=True)
        radstep = (2 * math.pi) / self.screw_count
        screws = []
        for screw_idx in range(self.screw_count):
            screw = Cylinder(d=self.screw_dia, h=self.screw_height, center=True)
            screw_head = Cylinder(d1=self.screw_dia, d2=self.screw_head_dia, h=self.screw_head_height, center=True)
            z_offset = (self.screw_head_height + self.screw_height) / 2.0
            screw_head = Translate(z=z_offset)(screw_head)
            screw = Union()(screw, screw_head)
            x_offset = math.cos(radstep * screw_idx) * self.screw_offset
            y_offset = math.sin(radstep * screw_idx) * self.screw_offset
            z_offset = self.screw_height / 2.0
            screw = Translate(x=x_offset, y=y_offset, z=z_offset)(screw)
            screws.append(screw)
        screws = Union()(*screws)
        cyl = Union()(top_cyl, mid_cyl, screws)
        cyl = Translate(z=self.mid_cyl_height / 2.0)(cyl)
        return cyl

    def neck_post(self):
        self.neck_post_dia = 26
        self.neck_post_len = 20
        dia = self.screw_dia * 2.5
        escs = []
        radstep = (2 * math.pi) / self.screw_count
        for screw_idx in range(self.screw_count):
            esc = Cylinder(d1=dia, h=self.neck_post_len / 2.0, center=True)
            x_offset = math.cos(radstep * screw_idx) * (self.screw_offset + 1)
            y_offset = math.sin(radstep * screw_idx) * (self.screw_offset + 1)
            z_offset = self.neck_post_len / -4.0
            esc = Translate(x=x_offset, y=y_offset, z=z_offset)(esc)
            escs.append(esc)
        escs = Union()(*escs)
        neck_post = Cylinder(d=self.neck_post_dia + 1.0, h=self.neck_post_len, center=True)
        return neck_post

    def magnet(self):
        magnet = Cube(x=self.magnet_size, y=self.magnet_size, z=self.magnet_size, center=True)
        return magnet
    
    def scad(self):
        base = self.base()
        spindle = Cylinder(d=self.mid_cyl_dia + 10, h=self.spindle_height)
        magnet = self.magnet()
        x_offset = (self.mid_cyl_dia + 10) / 2.0 - (self.magnet_size / 2.0) + 0.2
        z_offset = (self.magnet_size + self.mid_cyl_height) / 2.0
        magnet = Translate(x=x_offset, z=z_offset)(magnet)
        spinhole = Cylinder(d=8.8, h=4)
        spinhole2 = Cylinder(d2=6.5, d1=7.8, h=6)
        spinhole2 = Translate(z=4)(spinhole2)
        spinhole = Union()(spinhole, spinhole2)
        neck_post = self.neck_post()
        z_offset = (self.neck_post_len / 2.0) + self.spindle_height
        neck_post = Translate(z=z_offset)(neck_post)
        #nuthole = Cylinder(d=12, h=40, fn=6)
        nuthole = Cylinder(d=20, h=40)
        nuthole = Translate(z=8)(nuthole)
        spindle = Union()(spindle, neck_post)
        spindle = Difference()(spindle, magnet, spinhole, nuthole)
        key = Cube(y=8, x=2, z=4, center=True)
        key1 = Translate(x=4.5, z=2)(key)
        key2 = Translate(x=-4.5, z=2)(key)
        spindle = Union()(spindle, key1, key2)
        spindle = SCAD_Globals(fn=50)(spindle)
        debug = Cylinder(h=8, d=12)()
        #spindle = intersection()(debug, spindle)
        return spindle

    def balance_spindle(self):
        base = self.base()
        spindle = Cylinder(d=self.mid_cyl_dia + 10, h=self.spindle_height)
        magnet = self.magnet()
        x_offset = (self.mid_cyl_dia + 10) / 2.0 - (self.magnet_size / 2.0) + 0.2
        z_offset = (self.magnet_size + self.mid_cyl_height) / 2.0
        magnet = Translate(x=x_offset, z=z_offset)(magnet)
        spinhole = Cylinder(d=8.8, h=60, center=True)
        neck_post = self.neck_post()
        z_offset = (self.neck_post_len / 2.0) + self.spindle_height
        neck_post = Translate(z=z_offset)(neck_post)
        nuthole = Cylinder(d=22.4, h=7)
        nuthole2 = Translate(z=20.8)(nuthole)
        spindle = Union()(spindle, neck_post)
        spindle = Difference()(spindle, magnet, spinhole, nuthole, nuthole2)
        #spindle = Union()(spindle, base)
        spindle = SCAD_Globals(fn=50)(spindle)
        return spindle

    def spindle_brace(self):
        dim = 20
        shdim = 3
        offset = (dim - 2) - shdim * 0.5
        base = Cube(x=dim * 2, y=dim * 2, z=7, center=True)
        bearing = Cylinder(d=22.4, h=7, center=True)
        shole = Cylinder(d=3, h=7, center=True)
        shole1 = Translate(x=offset, y=offset)(shole)
        shole2 = Translate(x=-offset, y=offset)(shole)
        shole3 = Translate(x=-offset, y=-offset)(shole)
        shole4 = Translate(x=offset, y=-offset)(shole)
        sholes = Union()(shole1, shole2, shole3, shole4)
        brace = Difference()(base, bearing, sholes)
        brace = SCAD_Globals(fn=50)(brace)
        return brace
    
sb = SpindleBase()
sb.render("spindle.scad")
if not os.path.exists("spindle.stl"):
    sb.render("spindle.stl")

sb.balance_spindle().render("balance_spindle.scad")
if not os.path.exists("balance_spindle.stl"):
    sb.balance_spindle().render("balance_spindle.stl")

sb.spindle_brace().render("spindle_brace.scad")
if not os.path.exists("spindle_brace.stl"):
    sb.spindle_brace().render("spindle_brace.stl")
