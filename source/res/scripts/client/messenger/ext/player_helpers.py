# Embedded file name: scripts/client/messenger/ext/player_helpers.py
import BigWorld
from debug_utils import LOG_ERROR
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared import g_itemsCache
from gui.shared.utils import getPlayerDatabaseID, getPlayerName
from messenger.m_constants import USER_TAG
from messenger.proto.entities import ClanInfo
from messenger.storage import storage_getter

def _getInfo4AccountPlayer():
    return (getPlayerDatabaseID(), getPlayerName(), None)


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

    def initPersonalAccount(self):
        dbID, name, clanAbbrev = _getInfo4AccountPlayer()
        if dbID:
            if self.usersStorage.getUser(dbID) is None:
                from messenger.proto.entities import CurrentUserEntity
                user = CurrentUserEntity(dbID, name, ClanInfo(abbrev=clanAbbrev))
                user.addTags({USER_TAG.CLAN_MEMBER})
                self.usersStorage.addUser(user)
        else:
            LOG_ERROR('Current player is not found')
        return

    def initCachedData(self):
        accountAttrs = g_itemsCache.items.stats.attributes
        self.__setAccountAttrs(accountAttrs)
        clanInfo = g_itemsCache.items.stats.clanInfo
        self.__setClanInfo(clanInfo)
        g_clientUpdateManager.addCallbacks({'account.attrs': self.__setAccountAttrs,
         'stats.clanInfo': self.__setClanInfo})

    def onAvatarShowGUI(self):
        dbID, name, clanAbbrev = _getInfo4AvatarPlayer()
        user = self.usersStorage.getUser(dbID)
        if dbID:
            if user is None:
                from messenger.proto.entities import CurrentUserEntity
                self.usersStorage.addUser(CurrentUserEntity(dbID, name, clanInfo=ClanInfo(abbrev=clanAbbrev)))
        else:
            LOG_ERROR('Current player is not found')
        return

    def onAvatarBecomePlayer(self):
        self.clear()

    def onDisconnected(self):
        self.clear()

    def __setAccountAttrs(self, accountAttrs):
        self.playerCtx.setAccountAttrs(accountAttrs)

    def __setClanInfo(self, info):
        if info:
            length = len(info)
        else:
            length = 0
        if length > 1:
            abbrev = info[1]
        else:
            abbrev = ''
        if length > 3:
            role = info[3]
        else:
            role = 0
        clanInfo = ClanInfo(abbrev=abbrev, role=role)
        self.playerCtx.setClanInfo(clanInfo)
        user = self.usersStorage.getUser(getPlayerDatabaseID())
        if user:
            user.update(clanInfo=clanInfo)
            user.addTags({USER_TAG.CLAN_MEMBER})
