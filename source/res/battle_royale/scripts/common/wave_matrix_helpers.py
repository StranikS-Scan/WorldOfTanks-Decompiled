# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/common/wave_matrix_helpers.py
import heapq
import random
from math import sqrt
from death_zones_helpers import zoneIdFrom, idxFrom
from debug_utils import LOG_DEBUG_DEV

class WaveMatrix(object):

    def __init__(self, size):
        self.size = size
        self._grid = [0] * size ** 2

    def setValue(self, x, y, value):
        self._grid[zoneIdFrom(x, y, self.size)] = value

    def getValue(self, x, y):
        return self._grid[zoneIdFrom(x, y, self.size)]

    def validate(self, x, y):
        return -1 < x < self.size and -1 < y < self.size

    def fillWave(self, fromX, fromY, weight):
        for y in xrange(self.size):
            for x in xrange(self.size):
                distance = round(sqrt((fromX - x) * (fromX - x) + (fromY - y) * (fromY - y)), 2)
                if distance < weight:
                    self.setValue(x, y, int(weight - distance))

    def dump(self):
        for y in xrange(self.size):
            row = []
            for x in xrange(self.size):
                row.append(self.getValue(x, y))

            LOG_DEBUG_DEV(row)

    def appendWave(self, centerX, centerY, matrix, sign=1):
        sz = self.size
        matrixSz = matrix.size
        matrixGrid = matrix._grid
        fromX = centerX - int(matrixSz / 2)
        fromY = centerY - int(matrixSz / 2)
        for y in xrange(matrixSz):
            localY = fromY + y
            if localY < 0:
                continue
            if localY >= sz:
                break
            offset = localY * sz
            matrixOffset = y * matrixSz
            for x in xrange(matrixSz):
                localX = fromX + x
                if localX < 0:
                    continue
                if localX >= sz:
                    break
                self._grid[localX + offset] += matrixGrid[x + matrixOffset] * sign

    def randomSafeCell(self):
        idx = heapq.nsmallest(1, random.sample(xrange(self.size ** 2), self.size ** 2), key=lambda i: self._grid[i])[0]
        return idxFrom(idx, self.size)


def createCenterWaweMatrix(weight):
    size = lambda w: max(w * 2 - 1, 0)
    center = lambda s: max((s - 1) / 2, 0)
    wave = WaveMatrix(size(weight))
    wave.fillWave(center(size(weight)), center(size(weight)), weight)
    return wave
