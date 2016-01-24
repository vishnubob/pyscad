from boiler import *

class TestNameResolution(unittest.TestCase):
    def test_name_attribute(self):
        c1 = Cube(name="bob", x=1, y=1, z=1)
        self.assertEquals(c1.name, "bob")

    def test_automatic_name(self):
        c1 = Cube(x=1, y=1, z=1)
        c2 = Cube(x=1, y=1, z=1)
        (c1_name, c1_index) = c1.name.split('_')
        (c2_name, c2_index) = c2.name.split('_')
        self.assertEquals(c1_name, "Cube")
        self.assertEquals(c2_name, "Cube")
        self.assertEquals(int(c1_index) + 1, int(c2_index))

    def test_name_resolution(self):
        c1 = Cube(name="bob", x=1, y=1, z=1)
        c2 = Cube(name="ann", x=-1, y=-1, z=-1)
        u = Union()(c1, c2)
        self.assertEquals(c1, u.bob)
        self.assertEquals(c2, u.ann)

    def test_multilevel_name_resolution(self):
        c1 = Cube(name="bob", x=1, y=1, z=1)
        tr = Translate(name="bob_tr", x=1)(c1)
        u = Union()(c1, tr)
        self.assertEquals(c1, u.bob)
        self.assertEquals(c1, u.bob_tr.bob)
