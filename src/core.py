import os
import math
import sys
import tempfile
import logging
import inspect
from utils import which
from base import BaseObject, BaseObjectMetaclass, SCAD_BaseObjectMetaclass
from vector import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

__all__ = [
    "RadialResolution",
    "SCAD_Primitive",
    "SCAD_Object",
    "Vector3D_SCAD_Primitive",
    "OpenSCAD",
]

class SCAD_Object(BaseObject):
    __metaclass__ = SCAD_BaseObjectMetaclass

    Defaults = {
        "disable": {"type": bool, "default": False, "propagate": True},
        "debug": {"type": bool, "default": False, "propagate": True},
        "root": {"type": bool, "default": False, "propagate": True},
        "background": {"type": bool, "default": False, "propagate": True},
        "center": {"type": bool, "default": False, "propagate": True},
    }

    @property
    def scad_modifier(self):
        ret = ''
        if self.background:
            ret = '%'
        elif self.debug:
            ret = '#'
        elif self.root:
            ret = '!'
        elif self.disable:
            ret = '*'
        return ret

    def render_scad(self, *args, **kw):
        pass

    def render(self, *args, **kw):
        engine = OpenSCAD()
        return engine.render(self, *args, **kw)

class SCAD_Primitive(SCAD_Object):
    SCAD_Name = '__SCAD_Primitive__'

    def translate_arg_to_scad(self, arg):
        if isinstance(arg, tuple) and len(arg) == 2:
            lhs = self.translate_arg_to_scad(arg[0])
            rhs = self.translate_arg_to_scad(arg[1])
            return "%s=%s" % (lhs, rhs)
        if isinstance(arg, BaseVector):
            return str(list(arg))
        if isinstance(arg, bool):
            return str(arg).lower()
        return arg

    def render_args(self):
        args = self.get_scad_args()
        ret = str.join(', ', [self.translate_arg_to_scad(arg) for arg in args])
        return ret
    
    def render_scad(self, margin=4, level=0):
        args = self.render_args()
        macros = {
            "name": self.SCAD_Name,
            "margin": (' ' * margin) * level,
            "args": args,
            "modifier": self.scad_modifier,
        }
        if self.children:
            macros["body"] = str.join('\n', [child.render_scad(margin, level + 1) for child in self.children])
            scad = "%(margin)s%(modifier)s %(name)s(%(args)s) {\n%(body)s\n%(margin)s}\n"
        else:
            scad = "%(margin)s%(modifier)s %(name)s(%(args)s);"
        return scad % macros

    def get_scad_args(self):
        return []

class Vector3D_SCAD_Primitive(SCAD_Primitive):
    SCAD_Name = "translate"
    Aliases = {
        'x': 'vector.x',
        'y': 'vector.y',
        'z': 'vector.z',
    }
    Defaults = {
        "vector": {"type": Vector3D, "default": lambda: Vector3D([0.0, 0.0, 0.0])},
    }

    def __init__(self, args=(), **kw):
        if args:
            kw["vector"] = args
        super(Vector3D_SCAD_Primitive, self).__init__(**kw)
    
    def get_scad_args(self):
        return [self.vector]

class OpenSCAD_Camera(SCAD_Primitive):
    Defaults = {
        "v1": {"type": Vector3D, "default": None},
        "v2": {"type": Vector3D, "default": None},
        "distance": {"type": int, "default": None},
    }
    AliasMap = {
        'v1': ('eye', 'e', 'translate', 't'),
        'v2': ('rotation', 'rot', 'r', 'center', 'c'),
        'distance': ('distance',)
    }

