#!/usr/bin/env python

from scad import *

M3_TAP = inch2mm(0.0995)
M3_CLEARANCE = inch2mm(1/8.0)

def frame(x=0, y=0, z=0, xt=0, yt=0, zt=0, **kw):
    return Difference()(
        Cube(x=x+xt, y=y+yt, z=z+zt, **kw),
        Cube(x=x, y=y, z=z, **kw))

def nozzle_internal(h, segments=8, fn=30):
    return Cylinder(r=inch2mm(.093), h=h, fn=fn, center=True)

def nozzle(h, segments=8, fn=30):
    hstep = float(h) / segments
    res = []
    for s in range(segments):
        seg = Pipe(ir1=inch2mm(.093),  ir2=inch2mm(.093), or1=inch2mm(.185), or2=inch2mm(.1), h=hstep, ifn=fn, ofn=fn, center=True)
        seg = Translate(z=hstep * s)(seg)
        res.append(seg)
    return Union()(*res)

class ValveStage(SCAD_Object):
    Defaults = {
        "drum": {"type": object, "cast": False},
    }

    body_length = 30
    body_thickness = 2
    body_width = 20
    body_height = 15 / 2.0
    screw_wall_dia = 15
    screw_wall_zoffset = 3
    screw_clearance = M3_CLEARANCE
    screw_tap = M3_TAP
    nut_clearance = 6
    nut_height = 2.5
    stage_thickness = 3
    stage_overlap = .5
    stage_width = body_width
    stage_height = 15
    stage_length = body_length

    @property
    def outlet_head(self):
        body_width = 20
        body_height = 2.0
        body_length = 30
        body = Cube(x=body_width, y=body_height, z=body_length, center=True)
        body = self.body_transform(body)
        dia = self.screw_wall_dia
        zoffset = 4
        screws = self.screw_posts(dia, dia / 2.0, zoffset=-zoffset)
        screw_walls = self.screw_posts(dia, dia / 2.0, dia2=dia + self.body_thickness)
        screw_walls_base = body
        screw_walls = Union()(screw_walls, screw_walls_base)
        body = difference()(body, screws)
        screw_walls = Intersection()(body, screw_walls)
        screw_holes = self.screw_posts(self.screw_clearance, self.screw_clearance / -2.0)
        # nozzle
        noz = nozzle(inch2mm(.5), segments=4)
        inoz = nozzle_internal(20)
        noz = Rotate(x=-90)(noz)
        inoz = Rotate(x=-90)(inoz)
        noz = Translate(y=self.body_thickness)(self.body_transform(noz))
        inoz = Translate(y=self.body_thickness + 3)(self.body_transform(inoz))
        body = Union()(body, screw_walls, noz)
        body = Difference()(body, inoz, screw_holes)
        return body
    
    @property
    def inlet_head(self):
        body = self.body
        dia = self.screw_wall_dia
        zoffset = self.screw_wall_zoffset
        screws = self.screw_posts(dia, dia / 2.0, zoffset=-zoffset)
        screw_walls = self.screw_posts(dia, dia / 2.0, dia2=dia + self.body_thickness)
        #screw_walls_base = self.screw_posts(dia + self.body_thickness, (dia + self.body_thickness) / 2.0, h=zoffset, zoffset=self.body_height / 2.0 - zoffset / 2.0)
        screw_walls_base = Translate(z=self.body_length / 2.0, y=-1)(Cube(x=self.body_width, z=self.body_length / 2.0, y=self.body_thickness * 3, center=True))
        screw_walls_base = Union()(screw_walls_base, Rotate(y=180)(screw_walls_base))
        screw_walls_base = self.body_transform(screw_walls_base)
        screw_walls = Union()(screw_walls, screw_walls_base)
        body = difference()(body, screws)
        screw_walls = Intersection()( self.body_transform(self.outer_body), screw_walls)
        screw_holes = self.screw_posts(self.screw_clearance, self.screw_clearance / -2.0)
        # nozzle
        noz = nozzle(inch2mm(.5), segments=4)
        inoz = nozzle_internal(20)
        noz = Rotate(x=-90)(noz)
        inoz = Rotate(x=-90)(inoz)
        noz = Translate(y=self.body_thickness + 3)(self.body_transform(noz))
        inoz = Translate(y=self.body_thickness + 2)(self.body_transform(inoz))
        body = Difference()(body, inoz)
        body = Union()(body, screw_walls, noz)
        body = Difference()(body, screw_holes)
        return body
    
    def posts(self, screw_post, dia, x_offset=0, y_offset=0, dia2=0, zoffset=0, h=None, width=None, height=None):
        r = dia / 2.0
        width = width or self.body_width / 2.0 - r
        height = height or self.body_length / 2.0 - r
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

    def screw_posts(self, dia, x_offset=0, y_offset=None, dia2=0, zoffset=0, h=None, fn=20):
        h = h or self.body_height
        if y_offset == None:
            y_offset = x_offset
        dia = dia
        post = Cylinder(d=dia, h=h, center=True, fn=20)
        if dia2:
            post = Pipe(oD=dia2, iD=dia, h=h, center=True, fn=20)
        return self.posts(post, dia, x_offset=x_offset, y_offset=y_offset, dia2=dia2, zoffset=zoffset, h=h)
            
    ##
    ## Body
    def body_transform(self, body):
        body = Translate(y=self.drum.body_radius + self.body_height / 2.0 + 30)(body)
        return body

    @property
    def body(self):
        inner = self.body_transform(self.inner_body)
        outer = self.body_transform(self.outer_body)
        body = Difference()(outer, inner)
        return body

    @property
    def outer_body(self):
        body = Cube(x=self.body_width, y=self.body_height, z=self.body_length, center=True)
        return body

    @property
    def inner_body(self):
        body = Cube(x=self.body_width - self.body_thickness, y=self.body_height - self.body_thickness, z=self.body_length - self.body_thickness, center=True)
        body = Translate(y=-self.body_thickness / 2.0 - 0.1)(body)
        return body

    def stage_transform(self, stage):
        stage = Translate(y=self.drum.body_radius)(stage)
        return stage

    @property
    def nutslot(self):
        width=self.body_width / 2.0 - self.screw_clearance / 2.0
        height=self.body_height / 2.0 - self.screw_clearance / 2.0
        return Union()(
            self.posts(Cylinder(r=self.nut_clearance / 2.0, h=self.nut_height, fn=6, center=True), self.nut_clearance, self.screw_clearance / -2.0, width=width, y_offset=-1, zoffset=38),
            self.posts(Cube(x=self.nut_clearance, y=10, z=self.nut_height, center=True), self.nut_clearance, self.screw_clearance / -2.0, width=width, y_offset=4, zoffset=32))

    @property
    def stage(self):
        zoff = 13
        stage1 = frame(x=self.stage_width, y=self.stage_height, z=self.stage_length, xt=self.stage_thickness, zt=self.stage_thickness, center=True)
        stage2 = cube(x=self.body_width, y=self.stage_height / 2.0 - self.stage_thickness + 5.0, z=self.stage_length, center=True)
        stage = Union()(stage1, stage2)
        stage = self.stage_transform(stage)
        screw_holes = self.screw_posts(self.screw_clearance, self.screw_clearance / -2.0, zoffset=30)
        stage = Difference()(stage, self.drum.outer_body, screw_holes, self.nutslot )
        return stage

