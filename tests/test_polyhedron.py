from boiler import *

class TestPolyhedron(unittest.TestCase):
    def test_polyhedron_creation(self):
        p = Polyhedron()

    def test_sphere_scad(self):
        p = Polyhedron()
        p.points = [[1,1,1], [2,2,2], [3,3,3]]
        p.faces = [[0, 1, 2]]
        answer = "polyhedron(points=[[1.0, 1.0, 1.0], [2.0, 2.0, 2.0], [3.0, 3.0, 3.0]], faces=[[0.0, 1.0, 2.0]]);"
        code_compare(p.render_scad(), answer)
