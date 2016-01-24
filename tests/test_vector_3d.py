from boiler import *

class TestVector3D(unittest.TestCase):
    def test_vector_creation(self):
        answers = {'x': 1.0, 'y': 2.0, 'z': 3.0}
        v1 = Vector3D([1, 2, 3])
        check_vector(v1, **answers)
        v1 = Vector3D([1, 2, 3])
        check_vector(v1, **answers)

    def test_vector_aliases(self):
        answers = {'X': 1.0, 'Y': 2.0, 'Z': 3.0}
        v1 = Vector3D([1, 2, 3])
        check_vector(v1, **answers)

    def test_vector_subtraction(self):
        answers = {'x': 1.0, 'y': -1.0, 'z': 2.0}
        v1 = Vector3D([2, 1, 5])
        v2 = Vector3D([1, 2, 3])
        check_vector(v1 - v2, **answers)

    def test_vector_dot_product(self):
        # http://www.mathsisfun.com/algebra/vectors-dot-product.html
        v1 = Vector3D([9, 2, 7])
        v2 = Vector3D([4, 8, 10])
        self.assertEquals(v1.dotproduct(v2), 122)

    def test_vector_cross_product(self):
        # http://www.mathsisfun.com/algebra/vectors-cross-product.html
        answers = {'x': -3.0, 'y': 6.0, 'z': -3.0}
        v1 = Vector3D([2, 3, 4])
        v2 = Vector3D([5, 6, 7])
        check_vector(v1.crossproduct(v2), **answers)

    def test_vector_distance(self):
        # http://www.econ.upf.edu/~michael/stanford/maeb4.pdf
        v1 = Vector3D([6.1, 51, 3.0])
        v2 = Vector3D([1.9, 99, 2.9])
        tolerance = 1
        self.assertAlmostEqual(v1.distance(v2), 48.17, places=tolerance)
