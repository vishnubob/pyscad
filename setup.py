#!/usr/bin/env python

from setuptools import setup

sctk = {
    "name": "python-scad",
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
    "version": "0.1",
}

if __name__ == "__main__":
    setup(**sctk)
