import math
import operator
import itertools
from base import BaseObject, BaseObjectMetaclass, SCAD_BaseObjectMetaclass

__all__ = [
    "Vector2D",
    "ListVector2D",
    "Vector3D",
    "ListVector3D",
    "BaseVector",
]

class BaseVectorMetaClass(SCAD_BaseObjectMetaclass):
    @classmethod
    def new_hook(cls, name, bases, ns):
        axes = ns.get("Axes")
        defaults = ns.get("Defaults", {})
        defaults.update({axis: {"type": float} for axis in axes if axis not in defaults})
        ns["Defaults"] = defaults
        return SCAD_BaseObjectMetaclass.new_hook(name, bases, ns)

class BaseVector(BaseObject):
    __metaclass__ = BaseVectorMetaClass

    Axes = ()
    Defaults = {}
    Aliases = {}

    def __init__(self, args=(), **kw):
        kw.update({self.Axes[idx]: val for (idx, val) in enumerate(args)})
        super(BaseVector, self).__init__(**kw)
    
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
        return sum([val ** len(self.Axes) for val in self]) ** (1.0 / len(self.Axes))
    
    def distance(self, other):
        return math.sqrt(sum([(a1 - a2) ** 2 for (a1, a2) in zip(self, other)]))

    def dotproduct(self, other):
        return sum([self[axis] * other[axis] for axis in self.Axes])

    def norm(self):
        return sum([i ** 2 for i in self]) ** .5

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

    def __init__(self, iterable=()):
        vv = [self.cast(i) for i in iterable]
        super(ListVector, self).__init__(vv)

    def cast(self, item):
        if not isinstance(item, self.VectorType):
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

    @classmethod
    def factory(cls, vector_type, name=None):
        name = name or "List" + vector_type.__name__
        return type(name, (cls,), {"VectorType": vector_type})

class Vector2D(BaseVector):
    Axes = ['x', 'y']
    AliasMap = {
        'x': ('X', 'width', 'w'),
        'y': ('Y', 'depth', 'd'),
    }
ListVector2D = ListVector.factory(Vector2D)

class Vector3D(BaseVector):
    Axes = ['x', 'y', 'z']
    AliasMap = {
        'x': ('X', 'width', 'w'),
        'y': ('Y', 'depth', 'd'),
        'z': ('Z', 'height', 'h'),
    }
ListVector3D = ListVector.factory(Vector3D)
