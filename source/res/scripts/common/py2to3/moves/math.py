# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/py2to3/moves/math.py
from __future__ import absolute_import
from math import *
try:
    from math import gcd as _gcd
except ImportError:
    from fractions import gcd as _gcd

def gcd(*args):
    return _gcd(*args)
