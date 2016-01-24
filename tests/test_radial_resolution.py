from boiler import *

class TestRadialResolution(unittest.TestCase):
    def test_cylinder_radial_resolution_scad(self):
        c = Cylinder(h=10, r=20, fn=10, fa=1)
        answer = "cylinder(r=20.0, h=10.0, center=false, $fn=10.0);"
        code_compare(c.render_scad(), answer)
        c.fn = 0
        answer = "cylinder(r=20.0, h=10.0, center=false, $fa=1.0);"
        code_compare(c.render_scad(), answer)
        c.fs = 3
        answer = "cylinder(r=20.0, h=10.0, center=false, $fa=1.0, $fs=3.0);"
        code_compare(c.render_scad(), answer)
        c.fs = 2
        c.fa = 2
        answer = "cylinder(r=20.0, h=10.0, center=false);"
        code_compare(c.render_scad(), answer)
