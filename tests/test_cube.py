from boiler import *

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
        code_compare(scad, answer)
