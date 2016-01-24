from boiler import *

class TestDrill(unittest.TestCase):
    def test_imperial_table(self):
        ds = drill_sizes.imperial.lookup("1/2 inch", False)
        self.assertEqual(ds, unit("1/2 inch"))
        try:
            ds = drill_sizes.imperial.lookup("0.1765 inch", False)
            assert 0, "Should of thrown an error"
        except:
            pass
        ds = drill_sizes.imperial.lookup("0.1765 inch")
        self.assertEqual(ds, unit(".177 inch"))
