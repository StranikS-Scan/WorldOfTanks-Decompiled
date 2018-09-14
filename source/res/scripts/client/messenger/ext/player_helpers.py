# Embedded file name: scripts/client/messenger/ext/player_helpers.py
import BigWorld
import account_helpers
from adisp import process
from debug_utils import LOG_ERROR
from gui.ClientUpdateManager import g_clientUpdateManager
from messenger.storage import storage_getter

def _getInfo4AccountPlayer():
    return (account_helpers.getPlayerDatabaseID(), BigWorld.player().name, None)


def _getAccountDatabaseID():
    return account_helpers.getPlayerDatabaseID()


def _getInfo4AvatarPlayer():
    dbID, name, clanAbbrev = (0L, '', None)
    player = BigWorld.player()
    arena = getattr(player, 'arena', None)
    if arena is not None:
        vehID = getattr(player, 'playerVehicleID', None)
        if vehID is not None and vehID in arena.vehicles:
            vehData = arena.vehicles[vehID]
            dbID = vehData['accountDBID']
            name = vehData['name']
            clanAbbrev = vehData['clanAbbrev']
    return (dbID, name, clanAbbrev)


def _getAvatarDatabaseID():
    dbID = 0L
    player = BigWorld.player()
    arena = getattr(player, 'arena', None)
    if arena is not None:
        vehID = getattr(player, 'playerVehicleID', None)
        if vehID is not None and vehID in arena.vehicles:
            dbID = arena.vehicles[vehID]['accountDBID']
    return dbID


def getPlayerDatabaseID():
    return _getAccountDatabaseID() or _getAvatarDatabaseID()


def isCurrentPlayer(dbID):
    return getPlayerDatabaseID() == dbID


class CurrentPlayerHelper(object):

    def __init__(self):
        super(CurrentPlayerHelper, self).__init__()

    @storage_getter('playerCtx')
    def playerCtx(self):
        return None

    @storage_getter('users')
    def usersStorage(self):
        return None

    def clear(self):
        g_clientUpdateManager.removeObjectCallbacks(self)

    @process
    def onAccountShowGUI(self):
        from gui.shared.utils.requesters import DeprecatedStatsRequester
        dbID, name, clanAbbrev = _getInfo4AccountPlayer()
        if dbID:
            if self.usersStorage.getUser(dbID) is None:
                from messenger.proto.entities import CurrentUserEntity
                self.usersStorage.addUser(CurrentUserEntity(dbID, name, clanAbbrev))
        else:
            LOG_ERROR('Current player is not found')
        accountAttrs = yield DeprecatedStatsRequester().getAccountAttrs()
        self.__setAccountAttrs(accountAttrs)
        clanInfo = yield DeprecatedStatsRequester().getClanInfo()
        self.__setClanInfo(clanInfo)
        g_clientUpdateManager.addCallbacks({'account.attrs': self.__setAccountAttrs,
         'stats.clanInfo': self.__setClanInfo})
        return

    def onAvatarShowGUI(self):
        dbID, name, clanAbbrev = _getInfo4AvatarPlayer()
        user = self.usersStorage.getUser(dbID)
        if dbID:
            if user is None:
                from messenger.proto.entities import CurrentUserEntity
                self.usersStorage.addUser(CurrentUserEntity(dbID, name, clanAbbrev))
        else:
            LOG_ERROR('Current player is not found')
        return

    def onAvatarBecomePlayer(self):
        self.clear()

    def onDisconnected(self):
        self.clear()

    def __setAccountAttrs(self, accountAttrs):
        self.playerCtx._setAccountAttrs(accountAttrs)

    def __setClanInfo(self, clanInfo):
        self.playerCtx._setClanInfo(clanInfo)
        user = self.usersStorage.getUser(getPlayerDatabaseID())
        if user:
            user.update(clanAbbrev=self.playerCtx.getClanAbbrev())
