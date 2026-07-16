# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/formatters/ranges.py
from __future__ import absolute_import
from builtins import range
from future.utils import lmap
from helpers import int2roman

def toRangeString(sequence, step=1, itemDelimiter=', ', rangeDelimiter='-'):
    return itemDelimiter.join((rangeDelimiter.join(item) for item in stringRanges(sequence, step)))


def toRomanRangeString(sequence, step=1, itemDelimiter=', ', rangeDelimiter='-'):
    return itemDelimiter.join((rangeDelimiter.join(item) for item in romanStringRanges(sequence, step)))


def stringRanges(sequence, step):
    for item in numberRanges(sequence, step):
        yield lmap(str, item)


def romanStringRanges(sequence, step):
    for item in numberRanges(sequence, step):
        yield lmap(int2roman, item)


def numberRanges(sequence, step):
    length = len(sequence)
    if length > 0:
        q = sorted(sequence)
        i = 0
        for j in range(1, length):
            if q[j] > step + q[j - 1]:
                if i == j - 1:
                    yield (q[i],)
                else:
                    yield (q[i], q[j - 1])
                i = j

        if i == length - 1:
            yield (q[i],)
        else:
            yield (q[i], q[-1])
