import math
from scad import *

class Helix(object):
    def __init__(self, radius, pitch, height, resolution=20, offset=(0, 0, 0), phase=0, min_limit=(None, None, None), max_limit=(None, None, None)):
        self.radius = radius
        self.pitch = pitch
        self.height = height
        self.resolution = resolution
        self.offset = offset
        self.phase = phase
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

    def step_offset(self, other):
        angle_step = (2 * math.pi) / self.resolution
        angle = self.phase - other.phase
        return int(angle / angle_step)
    
    def debug(self):
        c = Cube(x=.1, y=.1, z=.1, center=True)
        objs = []
        for coord in self:
            _c = Translate(coord)(c)
            objs.append(_c)
        objs = Union()(*objs)
        return objs

    def __iter__(self):
        angle_step = (2 * math.pi) / self.resolution
        pitch_step = self.pitch / (2 * math.pi)
        (xo, yo, zo) = self.offset
        for idx in range(len(self)):
            angle = angle_step * idx + self.phase
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

class DistanceSelect(list):
    def euclidean_distance(self, pt1, pt2):
        return math.sqrt(sum([(val1 - val2) ** 2 for (val1, val2) in zip(pt1, pt2)]))

    def nearest(self, pt1):
        def distance_sort(this, that):
            return cmp(this[1], that[1])
        distance = [(idx, self.euclidean_distance(pt1, pt2)) for (idx, pt2) in enumerate(self)]
        distance.sort(distance_sort)
        return distance[0]

class Screw(SCAD_Object):
    major_diameter = 6.35
    #pitch = 1.27
    pitch = 5
    length = pitch

    def prepare_helix_list(self, hlist):
        points = []
        helix_list = []
        for helix in hlist:
            _points = list(helix)
            helix_map = {}
            helix_map["helix"] = helix
            helix_map["select"] = DistanceSelect(_points)
            helix_map["points"] = _points
            helix_map["offset"] = len(points)
            points.extend(_points)
            helix_list.append(helix_map)
        return (points, helix_list)

    def build_screw(self, helix_list):
        (points, helix_list) = self.prepare_helix_list(helix_list)
        faces = []
        for (hidx, helix) in enumerate(helix_list):
            next_helix = helix_list[(hidx + 1) % len(helix_list)]
            prev_helix = helix_list[(hidx - 1) % len(helix_list)]
            offset = helix["offset"]
            next_offset = next_helix["offset"]
            prev_offset = prev_helix["offset"]
            for (idx, pt) in enumerate(helix["points"][:-1]):
                (next_idx, distance) = next_helix["select"].nearest(pt)
                face = (idx + offset, idx + offset + 1, next_idx + next_offset)
                faces.append(face)
        return Polyhedron(points=points, faces=faces)

    def _build_screw(self, helix_list):
        points = []
        helix_offset_map = {}
        for helix in helix_list:
            helix_offset_map[helix] = len(points)
            points.extend(list(helix))
        faces = []
        helix = helix_list[0]
        point_count = len(helix)
        resolution = helix.resolution
        for (hidx, helix) in enumerate(helix_list):
            next_helix = helix_list[(hidx + 1) % len(helix_list)]
            previous_helix = helix_list[(hidx - 1) % len(helix_list)]
            offset = helix_offset_map[helix]
            next_helix_offset = helix.step_offset(next_helix) + helix_offset_map[next_helix]
            previous_helix_offset = helix.step_offset(previous_helix) + helix_offset_map[previous_helix] - 1
            for idx in range(point_count):
                if helix != helix_list[0]:
                    continue
                if helix != helix_list[-1]:
                    if idx < (point_count - 1) and (idx + next_helix_offset) < helix_offset_map[next_helix] + point_count:
                        face = (idx + offset, idx + offset + 1, idx + next_helix_offset)
                        faces.append(face)
                else:
                    if (idx + next_helix_offset + resolution) < point_count:
                        face = (idx + offset, idx + offset + 1, idx + next_helix_offset + resolution)
                        #faces.append(face)
                if helix == helix_list[0]:
                    if (idx + previous_helix_offset - resolution) > 0:
                        face = (idx + offset, idx + offset - 1, idx + previous_helix_offset - resolution + 8)
                        faces.append(face)
                elif idx > 0:
                    if (idx + previous_helix_offset >= helix_offset_map[previous_helix]):
                        face = (idx + offset, idx + offset - 1, idx + previous_helix_offset)
                        #faces.append(face)
        """
        points.append((0, 0, self.length))
        endpoint = len(points) - 1
        for idx in range(resolution):
            offset = len(helix_list) * point_count - resolution + idx
            face = (offset - 1, offset, endpoint)
            faces.append(face)
        """
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
    
    def debug(self):
        colors = ["red", "green", "blue", "cyan"]
        profile = ThreadProfile(self.major_diameter, self.pitch)
        helix_list = []
        for (radius, z_offset) in profile:
            phase = (-z_offset / self.pitch) * (2 * math.pi)
            offset = (0, 0, z_offset)
            helix = Helix(radius, self.pitch, self.length, phase=phase, offset=offset)
            helix_list.append(helix)
        helix_list = helix_list[:2]
        screw = self.build_screw(helix_list)
        debug = [Color(colorname=color)(helix.debug()) for (color, helix) in zip(colors, helix_list)]
        debug.append(screw)
        debug = Union()(*debug)
        return debug

s = Screw()
s = s.debug()
s.render("helix.scad")
