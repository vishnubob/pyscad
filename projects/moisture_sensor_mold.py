#!/usr/bin/env python
from scad import *

mold_dia = 12
nail_dia = 3
mold_height = 30


def half_mold(thickness, extra=0, inner_dia=0):
    #ring = Pipe(iD=nail_dia, oD=nail_dia + thickness, height=1, ifn=40, ofn=40)
    inner_dia = inner_dia or mold_dia
    outer_dia = inner_dia + thickness
    tube_height = mold_height - (outer_dia / 2.0)
    mold_tube = Pipe(iD=inner_dia, oD=outer_dia, height=tube_height, ifn=40, ofn=40, icenter=True, ocenter=True)
    mold_endcap = Difference()( 
        Sphere(dia=outer_dia, fn=40, center=True), 
        Sphere(dia=inner_dia, fn=40, center=True), 
        Translate(z=outer_dia / -2.0)( Cube([outer_dia, outer_dia, outer_dia], center=True))
    )

    mold = Union()(
        mold_tube, 
        Translate(z=tube_height / 2.0 - 0.1)( mold_endcap ),
    )

    return Difference()( 
        mold,
        Translate(y=(mold_dia + thickness + extra) / 2.0, z=((mold_dia + thickness) / 4.0))(
            Cube([mold_dia + thickness, mold_dia + thickness, mold_height + 1], center=True),
        )
    )


male_side = Translate(z=-.5)( Rotate(z=180)( half_mold(3.01, extra=1) ))

female_side = Difference() (
        half_mold(5, extra=1),
        Translate(z=-.5)( Rotate(z=180)( half_mold(3.01, extra=1, inner_dia=mold_dia-.01) ))
)

scene = Union() (
        Rotate(y=180, x=90)(
            Translate(x=10, y=mold_dia / -2.0 - 1.5)( male_side ),
            Translate(x=-10, y=mold_dia / -2.0 - 2.5)( Rotate(z=180)( female_side ))
        ))

scene.render("mold.scad")
