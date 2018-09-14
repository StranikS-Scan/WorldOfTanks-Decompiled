# Embedded file name: scripts/common/goodies/GoodieConditions.py


class Condition(object):

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def check(self, other):
        return self == other

    def __ne__(self, other):
        return not self.__eq__(other)


class MaxVehicleLevel(Condition):

    def __init__(self, level):
        self.level = level

    def __lt__(self, other):
        return self.level < other.level
