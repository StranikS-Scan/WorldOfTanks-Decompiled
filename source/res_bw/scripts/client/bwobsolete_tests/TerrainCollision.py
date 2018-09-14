# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bwobsolete_tests/TerrainCollision.py
import BigWorld
import Math
import math
import random

def stab(start):
    samplePointStart = start - (0, 10000, 0)
    samplePointEnd = start + (0, 10000, 0)
    return BigWorld.collide(BigWorld.player().spaceID, samplePointStart, samplePointEnd)


def spam(numSamples, start, extent):
    misses = 0
    for i in range(numSamples):
        samplePoint = Math.Vector3()
        samplePoint[0] = start[0] + extent[0] * random.random()
        samplePoint[1] = 0
        samplePoint[2] = start[2] + extent[2] * random.random()
        samplePointStart = samplePoint - (0, 10000, 0)
        samplePointEnd = samplePoint + (0, 10000, 0)
        if None == stab(samplePoint):
            print 'Miss @ X,Z (', samplePointStart[0], ',', samplePointEnd[2], ')'
            misses += 1

    return misses


def scan(numSamples, start, extent):
    misses = 0
    ooNumSamples = 1 / float(numSamples)
    for i in range(numSamples):
        t = i * ooNumSamples
        sample = Math.Vector3()
        sample[0] = start[0] + extent[0] * t
        sample[1] = 0
        sample[2] = start[2] + extent[2] * t
        if None == stab(sample):
            print 'Miss @ X,Z (', sample[0], ',', sample[2], ')'
            misses += 1

    return misses
