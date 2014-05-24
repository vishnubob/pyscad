import math
import operator
import itertools
from base import BaseObject

__all__ = [
    "Vector2D",
    "ListVector2D",
    "Vector3D",
    "ListVector3D",
    "BaseVector",
]

class BaseVector(BaseObject):
    Axes = ()
    Defaults = {}
    Aliases = {}

    def process_args(self, args):
        if args and (len(args) == 1) and (type(args[0]) in (list, tuple)):
            args = args[0]
        ret = {self.Axes[idx]: val for (idx, val) in enumerate(args)}
        return ret
    
    @property
    def vector(self):
        return tuple([self[axis] for axis in self.Axes])

    def __iter__(self):
        return iter(self.vector)

    def __add__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__([(v1 + v2) for (v1, v2) in zip(self, other)])
        else:
            return self.__class__([(v1 + other) for v1 in self.vector])

    def __sub__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__([(v1 - v2) for (v1, v2) in zip(self, other)])
        else:
            return self.__class__([(v1 - other) for v1 in self])

    def scale(self, other):
        return self.__class__([operator.mult(v1, other) for v1 in self])

    def magnitude(self):
        return pow(sum([pow(val, len(self.Axes)) for val in self]), 1.0 / len(self.Axes))
    
    def distance(self, other):
        return math.sqrt(sum([pow(a1 - a2, 2) for (a1, a2) in zip(self, other)]))

    def dotproduct(self, other):
        return sum([self[axis] * other[axis] for axis in self.Axes])

    def crossproduct(self, other):
        new_vector = {}
        for (axis_idx, axis) in enumerate(self.Axes):
            other_axes = [idx % len(self.Axes) for idx in range(axis_idx + 1, len(self.Axes)  + axis_idx)]
            other_axes = [self.Axes[other_axis] for other_axis in other_axes]
            val = reduce(operator.sub, [self[a1] * other[a2] for (a1, a2) in itertools.permutations(other_axes)])
            new_vector[axis] = val
        return self.__class__(**new_vector)

    def __slice__(self, *args, **kw):
        return self.vector.__slice__(*args, **kw)

    def __delattr__(self, key):
        raise RuntimeError, "operation not supported"

class ListVector(list):
    VectorType = BaseVector

    def __init__(self, *args):
        import traceback
        frames = 4
        vv = [self.cast(i) for i in args]
        super(ListVector, self).__init__(vv)

    def cast(self, item):
        if isinstance(item, self.VectorType):
            item = self.VectorType(item)
        return item

    def __setitem__(self, item):
        super(ListVector, self).__setitem__(self.cast(item))

    def append(self, item):
        super(ListVector, self).append(self.cast(item))

    def extend(self, items):
        super(ListVector, self).extend([self.cast(i) for i in args])

    def insert(self, index, item):
        super(ListVector, self).insert(index, self.cast(item))


def vector_type_factory(name, axes, aliases=None, default=0.0, defaults_map=None, baseclass=None):
    # vector_type
    defaults_map = defaults_map or {}
    baseclass = baseclass or BaseVector
    axes = tuple([axis.lower() for axis in axes])
    aliases = aliases or {axis: (axis.upper(),) for axis in axes}
    aliases = dict(itertools.chain(*[itertools.product(tag, val) for (val, tag) in aliases.items()]))
    defaults = {axis: {"type": float, "default": defaults_map.get(axis, default)} for axis in axes}
    ns = {
        "Axes": axes,
        "Defaults": defaults,
        "Aliases": aliases,
    }
    vector_type = type(name, (baseclass,), ns)
    # list_vector_type
    list_vector_type = type("List" + name, (ListVector,), {"VectorType": vector_type})
    return (vector_type, list_vector_type)

(Vector2D, ListVector2D) = vector_type_factory("Vector2D", ['x', 'y'])
(Vector3D, ListVector3D) = vector_type_factory("Vector3D", ['x', 'y', 'z'], aliases={'x': ('X', 'h', 'height'), 'y': ('Y', 'w', 'width'), 'z': ('Z', 'd', 'depth')})

