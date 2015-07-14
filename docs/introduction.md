# PySCAD

PySCAD is a python library that wraps the OpenSCAD language.  It simplifies the task of building complex geometires by combining the expressive power of OpenSCAD with the versatility of python.  The library wraps nearly every feature of the OpenSCAD language.  It also includes geometric definitions not included with OpenSCAD (such as pipes, gears and threads).  Not only is it simple to write out SCAD files from python, PySCAD can also execute OpenSCAD making it easy to automate rendering tasks such as generating .STL files.  Here is a usage example:

<!-- %EXAMPLE% rods --> 
```
from scad import *
import math

rod = Cylinder(diameter=2, height=20, fn=20, center=True)
rod = Rotate(x=90)(rod)
rods = []
for index in range(30):
    _rod = Rotate(z=(360.0 / 30) * index)(rod)
    _rod = Translate(z=index * 1)(_rod)
    rods.append(_rod)
rods = Union()(*rods)
rods.render("rods.scad")
rods.render("rods.png")
rods.render("rods.stl")
```