class OpenSCAD(SCAD_Primitive):
    Defaults = {
        "_command": {"type": str, "default": None, "cast": False},
        "output": {"type": str, "default": None, "cast": False},
        "deps": {"type": str, "default": None, "cast": False},
        "make": {"type": str, "default": None, "cast": False},
        "define": {"type": dict, "default": lambda: dict()},
        "version": {"type": bool, "default": False},
        "info": {"type": bool, "default": False},
        "camera": {"type": OpenSCAD_Camera, "default": None, "cast": False},
        "imgsize": {"type": Vector2D, "default": lambda: Vector2D((640, 480))},
        "_projection": {"type": str, "default": None, "cast": False},
        "_render": {"type": bool, "default": True},
        "csglimit": {"type": int, "default": None, "cast": False},
        "input": {"type": str, "default": None, "cast": False},
    }

    def render_command_line(self):
        cmd = [self.command]
        # exclusive options
        if self.info:
            cmd.append("--info")
        elif self.version:
            cmd.append("--version")
        else:
            # everything else
            if self.output:
                cmd.extend(("-o", self.output))
            if self.deps:
                cmd.extend(("-d", self.deps))
            if self.make:
                cmd.extend(("-m", self.make))
            if self.define:
                defs = ["'%s=\"%s\"'" % i for i in self.define.items()]
                cmd.extend(("-D", defs))
            if self.camera != None:
                opts = list(self.camera.eye) + list(self.camera.center)
                if self.camera.distance:
                    opts.append(self.camera.distance)
                cmd.append("--camera=%s" % str.join(',', opts))
            if self.imgsize != None:
                cmd.append("--imgsize=%d,%d" % tuple(self.imgsize))
            if self.projection != None:
                cmd.append("--projection=%s" % self.projection)
            if self._render:
                cmd.append("--render")
            else:
                cmd.append("--preview")
            if self.csglimit:
                cmd.append("--csglimit=%s" % self.csglimit)
            cmd.append(self.input)
        return str.join(' ', cmd)

    # preview
    def get_preview(self):
        return not self._render
    def set_preview(self, val):
        self._render = not bool(val)
    preview = property(get_preview, set_preview)

    # projecton
    def get_projection(self):
        return self._projection
    def set_projection(self, val):
        if val == None:
            self._projection = None
        elif "ortho".startswith(val):
            self._projection = "ortho"
        elif "persp".startswith(val):
            self._projection = "persp"
        else:
            raise ValueError, "projection must be either 'ortho' or 'persp', not '%s'" % val
        self["_render"] = False
    projection = property(get_projection, set_projection)

    # command
    def get_command(self):
        if not self._command or not (os.path.exists(self._command) and os.access(self._command, os.X_OK)):
            self._command = self._command or self.open_scad_exe()
            self._command = which(self._command)
        return self._command
    def set_command(self, command):
        self._command = which(command)
    command = property(get_command, set_command)

    @classmethod
    def open_scad_exe(cls):
        if sys.platform.startswith("win"):
            return "openscad.exe"
        else:
            return "openscad"

    def render(self, scene, output=None, background=False, **kw):
        scad = scene.render_scad()
        if output and os.path.splitext(output)[-1].lower() == ".scad":
            with open(output, 'w') as f:
                f.write(scad)
            return
        # need to run OpenSCAD
        kw["output"] = output
        self.push()
        try:
            self.update(kw)
            (fh, fn) = tempfile.mkstemp()
            try:
                os.write(fh, scad)
                os.close(fh)
                self.input = fn
                cli = self.render_command_line()
                if background:
                    cli += "; rm %s &" % fn
                msg = "executing '%s'" % cli
                logger.debug(msg)
                retcode = os.system(cli)
                if retcode != 0:
                    msg = "OpenSCAD returned a non-zero exit code (%s)" % retcode
                    logger.error(msg)
            finally:
                if not background:
                    os.unlink(fn)
        finally:
            self.pop()

class RadialResolution(SCAD_Primitive):
    Defaults = {
        "fn": {"type": float, "default": 0.0},
        "fs": {"type": float, "default": 2.0},
        "fa": {"type": float, "default": 2.0},
    }

    def get_scad_args(self):
        ret = []
        if self.fn != self.Defaults["fn"]["default"]:
            ret.append(("$fn", self.fn))
        else:
            if self.fa != self.Defaults["fa"]["default"]:
                ret.append(("$fa", self.fa))
            if self.fs != self.Defaults["fs"]["default"]:
                ret.append(("$fs", self.fs))
        return ret
    
    def get_fragments(self, length, angle=360):
        if self.fn > 0:
            fragments = max(self.fn, 3)
        else:
            fragments = math.ceil(max(min(angle / self.fa, length / self.fs), 5))
        return int(fragments)

def render(scene, **kw):
    OpenSCAD(**kw).render(scene)
