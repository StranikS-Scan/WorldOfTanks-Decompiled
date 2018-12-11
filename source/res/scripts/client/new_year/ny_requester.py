# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_requester.py
import BigWorld
from adisp import async
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from new_year.ny_constants import SyncDataKeys
from new_year.ny_toy_info import NewYear19ToyInfo

class _NewYearToy(NewYear19ToyInfo):
    __slots__ = ('__totalCount', '__unseenCount', '__unseenInCollection')

    def __init__(self, toyId, totalCount, unseenFlag):
        super(_NewYearToy, self).__init__(toyId)
        self.__totalCount = totalCount
        self.__unseenCount = unseenFlag >> 1
        self.__unseenInCollection = not bool(unseenFlag % 2)

    def getCount(self):
        return self.__totalCount

    def getUnseenCount(self):
        return self.__unseenCount

    def isNewInCollection(self):
        return self.__unseenInCollection

    def __cmp__(self, other):
        if other.getRank() != self.getRank():
            return other.getRank() - self.getRank()
        if self.__unseenCount and not other.getUnseenCount():
            return -1
        return 1 if not self.__unseenCount and other.getUnseenCount() else self.getID() - other.getID()


class NewYearRequester(AbstractSyncDataRequester):
    dataKey = 'newYear19'

    def getToys(self):
        return self.getCacheValue(SyncDataKeys.INVENTORY_TOYS, {})

    def getSlots(self):
        return self.getCacheValue(SyncDataKeys.SLOTS, [])

    def getMaxLevel(self):
        return self.getCacheValue(SyncDataKeys.LEVEL, 0)

    def getAlbums(self):
        return self.getCacheValue(SyncDataKeys.ALBUMS, {})

    def getToyCollection(self):
        return self.getCacheValue(SyncDataKeys.TOY_COLLECTION)

    def getCollectionDistributions(self):
        return self.getCacheValue(SyncDataKeys.COLLECTION_DISTRIBUTIONS)

    def getSelectedDiscounts(self):
        return self.getCacheValue(SyncDataKeys.SELECTED_DISCOUNTS, set())

    def getShardsCount(self):
        return self.getCacheValue(SyncDataKeys.TOY_FRAGMENTS, 0)

    @async
    def _requestCache(self, callback):
        BigWorld.player().festivities.getCache(lambda resID, value: self._response(resID, value, callback))

    def _preprocessValidData(self, data):
        nyData = data.get(self.dataKey, {})
        result = dict(nyData)
        if SyncDataKeys.INVENTORY_TOYS in nyData:
            inventoryToys = {}
            for toyId, (totalCount, unseenCount) in nyData[SyncDataKeys.INVENTORY_TOYS].iteritems():
                inventoryToys[toyId] = _NewYearToy(toyId, totalCount, unseenCount)

            result[SyncDataKeys.INVENTORY_TOYS] = inventoryToys
        return result
