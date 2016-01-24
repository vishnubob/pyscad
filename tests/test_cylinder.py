from boiler import *

class TestCylinder(unittest.TestCase):
    def test_sphere_creation(self):
        c = Cylinder(h=10, r=20)
        self.assertEquals(c.h, 10)
        self.assertEquals(c.r, 20)
        self.assertEquals(c.d1, 40)

    def test_sphere_scad(self):
        c = Cylinder(h=10, r=20)
        answer = "cylinder(r=20.0, h=10.0, center=false);"
        code_compare(c.render_scad(), answer)
