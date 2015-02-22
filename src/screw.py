import math
from scad import *

class Helix(object):
    def __init__(self, radius, pitch, height, resolution=20, offset=(0, 0, 0)):
        self.radius = radius
        self.pitch = pitch
        self.height = height
        self.resolution = resolution
        self.offset = offset

    def __len__(self):
        return int(self.height / self.pitch * self.resolution)

    def __iter__(self):
        angle_step = (2 * math.pi) / self.resolution
        pitch_step = self.pitch / (2 * math.pi)
        (xo, yo, zo) = self.offset
        for idx in range(len(self)):
            angle = angle_step * idx
            x = self.radius * math.cos(angle) + xo
            y = self.radius * math.sin(angle) + yo
            z = pitch_step * angle + zo
            yield (x, y, z)

class HelixStitcher(SCAD_Object):
    def __init__(self, helix_list):
        self.helix_list = helix_list

    def scad(self):
        points = []
        for helix in self.helix_list:
            points.extend(list(helix))
        faces = []
        helix = self.helix_list[0]
        point_count = len(helix)
        resolution = helix.resolution
        for hidx in range(len(self.helix_list)):
            offset = point_count * hidx
            next_helix = (offset + point_count) % len(points)
            previous_helix = (offset - point_count) % len(points)
            for idx in range(point_count):
                if hidx < (len(self.helix_list) - 1):
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
        return Polyhedron(points=points, faces=faces)

helix1 = Helix(10, 8, 40, 10)
helix2 = Helix(15, 8, 40, 10, offset=(0, 0, 2))
helix3 = Helix(13, 8, 40, 10, offset=(0, 0, 4))
hlist = [helix1, helix2, helix3]
hs = HelixStitcher(hlist)
hs.render("helix.scad")

class Thread(SCAD_Object):
    major_diameter = 0
    pitch = 0
    length = 0
    thread_angle = math.radians(60)
    resolution = 100

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

    def thread_profile(self, offset=(0, 0, 0)):
        z = 0
        pt1 = (0, self.minor_diameter, z)
        z += self.valley_offset
        pt2 = (0, self.minor_diameter, z)
        z += self.slope_offset
        pt3 = (0, self.major_diameter, z)
        z += self.crest_offset
        pt4 = (0, self.major_diameter, z)
        z += self.slope_offset
        pt5 = (0, self.minor_diameter, z)
        points = [pt1, pt2, pt3, pt4, pt5]
        points = [(x + offset[0], y + offset[1], z + offset[2]) for (x, y, z) in points]
        return points

    def scad(self):
        points = self.thread_profile()
        points += self.thread_profile((5, 0, 0))
        faces = [
            [0, 1, 5], [5, 6, 1],
            [1, 2, 6], [6, 7, 2],
            [2, 3, 7], [7, 8, 3],
            [3, 4, 8], [8, 9, 4],
        ]
        p = Polyhedron(points=points, faces=faces)
        return p

t = Thread(pitch=2, major_diameter=2)
t.render("threads.scad")
