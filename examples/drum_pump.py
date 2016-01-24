#!/usr/bin/env python

import math
from scad import *

class DrumPumpObject(SCAD_Object):
    # pump body
    pump_body_inner_radius = 15
    pump_body_thickness = 4
    pump_body_radius = pump_body_inner_radius + pump_body_thickness
    pump_body_length = 35
    pump_body_color = "orange"

    # 
    screw_wall_dia = 15
    screw_wall_zoffset = 3
    nut_clearance = 8
    nut_height = 2.5
    endcap_length = 4
    #
    #inlet_port_radius = inch2mm(5/16.0)
    #outlet_port_radius = inch2mm(1/8.0)
    #inlet_port_radius = 5
    #outlet_port_radius = 3
    inlet_port_radius = 10
    outlet_port_radius = 10
    # block
    block_width = 30
    block_height = pump_body_thickness

    def body_transform(self, body):
        return body
    
    def posts(self, screw_post, dia, x_offset=0, y_offset=0, dia2=0, zoffset=0, h=None, width=None, height=None):
        r = dia / 2.0
        width = width or self.stage_body_width / 2.0 - r
        height = height or self.stage_body_length / 2.0 - r
        posts = [ [1, 1], [1, -1], [-1, 1], [-1, -1] ]
        res = []
        for (wp, hp) in posts:
            post = screw_post
            args = {}
            if x_offset:
                args.update({'x': wp * x_offset})
            if y_offset:
                args.update({'y': hp * y_offset})
            if args:
                post = Translate(**args)(post)
            args = {'x': width * wp, 'y': height * hp, 'z': zoffset}
            post = Translate(**args)(post)
            post = Rotate(x=90)(post)
            res.append(post)
        posts = Union()(*res)
        posts = self.body_transform(posts)
        return posts

    def screw_posts(self, dia, x_offset=0, y_offset=None, dia2=0, zoffset=0, h=None):
        if y_offset == None:
            y_offset = x_offset
        dia = dia
        post = Cylinder(d=dia, h=h, center=True)
        if dia2:
            post = Pipe(oD=dia2, iD=dia, h=h, center=True)
        return self.posts(post, dia, x_offset=x_offset, y_offset=y_offset, dia2=dia2, zoffset=zoffset, h=h)
            
    @property
    def pump_body(self):
        return DrumPump(**self.__dict__)

    @property
    def endcap_open(self):
        ec = EndCap(**self.__dict__)
        ec = Difference()(ec, Translate(z=self.pump_body_length / 2.0)(self.pump_body.outer_body))
        return ec

    @property
    def endcap_closed(self):
        ec = EndCap(closed=True, **self.__dict__)
        ec = Difference()(ec, Translate(z=self.pump_body_length / 2.0)(self.pump_body.outer_body))
        #spring = SpringPedestal()
        #pedestal = spring.spring_side
        #pedestal = Translate(z=spring.pedestal_length / 2.0)(pedestal)
        #ec = Union()(pedestal, ec)
        return ec

    @property
    def brace(self):
        return EndCap(**self.__dict__)

    @property
    def inlet_valve_stage(self):
        kw = self.__dict__.copy()
        kw["mode"] = "inlet"
        return ValveStage(**kw)

    @property
    def outlet_valve_stage(self):
        kw = self.__dict__.copy()
        kw["mode"] = "outlet"
        return ValveStage(**kw)

    @property
    def inlet_valve_head(self):
        kw = self.__dict__.copy()
        kw["mode"] = "inlet"
        return ValveHead(**kw)

    @property
    def outlet_valve_head(self):
        kw = self.__dict__.copy()
        kw["mode"] = "outlet"
        return ValveHead(**kw)

    @property
    def inlet_valve_flap(self):
        kw = self.__dict__.copy()
        kw["mode"] = "inlet"
        return ValveFlap(**kw)

    @property
    def outlet_valve_flap(self):
        kw = self.__dict__.copy()
        kw["mode"] = "outlet"
        return ValveFlap(**kw)

    @property
    def outlet_port(self):
        outlet_port = Cylinder(h=self.pump_body_thickness * 4.0, r=self.outlet_port_radius, center=True)
        outlet_port = Rotate(x=90)(outlet_port)
        outlet_port = Translate(y=self.pump_body_radius - self.pump_body_thickness / 2.0)(outlet_port)
        return outlet_port

    @property
    def inlet_port(self):
        inlet_port = Cylinder(h=self.pump_body_thickness * 4.0, r=self.inlet_port_radius, center=True)
        inlet_port = Rotate(x=90)(inlet_port)
        inlet_port = Translate(y=(self.pump_body_radius - self.pump_body_thickness / 2.0))(inlet_port)
        return inlet_port

