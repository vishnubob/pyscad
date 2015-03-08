import math
from . core import *
from . primitives import *

__all__ = [
    "BaseGear",
    "GearProfile",
    "SVG_Gear",
    "Gear",
]

class BaseGear(object):
    Formulas = {
        "diametral_pitch": ["number_of_teeth / float(pitch_diameter)", "math.pi / circular_pitch", "(number_of_teeth + 2.0) * outside_diameter"],
        "pitch_diameter": ["number_of_teeth / diametral_pitch"],
        "outside_diameter": ["(number_of_teeth + 2) / diametral_pitch", "(pitch_diameter + 2) / diamteral_pitch"],
        "number_of_teeth": ["pitch_diametr * diametral_pitch"],
        "addendum": ["1.0 / (pitch_diameter * diametral_pitch)"],
        "dedendum": ["whole_depth - addendum"],
        "tooth_thickness": ["(math.pi / 2.0) / diametral_pitch"],
        "working_depth": ["2 * addendum"],
        "circular_pitch": ["math.pi / diametral_pitch"],
        "base_diameter": ["pitch_diameter * math.cos(pressure_angle)"],
        "clearance": [".157 / diametral_pitch"],
        "pitch_radius": ["pitch_diameter / 2.0"],
        "root_diameter" : ["outside_diameter - (2 * whole_depth)"],
        "whole_depth" : ["2.157 / diametral_pitch"],
        "outside_radius": ["outside_diameter / 2.0"],
        "base_radius": ["base_diameter / 2.0"],
        "pitch_radius": ["pitch_diameter / 2.0"],
        "root_radius": ["root_diameter / 2.0"],
        "module": ["pitch_diameter / number_of_teeth"],
    }

    def __init__(self, **kw):
        super(BaseGear, self).__setattr__("_cached", {})
        super(BaseGear, self).__setattr__("_defined", kw.copy())
        super(BaseGear, self).__setattr__("_unresolved", set())
    
    def __getattr__(self, name):
        if name not in self._defined:
            if name not in self._cached:
                self._cached[name] = self._eval(name)
            return self._cached[name]
        else:
            return self._defined[name]

    def __setattr__(self, name, val):
        self._defined[name] = val
        self._cached.clear()

    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except NameError, err:
            raise KeyError, err

    def _eval(self, name):
        if name not in self.Formulas:
            raise NameError, "Name '%s' is not defined." % name
        if name not in self._unresolved:
            ret = None
            self._unresolved.add(name)
            for formula in self.Formulas[name]:
                try:
                    ret = eval(formula, globals(), self)
                    break
                except NameError:
                    pass
            if ret != None:
                self._unresolved.remove(name)
                return ret
        raise NameError, "Name '%s' requires more information to resolve." % name

