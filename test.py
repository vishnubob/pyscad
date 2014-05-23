import unittest
from scad import *

def check_vector(vector, **answers):
    for (key, value) in answers.items():
        assert getattr(vector, key) == value

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
        answer = "cube([1, 2, 3], center=false)"
        c = Cube([1,2,3])
        scad = c.render_scad()
        self.assertEquals(scad.strip(), answer)

class TestVector3D(unittest.TestCase):
    def test_vector_creation(self):
        answers = {'x': 1, 'y': 2, 'z': 3}
        v1 = Vector3D(1, 2, 3)
        check_vector(v1, **answers)
        v1 = Vector3D([1, 2, 3])
        check_vector(v1, **answers)

    def test_vector_aliases(self):
        answers = {'X': 1, 'Y': 2, 'Z': 3}
        v1 = Vector3D(1, 2, 3)
        check_vector(v1, **answers)

    def test_vector_subtraction(self):
        answers = {'x': 1, 'y': -1, 'z': 2}
        v1 = Vector3D(2, 1, 5)
        v2 = Vector3D(1, 2, 3)
        check_vector(v1 - v2, **answers)

    def test_vector_dot_product(self):
        v1 = Vector3D(9, 2, 7)
        v2 = Vector3D(4, 8, 10)
        self.assertEquals(v1.dotproduct(v2), 122)

    def test_vector_cross_product(self):
        answers = {'x': -3, 'y': 6, 'z': -3}
        v1 = Vector3D(2, 3, 4)
        v2 = Vector3D(5, 6, 7)
        check_vector(v1.crossproduct(v2), **answers)

if __name__ == '__main__':
    unittest.main()