class ValveBaseObject(DrumPumpObject):
    mode = "inlet"

    def render_scad(self, *args, **kw):
        if self.mode == "inlet":
            return self.inlet.render_scad()
        elif self.mode == "outlet":
            return self.outlet.render_scad()
        else:
            raise RuntimeError, "Unknown Valve mode: %s" % mode

    @property
    def inlet(self):
        pass

    @property
    def outlet(self):
        pass

class ValveStage(ValveBaseObject):
    valve_overlap = 3
    stage_thickness = 2.0
    #stage_inner_radius = DrumPumpObject.inlet_port_radius + valve_overlap
    stage_inner_radius = DrumPumpObject.inlet_port_radius
    stage_radius = stage_inner_radius + stage_thickness
    #stage_length = DrumPumpObject.pump_body_length * .30
    stage_length = stage_inner_radius + 2
    # lugs
    lug_radius = stage_radius + 1.5
    lug_length = 5
    lug_ring_radius = ValveBaseObject.pump_body_length / 2.0
    lug_ring_inner_radius = stage_radius

    @property
    def lugs(self):
        r = ValveHead.inlet_breech_radius + 2.0
        lugs = LugWreath(wreath_radius=self.lug_radius, 
                lug_length=self.lug_length, 
                ring_radius=self.lug_ring_radius + 2.5, 
                ring_inner_radius=self.lug_ring_inner_radius, 
                m3_nuts_top=True)
        return lugs

    @property
    def stage(self):
        stage_length = self.stage_length + self.pump_body_thickness
        lugs = self.lugs
        lugs = Translate(z=(stage_length - ValveHead.lug_length) / -2.0)(lugs)
        chamfer = Chamfer(r=self.stage_inner_radius, chamfer=2, invert=True, center=True)
        chamfer = Translate(z=stage_length / -2.0)(chamfer)
        stage = Pipe(ir=self.stage_inner_radius, oR=self.stage_radius, h=stage_length, center=True, padding=1.2)
        stage = Difference()(stage, chamfer)
        stage = Rotate(x=90)(stage, lugs)
        #stage = Rotate(x=90)(stage)
        stage = Translate(y=self.pump_body_radius + stage_length / 2.0 - self.pump_body_thickness)(stage)
        return stage

    @property
    def _inlet(self):
        stage = Color(colorname="steelblue")(self.stage)
        stage = Difference()(stage, self.pump_body.outer_body, self.inlet_port)
        return stage

    @property
    def _outlet(self):
        stage = Color(colorname="salmon")(self.stage)
        stage = Difference()(stage, self.pump_body.outer_body, self.outlet_port)
        return stage

    @property
    def _inlet(self):
        stage = Color(colorname="steelblue")(self.stage)
        base = Cylinder(r=self.stage_inner_radius, h=2, center=True)
        base = Rotate(x=90)(base)
        base = Translate(y=self.pump_body_inner_radius + 2)(base)
        #base = Difference()(base, self.valve_holes("inlet"))
        stage = Union()(stage, base)
        stage = Difference()(stage, self.pump_body.inner_body)
        return stage

    @property
    def _outlet(self):
        stage = Color(colorname="salmon")(self.stage)
        base = Cylinder(r=self.stage_inner_radius, h=8, center=True)
        base = Rotate(x=90)(base)
        base = Translate(y=self.pump_body_inner_radius - 2)(base)
        stage = Union()(stage, base)
        #stage = Difference()(stage, self.pump_body.inner_body, self.valve_holes("outlet"))
        return stage

    @property
    def inlet(self):
        stage = Color(colorname="steelblue")(self.stage)
        base = Pipe(iR=self.stage_inner_radius - 2, oR=self.stage_inner_radius, h=6, padding=1.2, center=True)
        base = Rotate(x=90)(base)
        base = Translate(y=self.pump_body_inner_radius - 2)(base)
        stage = Union()(stage, base)
        stage = Difference()(stage, self.pump_body.inner_body)
        return stage

    @property
    def outlet(self):
        stage = Color(colorname="salmon")(self.stage)
        base = Pipe(iR=self.stage_inner_radius - 2, oR=self.stage_inner_radius, h=6, padding=1.2, center=True)
        base = Rotate(x=90)(base)
        base = Translate(y=self.pump_body_inner_radius - 2)(base)
        stage = Union()(stage, base)
        stage = Difference()(stage, self.pump_body.inner_body)
        return stage

