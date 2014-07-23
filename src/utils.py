import json
import os
import logging
import sys
from ctypes import pythonapi, py_object
from _ctypes import PyObj_FromPtr
from operator import mul
from fractions import Fraction

logger = logging.getLogger(__name__)

def midpoint(pt1, pt2):
    res = []
    for (p1, p2) in zip(pt1, pt2):
        res.append((p1 + p2) / 2.0)
    return tuple(res)

def binomial(n, k): 
    return int(reduce(mul, (Fraction(n-i, i+1) for i in xrange(k)), 1))

def bezier_curve(points, steps):
    npts = len(points) - 1
    ndims = len(points[0])
    _points = [[pt[dim] for pt in points] for dim in xrange(ndims)]
    def intp(t, n, i, pt):
        polyt = ((1 - t) ** (n - i)) * (t ** i)
        return binomial(n, i) * polyt * pt
    for step in xrange(steps + 1):
        step = float(step) / steps
        yield tuple([sum([intp(step, npts, pidx, pt) for (pidx, pt) in enumerate(dim)]) for dim in _points])

def dict_proxy(obj):
    # http://code.activestate.com/recipes/576540-make-dictproxy-object-via-ctypespythonapi-and-type/
    PyDictProxy_New = pythonapi.PyDictProxy_New
    PyDictProxy_New.argtypes = (py_object,)
    PyDictProxy_New.rettype = py_object
    assert isinstance(obj, dict)
    return PyObj_FromPtr(PyDictProxy_New(obj))
    
def get_midpoint(points):
    return [sum(pts) / 2.0 for pts in zip(*points)]

def save_json(obj, json_fn, lazy=True):
    if os.path.exists(json_fn) and lazy:
        return
    msg = "saving %s" % json_fn
    logger.info(msg)
    with open(json_fn, 'w') as fh:
        json.dump(obj, fh, sort_keys=True, indent=4, separators=(',', ': '))

def load_json(json_fn):
    msg = "loading %s" % json_fn
    logger.info(msg)
    with open(json_fn) as fh:
        content = fh.read()
    content = str.join('', [line.strip() for line in content.split('\n')])
    obj = json.loads(content)
    return obj

def inch2mm(inches):
    return inches / 0.0393701

def mm2inch(mm):
    return mm * 0.0393701

# http://stackoverflow.com/questions/1724693/find-a-file-in-python
def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)

def which(program):
    if not program:
        return
    def is_qualified_exe(fpath):
        return len(os.path.split(fpath)[0]) and os.path.isfile(fpath) and os.access(fpath, os.X_OK)
    if is_qualified_exe(program):
        return program
    if sys.platform == "darwin":
        bg1 = "/Applications/%s/%s.app/Contents/MacOS/%s" % (program, program, program)
        bg2 = "/Applications/%s.app/Contents/MacOS/%s" % (program, program)
        for best_guess in (bg1, bg2):
            if is_qualified_exe(best_guess):
                return best_guess
    for path in os.environ["PATH"].split(os.pathsep):
        path = path.strip('"')
        best_guess = os.path.join(path, program)
        if is_qualified_exe(best_guess):
            return best_guess
