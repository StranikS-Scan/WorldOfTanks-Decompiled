# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/clientgw/ny_tamagotchi/contexts.py
from gui.clientgw.base.contexts import CommonWebRequestCtx
from gui.clientgw.settings import WebRequestDataType

class NyTamagotchiBaseCtx(CommonWebRequestCtx):

    def isAuthorizationRequired(self):
        return True

    def isClanSyncRequired(self):
        return False

    def isCaching(self):
        return False


class NyTamagotchiGetPlayerInfoCtx(NyTamagotchiBaseCtx):

    def getRequestType(self):
        return WebRequestDataType.NY_TAMAGOTCHI_PLAYER_INFO


class NyTamagotchiGetPlayerStatsCtx(NyTamagotchiBaseCtx):

    def getRequestType(self):
        return WebRequestDataType.NY_TAMAGOTCHI_PLAYER_STATS


class NyTamagotchiGetCurrentStateCtx(NyTamagotchiBaseCtx):
    __slots__ = ('notRecalc',)

    def __init__(self, notRecalc=False, waitingID=''):
        super(NyTamagotchiGetCurrentStateCtx, self).__init__(waitingID)
        self.notRecalc = notRecalc

    def getRequestType(self):
        return WebRequestDataType.NY_TAMAGOTCHI_CURRENT_STATE


class NyTamagotchiGetLeaderboardPageCtx(NyTamagotchiBaseCtx):
    __slots__ = ('page', 'isUserPage')

    def __init__(self, page=0, isUserPage=False, waitingID=''):
        super(NyTamagotchiGetLeaderboardPageCtx, self).__init__(waitingID)
        self.page = page
        self.isUserPage = isUserPage

    def getRequestType(self):
        return WebRequestDataType.NY_TAMAGOTCHI_LEADERBOARD_PAGE


class NyTamagotchiTakeGiftCtx(NyTamagotchiBaseCtx):

    def getRequestType(self):
        return WebRequestDataType.NY_TAMAGOTCHI_TAKE_GIFT


class NyTamagotchiBuyItemsCtx(NyTamagotchiBaseCtx):
    __slots__ = ('__items',)

    def __init__(self, items=None, waitingID=''):
        super(NyTamagotchiBuyItemsCtx, self).__init__(waitingID)
        self.__items = items or {}

    def getData(self):
        return [ {'id': int(key),
         'count': int(value)} for key, value in self.__items.items() ]

    def addItem(self, itemId, count):
        if itemId in self.__items:
            self.__items[itemId] += count
        else:
            self.__items[itemId] = count

    def getItem(self, itemId):
        return self.__items.get(itemId, None)

    def getRequestType(self):
        return WebRequestDataType.NY_TAMAGOTCHI_BUY_ITEMS


class NyTamagotchiActivateItemCtx(NyTamagotchiBaseCtx):
    __slots__ = ('__id', '__count')

    def __init__(self, itemId, count, waitingID=''):
        super(NyTamagotchiActivateItemCtx, self).__init__(waitingID)
        self.__id = itemId
        self.__count = count

    def getData(self):
        return {'id': int(self.__id),
         'count': int(self.__count)}

    def getRequestType(self):
        return WebRequestDataType.NY_TAMAGOTCHI_ACTIVATE_ITEMS
