# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Login.py
# Compiled at: 2011-11-16 14:14:03
import BigWorld
from PlayerEvents import g_playerEvents
from debug_utils import *

class PlayerLogin(BigWorld.Entity):

    def __init__(self):
        pass

    def onBecomePlayer(self):
        pass

    def onBecomeNonPlayer(self):
        pass

    def onKickedFromServer(self, checkoutPeripheryID):
        LOG_MX('onKickedFromServer', checkoutPeripheryID)
        g_playerEvents.onKickWhileLoginReceived(checkoutPeripheryID)

    def receiveLoginQueueNumber(self, queueNumber):
        LOG_MX('receiveLoginQueueNumber', queueNumber)
        g_playerEvents.onLoginQueueNumberReceived(queueNumber)

    def handleKeyEvent(self, event):
        return False


Login = PlayerLogin
