# Embedded file name: scripts/client/gui/game_control/roaming.py
from debug_utils import LOG_DEBUG
from gui import GUI_SETTINGS
from gui.LobbyContext import g_lobbyContext
from gui.game_control.controllers import Controller

class RoamingController(Controller):

    def __init__(self, proxy):
        super(RoamingController, self).__init__(proxy)
        self.__roamingSettings = None
        self.__reloginChain = None
        self.__reloginStoppedHandler = None
        return

    def fini(self):
        self.__roamingSettings = None
        self.__clearReloginChain()
        super(RoamingController, self).fini()
        return

    def onAccountBecomePlayer(self):
        self.__roamingSettings = g_lobbyContext.getServerSettings().roaming

    def isEnabled(self):
        return GUI_SETTINGS.roaming

    def isInRoaming(self):
        return self.getCurrentCenterID() != self.getHomeCenterID()

    def getHomeCenterID(self):
        if self.__roamingSettings is not None:
            return self.__roamingSettings.homeCenterID
        else:
            return -1

    def getCurrentCenterID(self):
        if self.__roamingSettings is not None:
            return self.__roamingSettings.curCenterID
        else:
            return -1

    def getRoamingCenters(self):
        if self.__roamingSettings is not None:
            return self.__roamingSettings.servers
        else:
            return []

    def getPlayerHome(self, playerDBID):
        for s in self.getRoamingCenters():
            if s.isPlayerHome(playerDBID):
                return (s.centerID, s.regionCode)

        return (None, None)

    def isPlayerInRoaming(self, playerDBID):
        centerID, _ = self.getPlayerHome(playerDBID)
        return centerID != self.getCurrentCenterID()

    def isSameRealm(self, playerDBID):
        centerID, _ = self.getPlayerHome(playerDBID)
        return self.getHomeCenterID() == centerID

    def relogin(self, peripheryID, onStoppedHandler = None):
        from gui.shared import actions
        LOG_DEBUG('Attempt to relogin to the another periphery', peripheryID)
        chain = [actions.LeavePrbModalEntity(), actions.DisconnectFromPeriphery(), actions.ConnectToPeriphery(peripheryID)]
        self.__reloginStoppedHandler = onStoppedHandler
        self.__reloginChain = actions.ActionsChain(chain)
        self.__reloginChain.onStopped += self.__onReloginStopped
        self.__reloginChain.start()

    def __onReloginStopped(self, isCompleted):
        if self.__reloginStoppedHandler is not None:
            self.__reloginStoppedHandler(isCompleted)
        LOG_DEBUG('Relogin finished', isCompleted)
        return

    def __clearReloginChain(self):
        if self.__reloginChain is not None:
            self.__reloginChain.onStopped -= self.__onReloginStopped
            self.__reloginChain.stop()
            self.__reloginChain = None
            self.__reloginStoppedHandler = None
        return
