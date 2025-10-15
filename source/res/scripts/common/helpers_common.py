# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/helpers_common.py
from typing import Sequence
from soft_exception import SoftException
from math_common import isAlmostEqual

def bisectLE(a, v, lo=0, hi=None):
    if lo < 0:
        raise SoftException('lo must be non-negative')
    if hi is None:
        hi = len(a) - 1
    while lo < hi:
        mid = (lo + hi >> 1) + 1
        if a[mid] <= v:
            lo = mid
        hi = mid - 1

    return lo


def computeDistanceFactor(shellDescr, distance, factorName):
    distanceFactor = shellDescr.distanceFactor
    if distanceFactor is None:
        return 1.0
    else:
        prevFactor = factor = 1.0
        prevDistance = maxDistance = 0
        for maxDistance, factor in getattr(distanceFactor, factorName):
            if maxDistance > distance:
                break
            prevFactor = factor
            prevDistance = maxDistance

        result = factor - prevFactor
        if not isAlmostEqual(result, 0.0):
            result /= maxDistance - prevDistance
        return prevFactor + result * (distance - prevDistance)
