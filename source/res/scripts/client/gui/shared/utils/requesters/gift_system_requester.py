# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/gift_system_requester.py
from collections import OrderedDict
from itertools import islice
import BigWorld
from adisp import async
from gui.gift_system.constants import GIFTS_STORAGE_KEY
from gui.gift_system.wrappers import GiftStorageData
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from skeletons.gui.shared.utils.requesters import IGiftSystemRequester

class GiftSystemRequester(AbstractSyncDataRequester, IGiftSystemRequester):

    def __init__(self):
        self.__giftStorage = {}
        super(GiftSystemRequester, self).__init__()

    def clear(self):
        self.__giftStorage.clear()
        super(GiftSystemRequester, self).clear()

    @property
    def isHistoryReady(self):
        return bool(self.getCacheValue('isReady', False))

    def getGiftFromStorage(self, giftTypeID, offset=0, limit=0):
        return [ GiftStorageData(receiverID, giftData[0], giftData[1]) for receiverID, giftData in islice(self.__giftStorage.get(giftTypeID, {}).iteritems(), offset if offset else None, offset + limit if limit else None) ]

    def getGiftStorageGroupedCount(self, giftTypeID):
        return len(self.__giftStorage.get(giftTypeID, {}))

    def getGiftStorageDataCount(self, giftTypeID):
        return sum((giftData[0] for giftData in self.__giftStorage.get(giftTypeID, {}).values()))

    def findGiftBySenderID(self, giftTypeID, senderID):
        storage = self.__giftStorage.get(giftTypeID, {})
        for idx, dataKey in enumerate(storage):
            if senderID == dataKey:
                data = storage[dataKey]
                return (idx, GiftStorageData(dataKey, data[0], data[1]))

        return (-1, None)

    def sortGiftStorage(self, giftTypeID):
        if giftTypeID in self.__giftStorage:
            self.__giftStorage[giftTypeID] = OrderedDict(sorted(self.__giftStorage[giftTypeID].iteritems(), key=lambda d: (-d[1][0], d[1][1])))

    @async
    def _requestCache(self, callback):
        BigWorld.player().giftSystem.getCache(lambda resID, value: self._response(resID, value, callback))

    def _preprocessValidData(self, data):
        res = dict(data)
        if GIFTS_STORAGE_KEY in res:
            self.__updateDataStorage(res[GIFTS_STORAGE_KEY])
        return res

    def __updateDataStorage(self, data):
        for giftID in data:
            if giftID not in self.__giftStorage:
                self.__giftStorage[giftID] = OrderedDict(data[giftID])
            self.__giftStorage[giftID].update(data[giftID])
            for key in set(self.__giftStorage[giftID].keys()).difference(data[giftID]):
                self.__giftStorage[giftID].pop(key)
