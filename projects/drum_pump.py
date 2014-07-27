#!/usr/bin/env python

import math
from scad import *

M3_TAP = inch2mm(0.0995)
M3_CLEARANCE = inch2mm(1/8.0)

def frame(x=0, y=0, z=0, xt=0, yt=0, zt=0, **kw):
    return Difference()(
        Cube(x=x+xt, y=y+yt, z=z+zt, **kw),
        Cube(x=x, y=y, z=z, **kw))

def nozzle_internal(h, segments=8):
    return Cylinder(r=inch2mm(.093) / 2.0, h=h, center=True)

def nozzle(h, segments=8):
    return pipe(h=h, iD=inch2mm(.093), oD=inch2mm(.185), ifn=fn, ofn=fn)
    hstep = float(h) / segments
    res = []
    for s in range(segments):
        seg = Pipe(id1=inch2mm(.093),  id2=inch2mm(.093), od1=inch2mm(.185), od2=inch2mm(.1), h=hstep, ifn=fn, ofn=fn, center=True)
        seg = Translate(z=hstep * s)(seg)
        res.append(seg)
    return Union()(*res)

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
    screw_clearance = M3_CLEARANCE
    screw_tap = M3_TAP
    nut_clearance = 8
    nut_height = 2.5
    endcap_length = 4
    #
    inlet_port_radius = inch2mm(5/16.0)
    outlet_port_radius = inch2mm(1/8.0)
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
        return EndCap(**self.__dict__)

    @property
    def endcap_closed(self):
        return EndCap(closed=True, **self.__dict__)

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
    stage_thickness = 1
    stage_length = DrumPumpObject.pump_body_length * .5
    stage_inner_radius = DrumPumpObject.inlet_port_radius + valve_overlap
    stage_radius = stage_inner_radius + stage_thickness

    @property
    def stage(self):
        stage_length = self.stage_length + self.pump_body_thickness
        lugs = LugWreath(wreath_radius=ValveHead.inlet_breech_radius, lug_length=ValveHead.inlet_breech_length, ring_radius=ValveHead.inlet_breech_radius + LugWreath.lug_radius * 2 + 2)
        lugs = Translate(z=(ValveHead.inlet_bore_length - ValveHead.inlet_breech_length + self.pump_body_thickness) / -2.0)(lugs)
        base = Cylinder(r=self.stage_inner_radius, h=self.pump_body_thickness, center=True)
        base = Translate(z=(stage_length - self.pump_body_thickness) / 2.0)(base)
        stage = Pipe(ir=self.stage_inner_radius, oR=self.stage_radius, h=stage_length, center=True, padding=1.2)
        stage = Rotate(x=90)(stage, lugs, base)
        stage = Translate(y=self.pump_body_radius + stage_length / 2.0 - self.pump_body_thickness)(stage)
        return stage

    @property
    def inlet(self):
        stage = Color(colorname="steelblue")(self.stage)
        stage = Difference()(stage, self.pump_body.outer_body, self.inlet_port)
        return stage

    @property
    def outlet(self):
        stage = Color(colorname="salmon")(self.stage)
        stage = Difference()(stage, self.pump_body.outer_body, self.outlet_port)
        return stage

class ValveHead(ValveBaseObject):
    # inlet head
    inlet_bore_length = ValveStage.stage_length
    inlet_bore_radius = ValveStage.stage_inner_radius
    inlet_bore_inner_radius = ValveBaseObject.outlet_port_radius
    inlet_bore_thickness = inlet_bore_radius - inlet_bore_inner_radius
    inlet_breech_length = 5
    inlet_breech_radius = ValveStage.stage_radius
    # outlet head
    outlet_bore_length = ValveStage.stage_length
    outlet_bore_radius = ValveStage.stage_inner_radius
    outlet_bore_thickness = 2
    outlet_bore_inner_radius = outlet_bore_radius - outlet_bore_thickness
    outlet_breech_length = 5
    outlet_breech_radius = ValveStage.stage_radius

    @property
    def outlet(self):
        lugs = LugWreath(wreath_radius=self.outlet_breech_radius, lug_length=self.outlet_breech_length, ring_radius=self.outlet_breech_radius + LugWreath.lug_radius * 2 + 2)
        lugs = Translate(z=(self.outlet_bore_length - self.outlet_breech_length) / -2.0)(lugs)
        bore = Pipe(oR=self.outlet_bore_radius, ir=self.outlet_bore_inner_radius, h=self.outlet_bore_length, padding=1.2, center=True)
        breech = Pipe(oR=self.outlet_breech_radius, ir=self.outlet_bore_inner_radius, h=self.outlet_breech_length, padding=1.2, center=True)
        breech = Translate(z=(self.outlet_bore_length - self.outlet_breech_length) / -2.0)(breech)
        head = Rotate(x=90)(bore, breech, lugs)
        return head
    
    @property
    def inlet(self):
        lugs = LugWreath(wreath_radius=self.inlet_breech_radius, lug_length=self.inlet_breech_length, ring_radius=self.inlet_breech_radius + LugWreath.lug_radius * 2 + 2)
        lugs = Translate(z=(self.inlet_bore_length - self.inlet_breech_length) / -2.0)(lugs)
        bore = Pipe(oR=self.inlet_bore_radius, ir=self.inlet_bore_inner_radius, h=self.inlet_bore_length, padding=1.2, center=True)
        breech = Pipe(oR=self.inlet_breech_radius, ir=self.inlet_bore_inner_radius, h=self.inlet_breech_length, padding=1.2, center=True)
        breech = Translate(z=(self.outlet_bore_length - self.outlet_breech_length) / -2.0)(breech)
        head = Rotate(x=90)(bore, breech, lugs)
        return head

