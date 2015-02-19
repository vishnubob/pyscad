import math
from scad import *

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
