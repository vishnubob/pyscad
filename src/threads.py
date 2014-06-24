# Based on OpenSCAD code by:
#   Dan Kirshner - dan_kirshner@yahoo.com

import math
from . import *

__all__ = [
    "metric_thread",
    "english_thread"
]

def segments(diameter):
    return int(min(50, math.ceil(diameter * 6.0)))

# ----------------------------------------------------------------------------
# internal - true = clearances for internal thread (e.g., a nut).
#            false = clearances for external thread (e.g., a bolt).
#            (Internal threads should be "cut out" from a solid using
#            difference()).
# n_starts - Number of thread starts (e.g., DNA, a "double helix," has
#            n_starts=2).  See wikipedia Screw_thread.

def metric_thread(diameter=8, pitch=1, length=1, internal=False, n_starts=1):
    def thread_turn(i):
        return Translate(z=i * pitch) (metric_thread_turn(diameter, pitch, internal, n_starts))
    #
    n_turns = int(math.floor(length / pitch))
    n_segments = segments(diameter)
    h = pitch * math.cos(math.radians(30))
    threads = [thread_turn(idx) for idx in xrange(-1 * n_starts, n_turns)]
    threads = Union()(*threads)
    cutcube = Translate(z=length / 2.0)( Cube(x=diameter * 1.1, y=diameter*1.1, z=length, center=True) )
    threads = Intersection()(threads, cutcube)
    if internal:
        radius = diameter / 2.0 - h * (5.0 / 8)
    else:
        radius = diameter / 2.0 - h * (5.3 / 8)
    return Union() (threads, Cylinder(r=radius, h=length, fn=n_segments))

def english_thread(diameter=0.25, threads_per_inch=20, length=1, internal=False, n_starts=1):
   # Convert to mm.
   mm_diameter = inch2mm(diameter)
   mm_pitch = inch2mm(1.0 / threads_per_inch)
   mm_length = inch2mm(length)
   return metric_thread(mm_diameter, mm_pitch, mm_length, internal, n_starts)

# ----------------------------------------------------------------------------
def metric_thread_turn(diameter, pitch, internal, n_starts):
    def metric_turn(i):
        return \
            Rotate(z=i * 360.0 * fraction_circle)(
                Translate(z=i * n_starts * pitch * fraction_circle)(
                    thread_polyhedron(diameter / 2.0, pitch, internal, n_starts)))
    n_segments = segments(diameter)
    fraction_circle = 1.0 / n_segments
    return [metric_turn(idx) for idx in range(n_segments)]

# ----------------------------------------------------------------------------
# z (see diagram) as function of current radius.
# (Only good for first half-pitch.)
def z_fct(current_radius, radius, pitch):
   return 0.5 * (current_radius - (radius - 0.875 * pitch * math.cos(math.radians(30)))) / math.cos(math.radians(30))

# ----------------------------------------------------------------------------
def thread_polyhedron(radius, pitch, internal, n_starts):
    n_segments = segments(radius * 2.0)
    fraction_circle = 1.0 / n_segments
    h = pitch * math.cos(math.radians(30))
    outer_r = radius
    if internal:
        # Adds internal relief.
        outer_r += h / 20
    #echo(str("outer_r: ", outer_r))
    # Does NOT do Dmin_truncation - do later with cylinder.
    inner_r = radius - 0.875 * h

    # Make these just slightly bigger (keep in proportion) so polyhedra will overlap.
    x_incr_outer = outer_r * fraction_circle * 2 * math.pi * 1.005
    x_incr_inner = inner_r * fraction_circle * 2 * math.pi * 1.005
    z_incr = n_starts * pitch * fraction_circle * 1.005
    x1_outer = outer_r * fraction_circle * 2 * math.pi
    z0_outer = z_fct(outer_r, radius, pitch)
    z1_outer = z0_outer + z_incr

    # Rule for triangle ordering: look at polyhedron from outside: points must
    # be in clockwise order.
    points = [
        [-x_incr_inner/2, -inner_r, 0],                                    # [0]
        [x_incr_inner/2, -inner_r, z_incr],                    # [1]
        [x_incr_inner/2, -inner_r, pitch + z_incr],            # [2]
        [-x_incr_inner/2, -inner_r, pitch],                                # [3]
        [-x_incr_outer/2, -outer_r, z0_outer],                             # [4]
        [x_incr_outer/2, -outer_r, z0_outer + z_incr],         # [5]
        [x_incr_outer/2, -outer_r, pitch - z0_outer + z_incr], # [6]
        [-x_incr_outer/2, -outer_r, pitch - z0_outer]                      # [7]
    ]
    faces = [
        [0, 3, 4],  # This-side trapezoid, bottom
        [3, 7, 4],  # This-side trapezoid, top
        [1, 5, 2],  # Back-side trapezoid, bottom
        [2, 5, 6],  # Back-side trapezoid, top
        [0, 1, 2],  # Inner rectangle, bottom
        [0, 2, 3],  # Inner rectangle, top
        [4, 6, 5],  # Outer rectangle, bottom
        [4, 7, 6],  # Outer rectangle, top
        [7, 2, 6],  # Upper rectangle, bottom
        [7, 3, 2],  # Upper rectangle, top
        [0, 5, 1],  # Lower rectangle, bottom
        [0, 4, 5]   # Lower rectangle, top
    ]
    return Polyhedron(points=points, faces=faces)
