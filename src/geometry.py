from core import *
from primitives import *
from vector import *
import math
import inspect
import sys

class Pipe(SCAD_Object):
    Defaults = {
        "inner": {"type": Cylinder},
        "outer": {"type": Cylinder},
        "_height": {"type": int},
    }
    Aliases = {
        'i': 'inner',
        'o': 'outer'
    }
    def render_scad(self):
        return Difference()(self.outer, self.inner).render_scad()
    def get_height(self):
        return self.inner.height
    def set_height(self, height):
        self.inner.height = height
        self.outer.height = height
    height = property(get_height, set_height)

class PieSlice(SCAD_Object):
    Defaults = {
        "angle": {"type": float, "default":180},
        "phase": {"type": float},
        "radius": {"type": float},
        "height": {"type": float},
        "resolution": {"type": RadialResolution},
    }

    @property
    def points(self):
        arclength = (self.angle * math.pi * self.radius) / 180.0
        if not arclength:
            return ListVector2D()
        fragments = self.resolution.get_fragments(arclength, angle=self.angle)
        angle_step = self.angle / fragments if fragments else 0
        points = []
        rem = (self.angle - fragments * angle_step) / 2.0
        x = math.cos(math.radians(self.phase)) * self.radius
        y = math.sin(math.radians(self.phase)) * self.radius
        points.append([x, y])
        for fragment in range(fragments):
            step = fragment * angle_step + self.phase + rem
            x = math.cos(math.radians(step)) * self.radius
            y = math.sin(math.radians(step)) * self.radius
            points.append([x, y])
        x = math.cos(math.radians(self.angle + self.phase)) * self.radius
        y = math.sin(math.radians(self.angle + self.phase)) * self.radius
        points.append([x, y])
        return ListVector2D(points)

    def render_scad(self):
        ret = Polygon(points=self.points)
        if self.height:
            ret = LinearExtrude(height=self.height)(ret)
        print ret.__dict__
        return ret.render_scad()

class SemiCylinder(Cylinder):
    Defaults = {
        "angle": {"type": float, "default":180},
        "phase": {"type": float},
    }
    def render_scad(self):
        return Difference()(self, self.inner).render_scad()

class Octohedron(SCAD_Object):
    Defaults = {
        "height": {"type": float, "default": 1.0},
        "center": {"type": bool, "default": False},
    }
    def get_edge(self):
        return self.height / (math.sqrt(3.0) / 2.0)
    def set_edge(self, edge):
        self.height = edge * (math.sqrt(3.0) / 3.0)
    edge = property(get_edge, set_edge)

    @property
    def points(self):
        return ListVector3D([
            [0, self.triangle_height - (self.triangle_height / 3.0), self.height],
            [self.edge, self.triangle_height - (self.triangle_height / 3.0), self.height],
            [self.edge / 2.0,  -(self.triangle_height / 3.0), self.height],
            [0, 0, 0], 
            [self.edge, 0, 0], 
            [self.edge / 2.0, self.triangle_height, 0] 
        ])
        if self.center:
            cv = (self.edge / 2.0, self.triangle_height / 3.0, self.height / 2.0)
            points = [subtract_vector(vv, cv) for vv in points]
        return points

    @property
    def faces(self):
        return ListVector3D([
            [1, 2, 0], [2, 3, 0], [3, 5, 0],
            [4, 2, 1], [5, 1, 0], [3, 2, 4],
            [1, 5, 4], [4, 5, 3],
        ])

    @property
    def triangle_height(self):
        return self.edge * (math.sqrt(3.0) / 2.0)

    def render_scad(self):
        return Polyhedron(points=list(self.points), faces=list(self.faces)).render_scad()

class Tetrahedron(SCAD_Object):
    Defaults = {
        "height": {"type": float, "default": 1.0},
        "center": {"type": bool, "default": False},
    }
    def get_edge(self):
        return self.height / math.sqrt(2.0 / 3.0)
    def set_edge(self, edge):
        self.height = edge * math.sqrt(2.0 / 3.0)
    edge = property(get_edge, set_edge)

    @property
    def triangle_height(self):
        return self.edge * (math.sqrt(3.0) / 2.0)

    @property
    def points(self):
        points = ListVector3D([
            [0, 0, 0],
            [self.edge, 0, 0],
            [self.edge / 2.0, self.triangle_height, 0],
            [self.edge / 2.0, self.triangle_height / 3.0, self.height],
        ])
        if self.center:
            tv = Vector3D([self.edge / 2.0, self.triangle_height / 3.0, self.height / 2.0])
            points = [vv - tv for vv in points]
        return points

    @property
    def faces(self):
        return ListVector3D([[0, 1, 2], [1, 0, 3], [0, 2, 3], [2, 1, 3]])

    def render_scad(self):
        return Polyhedron(points=list(self.points), faces=list(self.faces)).render_scad()

"""
def pyramid(height, width=None, depth=None, center=False):
    if width == None:
        width = height
    if depth == None:
        depth = width
    logger.debug(msg)
    points = [
        [0, 0, 0],
        [width, depth, 0],
        [width, 0, 0],
        [0, depth, 0],
        [width / 2, depth / 2, height],
    ]
    faces = [[0, 2, 1], [0, 1, 3], [2, 0, 4], [0, 3, 4], [3, 1, 4], [1, 2, 4]]
    if center:
        cv = (height / 2, width / 2, depth / 2)
        points = [subtract_vector(vv, cv) for vv in points]
    return polyhedron(points=list(points), faces=list(faces))

def render_crosshairs(length=25, width=1, height=1, rad=2):
    scad = \
        union()([
            # red
            rotate([0, 90, 0])( 
                translate([0, -width, -length/ 2.0 + width])( color([1, 0, 0])( cube([width, height, length]) ) ),
                translate([rad / 4.0, rad / 4.0 - width, length / 2.0])( color([1, 0, 0])( sphere(rad) ) ),
            ), 
            # green
            rotate([-90, 0, 0])( 
                translate([0, 0, -length / 2.0])( color([0, 1, 0])( cube([width, height, length]) ) ), 
                translate([rad / 4.0, rad / 4.0, length / 2.0])( color([0, 1, 0])( sphere(rad) ) ),
            ), 
            # blue
            rotate([0, 0, -90])( 
                translate([0, 0, -length/ 2.0])( color([0, 0, 1])( cube([width, height, length]) ) ),
                translate([rad / 4.0,  rad / 4.0, length / 2.0])( color([0, 0, 1])( sphere(rad) ) ),
            ), 
        ])
    return scad
"""

#
# auto generate __all__
#

_current_module = sys.modules[__name__]
__all__ = [name for (name, obj) in globals().items() if (inspect.getmodule(obj) == _current_module) and inspect.isclass(obj) and issubclass(obj, SCAD_Object)]
