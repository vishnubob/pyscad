#!/usr/bin/env python

#from setuputils import setup
from distutils.core import setup

sctk = {
    "name": "scad",
    "description": "Python based OpenSCAD framework",
    "author":"Giles Hall",
    "packages": ["scad"],
    "package_dir": {"scad": "src"},
    "py_modules":[
        "scad.__init__", 
        "scad.base", 
        "scad.color", 
        "scad.colornames",
        "scad.core", 
        "scad.geometry", 
        "scad.utils", 
        "scad.vector", 
        "scad.threads", 
        "scad.text", 
        "scad.drill", 
        "scad.drill_sizes", 
    ],
    "version": "0.1",
}

if __name__ == "__main__":
    setup(**sctk)
