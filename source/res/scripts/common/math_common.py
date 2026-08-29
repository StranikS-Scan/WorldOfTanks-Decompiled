# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/math_common.py
from __future__ import absolute_import, division
from decimal import ROUND_HALF_UP, Decimal
from math import ceil, floor
from future.utils import PY3
from typing import Union
_CEIL_EPS = 1

def ceilTo(num, decimals=0, epsilon=0.0004):
    multiplier = 10 ** decimals
    return ceil(decimal_round((num + epsilon) / multiplier, _CEIL_EPS)) * multiplier


def isAlmostEqual(first, second, epsilon=0.0004):
    return second - epsilon <= first <= second + epsilon


def almostZero(val, epsilon=0.0004):
    return -epsilon < val < epsilon


def trim(v, min, max):
    if v < min:
        v = min
    elif v > max:
        v = max
    return v


def round_py2_style(number):
    if PY3:
        if number % 1 == 0.5:
            return float(ceil(number) if number >= 0 else floor(number))
        return float(round(number))
    return round(number)


def round_py2_style_int(number):
    if PY3:
        if number % 1 == 0.5:
            if number >= 0:
                return ceil(number)
            return floor(number)
        return round(number)
    return int(round(number))


def decimal_round(number, precision=0, rounding=ROUND_HALF_UP):
    decimal_for_processing = number
    if not isinstance(number, Decimal):
        decimal_for_processing = Decimal(repr(number))
    rounded = decimal_for_processing.quantize(Decimal(10) ** (-precision), rounding=rounding)
    return int(rounded) if precision == 0 else float(rounded)