class GearProfile(object):
    """
    All of the math/trig in this class is based on the paper:
        "An algorithm to describe the ideal spur gear profile"
        Proceedings of ICME 2008
        2008 WCE, World Congress on Engineering
        2-4 July, 2008, London, U.K.
        O.Reyes, A.Rebolledo, G.Sanchez 
        http://prof.usb.ve/gsanchez/icme2008.pdf
    """

    def __init__(self, gear, resolution=10):
        self.gear = gear
        self.resolution = resolution
        self.theta_re = math.sqrt((self.gear.outside_radius ** 2 - self.gear.base_radius ** 2) / self.gear.base_radius ** 2)
        self.theta_rp = math.sqrt((self.gear.pitch_radius ** 2 - self.gear.base_radius ** 2) / (self.gear.base_radius ** 2))
        self.alpha_re = self.theta_re - math.atan(self.theta_re)
        self.alpha_rp = self.theta_rp - math.atan(self.theta_rp)
        self.epsilon = self.alpha_re - self.alpha_rp
        self.gamma = (math.pi * self.gear.module) / self.gear.pitch_diameter
        self.xi = self.gamma - 2.0 * self.epsilon
        self.sigma = self.xi + 2.0 * self.alpha_re
        self.tau = (2 * math.pi) / self.gear.number_of_teeth

    def teeth_angle(self):
        angle_step = 2.0 * math.pi / self.gear.number_of_teeth
        for tooth_idx in range(self.gear.number_of_teeth):
            yield angle_step * tooth_idx
    
    def draw_gear(self):
        path = []
        for tooth_angle in self.teeth_angle():
            subpath = self.draw_teeth()
            path += self.rotate_path(tooth_angle, subpath)
        return path

    def draw_teeth(self):
        path = []
        path += [[self.gear.root_radius, 0]]
        path += [[self.gear.base_radius, 0]]
        path += list(self.involute_curve(self.resolution))
        path += list(self.tooth_land(self.resolution))
        path += list(self.involute_curve_mirror(self.resolution))
        path += [[self.gear.root_radius * math.cos(self.sigma), self.gear.root_radius * math.sin(self.sigma)]]
        path += self.arc(self.gear.root_radius, self.sigma, self.tau, self.resolution)
        return path

    def rotate(self, angle, pos):
        (x, y) = pos
        _x = x * math.cos(angle) - y * math.sin(angle)
        _y = x * math.sin(angle) + y * math.cos(angle)
        return (_x, _y)
    
    def tooth_land(self, steps):
        return self.arc(self.gear.outside_radius, self.alpha_re, self.alpha_re + self.xi, steps)

    def rotate_path(self, angle, path):
        _path = []
        for point in path:
            _path.append(self.rotate(angle, point))
        return _path

    def involute(self, radius, angle):
        x = radius * (math.cos(angle) + angle * math.sin(angle))
        y = radius * (math.sin(angle) - angle * math.cos(angle))
        return (x, y)

    def involute_curve(self, steps):
        angle_step = self.theta_re / float(steps)
        for idx in range(steps):
            angle = angle_step * idx 
            yield self.involute(self.gear.base_radius, angle)

    def involute_mirror(self, radius, angle):
        x = (radius * math.cos(angle) + radius * angle * math.sin(angle)) * math.cos(self.sigma) - (-radius * math.sin(angle) + radius * angle * math.cos(angle)) * math.sin(self.sigma)
        y = (radius * math.cos(angle) + radius * angle * math.sin(angle)) * math.sin(self.sigma) + (-radius * math.sin(angle) + radius * angle * math.cos(angle)) * math.cos(self.sigma)
        return (x, y)

    def involute_curve_mirror(self, steps):
        angle_step = -self.theta_re / float(steps)
        for idx in range(steps):
            angle = angle_step * idx + self.theta_re
            yield self.involute_mirror(self.gear.base_radius, angle)

    def arc(self, radius, start_angle, end_angle, steps):
        angle_step = (end_angle - start_angle) / float(steps)
        for idx in range(steps):
            angle = idx * angle_step + start_angle
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            yield (x, y)

class SVG_Gear(GearProfile):
    def draw_path(self, points=(), **kw):
        points = str.join(' ', ['L' + str.join(',', map(str, xy)) for xy in points])
        points = 'M' + points[1:] + ' Z'
        style = {"fill": "none", "stroke-width": 1, "stroke": "black"}
        style.update(kw)
        attrs = {"d": points}
        path = self.render_tag("path", attrs, style)
        return [path]

    def render_tag(self, tagname, attrs, style=None, body=None):
        if style:
            style = self.render_style(style)
            attrs.update(style)
        attrs = ['%s="%s"' % kv for kv in attrs.items()]
        attrs = str.join(' ', attrs)
        if body:
            tag = '<%s %s>%s</%s>' % (tagname, attrs, body, tagname)
        else:
            tag = '<%s %s />' % (tagname, attrs)
        return tag

    def render_style(self, style):
        style = ["%s:%s" % kv for kv in style.items()]
        style = str.join(';', style)
        return {"style": style}

    def render(self, filename=None, center=(0, 0)):
        if filename == None:
            filename = "gear.svg"
        svg = []
        gear_path = self.draw_gear()
        gear_path = self.center_points(gear_path, center)
        svg += self.draw_path(points=gear_path)
        svg = str.join('\n', svg)
        svg = '<svg width="100%%" height="100%%" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">\n%s\n</svg>\n' % svg
        f = open(filename, 'w')
        f.write(svg)

    def center_points(self, points, center):
        return [(x + center[0], y + center[1]) for (x, y) in points]

class Gear(SCAD_Object):
    Defaults = {
        "gear": {"type": BaseGear, "default": lambda: BaseGear()},
        "resolution": {"type": RadialResolution, "default": lambda: RadialResolution(), "propagate": True},
        "height": {"type": float, "default": 1},
        "center": {"type": bool, "default": False},
    }

    def scad(self):
        profile = GearProfile(self.gear, resolution=self.resolution.get_fragments(self.height))
        points = profile.draw_gear()
        polygon_profile = Polygon(points=points)
        return LinearExtrude(height=self.height, center=self.center)(polygon_profile)

