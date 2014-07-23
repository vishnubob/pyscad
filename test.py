import unittest
import tempfile
import shutil
from scad import *
from scad.base import BaseObject

def check_vector(vector, **answers):
    for (key, value) in answers.items():
        assert getattr(vector, key) == value, "%s != %s" % (getattr(vector, key), value)

def code_compare(result, expected):
    def wash_str(_str):
        for ch in _str:
            if ch in [' ', '\t', '\n']:
                continue
            yield ch
    expected = str.join('', wash_str(expected))
    result = str.join('', wash_str(result))
    assert expected == result, "Generated code does not match expected result: \nExpected: %s\n  Result: %s\n" % (expected, result)

def open_scad_exe():
    scad = OpenSCAD()
    return scad.command

class TestBase(unittest.TestCase):
    def test_children(self):
        self.parent_1 = BaseObject(name="parent_1")
        self.parent_2 = BaseObject(name="parent_2")
        self.child_1 = BaseObject(name="child_1")
        self.child_2 = BaseObject(name="child_2")
        self.parent_1.children = (self.child_1)
        self.parent_2.children = (self.child_1, self.child_2)
        self.assertIn(self.child_1, self.parent_1.children)
        self.assertNotIn(self.child_2, self.parent_1.children)
        self.assertIn(self.child_1, self.parent_2.children)
        self.assertIn(self.child_2, self.parent_2.children)

class TestRadialResolution(unittest.TestCase):
    def test_cylinder_radial_resolution_scad(self):
        c = Cylinder(h=10, r=20, fn=10, fa=1)
        answer = "cylinder(r=20.0, h=10.0, center=false, $fn=10.0);"
        code_compare(c.render_scad(), answer)
        c.fn = 0
        answer = "cylinder(r=20.0, h=10.0, center=false, $fa=1.0);"
        code_compare(c.render_scad(), answer)
        c.fs = 3
        answer = "cylinder(r=20.0, h=10.0, center=false, $fa=1.0, $fs=3.0);"
        code_compare(c.render_scad(), answer)
        c.fs = 2
        c.fa = 2
        answer = "cylinder(r=20.0, h=10.0, center=false);"
        code_compare(c.render_scad(), answer)

class TestCylinder(unittest.TestCase):
    def test_sphere_creation(self):
        c = Cylinder(h=10, r=20)
        self.assertEquals(c.h, 10)
        self.assertEquals(c.r, 20)
        self.assertEquals(c.d1, 40)

    def test_sphere_scad(self):
        c = Cylinder(h=10, r=20)
        answer = "cylinder(r=20.0, h=10.0, center=false);"
        code_compare(c.render_scad(), answer)

class TestPolyhedron(unittest.TestCase):
    def test_polyhedron_creation(self):
        p = Polyhedron()

    def test_sphere_scad(self):
        p = Polyhedron()
        p.points = [[1,1,1], [2,2,2], [3,3,3]]
        p.faces = [[0, 1, 2]]
        answer = "polyhedron(points=[[1.0, 1.0, 1.0], [2.0, 2.0, 2.0], [3.0, 3.0, 3.0]], faces=[[0.0, 1.0, 2.0]]);"
        code_compare(p.render_scad(), answer)

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

class TestUnion(unittest.TestCase):
    def test_union_creation(self):
        u = Union()
        u = Union()(Cube())
        u = Union()(Cube(), Cube())

    def test_union_scad(self):
        u = Union()(Cube(), Cube(2))
        answer = 'union() {\n    cube([1.0, 1.0, 1.0], center=false);\n    cube([2.0, 2.0, 2.0], center=false);\n}'
        code_compare(u.render_scad(), answer)

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

class TestGeometry(unittest.TestCase):
    def _test_pieslice(self):
        PieSlice()
        pie = PieSlice(height=4, r=4, center=True)
        self.assertEquals(pie.h, 4.0)
        scad = pie.render_scad()
        answer = ""
        code_compare(scad, answer)

    def test_arc(self):
        Arc()
        arc = Arc(height=4, iR=4, oR=8, center=True)
        self.assertEquals(arc.h, 4.0)
        #arc.render()
        #scad = pie.render_scad()
        #answer = ""
        #self.assertEquals(scad, answer)

    def test_tetrahedron(self):
        Tetrahedron()
        tet = Tetrahedron(h=1, center=True)
        self.assertEquals(tet.h, 1.0)
        scad = tet.render_scad()
        answer = "polyhedron(points=[[-0.6123724356957945, -0.35355339059327373, -0.5], [0.6123724356957945, -0.35355339059327373, -0.5], [0.0, 0.7071067811865475, -0.5], [0.0, 0.0, 0.5]], faces=[[0.0, 1.0, 2.0], [1.0, 0.0, 3.0], [0.0, 2.0, 3.0], [2.0, 1.0, 3.0]]);"
        code_compare(scad, answer)

    def test_pipe(self):
        Pipe()
        p = Pipe()
        scad = p.render_scad()
        answer = "difference(){cylinder(r=1.0,h=1.0,center=false);cylinder(r=1.0,h=1.0,center=false);}"
        code_compare(scad, answer)
        p = Pipe(or1=8, or2=5, ir1=7, ir2=2, h=20.0)
        self.assertEquals(p.ir, 7.0)
        self.assertEquals(p.inner.r1, 7.0)
        self.assertEquals(p.inner.r2, 2.0)
        self.assertEquals(p.outer.r1, 8.0)
        self.assertEquals(p.outer.r2, 5.0)
        self.assertEquals(p.height, 20.0)
        scad = p.render_scad()
        answer = 'difference() {\n    cylinder(r1=8.0, r2=5.0, h=20.0, center=false);\n    cylinder(r1=7.0, r2=2.0, h=20.0, center=false);\n}'
        code_compare(scad, answer)

    def _test_octohedron(self):
        Octohedron()
        octo = Octohedron(h=1, center=True)
        self.assertEquals(octo.h, 1.0)
        scad = octo.render_scad()
        scad = octo.render()
        answer = ""
        code_compare(scad, answer)

class TestOpenSCAD(unittest.TestCase):
    def setUp(self):
        self._tdir = tempfile.mkdtemp()
    def tearDown(self):
        shutil.rmtree(self._tdir)

    def tdir(self, path):
        return os.path.join(self._tdir, path)

    def test_openscad_creation(self):
        scad = OpenSCAD()

    @unittest.skipUnless(open_scad_exe(), "No available OpenSCAD Binary")
    def test_openscad_render(self):
        scad = OpenSCAD()
        for ext in ("png", "dxf", "stl", "scad"):
            if ext == "dxf":
                scene = Projection(cut=True)( Translate([0, 0, 1])( (Cube((1, 2, 3)), Sphere(r=2)) ))
            else:
                scene = Union()(Cube((1, 2, 3)), Sphere(r=2))
            fn = "render." + ext
            self.assertFalse(os.path.exists(self.tdir(fn)))
            scad.render(scene, self.tdir(fn))
            self.assertTrue(os.path.exists(self.tdir(fn)))
            self.assertGreater(os.path.getsize(self.tdir("render.png")), 0)

if __name__ == '__main__':
    unittest.main()
