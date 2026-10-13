# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/py2to3/moves/socketserver.py
from __future__ import absolute_import
try:
    from SocketServer import *
except ImportError:
    from socketserver import *
