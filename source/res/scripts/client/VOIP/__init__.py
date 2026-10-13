# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/VOIP/__init__.py
from __future__ import absolute_import
import BigWorld

def getVOIPManager():
    if not globals().has_key('__handler'):
        from VOIP.VOIPManager import VOIPManager
        globals()['__handler'] = VOIPManager()
    return __handler
