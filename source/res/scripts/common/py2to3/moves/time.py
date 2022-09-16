# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/py2to3/moves/time.py
from __future__ import absolute_import
from py2to3.utils import PY3
from time import *
if not PY3:
    __future_module__ = True
    from time import clock as perf_counter
