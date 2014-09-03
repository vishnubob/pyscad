class DrillSize(object):
    def __init__(self, name, size, metric=False):
        self.name = name
        self.size = size

    def __cmp__(self, other):
        return cmp(self.size, other.size)

    def __str__(self):
        if self.metric:
            return "%smm" % self.size
        else:
            return "%s (%s\")" % (self.name, self.size)

class DrillTable(list):
