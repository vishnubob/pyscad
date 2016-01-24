import sys
import logging
import inspect
import types
import re

logger = logging.getLogger(__name__)

__all__ = ["SCAD_Object"]

__name_index__ = {}
def get_name_with_index(name):
    idx = __name_index__.get(name, 1)
    __name_index__[name] = idx + 1
    return "%s_%s" % (name, idx)

class BaseObjectMetaclass(type):
    def __new__(cls, name, bases, ns):
        ns["Defaults"] = ns.get("Defaults", {})
        ns["Defaults"].update(cls.mro_walk("Defaults", bases))
        ns["Aliases"] = ns.get("Aliases", {})
        ns["Aliases"].update(cls.mro_walk("Aliases", bases))
        ns["Resserved"] = ns.get("Reserved", {})
        ns["Resserved"].update(cls.mro_walk("Reserved", bases))
        ns["InnerObjects"] = cls.get_inner_objets(name, bases, ns)
        # call any hooks
        cls.new_hook(name, bases, ns)
        # add automatic properties
        for key in ns["Defaults"]:
            if key in ns:
                continue
            cls.property_hook(name, bases, ns, key)
        return type.__new__(cls, name, bases, ns)

    @classmethod
    def get_inner_objets(cls, name, bases, ns):
        res = []
        for key in ns["Defaults"].keys() + ns.keys():
            cobj = ns["Defaults"].get(key, {"type": None})["type"]
            if inspect.isclass(cobj) and issubclass(cobj, BaseObject):
                res.append((key, cobj))
        return res

    @classmethod
    def mro_walk(cls, name, bases):
        dct = {}
        map(lambda _cls: dct.update(getattr(_cls, name, {})), bases)
        return dct

    @classmethod
    def property_hook(cls, name, bases, ns, key):
        def fget(self, attr=key):
            return self[attr]
        def fset(self, value, attr=key):
            cast = self.Defaults[attr].get("cast", True)
            propagate = self.Defaults[attr].get("propagate", False)
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
            if propagate:
                for (oname, cobj) in self.InnerObjects:
                    try:
                        setattr(getattr(self, oname), attr, value)
                    except KeyError:
                        pass
                    except AttributeError:
                        pass
        ns[key] = property(fget, fset)

    @classmethod
    def new_hook(cls, name, bases, ns):
        pass

class SCAD_BaseObjectMetaclass(BaseObjectMetaclass):
    GlobalAliases = {
        'red': ('r', 'R'),
        'green': ('g', 'G'),
        'blue': ('b', 'B'),
        'alpha': ('a', 'A'),
        'height': ('h', 'H'),
        'radius': ('r', 'R'),
        'radius_1': ('r', 'R', 'r1', 'R1'),
        'radius_2': ('r2', 'R2'),
        'diameter': ('d', 'D', 'dia'),
        'diameter_1': ('d', 'D', 'dia', 'd1', 'D1', 'dia1'),
        'diameter_2': ('d2', 'D2', 'dia2'),
        'edge': ('e',),
        'x': ('X', 'width'),
        'y': ('Y', 'depth'),
        'z': ('Z', 'height'),
        'inner': ('i*', 'I*'),
        'outer': ('o*', 'O*'),
    }

    ResolutionGlobals = {
        'fn': 'resolution.fn',
        'fa': 'resolution.fa',
        'fs': 'resolution.fs',
    }

    @classmethod
    def new_hook(cls, name, bases, ns):
        aliases = ns.get("Aliases", {})
        defaults = ns.get("Defaults", {})
        new_aliases = {}
        new_aliases.update(cls.get_maps(aliases, cls.GlobalAliases))
        new_aliases.update(cls.get_maps(defaults, cls.GlobalAliases))
        new_aliases.update(cls.get_maps(ns, cls.GlobalAliases))
        if "resolution" in defaults:
            new_aliases.update(cls.ResolutionGlobals)
        new_aliases.update(aliases)
        ns["Aliases"] = new_aliases

    @classmethod
    def get_maps(cls, ns, aliases):
        return {alias: key for key in ns for alias in aliases.get(key, ()) if key != alias}
    
