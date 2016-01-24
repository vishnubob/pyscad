from boiler import *

class TestUnion(unittest.TestCase):
    def test_union_creation(self):
        u = Union()
        u = Union()(Cube())
        u = Union()(Cube(), Cube())

    def test_union_scad(self):
        u = Union()(Cube(), Cube(2))
        answer = 'union() {\n    cube([1.0, 1.0, 1.0], center=false);\n    cube([2.0, 2.0, 2.0], center=false);\n}'
        code_compare(u.render_scad(), answer)
