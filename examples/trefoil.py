from math import *
twopi = 2 * pi

function vec3(p) = len(p) < 3 ? concat(p,0) : p;
function vec4(p) = let (v3=vec3(p)) len(v3) < 4 ? concat(v3,1) : v3;
function unit(v) = v/norm(v);

function identity3()=[[1,0,0],[0,1,0],[0,0,1]]; 
function identity4()=[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]];


function take3(v) = [v[0],v[1],v[2]];
function tail3(v) = [v[3],v[4],v[5]];
function rotation_part(m) = [take3(m[0]),take3(m[1]),take3(m[2])];
function rot_trace(m) = m[0][0] + m[1][1] + m[2][2];
function rot_cos_angle(m) = (rot_trace(m)-1)/2;

function rotation_part(m) = [take3(m[0]),take3(m[1]),take3(m[2])];
function translation_part(m) = [m[0][3],m[1][3],m[2][3]];
function transpose_3(m) = [[m[0][0],m[1][0],m[2][0]],[m[0][1],m[1][1],m[2][1]],[m[0][2],m[1][2],m[2][2]]];
function transpose_4(m) = [[m[0][0],m[1][0],m[2][0],m[3][0]],
                           [m[0][1],m[1][1],m[2][1],m[3][1]],
                           [m[0][2],m[1][2],m[2][2],m[3][2]],
                           [m[0][3],m[1][3],m[2][3],m[3][3]]]; 
function invert_rt(m) = construct_Rt(transpose_3(rotation_part(m)), -(transpose_3(rotation_part(m)) * translation_part(m)));
function construct_Rt(R,t) = [concat(R[0],t[0]),concat(R[1],t[1]),concat(R[2],t[2]),[0,0,0,1]];

// Hadamard product of n-dimensional arrays
function hadamard(a,b) = !(len(a)>0) ? a*b : [ for(i = [0:len(a)-1]) hadamard(a[i],b[i]) ];

def rotation_from_axis(x, y, z):
    return [[x[0], y[0], z[0]], [x[1], y[1], z[1]], [x[2], y[2], z[2]]]

def rotate_from_to(a, b, _axis=[]):
    if len(_axis) == 0:
        return rotate_from_to(a, b, unit(cross(a,b))) 
    elif _axis * _axis >= 0.99:
        return rotation_from_axis(unit(b), _axis, cross(_axis,unit(b))) * transpose_3(rotation_from_axis(unit(a),_axis,cross(_axis,unit(a))))
    else:
        return identity3();

def construct_rt(r,t):
    return [r[0] + t[0], r[1] + t[1], r[2] + t[2], [0,0,0,1]] 

def unit(v):
    return v / norm(v)

def tangent_path(path, i):
    if i == 0:
        return unit(path[1] - path[0])
    elif i + 1 == len(path):
        return unit(path[i] - path[i-1])
    else:
        return unit(path[i+1] - path[i-1])

def construct_transform_path(path):
    for idx in range(len(path)):
        rot = rotate_from_to([0,0,1], tangent_path(path, i))
        yield construct_rt(rot, path[i])

def trefoil(a, b, t):
    trefoil = [
        a * cos (3 * t) / (1 - b* sin (2 *t)), 
        a * sin( 3 * t) / (1 - b* sin (2 *t)), 
        1.8 * b * cos (2 * t) /(1 - b* sin (2 *t)) 
    ] 
    return trefoil

a = 0.8 
b = (1 - a * a) ** .5
steps = 200
trefoil_path = [f(a, b, (float(t) / steps) * twopi) * steps for t in range(steps)]

path_transforms = construct_transform_path(path);
sweep(shape(), path_transforms, true);


function make_orthogonal(u,v) = unit(u - unit(v) * (unit(v) * u)); 

// Prevent creeping nonorthogonality 
function coerce(m) = [unit(m[0]), make_orthogonal(m[1],m[0]), make_orthogonal(make_orthogonal(m[2],m[0]),m[1])]; 

module sweep(shape, path_transforms, closed=false) {

    pathlen = len(path_transforms);
    segments = pathlen + (closed ? 0 : -1);
    shape3d = to_3d(shape);

    function sweep_points() =
      flatten([for (i=[0:pathlen-1]) transform(path_transforms[i], shape3d)]);

    function loop_faces() = [let (facets=len(shape3d))
        for(s=[0:segments-1], i=[0:facets-1])
          [(s%pathlen) * facets + i, 
           (s%pathlen) * facets + (i + 1) % facets, 
           ((s + 1) % pathlen) * facets + (i + 1) % facets, 
           ((s + 1) % pathlen) * facets + i]];

    bottom_cap = closed ? [] : [[for (i=[len(shape3d)-1:-1:0]) i]];
    top_cap = closed ? [] : [[for (i=[0:len(shape3d)-1]) i+len(shape3d)*(pathlen-1)]];
    polyhedron(points = sweep_points(), faces = concat(loop_faces(), bottom_cap, top_cap), convexity=5);
}
