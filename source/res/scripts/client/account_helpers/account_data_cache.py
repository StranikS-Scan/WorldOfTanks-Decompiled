# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/account_data_cache.py
import logging
from functools import partial
from shared_utils.account_helpers.diff_utils import synchronizeDicts
_logger = logging.getLogger()

class AccountDataStorage(object):
    __SYNC_DATA_CACHE_KEY = 'cache'

    def __init__(self, pdataKey, syncDataCacheKey=None, syncData=None, onAccountDataChangeCallback=None, onAccountCacheChangeCallback=None):
        super(AccountDataStorage, self).__init__()
        self.__pdataKey = pdataKey
        self.__syncDataCacheKey = syncDataCacheKey
        self.__syncData = syncData
        self.__onAccountDataChangeCallback = onAccountDataChangeCallback
        self.__onAccountCacheChangeCallback = onAccountCacheChangeCallback
        self.__pdataCache = {}
        self.__syncDataCache = {}

    @property
    def accountData(self):
        return self.__pdataCache

    @property
    def accountCache(self):
        return self.__syncDataCache

    def clear(self):
        self.__syncData = None
        self.__onAccountDataChangeCallback = None
        self.__onAccountCacheChangeCallback = None
        self.__pdataCache.clear()
        self.__syncDataCache.clear()
        return

    def isSynchronizationNeeded(self, diff):
        return self.__pdataKey in diff or self.__SYNC_DATA_CACHE_KEY in diff and self.__syncDataCacheKey in diff[self.__SYNC_DATA_CACHE_KEY]

    def synchronize(self, isFullSync, diff):
        if isFullSync:
            self.__pdataCache.clear()
            self.__syncDataCache.clear()
        dataResetKey = (self.__pdataKey, '_r')
        if dataResetKey in diff:
            self.__pdataCache = diff[dataResetKey]
        if self.__pdataKey in diff:
            synchronizeDicts(diff[self.__pdataKey], self.__pdataCache)
            if self.__onAccountDataChangeCallback and not isFullSync:
                self.__onAccountDataChangeCallback(diff[self.__pdataKey])
        if self.__SYNC_DATA_CACHE_KEY in diff and self.__syncDataCacheKey in diff[self.__SYNC_DATA_CACHE_KEY]:
            synchronizeDicts(diff[self.__SYNC_DATA_CACHE_KEY][self.__syncDataCacheKey], self.__syncDataCache)
            if self.__onAccountCacheChangeCallback and not isFullSync:
                self.__onAccountCacheChangeCallback(diff[self.__SYNC_DATA_CACHE_KEY][self.__syncDataCacheKey])

    def _getCacheAsync(self, callback=None):
        self.__syncData.waitForSync(partial(self.__onGetCacheResponse, callback))

    def __onGetCacheResponse(self, callback, resultID):
        if resultID < 0:
            if callback is not None:
                callback(resultID, None)
            return
        else:
            if callback is not None:
                callback(resultID, self.__pdataCache)
            return
