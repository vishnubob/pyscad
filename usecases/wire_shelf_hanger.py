#!/usr/bin/env python
from scad import *

horz_rod_dia = 6.18
vert_rod_dia = 3.0
inner_width = 22.18 - 0.1
inner_height = 13.15 - 1.2
offset = 1
#
m3_dia = 3 + 0.5
m3_head_height = 1.9
m3_head_dia = 5.5 + 0.5
m3_nut_dia = 7
m3_nut_height = 3

rod_length = 40

horz_rod = Cylinder(dia=horz_rod_dia, height=rod_length, center=True, fn=40)
vert_rod = Cylinder(dia=vert_rod_dia, height=rod_length, center=True, fn=40)
front_plate = Cube(x=inner_width + vert_rod_dia, z=inner_height + horz_rod_dia / 2, y=horz_rod_dia * .6, center=True)
back_plate = Cube(x=inner_width + vert_rod_dia, z=inner_height + horz_rod_dia / 2 + 2, y=horz_rod_dia * .6, center=True)

front_plate_wings = Cube(x=inner_width + vert_rod_dia * 2, z=inner_height + horz_rod_dia / 2, y=front_plate.depth - vert_rod_dia / 2.05, center=True)
back_plate_wings = Cube(x=inner_width + vert_rod_dia, z=inner_height + horz_rod_dia / 2 * 2, y=back_plate.depth - horz_rod_dia / 3, center=True)

def make_front_hanger():
    yoff_front = front_plate().depth / -2 - vert_rod_dia / 2
    return Difference()(
        Union()(
            Translate(y=yoff_front)( front_plate ),
            Translate(y=yoff_front - front_plate_wings.depth / 3)( front_plate_wings ),
        ),
        Union()(
            Translate(x=(inner_width + vert_rod_dia) / -3.5, y=yoff_front)( make_screw_hole(10) ),
            Translate(x=(inner_width + vert_rod_dia) / 3.5, y=yoff_front)( make_screw_hole(10) ),
            Translate(y=0)( Rotate(x=90)( Cylinder(dia=m3_dia, h=front_plate().h * 2, fn=40) )),
        ))

def make_back_hanger():
    yoff_back = back_plate().depth / 2 + horz_rod_dia / 2
    #return Union()(
    return Difference()(
        Union()(
            Translate(y=yoff_back)(back_plate()),
            Translate(y=yoff_back - back_plate_wings.depth)( back_plate_wings ),
        ),
        Union()(
            Translate(x=(inner_width + vert_rod_dia) / -3.5, y=yoff_back)( Rotate(z=180, y=90)( make_nut_hole(10) )),
            Translate(x=(inner_width + vert_rod_dia) / 3.5, y=yoff_back)( Rotate(z=180, y=90)( make_nut_hole(10) )),
            Translate(y=yoff_back)( Rotate(y=90, z=180)( make_screw_hole(10) ))
        ))

def make_screw_hole(depth):
    return Union()(
        # head
        Rotate(x=90)( Cylinder(dia=m3_head_dia, h=m3_head_height, fn=40) ),
        # shaft
        Translate(y=depth)(
            Rotate(x=90)( Translate(z=1)( Cylinder(dia=m3_dia, h=depth, fn=40) )),
        )
    )

def make_nut_hole(depth):
    return Union()(
        # head
        Rotate(x=90)( Cylinder(dia=m3_nut_dia, h=m3_nut_height, fn=6) ),
        # shaft
        Translate(y=depth)(
            Rotate(x=90)( Translate(z=1)( Cylinder(dia=m3_dia, h=depth, fn=40) )),
        )
    )

