from boiler import *

class TestColor(unittest.TestCase):
    def test_color_creation(self):
        answers = {'r': 0.0, 'g': 0.0, 'b': 0.0}
        c = Color()
        check_vector(c, **answers)
        answers = {'r': 3.0, 'g': 6.0, 'b': 3.0}
        c = Color([3,6,3])
        check_vector(c, **answers)
        c = Color([3,6,3])
        check_vector(c, **answers)

    def test_modification(self):
        c = Color([3,6,3])
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
        self.assertEquals(c.colorname, "green")
        c.g = 0
        self.assertNotEquals(c.colorname, "green")


