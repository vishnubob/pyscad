from boiler import *

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
        answer = "render(){difference(){cylinder(r=1.0,h=1.0,center=false);cylinder(r=1.0,h=1.0,center=false);}}"
        code_compare(scad, answer)
        p = Pipe(or1=8, or2=5, ir1=7, ir2=2, h=20.0)
        self.assertEquals(p.ir, 7.0)
        self.assertEquals(p.inner.r1, 7.0)
        self.assertEquals(p.inner.r2, 2.0)
        self.assertEquals(p.outer.r1, 8.0)
        self.assertEquals(p.outer.r2, 5.0)
        self.assertEquals(p.height, 20.0)
        scad = p.render_scad()
        answer = "render(){difference(){cylinder(r1=8.0,r2=5.0,h=20.0,center=false);cylinder(r1=7.0,r2=2.0,h=20.0,center=false);}}"
        code_compare(scad, answer)

    def _test_octohedron(self):
        Octohedron()
        octo = Octohedron(h=1, center=True)
        self.assertEquals(octo.h, 1.0)
        scad = octo.render_scad()
        scad = octo.render()
        answer = ""
        code_compare(scad, answer)
