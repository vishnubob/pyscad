#!/usr/bin/env python

from setuptools import setup

sctk = {
    "name": "PySCAD",
    "description": "Python based OpenSCAD framework",
    "author":"Giles Hall",
    "author_email": "giles@polymerase.org",
    "keywords": ["scad", "3D modeling", "3D printing"],
    "classifiers": [
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2 :: Only",
        "Topic :: Multimedia :: Graphics :: 3D Modeling",
        "Topic :: Multimedia :: Graphics :: 3D Rendering",
    ],
    "packages": ["scad"],
    "package_dir": {"scad": "src"},
    "install_requires": [
        "pint", 
        "freetype-py"
    ],
    "url": "https://github.com/vishnubob/pyscad",
    "download_url": "https://github.com/vishnubob/pyscad/archive/v0.1.zip",
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
        "scad.gear", 
        "scad.text", 
        "scad.drill", 
        "scad.drill_sizes", 
    ],
    "version": "0.1",
}

if __name__ == "__main__":
    setup(**sctk)
