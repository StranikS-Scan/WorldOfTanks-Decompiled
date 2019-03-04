# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/blueprints/FragmentLayouts.py
from bitstring import BitArray

class Layout(object):
    __slots__ = ('rows', 'columns', 'stamps', '__iadd__', '__isub__', '__len__', 'asInt', 'fromInt', 'layoutData')
    LAYOUTS = dict(((16, 4),
     (15, 5),
     (14, 7),
     (10, 5),
     (12, 4),
     (9, 3),
     (8, 4),
     (6, 3),
     (4, 2)))
    filledCount = property(lambda self: self.layoutData.count(1))
    emptyCount = property(lambda self: self.layoutData.count(0))

    @classmethod
    def fromInt(cls, packedLayout=None, length=None):
        length = length or 0
        return cls(0 if packedLayout is None else int(packedLayout), length)

    def __init__(self, intLayout, length):
        layoutDataLength = int(intLayout >> 28 or length)
        self.columns = intLayout >> 24 & 15 or self.LAYOUTS.get(layoutDataLength, layoutDataLength)
        self.rows = layoutDataLength / self.columns
        arrayData = BitArray(length=32, uint=intLayout)
        self.stamps = arrayData[8:16]
        self.layoutData = arrayData[-layoutDataLength:]

    def __iadd__(self, other):
        if type(other) not in (int, long):
            raise TypeError()
        layoutData = self.layoutData
        layoutDataLength = self.layoutData.length
        isInc = other > 0
        other = min(layoutDataLength, abs(other))
        for idx in xrange(layoutDataLength):
            if not other:
                break
            if isInc ^ layoutData[idx]:
                layoutData[idx] = isInc
                other -= 1

        return self

    def __isub__(self, other):
        return self.__iadd__(-other)

    def __len__(self):
        return self.layoutData.length

    def __setitem__(self, key, value):
        self.layoutData[key] = value

    def __getitem__(self, item):
        return self.layoutData[item]

    def __repr__(self):
        return bin(self.layoutData[-len(self)::].uint)

    def asInt(self):
        return (len(self) << 28) + (self.columns << 24) + (self.stamps.uint << 16) + self.layoutData.uint
