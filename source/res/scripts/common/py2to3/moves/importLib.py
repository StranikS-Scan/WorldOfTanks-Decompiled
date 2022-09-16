# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/py2to3/moves/importLib.py
from __future__ import absolute_import
from py2to3.utils import PY3
if PY3:
    from importlib import reload
else:
    from __builtin__ import reload
