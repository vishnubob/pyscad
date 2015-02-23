import math
from scad import *

class Helix(object):
    def __init__(self, radius, pitch, height, resolution=20, offset=(0, 0, 0), min_limit=(None, None, None), max_limit=(None, None, None)):
        self.radius = radius
        self.pitch = pitch
        self.height = height
        self.resolution = resolution
        self.offset = offset
        self.min_limit = min_limit
        self.max_limit = max_limit

    def __len__(self):
        return int(self.height / self.pitch * self.resolution)

    def apply_limits(self, xyz):
        ret = []
        for (val, _min, _max) in zip(xyz, self.min_limit, self.max_limit):
            val = _min if (_min != None and _min > val) else val
            val = _max if (_max != None and _max < val) else val
            ret.append(val)
        return tuple(ret)

    def __iter__(self):
        angle_step = (2 * math.pi) / self.resolution
        pitch_step = self.pitch / (2 * math.pi)
        (xo, yo, zo) = self.offset
        for idx in range(len(self)):
            angle = angle_step * idx
            x = self.radius * math.cos(angle) + xo
            y = self.radius * math.sin(angle) + yo
            z = pitch_step * angle + zo
            yield self.apply_limits((x, y, z))

class ThreadProfile(object):
    def __init__(self, major_diameter, pitch):
        self.major_diameter = major_diameter
        self.pitch = pitch

    @property
    def height(self):
        return math.cos(math.radians(30)) * self.pitch

    @property
    def minor_diameter(self):
        return self.major_diameter - (1.25 * self.height)

    @property
    def pitch_diameter(self):
        return self.major_diameter - (0.75 * self.height)

    @property
    def crest_offset(self):
        return self.pitch / 8.0

    @property
    def valley_offset(self):
        return self.pitch / 4.0

    @property
    def slope_offset(self):
        return self.pitch * (3 / 16.0)

    def __iter__(self):
        z = 0
        pt1 = (self.minor_diameter, z)
        z += self.valley_offset
        pt2 = (self.minor_diameter, z)
        z += self.slope_offset
        pt3 = (self.major_diameter, z)
        z += self.crest_offset
        pt4 = (self.major_diameter, z)
        points = [pt1, pt2, pt3, pt4]
        return iter(points)

class Screw(SCAD_Object):
    major_diameter = 6.35
    pitch = 1.27
    length = 20

    def build_screw(self, helix_list):
        points = []
        for helix in helix_list:
            points.extend(list(helix))
        faces = []
        helix = helix_list[0]
        point_count = len(helix)
        resolution = helix.resolution
        for hidx in range(len(helix_list)):
            offset = point_count * hidx
            next_helix = (offset + point_count) % len(points)
            previous_helix = (offset - point_count) % len(points)
            for idx in range(point_count):
                if hidx < (len(helix_list) - 1):
                    if idx < (point_count - 1):
                        face = (offset + idx, offset + idx + 1, next_helix + idx)
                        faces.append(face)
                else:
                    if (idx + resolution) < point_count:
                        face = (offset + idx, offset + idx + 1, next_helix + idx + resolution)
                        faces.append(face)
                if hidx == 0:
                    if (idx - resolution) > 0:
                        face = (offset + idx, offset + idx - 1, previous_helix + idx - resolution)
                        faces.append(face)
                elif idx > 0:
                    face = (offset + idx, offset + idx - 1, previous_helix + idx)
                    faces.append(face)
        points.append((0, 0, self.length))
        endpoint = len(points) - 1
        for idx in range(resolution):
            offset = len(helix_list) * point_count - resolution + idx
            face = (offset - 1, offset, endpoint)
            faces.append(face)
        return Polyhedron(points=points, faces=faces)

    def scad(self):
        profile = ThreadProfile(self.major_diameter, self.pitch)
        min_limit = (None, None, 0)
        max_limit = (None, None, self.length)
        length = self.length + self.pitch * 2
        helix_list = []
        for (radius, z_offset) in profile:
            offset = (0, 0, z_offset - self.pitch)
            helix = Helix(radius, self.pitch, length, offset=offset, min_limit=min_limit, max_limit=max_limit)
            helix_list.append(helix)
        return self.build_screw(helix_list)

s = Screw()
s.render("helix.scad")
