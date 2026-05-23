# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/intervals.py
from __future__ import absolute_import
import collections
from functools import total_ordering
_Interval = collections.namedtuple('Interval', ['begin', 'end'])

@total_ordering
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

    def __bool__(self):
        return self is not self.EMPTY

    __nonzero__ = __bool__

    def __or__(self, other):
        if self.begin in other or self.end in other:
            return Interval(min(self.begin, other.begin), max(self.end, other.end))
        raise ValueError('Non-overlapping intervals', self, other)

    def __and__(self, other):
        return Interval(max(self.begin, other.begin), min(self.end, other.end)) if self.begin in other or self.end in other else self.EMPTY

    def __hash__(self):
        return hash((self.begin, self.end))

    def __eq__(self, other):
        return self.__compare(other) == 0

    def __lt__(self, other):
        return self.__compare(other) < 0

    def __str__(self):
        return '[[{}, {}]]'.format(self.begin, self.end)

    def __compare(self, other):
        if self & other:
            return 0
        return 1 if self.begin > other.end else -1


Interval.EMPTY = Interval(None, None)
