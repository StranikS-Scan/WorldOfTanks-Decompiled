# Embedded file name: scripts/client/gui/LobbyContext.py
import BigWorld
from ConnectionManager import connectionManager
from helpers.ServerSettings import ServerSettings
from account_helpers import isRoamingEnabled
from debug_utils import LOG_ERROR
from gui.shared import g_itemsCache
from predefined_hosts import g_preDefinedHosts

class _LobbyContext(object):

    def __init__(self):
        super(_LobbyContext, self).__init__()
        self.__credentials = None
        self.__guiCtx = {}
        self.__serverSettings = None
        return

    def clear(self):
        self.__credentials = None
        self.__guiCtx.clear()
        return

    def onAccountBecomePlayer(self):
        self.__serverSettings = ServerSettings(BigWorld.player().serverSettings)

    def onAccountShowGUI(self, ctx):
        self.__guiCtx = ctx or {}

    def setCredentials(self, login, token):
        self.__credentials = (login, token)

    def getCredentials(self):
        return self.__credentials

    def updateGuiCtx(self, ctx):
        self.__guiCtx.update(ctx)

    def getGuiCtx(self):
        return self.__guiCtx

    def getServerSettings(self):
        return self.__serverSettings

    def getPlayerFullName(self, pName, clanInfo = None, clanAbbrev = None, regionCode = None, pDBID = None):
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
        clanAbbrev = None
        if clanInfo and len(clanInfo) > 1:
            clanAbbrev = clanInfo[1]
        return clanAbbrev

    def getRegionCode(self, dbID):
        regionCode = None
        from gui import game_control
        if dbID and not game_control.g_instance.roaming.isSameRealm(dbID):
            _, regionCode = game_control.g_instance.roaming.getPlayerHome(dbID)
        return regionCode

    def isAnotherPeriphery(self, peripheryID):
        return connectionManager.peripheryID != peripheryID

    def isPeripheryAvailable(self, peripheryID):
        result = True
        if g_preDefinedHosts.periphery(peripheryID) is None:
            LOG_ERROR('Periphery not found', peripheryID)
            result = False
        elif self.__credentials is None:
            LOG_ERROR('Login info not found', peripheryID)
            result = False
        elif g_preDefinedHosts.isRoamingPeriphery(peripheryID) and not isRoamingEnabled(g_itemsCache.items.stats.attributes):
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


g_lobbyContext = _LobbyContext()
