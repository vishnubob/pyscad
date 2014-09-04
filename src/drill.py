import bisect
from . utils import unit

class DrillTable(dict):
    def __init__(self, name="unknown", table=None):
        self.name = name
        if table == None:
            table = {}
        super(DrillTable, self).__init__(table)

    def __repr__(self):
        return "DrillTable(name=%r, table=%r)" % (self.name, self.table)

    def lookup(self, size, nearest=True):
        size = unit(size, unit=None)
        sizes = map(lambda s: unit(s, unit=None), self.values())
        sizes.sort()
        index = bisect.bisect_left(sizes, size)
        drill_1 = sizes[index]
        if drill_1 == size:
            return drill_1
        if not nearest:
            return IndexError, "There is no exact drill size for '%s'" % size
        if len(sizes) > (index - 1):
            drill_2 = sizes[index + 1]
            err1 = abs(drill_1 - size)
            err2 = abs(drill_2 - size)
            if (err1 > err2):
                return drill_2
        return drill_1
