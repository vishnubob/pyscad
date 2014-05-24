from core import *
from primitives import *
from vector import *
import math
import inspect
import sys

class Tetrahedron(SCAD_Object):
    Defaults = {
        "height": {"type": float, "default": 1.0},
        "center": {"type": bool, "default": False},
    }
    Aliases = {
        'h': "height",
        'e': "edge",
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

def tube(name, height, outer_dia, inner_dia, segments=None):
    msg = "Tube [%s]: Dia: inner=%.4f outer=%.4f, Height: %.4f" % (name, inner_dia, outer_dia, height)
    logger.debug(msg)
    return difference() (
        cylinder(h=height, r=outer_dia / 2.0, segments=segments),
        cylinder(h=height, r=inner_dia / 2.0, segments=segments)
    )

def tube2(name, height, outer_dia1, inner_dia1, outer_dia2, inner_dia2, segments=None):
    msg = "Tube2 [%s]: Dia1: inner=%.4f outer=%.4f, Dia2: inner=%.4f outer=%.4f, Height: %.4f" % (name, inner_dia1, outer_dia1, inner_dia2, outer_dia2, height)
    logger.debug(msg)
    return difference() (
        cylinder(h=height, r1=outer_dia1 / 2.0, r2=outer_dia2 / 2.0, segments=segments),
        cylinder(h=height, r1=inner_dia1 / 2.0, r2=inner_dia2 / 2.0, segments=segments),
    )

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