class ValveFlap(ValveBaseObject):
    flap_thickness = inch2mm(1/16.0)
    flap_radius = ValveStage.stage_inner_radius * .99
    cutout_radius = 8
    cutout_inner_radius = 6
    cutout_neck_width = cutout_inner_radius

    @property
    def inlet(self):
        flap = Cylinder(r=self.flap_radius, h=self.flap_thickness, center=True)
        cutout = Pipe(oR=self.cutout_radius, iR=self.cutout_inner_radius, h=self.flap_thickness * 1.2, center=True)
        neck = cube(x=self.cutout_neck_width, y=self.flap_radius, z=self.flap_thickness * 1.2, center=True)
        neck = Translate(y=self.flap_radius / 2.0)(neck)
        cutout = Difference()(cutout, neck)
        flap = Difference()(flap, cutout)
        flap = Rotate(x=90)(flap)
        return flap

    @property
    def outlet(self):
        return self.inlet

class LugWreath(DrumPumpObject):
    lug_count = 3
    phase = 0
    lug_length = 5
    lug_inner_radius = 0
    lug_radius = 1.8
    wreath_radius = 3
    ring_radius = 0

    @property
    def wreath(self):
        pie_slice = 360.0 / self.lug_count
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
            return Cylinder(r=self.lug_radius, h=self.lug_length + 1.2, padding=1.2, center=True)

    @property
    def ring(self):
        if self.ring_radius:
            return Pipe(oR=self.ring_radius, iR=self.wreath_radius, h=self.lug_length, padding=1.2, center=True)
        return Union()

    def render_scad(self, *args, **kw):
        lugs = []
        for xy in self.wreath:
            lug = Translate(**xy)(self.lug)
            lugs.append(lug)
        lugs = Union()(*lugs)
        lugs = Difference()(self.ring, lugs)
        return lugs.render_scad(*args, **kw)
    
class EndCap(DrumPumpObject):
    height = 6
    thickness = DrumPumpObject.pump_body_thickness * 3.0
    inner_radius = DrumPumpObject.pump_body_inner_radius
    radius = thickness + inner_radius
    closed = False

    @property
    def lugs(self):
        lugs = LugWreath(lug_count=6, wreath_radius=self.radius - LugWreath.lug_radius * 3, lug_length=self.height * 2)
        return lugs

    def render_scad(self, *args, **kw):
        if self.closed:
            ec = Cylinder(h=self.height, r=self.radius, padding=1.2, center=True)
        else:
            ec = Pipe(h=self.height, ir=self.inner_radius, oR=self.radius, padding=1.2, center=True)
        lugs = self.lugs
        body = Union()(ec, lugs)
        body = Difference()(ec, lugs)
        return body.render_scad(*args, **kw)

class DrumPump(DrumPumpObject):
    @property
    def body(self):
        body = Pipe(h=self.pump_body_length, ir=self.pump_body_inner_radius, oR=self.pump_body_radius, padding=1.2, center=True)
        body = Difference()(body, self.inlet_port, Rotate(z=180)(self.outlet_port))
        return body

    @property
    def outer_body(self):
        body = Cylinder(h=self.pump_body_length, r=self.pump_body_radius, center=True)
        return body

    @property
    def inner_body(self):
        body = Cylinder(h=self.pump_body_length, r=self.pump_body_inner_radius, center=True)
        return body
    
    def chamfer(self, c=4):
        return Pipe(ir2=self.pump_body_radius - c, or2=self.pump_body_radius, ir1=self.pump_body_radius, or1=self.pump_body_radius + c, h=c, center=True)

    def render_scad(self, *args, **kw):
        return self.body.render_scad(*args, **kw)
    
class DrumPumpFactory(DrumPumpObject):
    @property
    def valve_stages(self):
        outlet_stage = self.outlet_valve_stage
        outlet_stage = Rotate(Z=180)(outlet_stage)
        inlet_stage = self.inlet_valve_stage
        return Union()(inlet_stage, outlet_stage)

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
        outlet_head = Color(colorname="red")(outlet_head)
        inlet_head = self.inlet_valve_head
        inlet_head = Translate(y=self.pump_body_radius * 3.5)(inlet_head)
        inlet_head = Color(colorname="blue")(inlet_head)
        return Union()(inlet_head, outlet_head)

    @property
    def membrane(self):
        membrane = Cylinder(h=ValveFlap.flap_thickness, r=self.pump_body_radius)
        membrane = Translate(z=self.pump_body_length)(membrane)
        membrane = Color(colorname="grey")(membrane)
        return membrane

    @property
    def endcaps(self):
        ec1 = Difference()(Translate(z=self.pump_body_length / 2.0)(self.endcap_open), self.pump_body.outer_body)
        ec2 = Difference()(Translate(z=self.pump_body_length / -2.0)(self.endcap_closed), self.pump_body.outer_body)
        ec1 = Translate(z=self.pump_body_length)(ec1)
        ec2 = Translate(z=-self.pump_body_length)(ec2)
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

    def render_scad(self, *args, **kw):
        # scene
        pump_body = Color(colorname=self.pump_body_color)(self.pump_body)
        scene = Union()(pump_body, self.valve_stages, self.valve_heads, self.valve_flaps, self.endcaps, self.braces, self.membrane)
        scene = SCAD_Globals(fn=40)(scene)
        return scene.render_scad()

factory = DrumPumpFactory()
factory.render("drum_pump.scad")
if not os.path.exists("drum_pump.stl"):
    factory.render("drum_pump.stl")
