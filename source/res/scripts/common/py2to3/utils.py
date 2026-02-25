# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/py2to3/utils.py
from __future__ import absolute_import
import inspect
import sys
PY3 = sys.version_info.major >= 3

def getargspec(func):
    if PY3:
        return inspect.getfullargspec(func)
    else:
        return inspect.getargspec(func)
