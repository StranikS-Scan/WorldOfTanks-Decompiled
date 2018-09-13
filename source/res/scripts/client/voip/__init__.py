# Embedded file name: scripts/client/VOIP/__init__.py
from VOIPManager import VOIPManager
import BigWorld
from Vivox.VivoxHandler import VivoxHandler as VOIPHandler
from Vivox.VivoxManager import VivoxManager as VOIPManager

def getVOIPManager():
    if not globals().has_key('__handler'):
        globals()['__handler'] = VOIPManager(VOIPHandler())
        BigWorld.VOIP.setHandler(__handler.channelsMgr)
    return __handler
