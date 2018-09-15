# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/storage/PlayerCtxStorage.py
import types
import Event
from constants import ACCOUNT_ATTR, WG_GAMES
from debug_utils import LOG_WARNING
from messenger.storage import SimpleCachedStorage

class PlayerCtxStorage(SimpleCachedStorage):
    __slots__ = ('__accAttrs', '__clanInfo', '__banInfo', '__cachedItems', '__eManager', '__denunciations', 'onAccountAttrsChanged', 'onClanInfoChanged')

    def __init__(self):
        super(PlayerCtxStorage, self).__init__()
        self.__accAttrs = 0
        self.__clanInfo = None
        self.__banInfo = None
        self.__cachedItems = {'lastVoipUri': ''}
        self.__denunciations = set()
        self.__eManager = Event.EventManager()
        self.onAccountAttrsChanged = Event.Event(self.__eManager)
        self.onClanInfoChanged = Event.Event(self.__eManager)
        return

    def __repr__(self):
        return 'PlayerCtxStorage(id=0x{0:08X}, accAttrs={1:n}, clanInfo={2!r:s})'.format(id(self), self.__accAttrs, self.__clanInfo)

    def clear(self):
        self.__accAttrs = 0
        self.__clanInfo = None
        self.__eManager.clear()
        self.__denunciations.clear()
        return

    def getClanInfo(self):
        return self.__clanInfo

    def getClanAbbrev(self):
        return self.__clanInfo.abbrev if self.__clanInfo else ''

    def getClanRole(self):
        return self.__clanInfo.role if self.__clanInfo else 0

    def getClanDbID(self):
        """Gets clan db id by for current player if he is in clan
        :return: clan database id or 0
        :rtype: int
        """
        return self.__clanInfo.dbID if self.__clanInfo else 0

    def setClanInfo(self, clanInfo):
        self.__clanInfo = clanInfo
        self.onClanInfoChanged()

    def setAccountAttrs(self, accAttrs):
        if self.__accAttrs ^ accAttrs:
            self.__accAttrs = accAttrs
            self.onAccountAttrsChanged()

    def isGameAdmin(self):
        return self.__accAttrs & ACCOUNT_ATTR.ADMIN != 0

    def isChatAdmin(self):
        return self.__accAttrs & ACCOUNT_ATTR.CHAT_ADMIN != 0

    def isBanned(self, components=None):
        if self.__banInfo:
            result = self.__banInfo.isBanned(game=WG_GAMES.TANKS, components=components)
        else:
            result = False
        return result

    def getBanInfo(self):
        return self.__banInfo

    def setBanInfo(self, banInfo):
        self.__banInfo = banInfo

    def hasDenunciationFor(self, violatorID, topicID, arenaUniqueID):
        return (violatorID, topicID, arenaUniqueID) in self.__denunciations

    def addDenunciationFor(self, violatorID, topicID, arenaUniqueID):
        self.__denunciations.add((violatorID, topicID, arenaUniqueID))

    def setCachedItem(self, key, value):
        if not isinstance(key, types.StringType):
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
        return self.__cachedItems[key] if key in self.__cachedItems else None

    def _getCachedData(self):
        data = []
        lastVoipUri = self.__cachedItems['lastVoipUri']
        if lastVoipUri:
            data.append(lastVoipUri)
        return data

    def _setCachedData(self, data):
        lastVoipUri = data.pop(0)
        if isinstance(lastVoipUri, types.StringType):
            self.__cachedItems['lastVoipUri'] = lastVoipUri