class ValvePlate(ValveBaseObject):
    plate_thickness = 2
    overlap = 2
    plate_radius = ValveStage.stage_inner_radius
    hole_radius_small = 1.7 / 2.0
    hole_radius_large = 1.9 / 2.0 + 0.2
    pre_load_height = 0.6
    pre_load_inner_radius = 2.0
    pre_load_radius = (15 / 2.0)
    lug_length = plate_thickness + 1
    lug_radius = 1.6
    lug_radius = 1.0
    wreath_radius = (12.325 / 2.0) - lug_radius * 2

    @property
    def plate(self):
        plate = Cylinder(r=self.plate_radius, h=self.plate_thickness, center=True)
        center_hole = Cylinder(r2=self.hole_radius_small, r1=self.hole_radius_large, h=self.plate_thickness + 0.05, center=True)
        plate = Difference()(plate, center_hole)
        pre_load = Pipe(ir=self.pre_load_inner_radius, oR=self.pre_load_radius, h=self.pre_load_height, padding=1.2, center=True)
        pre_load = Rotate(x=90)(pre_load)
        pre_load = Translate(y=(self.plate_thickness - self.pre_load_height) / 2.0 + 0.05)(pre_load)
        lugs = LugWreath(lug_radius=self.lug_radius, wreath_radius=self.wreath_radius, lug_length=self.lug_length, lug_count=6)
        lugs = Rotate(x=90)(lugs)
        plate = Rotate(x=90)(plate)
        #plate = Difference()(plate, pre_load, lugs)
        plate = Difference()(plate, lugs)
        return plate

class ValveHead(ValveBaseObject):
    # inlet head
    inlet_breech_length = 5
    inlet_breech_radius = ValveStage.stage_radius
    inlet_bore_length = ValveStage.stage_length + 1
    inlet_bore_radius = ValveStage.stage_inner_radius
    inlet_bore_inner_radius = ValveBaseObject.outlet_port_radius
    #inlet_bore_thickness = inlet_bore_radius - inlet_bore_inner_radius
    inlet_bore_thickness = 2
    # outlet head
    outlet_breech_length = 5
    outlet_breech_radius = ValveStage.stage_radius
    outlet_bore_length = ValveStage.stage_length + outlet_breech_length
    outlet_bore_radius = ValveStage.stage_inner_radius
    outlet_bore_thickness = 2
    outlet_bore_inner_radius = outlet_bore_radius - outlet_bore_thickness
    # lugs
    lug_radius = ValveStage.lug_radius
    lug_length = inlet_breech_length
    lug_ring_radius = ValveBaseObject.pump_body_length / 2.0
    lug_ring_inner_radius = inch2mm(.1590) / 2.0

    @property
    def lugs(self):
        r = self.inlet_breech_radius + 2.0
        lugs = LugWreath(wreath_radius=self.lug_radius, lug_length=self.lug_length, ring_radius=self.lug_ring_radius + 2, ring_inner_radius=self.lug_ring_inner_radius)
        return lugs

    @property
    def outlet(self):
        lugs = self.lugs
        lugs = Translate(z=(self.outlet_bore_length - self.outlet_breech_length) / -2.0)(lugs)
        chamfer = Chamfer(r=self.outlet_bore_radius, chamfer=2, invert=True, center=True)
        chamfer = Translate(z=self.outlet_bore_length / 2.0)(chamfer)
        bore = Pipe(oR=self.outlet_bore_radius, ir=self.outlet_bore_inner_radius, h=self.outlet_bore_length, padding=1.2, center=True)
        bore = Difference()(bore, chamfer)
        breech = Pipe(oR=self.outlet_breech_radius, ir=self.outlet_bore_inner_radius, h=self.outlet_breech_length, padding=1.2, center=True)
        breech = Translate(z=(self.outlet_bore_length - self.outlet_breech_length) / -2.0)(breech)
        head = Rotate(x=90)(bore, breech, lugs)
        head = Color(colorname="red")(head)
        return head
    
    @property
    def inlet(self):
        lugs = self.lugs
        lugs = Translate(z=(self.outlet_bore_length - self.outlet_breech_length) / -2.0)(lugs)
        chamfer = Chamfer(r=self.outlet_bore_radius, chamfer=2, invert=True, center=True)
        chamfer = Translate(z=self.outlet_bore_length / 2.0 + 2)(chamfer)
        bore = Pipe(oR=self.inlet_bore_radius, ir=self.inlet_bore_inner_radius - 2, h=self.inlet_bore_length, padding=1.2, center=True)
        bore = Translate(z=3)(bore)
        bore = Difference()(bore, chamfer)
        breech = Pipe(oR=self.inlet_breech_radius, ir=self.inlet_bore_inner_radius, h=self.inlet_breech_length, padding=1.2, center=True)
        breech = Translate(z=(self.outlet_bore_length - self.outlet_breech_length) / -2.0)(breech)
        head = Rotate(x=90)(bore, breech, lugs)
        head = Color(colorname="blue")(head)
        return head

    @property
    def inlet_debug(self):
        debug = Union(debug=True)(ValveStage().inlet)
        debug = Translate(x=60, y=-27.5)(debug)
        plate = ValvePlate().plate
        plate = Translate(y=-10.5, x=0)(plate)
        head = Union()(debug, plate, self.inlet)
        return head

