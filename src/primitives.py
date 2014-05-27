from color import *
from core import *
from vector import *
import logging
import inspect
import sys

logger = logging.getLogger(__name__)

class Color(SCAD_Primitive):
    SCAD_Name = "color"

    Defaults = {
        "color": {"type": VectorColor, "default": lambda: VectorColor()},
    }
    Aliases = {
        "colorname": "color.colorname",
    }

    def __init__(self, args=(), **kw):
        if args:
            if type(args) in (str, unicode):
                kw["colorname"] = args
            else:
                kw["color"] = args
        super(SCAD_Primitive, self).__init__(**kw)
    
class Projection(SCAD_Primitive):
    SCAD_Name = "projection"
    Defaults = {
        "cut": {"type": bool, "default": False}
    }

class Union(SCAD_Primitive):
    SCAD_Name = "union"

class Difference(SCAD_Primitive):
    SCAD_Name = "difference"

class Intersection(SCAD_Primitive):
    SCAD_Name = "intersection"

class Minowski(SCAD_Primitive):
    SCAD_Name = "minowski"

class Hull(SCAD_Primitive):
    SCAD_Name = "hull"

class Render(SCAD_Primitive):
    SCAD_Name = "render"

class Rotate(Vector3D_SCAD_Primitive):
    SCAD_Name = "rotate"

class Translate(Vector3D_SCAD_Primitive):
    SCAD_Name = "translate"

class Polyhedron(Vector3D_SCAD_Primitive):
    SCAD_Name = "polyhedron"
    Defaults = {
        "points": {"type": ListVector3D},
        "faces": {"type": ListVector3D},
        "convexity": {"type": int, "default": None},
    }
    def get_scad_args(self):
        pts = [list(i) for i in self.points]
        faces = [list(i) for i in self.faces]
        args = [("points", pts), ("faces", faces)]
        if self.convexity != None:
            args.append(("convexity", self.convexity))
        return args

class Polygon(Vector3D_SCAD_Primitive):
    SCAD_Name = "polygon"
    Defaults = {
        "points": {"type": ListVector2D},
        "paths": {"type": ListVector2D},
        "convexity": {"type": int, "default": None},
    }
    def get_scad_args(self):
        pts = [list(i) for i in self.points]
        paths = [list(i) for i in self.paths]
        args = [("points", pts)]
        if paths:
            args.append(paths)
        if self.convexity != None:
            args.append(("convexity", self.convexity))
        return args

class LinearExtrude(SCAD_Primitive):
    SCAD_Name = "linear_extrude"
    Defaults = {
        "height": {"type": float},
        "center": {"type": bool, "default": False},
        "convexity": {"type": int, "default": None},
        "twist": {"type": float},
        "slices": {"type": int, "default": 20},
        "scale": {"type": float, "default": 1.0},
    }
    def get_scad_args(self):
        args = []
        args.append(("height", self.height))
        args.append(("center", self.center))
        args.append(("twist", self.twist))
        args.append(("slices", self.slices))
        args.append(("scale", self.scale))
        if self.convexity != None:
            args.append(("convexity", self.convexity))
        return args

class Cube(SCAD_Primitive):
    SCAD_Name = "cube"
    Aliases = {
        'x': 'size.x',
        'y': 'size.y',
        'z': 'size.z',
    }
    Defaults = {
        "size": {"type": Vector3D, "default": lambda: Vector3D([1.0, 1.0, 1.0])},
        "center": {"type": bool, "default": False},
    }

    def __init__(self, args=(), **kw):
        if args:
            kw["size"] = args
        super(Cube, self).__init__(**kw)

    def get_scad_args(self):
        return [self.size, ("center", self.center)]

    def get_size(self):
        return self["size"]

    def set_size(self, size):
        if type(size) in (int, float):
            size = [size] * 3
        self["size"] = Vector3D(size)
    size = property(get_size, set_size)

class Cylinder(SCAD_Primitive):
    SCAD_Name = "cylinder"
    Defaults = {
        "radius_1": {"type": float, "default": 1.0},
        "radius_2": {"type": float, "default": None},
        "center": {"type": bool, "default": False},
        "resolution": {"type": RadialResolution, "default": lambda: RadialResolution()},
        "height": {"type": float, "default": 1.0},
    }

    def get_scad_args(self):
        scad = []
        if not self.r2:
            scad.append(("r", self.radius_1))
        else:
            scad.append(("r1", self.radius_1))
            scad.append(("r2", self.radius_2))
        scad.append(("h", self.height))
        scad.append(("center", self.center))
        scad += self.resolution.get_scad_args()
        return scad

    def get_diamater_1(self):
        return self.radius_1 * 2
    def set_diamater_1(self, dia):
        self.radius_1 = dia / 2.0
    diameter_1 = property(get_diamater_1, set_diamater_1)

    def get_diamater_2(self):
        return self.radius_2 * 2
    def set_diamater_2(self, dia):
        self.radius_2 = dia / 2.0
    diameter_2 = property(get_diamater_2, set_diamater_2)

class Sphere(SCAD_Primitive):
    SCAD_Name = "sphere"
    Aliases = {
        'fn': 'resolution.fn',
        'fa': 'resolution.fa',
        'fs': 'resolution.fs',
    }
    Defaults = {
        "radius": {"type": float, "default": 1.0},
        "center": {"type": bool, "default": False},
        "resolution": {"type": RadialResolution, "default": lambda: RadialResolution()},
    }

    def get_scad_args(self):
        scad = []
        scad.append(("r", self.radius))
        scad.append(("center", self.center))
        scad += self.resolution.get_scad_args()
        return scad

    def get_diamater(self):
        return self.radius * 2
    def set_diamater(self, dia):
        self.radius = dia / 2.0
    diameter = property(get_diamater, set_diamater)

#
# auto generate __all__
#

_current_module = sys.modules[__name__]
__all__ = [name for (name, obj) in globals().items() if (inspect.getmodule(obj) == _current_module) and inspect.isclass(obj) and issubclass(obj, SCAD_Primitive)]
