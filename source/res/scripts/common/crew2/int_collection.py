# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/crew2/int_collection.py
import exceptions
import typing

def parseIntCollection(string):
    if ':' in string:
        if ',' in string:
            return IntCollection(string=string)
        else:
            return IntRange(string=string)
    else:
        return [ int(x) for x in string.split(',') ]


class IIntCollection(object):

    def __len__(self):
        raise exceptions.NotImplementedError()

    def __iter__(self):
        raise exceptions.NotImplementedError()

    def __contains__(self, item):
        raise exceptions.NotImplementedError()

    def __index__(self):
        raise exceptions.NotImplementedError()


class IntRange(IIntCollection):
    __slots__ = ('_first', '_last')

    def __init__(self, string=None):
        a, b = string.split(':')
        first, last = int(a), int(b)
        if last < first:
            raise exceptions.IOError('Last is less than First')
        self._first = first
        self._last = last

    def __len__(self):
        return self._last - self._first + 1

    def __iter__(self):
        i = self._first
        while i <= self._last:
            yield i
            i += 1

    def __contains__(self, item):
        return self._first <= item <= self._last

    def __getitem__(self, item):
        result = self._first + item
        if result > self._last:
            raise exceptions.KeyError('Index out of range')
        return result


class IntCollection(IIntCollection):
    __slots__ = ('_values', '_ranges', '_cachedLen')

    def __init__(self, string=None):
        if string is not None:
            self._initFromString(string)
        return

    def _initFromString(self, string):
        self._values = []
        self._ranges = []
        self._cachedLen = None
        items = string.split(',')
        for item in items:
            if ':' in item:
                self._ranges.append(IntRange(string=item))
            self._values.append(int(item))

        return

    def __len__(self):
        if self._cachedLen is not None:
            return self._cachedLen
        else:
            nLen = len(self._values)
            for r in self._ranges:
                nLen += len(r)

            self._cachedLen = nLen
            return self._cachedLen

    def __iter__(self):
        for v in self._values:
            yield v

        for r in self._ranges:
            for v in r:
                yield v

    def __contains__(self, item):
        if item in self._values:
            return True
        for r in self._ranges:
            if item in r:
                return True

        return False

    def __getitem__(self, item):
        index = item
        if index < len(self._values):
            return self._values[index]
        index -= len(self._values)
        for r in self._ranges:
            if index < len(r):
                return r[index]
            index -= len(r)

        raise exceptions.KeyError('Index out of range')
