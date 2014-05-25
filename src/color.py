from base import BaseObject
from vector import BaseVector, ListVector
from colornames import ColorNames as __colornames__

__all__ = [
    "VectorColor",
]

class VectorColor(BaseVector):
    ColorNames = __colornames__
    Axes = ['red', 'green', 'blue', 'alpha']
    Defaults = {
        "colorname": {"type": str, "default": None, "cast": False}
    }

    def set_colorname(self, color):
        if color not in self.ColorNames:
            raise ValueError, "Unknown color '%s'" % color
        ns = dict(zip(self.Axes, self.ColorNames[color]))
        self.update(ns)

    def get_colorname(self):
        distances = [(color, VectorColor(self.ColorNames[color]).distance(self)) for color in self.ColorNames]
        distances.sort(key=lambda x: x[1])
        return distances[0][0]
    colorname = property(get_colorname, set_colorname)

ListVectorColor = ListVector.factory(VectorColor)
