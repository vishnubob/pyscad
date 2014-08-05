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
        "_padding": {"type": float, "default": 1.0},
    }
    Aliases = {
        'i': 'inner',
        'o': 'outer'
    }
    def render_scad(self, *args, **kw):
        pad_offset = (self.inner.height - self.outer.height) / 2.0
        if pad_offset and not self.center:
            return Difference()(self.outer, Translate(z=-pad_offset)( self.inner )).render_scad()
        return Difference()(self.outer, self.inner).render_scad()
    def get_height(self):
        return self.outer.height
    def set_height(self, height):
        # We make the inner slightly longer
        self.inner.height = height * self.padding
        self.outer.height = height
    height = property(get_height, set_height)

    def get_padding(self):
        return self._padding
    def set_padding(self, padding):
        # We make the inner slightly longer
        self._padding = padding
        self.height = self.height
    padding = property(get_padding, set_padding)

class Chamfer(SCAD_Object):
    Defaults = {
        "chamfer": {"type": float, "default": 4},
        "radius": {"type": float, "default": 4},
        "center": {"type": bool, "default": False},
        "invert": {"type": bool, "default": False},
    }

    def render_scad(self, *args, **kw):
        if self.invert:
            return Pipe(
                        ir2=self.radius - self.chamfer, 
                        or2=self.radius, 
                        ir1=self.radius * 1.05, 
                        or1=self.radius + self.chamfer, 
                        h=self.chamfer, 
                        center=self.center,
                        padding=1.2,
                    ).render_scad(*args, **kw)
        else:
            return Pipe(
                        or2=self.radius + self.chamfer, 
                        ir2=self.radius * 1.05, 
                        or1=self.radius, 
                        ir1=self.radius - self.chamfer, 
                        h=self.chamfer, 
                        center=self.center,
                        padding=1.2,
                    ).render_scad(*args, **kw)

class Frame(SCAD_Object):
    Defaults = {
        "inner": {"type": Cube},
        "outer": {"type": Cube},
    }
    Aliases = {
        'i': 'inner',
        'o': 'outer'
    }
    def render_scad(self, *args, **kw):
        return Difference()(self.outer, self.inner).render_scad()

class SemiCylinder(SCAD_Object):
    Defaults = {
        "angle": {"type": float, "default":180},
        "phase": {"type": float},
        "radius": {"type": float, "default": 1.0},
        "resolution": {"type": RadialResolution, "default": lambda: RadialResolution(), "propagate": True},
        "height": {"type": float, "default": 1.0},
    }

    def _xy_angle(self, angle):
        x = math.cos(math.radians(angle)) * self.radius
        y = math.sin(math.radians(angle)) * self.radius
        return (x, y)

    @property
    def points(self):
        arclength = (self.angle * math.pi * self.radius) / 180.0
        if not arclength:
            return ListVector2D()
        fragments = self.resolution.get_fragments(arclength, angle=self.angle)
        angle_step = self.angle / fragments if fragments else 0
        points = []
        rem = (self.angle - fragments * angle_step) / 2.0
        points.append(self._xy_angle(self.phase))
        for fragment in range(fragments):
            step = fragment * angle_step + self.phase + rem
            points.append(self._xy_angle(step))
        points.append(self._xy_angle(self.angle + self.phase))
        return ListVector2D(points)

    def render_scad(self, *args, **kw):
        scad = ''
        ret = Polygon(points=self.points)
        if self.height:
            ret = LinearExtrude(height=self.height)(ret)
        return ret.render_scad()

class Arc(SCAD_Object):
    Defaults = {
        "inner": {"type": SemiCylinder},
        "outer": {"type": SemiCylinder},
        "_height": {"type": int},
    }
    Aliases = {
        'i': 'inner',
        'o': 'outer'
    }
    def render_scad(self, *args, **kw):
        return Difference()(self.outer, self.inner).render_scad()
    def get_height(self):
        return self.inner.height
    def set_height(self, height):
        self.inner.height = height
        self.outer.height = height
    height = property(get_height, set_height)

class Octohedron(SCAD_Object):
    Defaults = {
        "height": {"type": float, "default": 1.0},
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

    def render_scad(self, *args, **kw):
        return Polyhedron(points=list(self.points), faces=list(self.faces)).render_scad()

class Tetrahedron(SCAD_Object):
    Defaults = {
        "height": {"type": float, "default": 1.0},
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

    def render_scad(self, *args, **kw):
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

def init_module():
    _current_module = sys.modules[__name__]
    ret = []
    for (name, obj) in globals().items():
        if (inspect.getmodule(obj) == _current_module) and inspect.isclass(obj) and issubclass(obj, SCAD_Object):
            setattr(_current_module, name.lower(), getattr(_current_module, name))
            ret.extend((name, name.lower()))
    return ret

__all__ = init_module()
