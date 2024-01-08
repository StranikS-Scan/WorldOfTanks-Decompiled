# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/auxiliary/crew_books_helper.py
from collections import defaultdict
import BigWorld
from CurrentVehicle import g_currentVehicle
from account_helpers import AccountSettings
from account_helpers.AccountSettings import CREW_BOOKS_VIEWED
from adisp import adisp_async
from nations import INDICES, NONE_INDEX
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers.dependency import descriptor
from items.components.crew_books_constants import CREW_BOOK_RARITY
from items import tankmen
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
MAX_SKILL_VIEW_COUNT = 4
_g_crewBooksViewedCache = None

def crewBooksViewedCache():
    global _g_crewBooksViewedCache
    if _g_crewBooksViewedCache is None:
        _g_crewBooksViewedCache = _CrewBooksViewedCache()
    elif _g_crewBooksViewedCache.userLogin != getattr(BigWorld.player(), 'name', ''):
        _g_crewBooksViewedCache.destroy()
        _g_crewBooksViewedCache = _CrewBooksViewedCache()
    return _g_crewBooksViewedCache


class _CrewBooksViewedCache(object):
    _itemsCache = descriptor(IItemsCache)
    _lobbyContext = descriptor(ILobbyContext)

    def __init__(self):
        self.__viewedItems = AccountSettings.getSettings(CREW_BOOKS_VIEWED)
        self.__userLogin = getattr(BigWorld.player(), 'name', '')
        self.__booksCountByNation = defaultdict(lambda : defaultdict(int))
        self.__syncOwnedItems()
        self._itemsCache.onSyncCompleted += self.__onCacheResync

    @property
    def userLogin(self):
        return self.__userLogin

    def addViewedItems(self, nationID):
        if self.__needUpdate:
            for bookType, count in self.__booksCountByNation.iteritems():
                if bookType in CREW_BOOK_RARITY.NO_NATION_TYPES:
                    self.__viewedItems[bookType] = count
                self.__viewedItems[bookType][nationID] = count[nationID]

            AccountSettings.setSettings(CREW_BOOKS_VIEWED, self.__viewedItems)
            self.__needUpdate = False

    def haveNewCrewBooks(self):
        if self.isCrewBookAvailable:
            return False
        currentNation = g_currentVehicle.item.nationID
        for bookType, count in self.__booksCountByNation.iteritems():
            if bookType in CREW_BOOK_RARITY.NO_NATION_TYPES:
                viewedCount = self.__viewedItems.setdefault(bookType, 0)
                if viewedCount < count:
                    self.__needUpdate = True
                    return True
            if self.__viewedItems[bookType].setdefault(currentNation, 0) < count[currentNation]:
                self.__needUpdate = True
                return True

        return False

    @property
    def newCrewBooksAmount(self):
        result = 0
        if self.isCrewBookAvailable:
            return result
        currentNation = g_currentVehicle.item.nationID
        for bookType, count in self.__booksCountByNation.iteritems():
            if bookType in CREW_BOOK_RARITY.NO_NATION_TYPES:
                viewedCount = self.__viewedItems.setdefault(bookType, 0)
                if viewedCount < count:
                    result += count - viewedCount
                    self.__needUpdate = True
            if self.__viewedItems[bookType].setdefault(currentNation, 0) < count[currentNation]:
                result += count[currentNation] - self.__viewedItems[bookType].setdefault(currentNation, 0)
                self.__needUpdate = True

        return result

    @property
    def crewBooksAmount(self):
        result = 0
        if self.isCrewBookAvailable:
            return result
        currentNation = g_currentVehicle.item.nationID
        for bookType, count in self.__booksCountByNation.iteritems():
            if bookType in CREW_BOOK_RARITY.NO_NATION_TYPES:
                result += count
            result += count[currentNation]

        return result

    @property
    def isCrewBookAvailable(self):
        vehicle = g_currentVehicle.item
        return vehicle is None

    @adisp_async
    def onCrewBooksUpdated(self, diff, callback):
        inventory = diff.get('inventory', {})
        if GUI_ITEM_TYPE.CREW_BOOKS in inventory:
            for cd, count in inventory[GUI_ITEM_TYPE.CREW_BOOKS].iteritems():
                item = tankmen.getItemByCompactDescr(cd)
                if count is None:
                    count = 0
                if item.type in CREW_BOOK_RARITY.NO_NATION_TYPES:
                    self.__booksCountByNation[item.type] = count
                self.__booksCountByNation[item.type][self.__getNationID(item.nation)] = count

            self.__needUpdate = True
        callback(True)
        return

    def destroy(self):
        self._itemsCache.onSyncCompleted -= self.__onCacheResync
        self.__booksCountByNation.clear()
        self.__viewedItems.clear()

    def __onCacheResync(self, reason, diff):
        if reason not in (CACHE_SYNC_REASON.CLIENT_UPDATE, CACHE_SYNC_REASON.DOSSIER_RESYNC):
            self.__syncOwnedItems()

    def __syncOwnedItems(self):
        items = self._itemsCache.items.getItems(GUI_ITEM_TYPE.CREW_BOOKS, REQ_CRITERIA.CREW_ITEM.IN_ACCOUNT)
        for item in items.itervalues():
            bookType = item.getBookType()
            if bookType in CREW_BOOK_RARITY.NO_NATION_TYPES:
                self.__booksCountByNation[bookType] = item.getFreeCount()
            self.__booksCountByNation[bookType][item.getNationID()] = item.getFreeCount()

        self.__needUpdate = True

    def __getNationID(self, nationName):
        return INDICES.get(nationName, NONE_INDEX)