class ValveFlap(ValveBaseObject):
    flap_thickness = inch2mm(1/16.0)
    flap_radius = ValveStage.stage_inner_radius * .95
    cutout_radius = flap_radius - (ValveStage.valve_overlap / 2.0 * 1.2)
    cutout_inner_radius = ValveBaseObject.outlet_port_radius * 1.3
    cutout_neck_width = cutout_inner_radius

    @property
    def ver1_flap(self):
        flap = Cylinder(r=self.flap_radius, h=self.flap_thickness, center=True)
        cutout = Pipe(oR=self.cutout_radius, iR=self.cutout_inner_radius, h=self.flap_thickness * 1.2, center=True)
        neck = cube(x=self.cutout_neck_width, y=self.flap_radius, z=self.flap_thickness * 1.2, center=True)
        neck = Translate(y=self.flap_radius / 2.0)(neck)
        cutout = Difference()(cutout, neck)
        flap = Difference()(flap, cutout)
        flap = Rotate(x=90)(flap)
        return flap

    @property
    def ver2_flap(self):
        flap = Cylinder(r=self.flap_radius, h=self.flap_thickness, center=True)
        cutout = Pipe(oR=self.cutout_radius, iR=self.cutout_inner_radius, h=self.flap_thickness * 1.2, center=True)
        neck = cube(x=self.cutout_neck_width - 2.5, y=self.flap_radius * 2, z=self.flap_thickness * 1.2, center=True)
        #neck = Translate(y=self.flap_radius / 2.0)(neck)
        cutout = Difference()(cutout, neck)
        flap = Difference()(flap, cutout)
        flap = Rotate(x=90)(flap)
        return flap

    @property
    def inlet(self):
        return self.ver2_flap

    @property
    def outlet(self):
        return self.inlet
    
    @property
    def seal(self):
        lugs = LugWreath(wreath_radius=ValveHead.lug_radius, lug_length=ValveHead.lug_length)
        seal = Pipe(iR=ValveHead.inlet_bore_radius, oR=ValveHead.lug_ring_radius, h=self.flap_thickness, center=True, padding=1.2)
        seal = Difference()(seal, lugs)
        seal = Rotate(x=90)(seal)
        return seal

