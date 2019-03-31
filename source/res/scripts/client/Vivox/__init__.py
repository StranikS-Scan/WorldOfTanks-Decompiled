# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Vivox/__init__.py
# Compiled at: 2011-04-29 17:11:16
from ResponseHandler import ResponseHandler
import BigWorld

def getResponseHandler():
    if not globals().has_key('__handler'):
        globals()['__handler'] = ResponseHandler()
        BigWorld.VOIP.setHandler(__handler.channelsMgr)
    return __handler
