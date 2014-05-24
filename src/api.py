from scad import *
from vector import *
import logging

__all__ = [
    "Cube",
    "Union",
    "Cylinder",
]

logger = logging.getLogger(__name__)

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

class Cube(SCAD_Primitive):
    SCAD_Name = "cube"
    Aliases = {
        'x': 'size.x',
        'y': 'size.y',
        'z': 'size.z',
    }
    Defaults = {
        "size": {"type": Vector3D, "default": lambda: Vector3D(1.0, 1.0, 1.0)},
        "center": {"type": bool, "default": False},
    }

    def get_scad_args(self):
        return [self.size, ("center", self.center)]

    def get_size(self):
        return self["size"]

    def set_size(self, size):
        if type(size) in (int, float):
            size = [size] * 3
        self["size"] = Vector3D(size)
    size = property(get_size, set_size)

    def process_args(self, args):
        ret = {}
        if args:
            ret["size"] = args[0] if (len(args) == 1) else args
        return ret

class RadialResolution(SCAD_Primitive):
    Defaults = {
        "fn": {"type": float, "default": None},
        "fs": {"type": float, "default": None},
        "fa": {"type": float, "default": None},
    }

    def get_scad_args(self):
        ret = []
        if self.fn:
            ret.append(("$fn", self.fn))
        else:
            if self.fa:
                ret.append(("$fa", self.fa))
            if self.fs:
                ret.append(("$fs", self.fs))
        return ret

class Cylinder(SCAD_Primitive):
    SCAD_Name = "cylinder"
    Aliases = {
        'fn': 'resolution.fn',
        'fa': 'resolution.fa',
        'fs': 'resolution.fs',
        'radius': 'radius_1',
        'r': 'radius_1',
        'r1': 'radius_1',
        'r2': 'radius_2',
        'diameter': 'diameter_1',
        'd': 'diameter_1',
        'd1': 'diameter_1',
        'd2': 'diameter_2',
        'h': 'height',
    }
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

    def get_resolution(self):
        if self["resolution"] == None:
            self["resolution"] = RadialResolution()
        return self["resolution"]
    
    def set_resolution(self, val):
        self["resolution"] = val
    resolution = property(get_resolution, set_resolution)

