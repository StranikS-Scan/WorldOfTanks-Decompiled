# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/intervals.py
import collections
_Interval = collections.namedtuple('Interval', ['begin', 'end'])

class Interval(_Interval):
    EMPTY = None

    def __new__(cls, begin, end):
        return cls.EMPTY if cls.EMPTY is not None and (begin is None or end is None) else super(Interval, cls).__new__(cls, min(begin, end), max(begin, end))

    def __contains__(self, item):
        if isinstance(item, _Interval):
            if not self or not item:
                return False
            return item.begin in self and item.end in self
        else:
            return self.begin <= item <= self.end

    def __nonzero__(self):
        return self is not self.EMPTY

    def __or__(self, other):
        if self.begin in other or self.end in other:
            return Interval(min(self.begin, other.begin), max(self.end, other.end))
        raise ValueError('Non-overlapping intervals', self, other)

    def __and__(self, other):
        return Interval(max(self.begin, other.begin), min(self.end, other.end)) if self.begin in other or self.end in other else self.EMPTY

    def __cmp__(self, other):
        if self & other:
            return 0
        return 1 if self.begin > other.end else -1

    def __str__(self):
        return '[[{}, {}]]'.format(self.begin, self.end)


Interval.EMPTY = Interval(None, None)
