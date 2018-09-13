# Embedded file name: scripts/client/messenger/storage/PlayerCtxStorage.py
import Event
from constants import ACCOUNT_ATTR
from gui.LobbyContext import g_lobbyContext

class PlayerCtxStorage(object):
    __slots__ = ('accAttrs', 'clanInfo', '__eManager', 'onAccountAttrsChanged', 'onClanInfoChanged')

    def __init__(self):
        super(PlayerCtxStorage, self).__init__()
        self.accAttrs = 0
        self.clanInfo = None
        self.__eManager = Event.EventManager()
        self.onAccountAttrsChanged = Event.Event(self.__eManager)
        self.onClanInfoChanged = Event.Event(self.__eManager)
        return

    def __repr__(self):
        return 'PlayerCtxStorage(id=0x{0:08X}, accAttrs={1:n}, clanInfo={2!r:s})'.format(id(self), self.accAttrs, self.clanInfo)

    def getClanAbbrev(self):
        return g_lobbyContext.getClanAbbrev(self.clanInfo)

    def getClanRole(self):
        role = 0
        if self.clanInfo and len(self.clanInfo) > 3:
            role = self.clanInfo[3]
        return role

    def isChatAdmin(self):
        return self.accAttrs & ACCOUNT_ATTR.CHAT_ADMIN != 0 or self.accAttrs & ACCOUNT_ATTR.ADMIN != 0

    def clear(self):
        self.accAttrs = 0
        self.clanInfo = None
        self.__eManager.clear()
        return

    def _setAccountAttrs(self, accAttrs):
        if self.accAttrs ^ accAttrs:
            self.accAttrs = accAttrs
            self.onAccountAttrsChanged()

    def _setClanInfo(self, clanInfo):
        self.clanInfo = clanInfo
        self.onClanInfoChanged()
