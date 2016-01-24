from boiler import *

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
