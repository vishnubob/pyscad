#!/usr/bin/env python

import math
from scad import *

def hexagon(edge=1):
    for angle_idx in xrange(6):
        angle = math.radians(60 * angle_idx)
        x = math.cos(angle) * edge
        y = math.sin(angle) * edge
        yield {'x': x, 'y': y}

def x_clip(x):
    return x > 20

def y_clip(y):
    return y > 20

def circle_clip(r):
    def inner_circle_clip(x, y):
        return ((x - r) ** 2 + (y - r) ** 2) > (r ** 2) 
    return inner_circle_clip

def circle_pack(clip, radius=1):
    def next_xy(x, y):
        while 1:
            if not clip(x, y):
                return (x, y)
            x += (radius * 2)
    (x, y) = next_xy(0, 0)
    yield {'x': x, 'y': y}
    angle = math.radians(60)
    xoff = math.cos(angle) * (radius * 2)
    yoff = math.sin(angle) * (radius * 2)
    offset = 0
    while 1:
        x += radius * 2
        if clip(x, y):
            y += yoff
            if clip(0, y):
                break
            x = 0
            offset += 1
            if (offset % 2):
                x += xoff
            x = next_xy(x, y)
        yield {'x': x, 'y': y}

body = Cylinder(h=2, d=7, fn=20, center=True)
straw = Cylinder(h=10, d=2, fn=20)
straws = [Translate(**coords)(straw) for coords in circle_pack(circle_clip(100), 1)]
#scene = Difference() (body, *straws)
scene = Union() (*straws)
threads = english_thread(1.0625, 11.5, 1, internal=True)
scene = Difference() (Cylinder(d=inch2mm(1.2), h=inch2mm(.9)), threads)
scene.render("ljet.scad")