class LugWreath(DrumPumpObject):
    lug_count = 3
    phase = 0
    lug_length = 5
    lug_inner_radius = 0
    lug_radius = 2.0
    wreath_radius = 3
    ring_radius = 0
    ring_inner_radius = 0
    max_angle = 360.0
    m3_nuts_top = False
    m3_nuts_bottom = False
    m3_nut_radius = 3.2
    m3_nut_height = 2.5

    @property
    def wreath(self):
        if self.max_angle < 360:
            pie_slice = float(self.max_angle) / (self.lug_count - 1)
        else:
            pie_slice = float(self.max_angle) / self.lug_count
        for idx in range(self.lug_count):
            angle = self.phase + (pie_slice * idx)
            x = math.cos(math.radians(angle)) * (self.wreath_radius + self.lug_radius)
            y = math.sin(math.radians(angle)) * (self.wreath_radius + self.lug_radius)
            yield {'x': x, 'y': y}

    @property
    def lug(self):
        if self.lug_inner_radius:
            return Pipe(iR=self.lug_inner_radius, oR=self.lug_radius, h=self.lug_length, padding=1.2, center=True)
        else:
            return Cylinder(r=self.lug_radius, h=self.lug_length + 1.2, center=True)

    @property
    def nut(self):
        nuts = []
        nut = Cylinder(r=self.m3_nut_radius, h=self.m3_nut_height + 0.1, fn=6, center=True)
        if self.m3_nuts_top:
            _nut = Translate(z=(self.lug_length - self.m3_nut_height) / 2.0)(nut)
            nuts.append(_nut)
        if self.m3_nuts_bottom:
            _nut = Translate(z=(self.lug_length - self.m3_nut_height) / -2.0)(nut)
            nuts.append(_nut)
        return Union()(*nuts)

    @property
    def ring(self):
        if self.ring_radius:
            iR = self.ring_inner_radius or self.wreath_radius
            return Pipe(oR=self.ring_radius, iR=iR, h=self.lug_length, padding=1.2, center=True)
        return Union()

    def render_scad(self, *args, **kw):
        lugs = []
        for xy in self.wreath:
            lug = Translate(**xy)(self.lug)
            lugs.append(lug)
        lugs = Union()(*lugs)
        if self.m3_nuts_top or self.m3_nuts_bottom:
            nuts = []
            for xy in self.wreath:
                nut = Translate(**xy)(self.nut)
                nuts.append(nut)
            nuts = Union()(*nuts)
            lugs = Difference()(self.ring, lugs, nuts)
        else:
            lugs = Difference()(self.ring, lugs)
        return lugs.render_scad(*args, **kw)
    
class EndCap(DrumPumpObject):
    height = 6
    thickness = DrumPumpObject.pump_body_thickness * 3.0
    inner_radius = DrumPumpObject.pump_body_inner_radius
    radius = thickness + inner_radius
    lug_wreath_radius = radius - (LugWreath.lug_radius * 3)
    closed = False

    @property
    def lugs(self):
        max_angle = 90.0
        phase = (180 - max_angle) / 2.0 + 90
        lugs1 = LugWreath(lug_count=3, wreath_radius=self.lug_wreath_radius, lug_length=self.height * 2, max_angle=max_angle, phase=phase)
        lugs2 = LugWreath(lug_count=3, wreath_radius=self.lug_wreath_radius, lug_length=self.height * 2, max_angle=max_angle, phase=phase + 180)
        return Union()(lugs1, lugs2)

    def render_scad(self, *args, **kw):
        if self.closed:
            ec = Cylinder(h=self.height, r=self.radius, padding=1.2, center=True)
        else:
            ec = Pipe(h=self.height, ir=self.inner_radius, oR=self.radius, padding=1.2, center=True)
        chamfer = Chamfer(r=self.pump_body_radius, chamfer=2, invert=False, center=True)
        chamfer = Translate(z=self.height / 2.0)(chamfer)
        lugs = self.lugs
        body = Union()(ec, lugs, chamfer)
        body = Difference()(ec, lugs, chamfer)
        return body.render_scad(*args, **kw)

