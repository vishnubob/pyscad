from boiler import *

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
