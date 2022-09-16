# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/math_common.py
from math import ceil
_CEIL_EPS = 1

def ceilTo(num, decimals=0):
    multiplier = 10 ** decimals
    return ceil(round(num / multiplier, _CEIL_EPS)) * multiplier


def round_int(number):
    return int(round(number))


def roundToPower10(value, power):
    return round(value, max(0, power)) * 10 ** power


def isAlmostEqual(first, second, epsilon=0.0004):
    return second - epsilon <= first <= second + epsilon


def trim(v, min, max):
    if v < min:
        v = min
    elif v > max:
        v = max
    return v
