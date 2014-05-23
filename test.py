import unittest
from scad import *

class TestVector(unittest.TestCase):
    def check_vector(self, vector, **answers):
        for (key, value) in answers.items():
            self.assertEquals(getattr(vector, key), value)

    def test_vector_creation(self):
        answers = {'x': 1, 'y': 2, 'z': 3}
        v1 = Vector(1, 2, 3)
        self.check_vector(v1, **answers)
        v1 = Vector([1, 2, 3])
        self.check_vector(v1, **answers)

    def test_vector_aliases(self):
        answers = {'X': 1, 'Y': 2, 'Z': 3}
        v1 = Vector(1, 2, 3)
        self.check_vector(v1, **answers)

    def test_vector_subtraction(self):
        answers = {'x': 1, 'y': -1, 'z': 2}
        v1 = Vector(2, 1, 5)
        v2 = Vector(1, 2, 3)
        self.check_vector(v1 - v2, **answers)

    def test_vector_dot_product(self):
        v1 = Vector(9, 2, 7)
        v2 = Vector(4, 8, 10)
        self.assertEquals(v1.dotproduct(v2), 122)

    def test_vector_cross_product(self):
        answers = {'x': -3, 'y': 6, 'z': -3}
        v1 = Vector(2, 3, 4)
        v2 = Vector(5, 6, 7)
        self.check_vector(v1.crossproduct(v2), **answers)

if __name__ == '__main__':
    unittest.main()


