#!/usr/bin/env python

from sctk import *

class Octohedron(RootPart):
    Defaults = {
        "height": 1,
        "edge": None,
        "center": False,
    }

    def _translate_points(self, points):
        if self.center:
            cv = (self.edge / 2.0, self.eq_height / 3.0, self.height / 2.0)
            points = [subtract_vector(vv, cv) for vv in points]
        return points

    @property
    def bottom_points(self):
        return self._translate_points([ 
            [0, 0, 0], 
            [self.edge, 0, 0], 
            [self.edge / 2.0, self.eq_height, 0] 
        ])

    @property
    def top_points(self):
        return self._translate_points([
            [0, self.eq_height - (self.eq_height / 3.0), self.height],
            [self.edge, self.eq_height - (self.eq_height / 3.0), self.height],
            [self.edge / 2.0,  -(self.eq_height / 3.0), self.height],
        ])

    @property
    def points(self):
        return self.top_points + self.bottom_points

    @property
    def faces(self):
        return [
            [1, 2, 0], [2, 3, 0], [3, 5, 0],
            [4, 2, 1], [5, 1, 0], [3, 2, 4],
            [1, 5, 4], [4, 5, 3],
        ]

    @property
    def eq_height(self):
        return self.edge * (math.sqrt(3.0) / 2.0)

    @default
    def edge(self):
        return self.height / (math.sqrt(3.0) / 2.0)

    @default
    def center(self):
        return False

    @default
    def height(self):
        return self.get("height")
    
    def render_scad(self):
        return polyhedron(points=list(self.points), faces=list(self.faces))

def simple(size, level=0):
    if level == 0:
        ret = union()(
            pyramid("top", size, center=True),
            translate([-size / 2.0, -size / 2.0, -size])( pyramid("b1", size, center=True) ),
            translate([size / 2.0, -size / 2.0, -size])( pyramid("b1", size, center=True) ),
            translate([-size / 2.0, size / 2.0, -size])( pyramid("b1", size, center=True) ),
            translate([size / 2.0, size / 2.0, -size])( pyramid("b1", size, center=True) ),
        )
    else:
        ret = union()(
            pyramid("top", size, center=True),
            translate([-size / 2.0, -size / 2.0, -size])( unit(size, level-1) ),
            translate([size / 2.0, -size / 2.0, -size])( unit(size, level-1) ),
            translate([-size / 2.0, size / 2.0, -size])( unit(size, level-1) ),
            translate([size / 2.0, size / 2.0, -size])( unit(size, level-1) ),
        )
    return ret

class SierpinskiTriangle(RootPart):
    Defaults = {
        "iterations": 2,
        "height": 10,
    }

    def render(self, level=0, height=None):
        height = height or self.height
        edge = height / math.sqrt(2.0 / 3.0)

        if level == self.iterations:
            return None
        if level == 0:
            #return rotate([180, 0, 0])( self.render(level=level + 1, height=height / 2.0) )
            return union()(
                translate([0, 0, height / 2.0])( tetrahedron(height, center=True) ),
                rotate([0, 0, -30])( self.render(level=level + 1, height=height / 2.0) )
            )
        if level + 1 == self.iterations:
            return translate([0, 0, -height / 2.0])( octohedron(edge=height, center=True) )
        else:
            next_edge = (height / 2.0) / math.sqrt(2.0 / 3.0)
            radius = (math.sqrt(3.0) / 2.0 * edge / 2.0) / 3.0 + (math.sqrt(3.0) / 2.0 * next_edge) - (math.sqrt(3.0) / 2.0 * next_edge) / 3.0
            return union()(
                translate([0, 0, -height / 2.0])( octohedron(edge=height * 2, center=True) ),
                translate([math.cos(math.radians(45)) * radius, math.sin(math.radians(45)) * radius, 0])( self.render(level=level + 1, height=height / 2.0) ),
                translate([math.cos(math.radians(165)) * radius, math.sin(math.radians(165)) * radius, 0])( self.render(level=level + 1, height=height / 2.0) ),
                translate([math.cos(math.radians(285)) * radius, math.sin(math.radians(285)) * radius, 0])( self.render(level=level + 1, height=height / 2.0) ),
                translate([0, 0, -height])( self.render(level=level + 1, height=height / 2.0) ),
            )

    def octohedron_edge(self, idx, height):
        height = 10
        edge = height / (math.sqrt(3.0) / 2.0)
        eq_height = edge * (math.sqrt(3.0) / 2.0)
        octoedge = (height / 2.0) / math.sqrt(2.0 / 3.0)
        # top is offset from bottom by -(eq_height / 3.0)

    def render_scad(self):
        height = 10
        return union()(
            Octohedron(height=height).render_scad(),
            translate( [-edge / 2.0,0,0] )( cube([1, 1, height], center=True )),
            translate( [-edge / 2.0,0,0] )( rotate([-33 -2/3.0,0,0])( cube([1, 1, height], center=True ))),
            translate( [-edge / 4.0,8,0] )( cube([1, 1, height], center=True )),
            )
        return difference()(
            translate([0,0,0])( tetrahedron(height=height, center=True) ),
            translate([0,0,-height / 4.0])( 
            rotate([0,0,0])(
                octohedron(height=height / 2.0, edge=octoedge + .1, center=True) ),
            )
        )
        #return self.render()
        #return tetrahedron(10)

part = SierpinskiTriangle()
scad = part.render_scad()
save_scad(scad, "st.scad", lazy=False)