def make_cross_beams():
    return Union()(
        Translate(z=(inner_height + horz_rod_dia) / 2, y=horz_rod_dia / 2)(Rotate(y=90)(horz_rod)),
        Translate(z=(inner_height + horz_rod_dia) / -2, y=horz_rod_dia / 2)(Rotate(y=90)(horz_rod)),
        Translate(x=(inner_width + vert_rod_dia) / 2, y=vert_rod_dia / -2)(vert_rod),
        Translate(x=(inner_width + vert_rod_dia) / -2, y=vert_rod_dia / -2)(vert_rod),
    )

def make_hook():
    hook_height = in2mm(.5)
    hook_length = in2mm(.2)
    base_height = in2mm(.7) - hook_height
    base_length = in2mm(.9) - hook_length
    hook_width = in2mm(.25)

    points = [ [0, 0], [0, base_height], 
            [base_length, base_height], 
            [base_length, base_height + hook_height], 
            [base_length + hook_length, base_height + hook_height],
            [base_length + hook_length, 0] ]

    #return LinearExtrude(h=hook_width)( Polygon(points=points) )
    #return Union()(
    return Minkowski()(
        #Translate(z=hook_width/2)( Sphere(d=in2mm(.25), fn=20) ),
        Translate(z=hook_width/2, y=.26)( Cylinder(d=in2mm(.25), h=1, fn=20) ),
        LinearExtrude(h=hook_width)( Polygon(points=points) ))

def make_hook_plate():
    plate_length = in2mm(6)
    plate_height = in2mm(1)
    plate_depth = 4
    hook = lambda idx: Translate(x = plate_length / 2 - in2mm(.25) + in2mm(idx), y=plate_height / 2)( Rotate(x=90, y=270, z=90)( make_hook() ))
    return Union()( 
            Difference() (
                Cube(x=plate_length, y=plate_height, z=plate_depth, center=True),
                Translate(x=plate_length / 2 - in2mm(.5), z=.2)( Rotate(x=270)( make_screw_hole(plate_depth+4) )),
                Translate(x=plate_length / -2 + in2mm(.5), z=.2)( Rotate(x=270)( make_screw_hole(plate_depth+4) )),
            ),
            Translate(x=in2mm(-1), y=in2mm(-.25 + .135), z=in2mm(.05) )( *[hook(-idx) for idx in range(5)] )
        )

def make_base_pole():
    base_pole_height = 10
    nut_offset = 3
    cut_depth = 10
    return Difference()(
            Cylinder(h=base_pole_height, dia1=m3_nut_dia + 1.5, dia2=m3_nut_dia + 10, fn=40),
            Cylinder(h=base_pole_height - 1, dia=m3_dia, fn=40),
            Translate(z=nut_offset, y=(cut_depth / 2) - (m3_nut_dia / 2))(
                Cube((m3_nut_dia + 0.5,cut_depth,2), center=True),
            ),
            )

front_hanger = Difference() ( make_front_hanger(), make_cross_beams() )
back_hanger = Difference() ( make_back_hanger(), make_cross_beams() )
hanger = Union()(front_hanger, back_hanger)
"""
both_printable = Union()(
    Translate(y=10, z=-vert_rod_dia / 2)( Rotate(x=90, y=180)( front_hanger )),
    Translate(y=-10, z=-vert_rod_dia + .6)( Rotate(x=-90, y=180)( back_hanger )))
"""
both_printable = Union()(
    Translate(y=10, z=vert_rod_dia / 2 + front_plate.depth + .1)( Rotate(x=90, y=0)( front_hanger )),
    Translate(y=-10, z=vert_rod_dia / 2 + back_plate.depth + 1.6)( Rotate(x=-90, y=0)( back_hanger )))
base_pole = Rotate(x=0)( make_base_pole() )
hook_plate = Rotate(x=-90, z=180)( make_hook_plate() )

hook_plate.render("hook_plate.scad")
#hook_plate.render("hook_plate.stl")
base_pole.render("base_pole.scad")
hanger.render("wire_shelf_hanger.scad")
both_printable.render("printable_wire_shelf_hanger.scad")
#both_printable.render("printable_wire_shelf_hanger.stl")
