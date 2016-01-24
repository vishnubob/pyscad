from boiler import *

class TestNameResolution(unittest.TestCase):
    def test_name_resolution(self):
        c1 = Cube(name="bob", x=1, y=1, z=1)
        c2 = Cube(name="ann", x=-1, y=-1, z=-1)
        u = Union()(c1, c2)
        self.assertEquals(c1, u.bob)
        self.assertEquals(c2, u.ann)
