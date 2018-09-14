# Embedded file name: scripts/client/messenger/storage/PlayerCtxStorage.py
import types
import Event
from constants import ACCOUNT_ATTR
from debug_utils import LOG_WARNING
from gui.LobbyContext import g_lobbyContext
from messenger.storage import SimpleCachedStorage

class PlayerCtxStorage(SimpleCachedStorage):
    __slots__ = ('accAttrs', 'clanInfo', '__cachedItems', '__eManager', 'onAccountAttrsChanged', 'onClanInfoChanged')

    def __init__(self):
        super(PlayerCtxStorage, self).__init__()
        self.accAttrs = 0
        self.clanInfo = None
        self.__cachedItems = {'lastVoipUri': ''}
        self.__eManager = Event.EventManager()
        self.onAccountAttrsChanged = Event.Event(self.__eManager)
        self.onClanInfoChanged = Event.Event(self.__eManager)
        return

    def __repr__(self):
        return 'PlayerCtxStorage(id=0x{0:08X}, accAttrs={1:n}, clanInfo={2!r:s})'.format(id(self), self.accAttrs, self.clanInfo)

    def clear(self):
        self.accAttrs = 0
        self.clanInfo = None
        self.__eManager.clear()
        return

    def getClanAbbrev(self):
        return g_lobbyContext.getClanAbbrev(self.clanInfo)

    def getClanRole(self):
        role = 0
        if self.clanInfo and len(self.clanInfo) > 3:
            role = self.clanInfo[3]
        return role

    def isGameAdmin(self):
        return self.accAttrs & ACCOUNT_ATTR.ADMIN != 0

    def isChatAdmin(self):
        return self.accAttrs & ACCOUNT_ATTR.CHAT_ADMIN != 0

    def setCachedItem(self, key, value):
        if type(key) != types.StringType:
            LOG_WARNING('Key is not string', type(key), key)
            return
        if type(value) not in types.StringTypes:
            LOG_WARNING('Value is not string', type(value), value)
            return
        if key in self.__cachedItems:
            self.__cachedItems[key] = value
        else:
            LOG_WARNING('Item is not enabled', key)

    def getCachedItem(self, key):
        if key in self.__cachedItems:
            return self.__cachedItems[key]
        else:
            return None
            return None

    def _getCachedData(self):
        data = []
        lastVoipUri = self.__cachedItems['lastVoipUri']
        if lastVoipUri:
            data.append(lastVoipUri)
        return data

    def _setCachedData(self, data):
        lastVoipUri = data.pop(0)
        if type(lastVoipUri) is types.StringType:
            self.__cachedItems['lastVoipUri'] = lastVoipUri

    def _setAccountAttrs(self, accAttrs):
        if self.accAttrs ^ accAttrs:
            self.accAttrs = accAttrs
            self.onAccountAttrsChanged()

    def _setClanInfo(self, clanInfo):
        self.clanInfo = clanInfo
        self.onClanInfoChanged()
