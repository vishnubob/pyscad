from scad import *
from vector import *
import logging

__all__ = [
    "Cube",
]

logger = logging.getLogger(__name__)

class Cube(SCAD_Object):
    SCAD_Template = "cube(%(size)s, center=%(center)s)"
    Aliases = {
        'x': 'size.x',
        'y': 'size.y',
        'z': 'size.z',
    }
    Defaults = {
        "size": 1,
        "center": False
    }

    def get_size(self):
        return self["size"]

    def set_size(self, size):
        if type(size) in (int, float):
            size = [size] * 3
        self["size"] = Vector3D(size)
    size = property(get_size, set_size)

    def process_args(self, args):
        size = args[0] if (len(args) == 1) else args
        return {"size": size}
