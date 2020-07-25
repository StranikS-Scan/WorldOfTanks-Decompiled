# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/math_common.py
from math import ceil
_CEIL_EPS = 6

def ceilTo(num, decimals=0):
    multiplier = 10 ** decimals
    return ceil(round(num / multiplier, _CEIL_EPS)) * multiplier
