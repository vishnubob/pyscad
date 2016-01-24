from scad import *

ff = "tarpit/fonts/Times_New_Roman_Bold.ttf"
size = 60
f = Glyph(fontfile=ff, width=size, depth=20)
j = Translate(x=0)(f.get_char("J"))
w = Translate(x=size * .4)(f.get_char("W"))
m = Translate(x=size * 1.3)(f.get_char("M"))
scene = Union()(j,w,m)
scene.render("jwm.scad")
scene.render("jwm.stl")
