# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/floating_point_utils.py


def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)
