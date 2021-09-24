# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/lobby_context.py
import typing
if typing.TYPE_CHECKING:
    from Event import Event

class ILobbyContext(object):
    onServerSettingsChanged = None

    @property
    def collectUiStats(self):
        raise NotImplementedError

    @property
    def needLogUXEvents(self):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    def onAccountBecomePlayer(self):
        raise NotImplementedError

    def onAccountShowGUI(self, ctx):
        raise NotImplementedError

    def getArenaUniqueIDByClientID(self, clientArenaID):
        raise NotImplementedError

    def getClientIDByArenaUniqueID(self, arenaUniqueID):
        raise NotImplementedError

    def setCredentials(self, login, token):
        raise NotImplementedError

    def getCredentials(self):
        raise NotImplementedError

    def isAccountComplete(self):
        raise NotImplementedError

    def setAccountComplete(self, isComplete):
        raise NotImplementedError

    def getBattlesCount(self):
        raise NotImplementedError

    def update(self, diff):
        raise NotImplementedError

    def updateBattlesCount(self, battlesCount, epicBattlesCount):
        raise NotImplementedError

    def updateGuiCtx(self, ctx):
        raise NotImplementedError

    def getGuiCtx(self):
        raise NotImplementedError

    def getServerSettings(self):
        raise NotImplementedError

    def setServerSettings(self, serverSettings):
        raise NotImplementedError

    def getPlayerFullName(self, pName, clanInfo=None, clanAbbrev=None, regionCode=None, pDBID=None):
        raise NotImplementedError

    def getClanAbbrev(self, clanInfo):
        raise NotImplementedError

    def getRegionCode(self, dbID):
        raise NotImplementedError

    def isAnotherPeriphery(self, peripheryID):
        raise NotImplementedError

    def isPeripheryAvailable(self, peripheryID, itemsCache=None):
        raise NotImplementedError

    def getPeripheryName(self, peripheryID, checkAnother=True):
        raise NotImplementedError

    def addHeaderNavigationConfirmator(self, confirmator):
        raise NotImplementedError

    def deleteHeaderNavigationConfirmator(self, confirmator):
        raise NotImplementedError

    def isHeaderNavigationPossible(self, callback=None):
        raise NotImplementedError

    def addFightButtonConfirmator(self, confirmator):
        raise NotImplementedError

    def deleteFightButtonConfirmator(self, confirmator):
        raise NotImplementedError

    def isFightButtonPressPossible(self, callback=None):
        raise NotImplementedError

    def addPlatoonCreationConfirmator(self, confirmator):
        raise NotImplementedError

    def deletePlatoonCreationConfirmator(self, confirmator):
        raise NotImplementedError

    def isPlatoonCreationPossible(self, callback=None):
        raise NotImplementedError
