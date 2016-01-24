from boiler import *

class TestRotate(unittest.TestCase):
    def test_rotate(self):
        cyl = Cylinder(h=10, r=20)
        c = Rotate(x=20, y=30, z=40)(cyl)
        answer = "rotate(a=[20.0,30.0,40.0]){cylinder(r=20.0,h=10.0,center=false);}"
        code_compare(c.render_scad(), answer)
        c = Rotate(20)(cyl)
        answer = "rotate(a=20.0){cylinder(r=20.0,h=10.0,center=false);}"
        code_compare(c.render_scad(), answer)
        c = Rotate(20, [0, 0, 1])(cyl)
        answer = "rotate(a=20.0,v=[0.0,0.0,1.0]){cylinder(r=20.0,h=10.0,center=false);}"
        code_compare(c.render_scad(), answer)
