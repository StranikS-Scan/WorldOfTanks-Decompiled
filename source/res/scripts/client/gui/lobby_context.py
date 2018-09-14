# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/lobby_context.py
import BigWorld
from adisp import async, process
from constants import CURRENT_REALM
from helpers import dependency
from helpers.ServerSettings import ServerSettings
from account_helpers import isRoamingEnabled
from debug_utils import LOG_ERROR, LOG_NOTE
from ids_generators import Int32IDGenerator
from predefined_hosts import g_preDefinedHosts
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

class LobbyContext(ILobbyContext):
    """Player's context in lobby."""
    connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self):
        super(LobbyContext, self).__init__()
        self.__credentials = None
        self.__guiCtx = {}
        self.__arenaUniqueIDs = {}
        self.__serverSettings = ServerSettings({})
        self.__battlesCount = None
        self.__clientArenaIDGenerator = Int32IDGenerator()
        self.__headerNavigationConfirmators = set()
        return

    def clear(self):
        self.__headerNavigationConfirmators.clear()
        self.__credentials = None
        self.__battlesCount = None
        self.__guiCtx.clear()
        self.__arenaUniqueIDs.clear()
        if self.__serverSettings:
            self.__serverSettings.clear()
        return

    def onAccountBecomePlayer(self):
        self.setServerSettings(BigWorld.player().serverSettings)

    def onAccountShowGUI(self, ctx):
        self.__guiCtx = ctx or {}

    def getArenaUniqueIDByClientID(self, clientArenaID):
        for arenaUniqueID, cArenaID in self.__arenaUniqueIDs.iteritems():
            if cArenaID == clientArenaID:
                return arenaUniqueID

    def getClientIDByArenaUniqueID(self, arenaUniqueID):
        if arenaUniqueID in self.__arenaUniqueIDs:
            return self.__arenaUniqueIDs[arenaUniqueID]
        else:
            clientID = self.__clientArenaIDGenerator.next()
            self.__arenaUniqueIDs[arenaUniqueID] = clientID
            return clientID

    def setCredentials(self, login, token):
        """Set player credentials that required to accept invite form another periphery.
        :param login: string containing login.
        :param token: string containing token from last login.
        """
        self.__credentials = (login, token)

    def getCredentials(self):
        """Gets player credentials.
        :return: tuple(login, token)
        """
        return self.__credentials

    def getBattlesCount(self):
        """Gets player battlesCount.
        :return: integer containing number of battles that player took part in the game session.
        """
        return self.__battlesCount

    def updateBattlesCount(self, battlesCount):
        """Updates player's number of battles.
        :param battlesCount: integer containing number of battles that player took part in the game session.
        """
        self.__battlesCount = battlesCount

    def update(self, diff):
        if self.__serverSettings and 'serverSettings' in diff:
            self.__serverSettings.update(diff['serverSettings'])

    def updateGuiCtx(self, ctx):
        """Update previous context by new.
        :param ctx: [dict] onAccountShowGUI context.
        """
        self.__guiCtx.update(ctx)

    def getGuiCtx(self):
        """Gets GUI context.
        :return: [dict] onAccountShowGUI context.
        """
        return self.__guiCtx

    @property
    def collectUiStats(self):
        return self.__guiCtx.get('collectUiStats', True)

    @property
    def needLogUXEvents(self):
        return self.__guiCtx.get('logUXEvents', False)

    def getServerSettings(self):
        return self.__serverSettings

    def setServerSettings(self, serverSettings):
        self.__serverSettings = ServerSettings(serverSettings)

    def getPlayerFullName(self, pName, clanInfo=None, clanAbbrev=None, regionCode=None, pDBID=None):
        """Gets player's display name. The full name of the player consists of:
            <player name> [<clanAbbrev>]*
        :param pName: player's name
        :param clanInfo: tuple containing information about clan or None.
        :param clanAbbrev: string containing clan abbreviation.
        :param regionCode: string player home region id.
        :param pDBID: long containing account's database ID.
        :return: string containing player's display name.
        """
        fullName = pName
        if clanInfo and len(clanInfo) > 1:
            clanAbbrev = clanInfo[1]
        if clanAbbrev:
            fullName = '{0:>s} [{1:>s}]'.format(pName, clanAbbrev)
        if pDBID is not None:
            regionCode = self.getRegionCode(pDBID)
        if regionCode:
            fullName = '{0:>s} {1:>s}'.format(fullName, regionCode)
        return fullName

    def getClanAbbrev(self, clanInfo):
        """Gets clan abbreviation by information that received from server.
        :param clanInfo: tuple containing information about clan or None.
        :return: string containing clan abbreviation.
        """
        clanAbbrev = None
        if clanInfo and len(clanInfo) > 1:
            clanAbbrev = clanInfo[1]
        return clanAbbrev

    def getRegionCode(self, dbID):
        regionCode = None
        serverSettings = self.getServerSettings()
        if serverSettings is not None:
            roaming = serverSettings.roaming
            if dbID and not roaming.isSameRealm(dbID):
                _, regionCode = roaming.getPlayerHome(dbID)
        return regionCode

    def isAnotherPeriphery(self, peripheryID):
        if not self._isSkipPeripheryChecking():
            return self.connectionMgr.peripheryID != peripheryID
        LOG_NOTE('Skip periphery checking in standalone mode')
        return False

    @dependency.replace_none_kwargs(itemsCache=IItemsCache)
    def isPeripheryAvailable(self, peripheryID, itemsCache=None):
        result = True
        if self._isSkipPeripheryChecking():
            LOG_NOTE('Skip periphery checking in standalone mode')
            return result
        else:
            if g_preDefinedHosts.periphery(peripheryID) is None:
                LOG_ERROR('Periphery not found', peripheryID)
                result = False
            elif self.__credentials is None:
                LOG_ERROR('Login info not found', peripheryID)
                result = False
            elif g_preDefinedHosts.isRoamingPeriphery(peripheryID) and itemsCache is not None and not isRoamingEnabled(itemsCache.items.stats.attributes):
                LOG_ERROR('Roaming is not supported', peripheryID)
                result = False
            return result

    def getPeripheryName(self, peripheryID):
        name = None
        if self.isAnotherPeriphery(peripheryID):
            host = g_preDefinedHosts.periphery(peripheryID)
            if host is not None:
                name = host.name
        return name

    def addHeaderNavigationConfirmator(self, confirmator):
        self.__headerNavigationConfirmators.add(confirmator)

    def deleteHeaderNavigationConfirmator(self, confirmator):
        if confirmator in self.__headerNavigationConfirmators:
            self.__headerNavigationConfirmators.remove(confirmator)

    @async
    @process
    def isHeaderNavigationPossible(self, callback=None):
        for confirmator in self.__headerNavigationConfirmators:
            confirmed = yield confirmator()
            if not confirmed:
                callback(False)

        callback(True)

    @classmethod
    def _isSkipPeripheryChecking(cls):
        return cls.connectionMgr.isStandalone() and CURRENT_REALM == 'CT'
