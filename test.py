import unittest
from scad import *
from scad.base import BaseObject

def check_vector(vector, **answers):
    for (key, value) in answers.items():
        assert getattr(vector, key) == value, "%s != %s" % (getattr(vector, key), value)

class TestBase(unittest.TestCase):
    def setUp(self):
        self.parent_1 = BaseObject("parent_1")
        self.parent_2 = BaseObject("parent_2")
        self.child_1 = BaseObject("child_1")
        self.child_2 = BaseObject("child_2")
        self.child_3 = BaseObject("child_3")
        self.child_4 = BaseObject("child_4")
        self.child_5 = BaseObject("child_5")
        self.child_6 = BaseObject("child_6")
        self.parent_1.children = (self.child_1, self.child_2, self.child_3)
        self.parent_2.children = (self.child_4, self.child_5, self.child_6)

    def test_parent_child(self):
        self.assertIn(self.child_1, self.parent_1.children)
        self.assertIn(self.child_2, self.parent_1.children)
        self.assertNotIn(self.child_4, self.parent_1.children)
        self.assertEquals(self.child_1.parent, self.parent_1)
        self.assertNotEquals(self.child_4.parent, self.parent_1)
        self.parent_2.add_child(self.child_1)
        self.assertNotIn(self.child_1, self.parent_1.children)
        self.assertIn(self.child_1, self.parent_2.children)
        self.assertEquals(self.child_1.parent, self.parent_2)

class TestRadialResolution(unittest.TestCase):
    def test_cylinder_radial_resolution_scad(self):
        c = Cylinder(h=10, r=20, fn=10, fa=1)
        answer = "cylinder(r=20.0, h=10.0, center=false, $fn=10.0);"
        self.assertEquals(c.render_scad().strip(), answer)
        c.fn = 0
        answer = "cylinder(r=20.0, h=10.0, center=false, $fa=1.0);"
        self.assertEquals(c.render_scad().strip(), answer)
        c.fs = 2
        answer = "cylinder(r=20.0, h=10.0, center=false, $fa=1.0, $fs=2.0);"
        self.assertEquals(c.render_scad().strip(), answer)
        c.fs = 0
        c.fa = 0
        answer = "cylinder(r=20.0, h=10.0, center=false);"
        self.assertEquals(c.render_scad().strip(), answer)

class TestCylinder(unittest.TestCase):
    def test_sphere_creation(self):
        c = Cylinder(h=10, r=20)
        self.assertEquals(c.h, 10)
        self.assertEquals(c.r, 20)
        self.assertEquals(c.d1, 40)

    def test_sphere_scad(self):
        c = Cylinder(h=10, r=20)
        answer = "cylinder(r=20.0, h=10.0, center=false);"
        self.assertEquals(c.render_scad().strip(), answer)

class TestCube(unittest.TestCase):
    def test_cube_creation(self):
        answers = {'x': 1, 'y': 1, 'z': 1}
        c = Cube(1)
        check_vector(c.size, **answers)
        self.assertEquals(c.center, False)
        c = Cube(1, center=True)
        check_vector(c.size, **answers)
        self.assertEquals(c.center, True)
        c = Cube([1,2,3])
        answers = {'x': 1, 'y': 2, 'z': 3}
        check_vector(c.size, **answers)
        check_vector(c, **answers)

    def test_cube_scad(self):
        answer = "cube([1.0, 2.0, 3.0], center=false);"
        c = Cube([1,2,3])
        scad = c.render_scad()
        self.assertEquals(scad.strip(), answer)

class TestVector3D(unittest.TestCase):
    def test_vector_creation(self):
        answers = {'x': 1.0, 'y': 2.0, 'z': 3.0}
        v1 = Vector3D(1, 2, 3)
        check_vector(v1, **answers)
        v1 = Vector3D([1, 2, 3])
        check_vector(v1, **answers)

    def test_vector_aliases(self):
        answers = {'X': 1.0, 'Y': 2.0, 'Z': 3.0}
        v1 = Vector3D(1, 2, 3)
        check_vector(v1, **answers)

    def test_vector_subtraction(self):
        answers = {'x': 1.0, 'y': -1.0, 'z': 2.0}
        v1 = Vector3D(2, 1, 5)
        v2 = Vector3D(1, 2, 3)
        check_vector(v1 - v2, **answers)

    def test_vector_dot_product(self):
        # http://www.mathsisfun.com/algebra/vectors-dot-product.html
        v1 = Vector3D(9, 2, 7)
        v2 = Vector3D(4, 8, 10)
        self.assertEquals(v1.dotproduct(v2), 122)

    def test_vector_cross_product(self):
        # http://www.mathsisfun.com/algebra/vectors-cross-product.html
        answers = {'x': -3.0, 'y': 6.0, 'z': -3.0}
        v1 = Vector3D(2, 3, 4)
        v2 = Vector3D(5, 6, 7)
        check_vector(v1.crossproduct(v2), **answers)

    def test_vector_distance(self):
        # http://www.econ.upf.edu/~michael/stanford/maeb4.pdf
        v1 = Vector3D(6.1, 51, 3.0)
        v2 = Vector3D(1.9, 99, 2.9)
        tolerance = 1
        self.assertAlmostEqual(v1.distance(v2), 48.17, places=tolerance)

class TestUnion(unittest.TestCase):
    def test_union_creation(self):
        u = Union()
        u = Union()(Cube())
        u = Union()(Cube(), Cube())

    def test_union_scad(self):
        u = Union()(Cube(), Cube(2))
        answer = 'union() {\n    cube([1.0, 1.0, 1.0], center=false);\n    cube([2.0, 2.0, 2.0], center=false);\n}'
        self.assertEquals(u.render_scad().strip(), answer)

class TestColor(unittest.TestCase):
    def test_color_creation(self):
        answers = {'r': 0.0, 'g': 0.0, 'b': 0.0}
        c = Color()
        check_vector(c, **answers)
        answers = {'r': 3.0, 'g': 6.0, 'b': 3.0}
        c = Color((3,6,3))
        check_vector(c, **answers)
        c = Color(3,6,3)
        check_vector(c, **answers)

    def test_modification(self):
        c = Color(3,6,3)
        c.r += 1
        answers = {'r': 4.0, 'g': 6.0, 'b': 3.0}
        check_vector(c, **answers)
        c.g = 0
        answers = {'r': 4.0, 'g': 0.0, 'b': 3.0}
        check_vector(c, **answers)

    def test_color_selector(self):
        c = Color("green")
        answers = {'r': 0.0, 'g': 128.0, 'b': 0.0}
        check_vector(c, **answers)
        c.g += 1
        answers = {'r': 0.0, 'g': 129.0, 'b': 0.0}
        check_vector(c, **answers)
        self.assertEquals(c.color, "green")
        c.g = 0
        self.assertNotEquals(c.color, "green")

if __name__ == '__main__':
    unittest.main()
