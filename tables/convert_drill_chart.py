import pprint
import sys
import re

CodeTemplate = \
"""from drill import *
import sys

def build_drill_tables():
    self = sys.modules[__name__]

    fractional = {}
    wire = {}
    letter = {}

%s
    ns = {}
    ns["fractional"] = DrillTable("fractional", fractional)
    ns["wire"] = DrillTable("wire", wire)
    ns["letter"] = DrillTable("letter", letter)
    ns["imperial"] = DrillTable("imperial", dict(fractional.items() + wire.items() + letter.items()))
    self.__dict__.update(ns)

if "fractional" not in dir():
    build_drill_tables()
"""


def parse_drill_sizes():
    fractional_re = re.compile("([\w\d\.\"\/]+)[^\d]+([\d\.\"\/]+)")
    fn = "drill_sizes.txt"

    f = open(fn)
    for line in f:
        line = line.strip()
        idx = 0
        while 1:
            m = fractional_re.search(line, idx)
            if not m:
                break
            res = m.groups()
            idx = m.end(2)
            (key, val) = res
            if val[-1] == '"':
                val = val[:-1]
            val = float(val)
            try:
                int(key)
                tablename = "wire"
            except ValueError:
                if key.endswith('"'):
                    key = key[:-1]
                    tablename = "fractional"
                else:
                    tablename = "letter"
            ds = "%s[%r] = '%r inch'" % (tablename, key, val)
            yield ds

if __name__ == "__main__":
    code = ''
    res = parse_drill_sizes()
    code = str.join('\n', ["    %s" % line for line in res])
    code = CodeTemplate % code
    sys.stdout.write(code)
