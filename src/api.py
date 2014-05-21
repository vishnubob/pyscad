# sckt - OpenSCAD Tool Kit
# Giles Hall (C) 2014
from . utils import *
from solid import *
import logging

logger = logging.getLogger(__name__)

class BaseObject(dict):
    def __getattr__(self, key):
        if key in self and self[key] != None:
            return self[key]
        return super(BaseObject, self).__getattribute__(key)

    def __setattr__(self, key, val):
        if key in self:
            self[key] = val
            return
        super(BaseObject, self).__setattr__(key, val)

class RootObject(BaseObject):
    def __init__(self, **conf):
        self._parts = []
        _dct = {}
        _dct["name"] = conf.get("name", "root")
        _dct["build"] = conf.get("build", [])
        if "all" in _dct["build"]:
            _dct["build"] = parts.keys()
        super(RootObject, self).__init__(**_dct)

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

class Part(BaseObject):
    Defaults = {}
    Name = ''

    def __init__(self, root, **kw):
        self.root = root
        self.root.register_part(self)
        _dct = self.Defaults.copy()
        _dct.update(kw)
        super(Part, self).__init__(**_dct)

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