class DrumPump(SCAD_Object):
    endcap_length = 4
    body_inner_radius = inch2mm(2.0) / 2.0
    body_thickness = inch2mm(1/8.0)
    body_radius = body_inner_radius + body_thickness
    body_length = 45
    #
    port_radius = inch2mm(1/8.0)
    # block
    block_width = 30
    block_height = body_thickness

    def __init__(self, **kw):
        super(DrumPump, self).__init__(**kw)
        self.valves = ValveStage(drum=self)

    def body_transform(self, body):
        return body
    
    @property
    def body(self):
        body = Pipe(h=self.body_length, ir=self.body_inner_radius, oR=self.body_radius, fn=20, padding=1.2, center=True)
        body = self.body_transform(body)
        return body

    @property
    def endcap(self):
        endcap_radius = self.body_radius + self.body_thickness + 4
        ec1 = Pipe(h=self.body_thickness, ir=self.body_inner_radius, oR=endcap_radius, fn=20, padding=1.2, center=True)
        ec2 = Pipe(h=self.endcap_length, ir=self.body_radius, oR=endcap_radius, fn=20, padding=1.2, center=True)
        ec2 = Translate(z=-self.body_thickness * .9)(ec2)
        ec = Translate(z=self.body_length / 2.0 + 10)(Union()(ec1, ec2))
        xoff = (endcap_radius - self.body_radius) / 2.0 + self.body_radius
        screw_hole = Translate(x=xoff, z=10)(Cylinder(r=M3_CLEARANCE / 2.0, h=30, fn=20))
        holes = Union()(*[rotate(z=z)(screw_hole) for z in range(-50, 51, 25 )] + [rotate(z=z)(screw_hole) for z in range(-51 + 180, 51 + 180, 25 )])
        ec = Difference()(ec, holes)
        return ec

    @property
    def outer_body(self):
        body = Cylinder(h=self.body_length, r=self.body_radius, fn=20, center=True)
        return body

    @property
    def inner_body(self):
        body = Cylinder(h=self.body_length, r=self.body_inner_radius, fn=20, center=True)
        return body
    
    def port_transform(self, port):
        port = Rotate(x=90)(port)
        return port

    def chamfer(self, c=4):
        return Pipe(ir2=self.body_radius - c, or2=self.body_radius, ir1=self.body_radius, or1=self.body_radius + c, h=c, center=True)

    @property
    def port(self):
        port = Cylinder(h=self.body_radius * 4.0, r=self.port_radius, fn=20, center=True)
        port = self.port_transform(port)
        return port

    def render_scad(self, *args, **kw):
        body = self.body
        braces = Difference()( Union()( 
            Translate(z=-20)(self.endcap), 
            Translate(z=-41)(self.endcap) ), 
            Cube(x=self.valves.body_width, y=self.body_radius * 3, z=self.body_length, center=True))
        body = Union()(body, braces)
        ostage = self.valves.stage
        istage = Rotate(z=180)(self.valves.stage)
        stages = Union()(ostage, istage)
        chamfer_endcap = Translate(z=30 - 2)(Rotate(x=0)(self.chamfer(2)))
        endcap = self.endcap
        endcap = Difference()(endcap, chamfer_endcap)
        inlet_head = Rotate(z=180)(self.valves.inlet_head)
        outlet_head = self.valves.outlet_head
        body = Union()(body, stages, endcap, inlet_head, outlet_head)
        inlet = Translate(y=self.body_radius)(Cube(x=20, y=30, z=17, center=True))
        chamfer1 = Translate(z=self.body_length / 2.0)(self.chamfer(2))
        chamfer2 = Translate(z=self.body_length / -2.0)(Rotate(x=180)(self.chamfer(2)))
        body = Difference()(body, self.port, inlet, chamfer1, chamfer2)
        return body.render_scad()

    def save_bom(self):
        body = self.body
        braces = Difference()( Union()( 
            Translate(z=-20)(self.endcap), 
            Translate(z=-41)(self.endcap) ), 
            Cube(x=self.valves.body_width, y=self.body_radius * 3, z=self.body_length, center=True))
        body = Union()(body, braces)
        ostage = self.valves.stage
        istage = Rotate(z=180)(self.valves.stage)
        stages = Union()(ostage, istage)
        chamfer_endcap = Translate(z=30 - 2)(Rotate(x=0)(self.chamfer(2)))
        endcap = self.endcap
        endcap = Difference()(endcap, chamfer_endcap)
        inlet_head = Rotate(z=180)(self.valves.inlet_head)
        outlet_head = self.valves.outlet_head
        body = Union()(body, stages)
        inlet = Translate(y=self.body_radius)(Cube(x=20, y=30, z=17, center=True))
        chamfer1 = Translate(z=self.body_length / 2.0)(self.chamfer(2))
        chamfer2 = Translate(z=self.body_length / -2.0)(Rotate(x=180)(self.chamfer(2)))
        body = Difference()(body, self.port, inlet, chamfer1, chamfer2)
        inlet_head.render("inlet_head.scad")
        outlet_head.render("outlet_head.scad")
        endcap.render("endcap.scad")
        body.render("pump_body.scad")
        inlet_head.render("inlet_head.stl")
        outlet_head.render("outlet_head.stl")
        endcap.render("endcap.stl")
        body.render("pump_body.stl")

pump = DrumPump(center=True)
pump.render("drum_pump.scad")
pump.render("drum_pump.stl")
pump.save_bom()