class CoilMount(EndCap):
    height = 3.5
    thickness = DrumPumpObject.pump_body_thickness * 3.0
    core_depth = 14.5 + 0.5
    core_width = 45.2 + 0.5
    core_height = 30.25 + 5
    screw_spread = 37.67
    screw_height = 12
    screw_radius = 3
    post_width = 30
    post_height = screw_height + 13
    post_depth = core_depth * 1.3
    guard_length = 29
    guard_width = 29
    guard_height = 80

    def render_scad(self, *args, **kw):
        ec = Cylinder(h=self.height, r=self.radius, padding=1.2, center=True)
        lugs = self.lugs
        coil = cube(y=self.core_width, x=self.core_depth, z=self.core_height, center=True)
        coil = Translate(z=(self.core_height - self.height - 0.1) / 2.0)(coil)
        # coil posts
        post1 = cube(y=self.post_width, x=self.post_depth, z=self.post_height, center=True)
        post1 = Translate(y=-20)(post1)
        post2 = cube(y=self.post_width, x=self.post_depth, z=self.post_height, center=True)
        post2 = Translate(y=20)(post2)
        posts = Translate(z=self.post_height / 2.0)(post1, post2)
        outer = Pipe(ir=self.radius, oR=self.post_width * 2, h=self.post_height * 2, padding=1.2, center=True)
        outer = Translate(z=self.post_height / 2.0)(outer)
        posts = Difference()(posts, outer)
        # guard
        guard = cube(y=self.guard_width, x=self.guard_length, z=self.guard_height, center=True)
        # screw holes
        sfloor = (self.screw_height - self.screw_radius) / 2.0 + 1
        sceil = (self.screw_height - self.screw_radius) / 2.0 + 15 + 2
        sh1 = Cylinder(h=self.post_width * 2, r=2, center=True)
        sh1 = Rotate(y=90)(sh1)
        sh1 = Translate(y=self.screw_spread / 2.0, z=sfloor)(sh1)
        sh2 = Cylinder(h=self.post_width * 2, r=2, center=True)
        sh2 = Rotate(y=90)(sh2)
        sh2 = Translate(y=self.screw_spread / -2.0, z=sfloor)(sh2)
        sh3 = Cylinder(h=self.post_width * 2, r=2, center=True)
        sh3 = Rotate(y=90)(sh3)
        sh3 = Translate(y=self.screw_spread / 2.0, z=sceil)(sh3)
        sh4 = Cylinder(h=self.post_width * 2, r=2, center=True)
        sh4 = Rotate(y=90)(sh4)
        sh4 = Translate(y=self.screw_spread / -2.0, z=sceil)(sh4)
        shc = Cube(x=self.post_width * 2, y=4, z=15, center=True)
        shc1 = Translate(y=self.screw_spread / 2.0, z=(sceil - sfloor)/ 2.0 + sfloor)(shc)
        shc2 = Translate(y=self.screw_spread / -2.0, z=(sceil - sfloor)/ 2.0 + sfloor)(shc)
        # body
        ec = Union()(ec, posts)
        body = Difference()(ec, lugs, coil, sh1, sh2, sh3, sh4, guard, shc1, shc2)
        return body.render_scad(*args, **kw)

class Standoff(DrumPumpObject):
    standoff_length = 15
    standoff_inner_radius = 2
    standoff_thickness = 2
    standoff_radius = standoff_inner_radius + standoff_thickness

    def render_scad(self, *args, **kw):
        standoff = Pipe(h=self.standoff_length, ir=self.standoff_inner_radius, oR=self.standoff_radius, padding=1.2, center=True)
        return standoff.render_scad(*args, **kw)

class SpringPedestal(DrumPumpObject):
    pedestal_length = 34 * .75
    pedestal_thickness = 2
    pedestal_inner_radius = 3.3
    pedestal_radius = 3 + pedestal_thickness
    piston_length = pedestal_length / 2.0
    plate_thickness = 2
    plate_radius = pedestal_radius + plate_thickness * 2

    @property
    def spring_side(self):
        outside = Pipe(h=self.pedestal_length, ir=self.pedestal_inner_radius, oR=self.pedestal_radius, padding=1.2, center=True)
        return outside

    @property
    def plate(self):
        plate = cylinder(h=self.plate_thickness, r=self.plate_radius, center=True)
        plate = Translate(z=(self.piston_length + self.plate_thickness) / 2.0)(plate)
        piston = cylinder(h=self.piston_length, r=self.pedestal_radius + self.pedestal_thickness, center=True)
        pedestal = Pipe(h=self.pedestal_length, ir=self.pedestal_inner_radius * .9, oR=self.pedestal_radius * 1.1, padding=1.2, center=True)
        piston = Difference()(piston, pedestal)
        return Union()(plate, piston)

class DrumPump(DrumPumpObject):
    @property
    def body(self):
        base = Pipe(h=self.pump_body_length, ir=self.pump_body_inner_radius, oR=self.pump_body_radius, padding=1.2, center=True)
        chamfer1 = Chamfer(r=self.pump_body_radius, chamfer=2, invert=True, center=True)
        chamfer1 = Translate(z=self.pump_body_length / 2.0)(chamfer1)
        chamfer2 = Chamfer(r=self.pump_body_radius, chamfer=2, invert=False, center=True)
        chamfer2 = Translate(z=self.pump_body_length / -2.0)(chamfer2)
        outlet_port = Rotate(z=180)(self.outlet_port)
        inlet_port = self.inlet_port
        #body = Union()(base, inlet_port, outlet_port, chamfer1, chamfer2)
        body = Difference()(base, inlet_port, outlet_port, chamfer1, chamfer2)
        return body

    @property
    def outer_body(self):
        body = Cylinder(h=self.pump_body_length, r=self.pump_body_radius, center=True)
        return body

    @property
    def inner_body(self):
        body = Cylinder(h=self.pump_body_length, r=self.pump_body_inner_radius, center=True)
        return body
    
    def render_scad(self, *args, **kw):
        return self.body.render_scad(*args, **kw)

