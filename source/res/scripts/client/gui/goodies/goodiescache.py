# Embedded file name: scripts/client/gui/goodies/GoodiesCache.py
import weakref
from collections import defaultdict
from goodies.goodie_constants import GOODIE_VARIETY, GOODIE_STATE
from gui.goodies.Booster import Booster
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA

class _GoodiesCache(object):

    def __init__(self):
        self._items = weakref.proxy(g_itemsCache.items)
        self.__goodiesCache = defaultdict(dict)

    def init(self):
        g_itemsCache.onSyncStarted += self.__clearCache

    def fini(self):
        g_itemsCache.onSyncStarted -= self.__clearCache

    def clear(self):
        while len(self.__goodiesCache):
            _, cache = self.__goodiesCache.popitem()
            cache.clear()

    @property
    def personalGoodies(self):
        return self._items.goodies.goodies

    @property
    def shopBoosters(self):
        return self._items.shop.boosters

    def getActiveBoostersTypes(self):
        activeBoosterTypes = []
        for boosterID, boosterValues in self.personalGoodies.iteritems():
            if boosterValues.state == GOODIE_STATE.ACTIVE:
                boosterDescription = self.shopBoosters.get(boosterID, None)
                if boosterDescription:
                    activeBoosterTypes.append(boosterDescription.resource)

        return activeBoosterTypes

    def getBooster(self, boosterID):
        boosterDescription = self.shopBoosters.get(boosterID, None)
        boosterValues = self.personalGoodies.get(boosterID, None)
        return self.__makeBooster(boosterID, boosterDescription, boosterValues, self.getActiveBoostersTypes())

    def getBoosters(self, criteria = REQ_CRITERIA.EMPTY):
        results = {}
        activeBoosterTypes = self.getActiveBoostersTypes()
        for boosterID, boosterDescription in self.shopBoosters.iteritems():
            boosterValues = self.personalGoodies.get(boosterID, None)
            booster = self.__makeBooster(boosterID, boosterDescription, boosterValues, activeBoosterTypes)
            if criteria(booster):
                results[boosterID] = booster

        return results

    def __makeBooster(self, boosterID, boosterDescription, boosterValues, activeBoosterTypes):
        container = self.__goodiesCache[GOODIE_VARIETY.BOOSTER]
        if boosterID in container:
            return container[boosterID]
        else:
            booster = None
            if boosterDescription is not None:
                container[boosterID] = booster = Booster(boosterID, boosterDescription, boosterValues, activeBoosterTypes)
            return booster

    def __clearCache(self, *args):
        self.clear()


g_goodiesCache = _GoodiesCache()
