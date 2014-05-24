import logging
import inspect
import types

logger = logging.getLogger(__name__)

__all__ = ["SCAD_Object"]

class BaseObjectMetaclass(type):
    def __new__(cls, name, bases, ns):
        def mro_walk(name, bases):
            dct = {}
            map(lambda _cls: dct.update(getattr(_cls, name, {})), bases)
            return dct

        ns["Defaults"] = ns.get("Defaults", {})
        ns["Defaults"].update(mro_walk("Defaults", bases))
        ns["Aliases"] = ns.get("Aliases", {})
        ns["Aliases"].update(mro_walk("Aliases", bases))
        ns["Resserved"] = ns.get("Reserved", {})
        ns["Resserved"].update(mro_walk("Reserved", bases))
        for key in ns["Defaults"]:
            if key in ns:
                continue
            def fget(self, attr=key):
                return self[attr]
            def fset(self, value, attr=key):
                cast = self.Defaults[attr].get("cast", True)
                default_type = self.Defaults[attr]["type"]
                if cast and type(value) != default_type:
                    # cast variable to proper type
                    castfunc = cast if type(cast) == types.FunctionType else default_type
                    try:
                        value = castfunc(value)
                    except TypeError:
                        msg = "Attribute '%s' must be castable to a %s, and can not be a %s" % (attr, default_type, type(value))
                        raise TypeError, msg
                self[attr] = value
            ns[key] = property(fget, fset)
        return type.__new__(cls, name, bases, ns)

class BaseObject(object):
    __metaclass__ = BaseObjectMetaclass
    Defaults = {}
    Aliases = {}
    Reserved = {
        "parent": {"type": type, "default": None, "cast": False}, 
        "stack": {"type": list},
        "children": {"type": set},
        "name": {"type": str}
    }

    def __init__(self, *args, **kw):
        super(BaseObject, self).__init__()
        if len(args) == 1 and type(args[0]) in (list, tuple):
            args = args[0]
        self.__namespace__ = {}
        self.__kw__ = kw
        self.__args__ = args
        rem_kw = self.process_reserved_names(kw)
        self.__namespace__ = self.process_defaults()
        self.update(self.process_args(args))
        self.update(rem_kw)

    def process_defaults(self, kw={}):
        return {key: kw.get(key, self.default_value(self.Defaults[key])) for key in self.Defaults}

    def process_reserved_names(self, kw={}):
        for key in self.Reserved:
            mangled_name = "__%s__" % key.lower()
            value = kw.get(key, self.default_value(self.Reserved[key]))
            setattr(self, mangled_name, value)
        return {key: val for (key, val) in kw.items() if key not in self.Reserved}

    def default_value(self, info):
        _type = info.get("type")
        default = info["default"] if "default" in info else _type()
        if type(default) == types.FunctionType:
            default = default()
        return default

    def process_args(self, args):
        return {}

    def __call__(self, *args, **kw):
        pass

    # dict / object interface
    def update(self, ref):
        for (key, val) in ref.items():
            setattr(self, key, val)

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

    def copy(self, descend=True, stack=True):
        obj = self.__new__()
        obj.__init__(*self.__args, **self.__kw__)
        obj.update(self.__namespace__)
        obj.__dict__["__name__"] = self.__name__
        if stack:
            obj.__dict__["__stack__"] = self.__stack__[:]
        if descend:
            obj.__dict__["__children__"] = self.apply_children(lambda c: c.copy())
        return obj

    def get_namespace(self):
        return self.__namespace__

    def set_namespace(self, ns):
        self.__namespace__.clear()
        self.update(ns)
    namespace = property(get_namespace, set_namespace)

    def __hash__(self):
        return id(self)

    def __cmp__(self, other):
        return cmp(id(self), id(other))

    # attribute access
    def resolve(self, key):
        if type(key) in (str, unicode):
            key = key.split('.')
        obj = self
        for attr in key:
            obj = getattr(obj, attr)
        return obj
    
    def __getitem__(self, key):
        if '.' in key:
            return self.__getattr__(key, val)
        return self.__namespace__[key]

    def __getattr__(self, key):
        key = self.Aliases.get(key, key)
        if '.' in key:
            return self.resolve(key)
        if self.parent:
            try:
                return getattr(self.parent, key)
            except AttributeError:
                pass
        return super(BaseObject, self).__getattribute__(key)

    def __setitem__(self, key, val):
        if '.' in key:
            self.__setattr__(key, val)
        self.__namespace__[key] = val

    def __setattr__(self, key, val):
        key = self.Aliases.get(key, key)
        if '.' in key:
            parts = key.split('.')
            obj = self.resolve(parts[:-1])
            setattr(obj, parts[-1], val)
        super(BaseObject, self).__setattr__(key, val)

    # children
    def __call__(self, *args):
        if (len(args) == 1) and type(args[0]) in (list, tuple):
            args = args[0]
        self.set_children(args)
        return self

    def get_children(self):
        return tuple(self.__children__)

    def set_children(self, children):
        self.disown_children()
        self.__children__ = set(children)
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
        if child.parent != self:
            child.parent = self
        self.__children__.add(child)

    def remove_child(self, child):
        self.__children__.remove(child)
        child.__parent__ = None

    def disown_children(self):
        for child in self.children[:]:
            self.remove_child(child)

    # parent
    def get_parent(self):
        return self.__parent__

    def set_parent(self, parent):
        if self.__parent__ and (self in self.__parent__.children):
            self.__parent__.remove_child(self)
        assert self.__parent__ == None
        self.__parent__ = parent
        if self not in self.parent.children:
            parent.add_child(self)
    parent = property(get_parent, set_parent)
    
    # stack
    def get_stack(self):
        return tuple(self.__stack__)

    def set_stack(self, stack):
        self.__stack__ = stack
    stack = property(get_stack, set_stack)
    
    def push(self, descend=False):
        self.__stack__.append(self.__namespace__.copy())
        if descend:
            self.apply_children(lambda c: c.push())

    def pop(self, descend=False):
        self.__namespace__.clear()
        self.update(self.__stack__.pop())
        if descend:
            self.apply_children(lambda c: c.pop())
