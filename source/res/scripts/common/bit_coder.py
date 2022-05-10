# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/bit_coder.py


class BitCoder:

    def __init__(self, *args):
        self.dimension = sum(args)
        self.fieldDescriptor = tuple(args)

    @staticmethod
    def mask(bits):
        return 2 ** bits - 1

    def extract(self, bitField):
        res = [0] * len(self.fieldDescriptor)
        shift = self.dimension
        for i, v in enumerate(self.fieldDescriptor):
            shift -= v
            res[i] = bitField >> shift & self.mask(v)

        return tuple(res)

    def emplace(self, *fields):
        res = 0
        shift = self.dimension
        for i, f in enumerate(fields):
            bitCount = self.fieldDescriptor[i]
            shift -= bitCount
            res |= (f & self.mask(bitCount)) << shift

        return res

    def checkFit(self, fieldIndex, value):
        return value <= self.mask(self.fieldDescriptor[fieldIndex])
