import math
from scad import *

class Thread(SCAD_Object):
    major_diameter = 0
    minor_diameter = 0
    pitch_diameter = 0
    pitch = 0
    length = 0
    thread_angle = math.radians(60)
    resolution = 100

    @property
    def crest_length(self):
        return self.pitch / 8.0

    @property
    def root_length(self):
        return self.pitch / 4.0

    @property
    def slope_length(self):
        return (self.pitch - self.crest_length + self.root_length) / 2.0

    @property
    def pitch_radius(self):
        return self.pitch_diameter / 2.0

    @property
    def major_radius(self):
        return self.major_diameter / 2.0

    @property
    def minor_radius(self):
        return self.minor_diameter / 2.0
    
    def runs(self):
        self.helix(0, self.minor_radius, self.length)
        self.helix(self.root_length, self.minor_radius, self.length)
        self.helix(self.root_length + self.slope_length, self.pitch_radius, self.length)
        self.helix(self.root_length + self.slope_length + self.crest_length, self.pitch_radius, self.length)

    def helix(self, radius, length):
        rstep = (math.pi * 2) / resolution
        zstep = self.pitch / resolution
        for step in range(resolution):
            angle = rstep * step
            zoffset = zstep * step 
            res = (math.cos(angle), math.sin(angle), zoffset)
            yield res
    
    def profile(self, offset=(0, 0, 0)):
        (xo, yo, zo) = offset
        x_top = self.cos(self.thread_angle) * (self.major_radius - self.minor_radius)
        y_top = self.sin(self.thread_angle) * (self.major_radius - self.minor_radius)
        profile = [
            # left point of trough
            (self.pitch + xo, self.pitch_radius + yo, zo),
            # right point of trough
            (self.pitch * 0.25 + xo, self.pitch_radius + yo, zo),
            # left point of peak
            (x_top + self.pitch * 0.25 + xo, y_top + self.pitch_radius + yo, zo),
            # right point of peak
            (x_top + self.pitch * 0.375 + xo, y_top + self.pitch_radius + yo, zo),
            # left point of trough
            (self.pitch * 0.875 + xo, self.pitch_radius + yo, zo),
        ]
        return profile

    def profiles(self):
        rstep = (math.pi * 2) / resolution
        zstep = self.pitch / resolution
        for step in range(resolution):
            angle = rstep * step
            zoffset = zstep * step 
