# sckt - OpenSCAD Tool Kit
# Giles Hall (C) 2014
from . utils import *
from solid import *
import logging
import itertools

logger = logging.getLogger(__name__)

class BaseObject(dict):
    Defaults = {}
    Aliases = {}
    Reserved = {"parent": lambda: None, "stack": lambda: dict(), "children": lambda: list(), "name": lambda: None}

    def __init__(self, *args, **kw):
        super(BaseObject, self).__init__()
        self.__kw = kw
        self.__args = args
        self.process_reserved_names(kw)
        self.update(self.Defaults)
        self.update(self.__kw)
        self.update(self.process_args(args))

    def process_reserved_names(self, kw):
        for key in self.Reserved:
            if key in kw:
                setattr(self, key, kw[key])
            else:
                setattr(self, key, self.Reserved[key]())

    def process_args(self, args):
        return {}

    def __call__(self, *args, **kw):
        pass

    # dict interface
    def update(self, ref):
        pred = lambda key: (key[0] != "_") and (key not in self.Reserved)
        super(BaseObject, self).update({key: val for (key, val) in ref.items() if pred(key)})

    def __getstate__(self):
        state = {}
        state["__stack__"] = self.stack
        state["__children__"] = self.children
        state["__parent__"] = self.parent
        state["__name__"] = self.name
        state["__namespace__"] = dict(self)
        return obj
        
    def __setstate__(self, state):
        self.stack = state["__stack__"]
        self.children = state["__children__"]
        self.parent = state["__parent__"]
        self.name = state["__name__"]
        self.update(state["__namespace__"])

    def copy(self, descend=True, keep_stack=True):
        obj = self.__new__()
        obj.__init__(*self.__args, **self.__kw__)
        obj.update(self)
        if keep_stack:
            obj.__dict__["__stack__"] = self.__stack__[:]
        if descend:
            obj.__dict__["__children__"] = self.apply_children(lambda c: c.copy())
        return obj

    # attribute access
    def __getattr__(self, key):
        key = self.Aliases.get(key, key)
        if (key in self):
            return super(BaseObject, self).__getitem__(key)
        if self.parent:
            try:
                return getattr(self.parent, key)
            except AttributeError:
                pass
        return super(BaseObject, self).__getattr__(key)
    __getitem__ = __getattr__

    def __setattr__(self, key, val):
        key = self.Aliases.get(key, key)
        if (key[0] != "_"):
            super(BaseObject, self).__setitem__(key, val)
            if isinstance(val, BaseObject):
                val.name = key
                self.add_child(val)
        else:
            super(BaseObject, self).__setattr__(key, val)
    __setitem__ = __setattr__

    # children
    def get_children(self):
        return tuple(self.__children__)

    def set_children(self, children):
        self.__children__ = children
        for child in self.__children__:
            child.parent = self
    children = property(get_children, set_children)

    def iter_children(self):
        return iter(self.__children__)

    def apply_children(self, call, predicate=None):
        def default_predicate(child):
            return True
        predicate = predicate or default_predicate
        return [getattr(child, callname)(*args, **kw) for child in self.children if predicate(child)]

    def add_child(self, child):
        child.parent = self
        self.__children__.append(child)

    def remove_child(self, child):
        child.parent = None
        del self.__children__[self.__children__.index(child)]

    # parent
    @property
    def parent(self):
        return self.__parent__

    @parent.setter
    def set_parent(self, parent):
        if self.__parent__ and (self in self.__parent__.children):
            self.__parent__.remove_child(self)
        assert self.__parent__ == None
        self.__parent__ = parent
    
    # stack
    @property
    def stack(self):
        return tuple(self.__stack__)

    @stack.setter
    def set_stack(self, stack):
        self.__stack__ = stack
    
    def push(self, descend=True):
        self.__stack__.append(dict(self))
        if descend:
            self.apply_children(lambda c: c.push())

    def pop(self, descend=True):
        self.clear()
        self.update(self.__stack__.pop())
        if descend:
            self.apply_children(lambda c: c.pop())

class Vector(BaseObject):
    Axes = {'x': 0, 'y': 1, 'z': 2}
    AxesName = ['x', 'y', 'z']
    Defaults = {'x': 0.0, 'y': 0.0, 'z': 0.0}
    Aliases = {'X': 'x', 'Y': 'y', 'Z': 'z'}

    def process_args(self, args):
        if args and (len(args) == 1) and (type(args[0]) in (list, tuple)):
            args = args[0]
        ret = {self.AxesName[idx]: val for (idx, val) in enumerate(args)}
        return ret

    @property
    def vector(self):
        return tuple([self[axis] for axis in self.AxesName])

    def __iter__(self):
        return iter(self.vector)

    def __add__(self, other):
        if isinstance(other, self.__class__):
            return Vector([(v1 + v2) for (v1, v2) in zip(self, other)])
        else:
            return Vector([(v1 + other) for v1 in self.vector])

    def __sub__(self, other):
        if isinstance(other, self.__class__):
            return Vector([(v1 - v2) for (v1, v2) in zip(self, other)])
        else:
            return Vector([(v1 - other) for v1 in self])

    def scale(self, other):
        return Vector([operator.mult(v1, other) for v1 in self])

    def magnitude(self):
        return pow(sum([pow(val, len(self.Axis)) for val in self]), 1.0 / len(self.Axis))
    
    def dotproduct(self, other):
        return sum([self[axis] * other[axis] for axis in self.Axes])

    def crossproduct(self, other):
        new_vector = {}
        for (axis_idx, axis) in enumerate(self.AxesName):
            other_axes = [idx % len(self.Axes) for idx in range(axis_idx + 1, len(self.Axes)  + axis_idx)]
            other_axes = [self.AxesName[other_axis] for other_axis in other_axes]
            val = reduce(operator.sub, [self[a1] * other[a2] for (a1, a2) in itertools.permutations(other_axes)])
            new_vector[axis] = val
        return Vector(**new_vector)

    def __slice__(self, *args, **kw):
        return self.vector.__slice__(*args, **kw)

    def __delattr__(self, key):
        raise RuntimeError, "operation not supported"

class RootPart(BaseObject):
    def __init__(self, **conf):
        self._parts = []
        _dct = {}
        _dct["name"] = conf.get("name", "root")
        _dct["build"] = conf.get("build", [])
        if "all" in _dct["build"]:
            _dct["build"] = parts.keys()
        super(RootPart, self).__init__(**_dct)

    def register_part(self, part):
        self._parts.append(part)

    def override(self, config):
        for (key, val) in config.items():
            keys = key.split('.')
            obj = self
            for _key in keys[:-1]:
                obj = getattr(obj, _key)
            setattr(obj, keys[-1], val)

    def get_build(self):
        return {part_name: self.parts[part_name].get_build() for part_name in self.parts}

class LinkedPart(BaseObject):
    Defaults = {}
    Name = ''

    def __init__(self, root, **kw):
        self.root = root
        self.root.register_part(self)
        _dct = self.Defaults.copy()
        _dct.update(kw)
        super(LinkedPart, self).__init__(**_dct)

    @cproperty
    @classmethod
    def name(cls):
        return cls.Name or cls.__name__

    @cproperty
    @classmethod
    def names(cls):
        if hasattr(super(cls.__class__), "names"):
            return [cls.Name] + super(cls, cls.__class__).names
        return [cls.Name]

    def get_build(self):
        if self.name in self.root.build:
            return self.render_scad()
        return ''

    def render_scad(self):
        return ''