class PumpNozzle(DrumPumpObject):
    nozzle_height = 10
    lug_length = ValveHead.lug_length
    height = nozzle_height + lug_length

    def nozzle_internal(self, h, segments=8):
        return Cylinder(r=inch2mm(.093) / 2.0, h=h, center=True)

    @property
    def nozzle(self):
        lugs = ValveHead(lug_ring_inner_radius=inch2mm(.093), lug_length=self.lug_length).lugs
        lugs = Translate(z=self.lug_length / 2.0)(lugs)
        nozzle = Pipe(h=self.height, iD=inch2mm(.093), oD=inch2mm(.185), padding=1.2)
        nozzle = Union()(lugs, nozzle)
        return nozzle
    
    def barbed_nozzle(self, segments):
        hstep = float(h) / segments
        res = []
        for s in range(segments):
            seg = Pipe(id1=inch2mm(.093),  id2=inch2mm(.093), od1=inch2mm(.185), od2=inch2mm(.1), h=hstep, ifn=fn, ofn=fn, center=True)
            seg = Translate(z=hstep * s)(seg)
            res.append(seg)
        return Union()(*res)

    
class DrumPumpFactory(DrumPumpObject):
    fn = 40

    @property
    def valve_stages(self):
        outlet_stage = self.outlet_valve_stage
        outlet_stage = Rotate(Z=180)(outlet_stage)
        inlet_stage = self.inlet_valve_stage
        valve_stages = Union()(inlet_stage, outlet_stage)
        valve_stages = Intersection()(valve_stages, self.pump_bounding_box)
        return valve_stages

    @property
    def valve_flaps(self):
        outlet_flap = self.outlet_valve_flap
        outlet_flap = Translate(y=self.pump_body_radius * 2.5)(outlet_flap)
        outlet_flap = Rotate(z=180)(outlet_flap)
        inlet_flap = self.inlet_valve_flap
        inlet_flap = Translate(y=self.pump_body_radius * 2.5)(inlet_flap)
        return Color(colorname="grey")(Union()(inlet_flap, outlet_flap))

    @property
    def valve_heads(self):
        # heads
        outlet_head = self.outlet_valve_head
        outlet_head = Translate(y=self.pump_body_radius * 3.5)(outlet_head)
        outlet_head = Rotate(z=180)(outlet_head)
        inlet_head = self.inlet_valve_head
        inlet_head = Translate(y=self.pump_body_radius * 3.5)(inlet_head)
        return Union()(inlet_head, outlet_head)

    @property
    def inlet_debug(self):
        inlet_debug = ValveHead().inlet_debug
        return inlet_debug

    @property
    def membrane(self):
        membrane = Cylinder(h=ValveFlap.flap_thickness, r=self.pump_body_radius * 0.95)
        return membrane

    @property
    def endcaps(self):
        ec1 = Rotate(x=180)(self.endcap_open)
        ec1 = Translate(z=self.pump_body_length * 2)(ec1)
        ec2 = Translate(z=-self.pump_body_length * 2)(self.endcap_closed)
        return Union()(ec1, ec2)

    @property
    def braces(self):
        b1 = Translate(z=self.pump_body_length / 2.0 - self.endcap_open.height * 1.5)(self.brace)
        b2 = Translate(z=self.pump_body_length / -2.0 + self.endcap_closed.height * 1.5)(self.brace)
        braces = Union()(b1, b2)
        stage = Cylinder(r=ValveStage.stage_radius, h=self.pump_body_radius * 6, center=True)
        stage = Rotate(x=90)(stage)
        braces = Difference()(braces, stage)
        return braces

    @property
    def plate(self):
        sp = SpringPedestal()
        return sp.plate

    @property
    def seal(self):
        seal = ValveFlap().seal
        seal = Color(colorname="grey")(seal)
        return seal

    @property
    def standoff(self):
        standoff = Standoff()
        return standoff

    @property
    def valve_plate(self):
        plate = ValvePlate()
        return plate.plate

    @property
    def coil_mount(self):
        coil = CoilMount()
        coil = Color(colorname="aqua")(coil)
        return coil

    @property
    def nozzles(self):
        nozzle = PumpNozzle().nozzle
        nozzle = Color(colorname="green")(nozzle)
        nozzle = Rotate(x=90)(nozzle)
        nozzle = Translate(y=self.pump_body_length * -2.5)(nozzle)
        nozzle = Union()(Rotate(y=-60)(nozzle), Rotate(x=180)(nozzle))
        return nozzle
    
    @property
    def pump_bounding_box(self):
        box = Cube(z=self.pump_body_length, y=100, x=self.pump_body_radius * 2, center=True)
        return box

    def render_scad(self, *args, **kw):
        pump_body = Color(colorname=self.pump_body_color)(self.pump_body)
        membrane = Translate(z=self.pump_body_length * 1.5)(self.membrane)
        membrane = Color(colorname="grey")(membrane)
        seal1 = Translate(y=50)(self.seal)
        seal2 = Translate(y=-50)(self.seal)
        seals = Union()(seal1, seal2)
        plate = Translate(z=self.pump_body_length * 1)(self.plate)
        coil_mount = Translate(z=self.pump_body_length * 3)(self.coil_mount)
        #scene = Union()(pump_body, self.valve_stages, self.valve_heads, self.valve_flaps, self.endcaps, self.braces, membrane)
        #scene = Union()(pump_body, self.valve_stages, self.valve_heads, self.valve_flaps, self.endcaps, membrane, seal, self.nozzles, coil_mount)
        scene = Union()(pump_body, self.valve_stages, self.valve_heads, self.endcaps, membrane, coil_mount)
        scene = SCAD_Globals(fn=20)(scene)
        return scene.render_scad()
    
    def save(self, obj, name, dxf=False, stl=True, scad_only=False):
        def load(fn):
            txt = ''
            try:
                f = open(fn)
                txt = f.read()
            except:
                pass
            return txt

        obj = SCAD_Globals(fn=self.fn)(obj)
        fn = "%s.scad" % name
        last_scad = load(fn)
        print "Saving %s" % fn
        obj.render(fn)
        current_scad = load(fn)
        dirty = current_scad != last_scad
        if dirty and dxf and not scad_only:
            fn = "%s.dxf" % name
            print "Saving %s" % fn
            obj.render(fn)
        if dirty and stl and not scad_only:
            fn = "%s.stl" % name
            print "Saving %s" % fn
            obj.render(fn)

    def generate_bom(self, scad_only=True):
        #
        standoff = self.standoff
        self.save(standoff, "standoff", scad_only=scad_only)
        #
        coil_mount = self.coil_mount
        self.save(coil_mount, "coil_mount", scad_only=scad_only)
        #
        valve_flap = self.outlet_valve_flap
        valve_flap = Rotate(x=90)(valve_flap)
        valve_flap = Projection(cut=True)(valve_flap)
        self.save(valve_flap, "valve_flap", stl=False, dxf=True, scad_only=scad_only)
        #
        endcap_open = self.endcap_open
        self.save(endcap_open, "endcap_open", scad_only=scad_only)
        #
        endcap_closed = self.endcap_closed
        self.save(endcap_closed, "endcap_closed", scad_only=scad_only)
        #
        inlet_debug = self.inlet_debug
        self.save(inlet_debug, "inlet_debug", scad_only=scad_only)
        #
        seal = self.seal
        seal = Rotate(x=90)(seal)
        seal = projection(cut=True)(seal)
        self.save(seal, "seal", stl=False, dxf=True, scad_only=scad_only)
        #
        plate = self.plate
        plate = Rotate(x=180)(plate)
        self.save(plate, "plate", scad_only=scad_only)
        #
        membrane = self.membrane
        membrane = projection(cut=True)(membrane)
        self.save(membrane, "membrane", stl=False, dxf=True, scad_only=scad_only)
        #
        inlet_head = self.inlet_valve_head
        inlet_head = Rotate(x=-90)(inlet_head)
        self.save(inlet_head, "inlet_head", scad_only=scad_only)
        outlet_head = self.outlet_valve_head
        outlet_head = Rotate(x=-90)(outlet_head)
        self.save(outlet_head, "outlet_head", scad_only=scad_only)
        #
        nozzle = PumpNozzle().nozzle
        self.save(nozzle, "nozzle", scad_only=scad_only)
        #
        valve_plate = self.valve_plate
        valve_plate = Rotate(x=90)(valve_plate)
        self.save(valve_plate, "valve_plate", scad_only=scad_only)
        #
        pump_body = Union()(self.pump_body, self.valve_stages)
        self.save(pump_body, "pump_body", scad_only=scad_only)

factory = DrumPumpFactory()
factory.render("drum_pump.scad")
#factory.generate_bom()
factory.generate_bom(False)
#factory.render("drum_pump.stl")
