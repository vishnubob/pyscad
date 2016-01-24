import unittest
import tempfile
import shutil
from scad import *
from scad.base import BaseObject

def check_vector(vector, **answers):
    for (key, value) in answers.items():
        assert getattr(vector, key) == value, "%s != %s" % (getattr(vector, key), value)

def code_compare(result, expected):
    def wash_str(_str):
        for ch in _str:
            if ch in [' ', '\t', '\n']:
                continue
            yield ch
    expected = str.join('', wash_str(expected))
    result = str.join('', wash_str(result))
    assert expected == result, "Generated code does not match expected result: \nExpected: %s\n  Result: %s\n" % (expected, result)

def open_scad_exe():
    scad = OpenSCAD()
    return scad.command
