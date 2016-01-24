from scad import *

ff = "fonts/Vera.ttf"
ff = "fonts/Times_New_Roman.ttf"
g = Glyph(fontfile=ff, width=20, depth=10)
t = Text(text="Hello World!", glyph=g)
t.render("c.scad")
