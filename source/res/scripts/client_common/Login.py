# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/Login.py
import BigWorld
from PlayerEvents import g_playerEvents
from debug_utils import LOG_DEBUG

class PlayerLogin(BigWorld.Entity):

    def __init__(self):
        pass

    def onBecomePlayer(self):
        pass

    def onBecomeNonPlayer(self):
        pass

    def onKickedFromServer(self, checkoutPeripheryID):
        LOG_DEBUG('onKickedFromServer', checkoutPeripheryID)
        g_playerEvents.onKickWhileLoginReceived(checkoutPeripheryID)

    def receiveLoginQueueNumber(self, queueNumber):
        LOG_DEBUG('receiveLoginQueueNumber', queueNumber)
        g_playerEvents.onLoginQueueNumberReceived(queueNumber)

    def handleKeyEvent(self, event):
        return False

    def setPeripheryRoutingGroup(self, peripheryRoutingGroup, availableHosts):
        g_playerEvents.onPeripheryRoutingGroupReceived(peripheryRoutingGroup, availableHosts)


Login = PlayerLogin
