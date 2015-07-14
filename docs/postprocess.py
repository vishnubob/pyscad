#!/usr/bin/env python

import sys
import os
import re
import glob
import shutil
import tempfile

class ExampleGenerator(object):
    ExamplePattern = re.compile("<!--\s+\%EXAMPLE\%\s+([^\s]+)\s+-->")
    ExampleDirectory = "examples"
    ImageDirectory = "images"

    def __init__(self, rootdir='.'):
        rootdir = os.path.abspath(rootdir)
        self.example_dir = os.path.join(rootdir, self.ExampleDirectory)
        self.image_dir = os.path.join(rootdir, self.ImageDirectory)
        if not os.path.exists(self.example_dir):
            os.mkdir(self.example_dir)
        if not os.path.exists(self.image_dir):
            os.mkdir(self.image_dir)

    def parse(self, input_fn):
        inputf = open(input_fn)
        state = "searching"
        for line in inputf:
            if state == "searching":
                m = self.ExamplePattern.search(line)
                if m:
                    example_name = m.groups()[0]
                    state = "begin"
            elif state == "begin":
                if "```" in line:
                    code = ''
                    state = "block"
            elif state == "block":
                if "```" in line:
                    self.build_example(example_name, code)
                    state = "searching"
                else:
                    code += line
    
    def build_example(self, example_name, code):
        cwd = os.getcwd()
        try:
            rundir = tempfile.mkdtemp()
            os.chdir(rundir)
            self._build_example(example_name, code)
        finally:
            os.chdir(cwd)
            shutil.rmtree(rundir)

    def _build_example(self, example_name, code):
        msg = "Building example %s..." % example_name
        print msg
        ofn = example_name + ".py"
        f = open(ofn, 'w')
        f.write(code)
        f.close()
        os.system("python %s" % ofn)
        images = glob.glob("*.png")
        for img in images:
            shutil.copyfile(img, os.path.join(self.image_dir, img))
        shutil.copyfile(ofn, os.path.join(self.example_dir, ofn))

if __name__ == "__main__":
    rootdir = "."
    if len(sys.argv) > 1:
        rootdir = sys.argv[1]
    gen = ExampleGenerator(rootdir=rootdir)
    mdfiles = glob.glob(os.path.join(rootdir, "*.md"))
    for fn in mdfiles:
        gen.parse(fn)
