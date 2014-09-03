import pprint
import re

CodeTemplate = \
"""from . drill import *

fractional = DrillTable("fractional")
wire = DrillTable("wire")
letter = DrillTable("letter")

%s

imperial = DrillTable("imperial", [fractional, wire, letter])
"""


def parse_drill_sizes():
    fractional_re = re.compile("([\w\d\.\"\/]+)[^\d]+([\d\.\"\/]+)")
    fn = "drill_sizes.txt"

    wire_table = []
    fractional_table = []
    letter_table = []

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
                key = int(key)
            except:
                pass
            if type(key) == int:
                ds = "DrillSize('%s', %s)" % (key, val)
                wire_table.append(ds)
            elif key.endswith('"'):
                ds = "DrillSize('%s', %s)" % (key, val)
                fractional_table.append(ds)
            else:
                ds = "DrillSize('%s', %s)" % (key, val)
                letter_table.append(ds)

    return {
        "wire": wire_table,
        "fractional": fractional_table,
        "letter": letter_table,
    }

code = ''
res = parse_drill_sizes()
for key in res:
    for val in res[key]:
        code += "%s.append(%s)\n" % (key, val)

print CodeTemplate % code
