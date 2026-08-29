# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/VOIP/__init__.py
import BigWorld

def getVOIPManager():
    if not globals().has_key('handler'):
        from VOIP.VOIPSingleton import VOIPSingleton
        globals()['handler'] = VOIPSingleton()
        BigWorld.VOIP.setHandler(handler)
    return handler


def isOSSupported():
    return BigWorld.VOIP.isOSSupported()
