from base import BaseObject
from vector import vector_type_factory
from colornames import ColorNames as __colornames__

__all__ = [
    "VectorColor",
]

(BaseVectorColor, ListBaseVectorColor) = vector_type_factory(
    "BaseVectorColor", 
    ['r', 'g', 'b', 'a'], 
    aliases = {
        'r': ('R', 'red'),
        'g': ('G', 'green'),
        'b': ('B', 'blue'),
        'a': ('A', 'alpha'),
    })

class VectorColor(BaseVectorColor):
    ColorNames = __colornames__

    def process_args(self, args):
        if (len(args) == 1) and type(args[0]) in (str, list):
            return {"color": args[0]}
        return super(VectorColor, self).process_args(args)

    def set_color(self, color):
        if color not in self.ColorNames:
            raise ValueError, "Unknown color '%s'" % color
        ns = dict(zip(self.Axes, self.ColorNames[color]))
        self.update(ns)

    def get_color(self):
        distances = [(color, VectorColor(*self.ColorNames[color]).distance(self)) for color in self.ColorNames]
        distances.sort(key=lambda x: x[1])
        return distances[0][0]
    color = property(get_color, set_color)
