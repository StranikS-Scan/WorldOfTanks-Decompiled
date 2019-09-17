# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/binary_collection.py


class BinarySetCollection(object):
    __slots__ = ('_storage', '_itemsNum')

    def __init__(self, storage):
        self._storage = storage
        self._itemsNum = sum((hasItem for _, hasItem in self))

    @staticmethod
    def createStorage():
        return bytearray()

    def itemsNum(self):
        return self._itemsNum

    def reset(self):
        self._storage[::] = ''
        self._itemsNum = 0
        return

    def hasItem(self, itemID):
        bytePos, mask = self._getOffset(itemID)
        return bool(self._storage[bytePos] & mask) if bytePos < len(self._storage) else False

    def setItem(self, itemID):
        bytePos, mask = self._getOffset(itemID)
        size = len(self._storage)
        if bytePos >= size:
            self._storage.extend([0] * (bytePos - size + 1))
        if not self._storage[bytePos] & mask:
            self._itemsNum += 1
        self._storage[bytePos] |= mask

    def discardItem(self, itemID):
        bytePos, mask = self._getOffset(itemID)
        if bytePos < len(self._storage):
            if self._storage[bytePos] & mask:
                self._itemsNum -= 1
            self._storage[bytePos] &= ~mask
            self._cleanupEmptyBytes()

    @staticmethod
    def _getOffset(itemID):
        bytePos = itemID / 8
        mask = 1 << itemID % 8
        return (bytePos, mask)

    def _cleanupEmptyBytes(self):
        packedDataSize = len(self._storage)
        for byteNum in reversed(range(packedDataSize)):
            if self._storage[byteNum]:
                return
            del self._storage[byteNum]

    def __iter__(self):
        maxID = len(self._storage) * 8
        for itemID in xrange(maxID):
            yield (itemID, self.hasItem(itemID))