class BaseObject(object):
    __metaclass__ = BaseObjectMetaclass
    Defaults = {}
    Aliases = {}
    Reserved = {
        "stack": {"type": list},
        "children": {"type": list},
        "name": {"type": str}
    }

    def __init__(self, **kw):
        super(BaseObject, self).__init__()
        self.__namespace__ = {}
        if not kw.get("name", None):
            kw["name"] = get_name_with_index(self.__class__.__name__)
        self.__kw__ = kw
        rem_kw = self.process_reserved_names(kw)
        self.__namespace__ = self.process_defaults()
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

    # dict / object interface
    def update(self, ref):
        for (key, val) in ref.items():
            setattr(self, key, val)

    def __getstate__(self):
        state = {}
        state["__stack__"] = self.stack
        state["__children__"] = self.children
        state["__name__"] = self.name
        state["__namespace__"] = dict(self)
        return obj
        
    def __setstate__(self, state):
        self.stack = state["__stack__"]
        self.children = state["__children__"]
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

    # set item and get item do not translate keys,
    # nor will they call setters / getters
    def __getitem__(self, key):
        if '.' in key:
            return self.__getattr__(key, val)
        return self.__namespace__[key]

    def __setitem__(self, key, val):
        if '.' in key:
            self.__setattr__(key, val)
        self.__namespace__[key] = val

    @property
    def magic_aliases(self):
        for alias in self.Aliases:
            if alias.endswith('*'):
                regex = "(%s)(.*)" % alias[:-1]
                yield re.compile(regex)

    def resolve_magic_alias(self, key):
        m = None
        for regex in self.magic_aliases:
            m = regex.match(key)
            if m:
                break
        if m:
            (key, subkey) = m.groups()
            if hasattr(getattr(self, key), subkey):
                return "%s.%s" % (key, subkey)
        return key

    def resolve_alias(self, key):
        #if key in self.Defaults or key in dir(self):
        if key in self.Defaults or key in self.__dict__:
            return key
        if key not in self.Aliases:
            key = self.resolve_magic_alias(key)
            return key
        key = self.Aliases[key]
        if type(key) in (str, unicode):
            return self.resolve_alias(key)
        return [self.resolve_alias(subkey) for subkey in key]

    def __getattr__(self, key):
        key = self.resolve_alias(key)
        if type(key) in (str, unicode):
            if '.' in key:
                return self.resolve(key)
            for child in self.iter_children():
                if child.__name__ == key:
                    return child
            return super(BaseObject, self).__getattribute__(key)
        else:
            # XXX: only return the first key
            return self.__getattr__(key[0])

    def __setattr__(self, key, val):
        key = self.resolve_alias(key)
        if type(key) in (str, unicode):
            if '.' in key:
                parts = key.split('.')
                obj = self.resolve(parts[:-1])
                setattr(obj, parts[-1], val)
            else:
                super(BaseObject, self).__setattr__(key, val)
        else:
            for subkey in key:
                self.__setattr__(subkey, val)

    # children
    def __call__(self, *args):
        if (len(args) == 1) and type(args[0]) in (list, tuple):
            args = args[0]
        self.set_children(args)
        return self

    def get_children(self):
        return tuple(self.__children__)

    def set_children(self, children):
        if isinstance(children, BaseObject):
            children = (children,)
        self.disown_children()
        self.__children__ = list(children)
    children = property(get_children, set_children)

    def iter_children(self):
        return iter(self.__children__)

    def apply_children(self, call, predicate=None):
        def default_predicate(child):
            return True
        predicate = predicate or default_predicate
        return [getattr(child, callname)(*args, **kw) for child in self.children if predicate(child)]

    def disown_children(self):
        self.__children__ = list()

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

    # name
    def get_name(self):
        return self.__name__

    def set_name(self, name):
        self.__name__ = name
    name = property(get_name, set_name)
