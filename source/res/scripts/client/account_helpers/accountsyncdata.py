# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/AccountSyncData.py
from functools import partial
import AccountCommands
from SyncController import SyncController
from debug_utils import LOG_ERROR, LOG_DEBUG
from persistent_caches import SimpleCache
from live_crc_accountdata import accountDataPersistentHash, accountDataExtractPersistent, accountDataGetDiffForPersistent, accountDataMergePersistent
from shared_utils.account_helpers.diff_utils import synchronizeDicts

class AccountSyncData(object):

    def __init__(self):
        self.revision = 0
        self.__account = None
        self.__syncController = None
        self.__ignore = True
        self.__isSynchronized = False
        self.__syncID = 0
        self.__subscribers = []
        self.__isFirstSync = True
        self.__persistentCache = SimpleCache('account_caches', 'data')
        self.__persistentCache.data = None
        self.__persistentCache.isDirty = False
        return

    def onAccountBecomePlayer(self):
        self.__ignore = False
        self.__isFirstSync = True
        self._synchronize()

    def onAccountBecomeNonPlayer(self):
        self.__ignore = True
        self.__isSynchronized = False

    def setAccount(self, account):
        self.__account = account
        if self.__syncController is not None:
            self.__syncController.destroy()
            self.__syncController = None
        self.__savePersistentCache()
        if account is not None:
            self.__persistentCache.setAccount(account)
            self.__syncController = SyncController(account, self.__sendSyncRequest, self.__onSyncResponse, self.__onSyncComplete)
        else:
            self.__notifySubscribers(AccountCommands.RES_NON_PLAYER)
        return

    def waitForSync(self, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        elif self.__isSynchronized:
            callback(AccountCommands.RES_CACHE)
            return
        else:
            if callback is not None:
                self.__subscribers.append(callback)
            return

    def updatePersistentCache(self, ext, isFullSync):
        if ext.pop('__cache', None) is not None:
            if not self.__persistentCache.data:
                desc, cacheData = self.__persistentCache.data = self.__persistentCache.get()
                if accountDataPersistentHash(cacheData) != desc:
                    LOG_ERROR('Local account data cache is corrupted: resync')
                    self._resynchronize()
                    return False
                self.__persistentCache.data = cacheData
                self.__persistentCache.isDirty = False
            else:
                cacheData = self.__persistentCache.data
            if cacheData is None:
                LOG_ERROR("Incorrect cache state while syncing data: server said to use cache but I don't have any")
                self._resynchronize()
                return False
            accountDataMergePersistent(ext, cacheData)
            if synchronizeDicts(accountDataGetDiffForPersistent(ext), self.__persistentCache.data)[1]:
                self.__persistentCache.isDirty = True
        else:
            if self.__persistentCache.data is None:
                self.__persistentCache.data = {}
            synchronizeDicts(accountDataGetDiffForPersistent(ext), self.__persistentCache.data)
            self.__persistentCache.isDirty = True
        return True

    def _synchronize(self):
        if self.__ignore:
            return
        elif self.__isSynchronized:
            return
        else:
            self.__syncController.request(self.__getNextSyncID(), None)
            return

    def _resynchronize(self):
        LOG_DEBUG('resynchronize')
        if self.__ignore:
            return
        else:
            self.__isSynchronized = False
            self.revision = 0
            self.__clearPersistentCache()
            self.__syncController.request(self.__getNextSyncID(), None)
            return

    def __onSyncResponse(self, syncID, resultID, ext=None):
        ext = ext or {}
        if resultID == AccountCommands.RES_NON_PLAYER:
            return
        if syncID != self.__syncID:
            return
        if resultID < 0:
            LOG_ERROR('Data synchronization failed.')
            self._resynchronize()
            return
        if self.revision != ext.get('prevRev', self.revision):
            LOG_ERROR('Incorrect diff received', self.revision, ext['prevRev'])
            self._resynchronize()
            return
        self.revision = ext.get('rev', self.revision)
        self.__isSynchronized = True
        if not self.__account._update(not self.__isFirstSync, ext):
            return
        self.__isFirstSync = False
        self.__notifySubscribers(resultID)

    def __onSyncComplete(self, syncID, data):
        if syncID != self.__syncID:
            return
        elif data is None:
            return
        else:
            self.revision = data['rev']
            if not self.__account._update(False, data):
                return
            self._synchronize()
            return

    def __getNextSyncID(self):
        self.__syncID += 1
        if self.__syncID > 30000:
            self.__syncID = 1
        return self.__syncID

    def __sendSyncRequest(self, rqID, proxy):
        if self.__ignore:
            return
        crc = self.__persistentCache.getDescr()
        self.__account._doCmdInt3(AccountCommands.CMD_SYNC_DATA, self.revision, 0 if not crc else crc, 0, proxy)

    def __clearPersistentCache(self):
        self.__persistentCache.data = None
        self.__persistentCache.isDirty = False
        self.__persistentCache.clear()
        return

    def __savePersistentCache(self):
        if self.__persistentCache.isDirty and self.__persistentCache.data:
            self.__persistentCache.data = accountDataExtractPersistent(self.__persistentCache.data)
            self.__persistentCache.save(accountDataPersistentHash(self.__persistentCache.data), self.__persistentCache.data)
            self.__persistentCache.isDirty = False

    def __notifySubscribers(self, resultID):
        subscribers = self.__subscribers
        self.__subscribers = []
        for callback in subscribers:
            callback(resultID)


class BaseSyncDataCache(object):

    def __init__(self, syncData):
        self._account = None
        self._syncData = syncData
        self._cache = {}
        self._ignore = True
        return

    def onAccountBecomePlayer(self):
        self._ignore = False

    def onAccountBecomeNonPlayer(self):
        self._ignore = True

    def setAccount(self, account):
        self._account = account

    def synchronize(self, isFullSync, diff):
        if isFullSync:
            self._cache.clear()
        self._synchronize(diff)

    def _synchronize(self, diff):
        raise NotImplementedError

    def getCache(self, callback=None):
        if self._ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, None)
            return
        else:
            self._syncData.waitForSync(partial(self._onGetCacheResponse, callback))
            return

    def getItems(self, itemsType, callback):
        if self._ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, None)
            return
        else:
            self._syncData.waitForSync(partial(self._onGetItemsResponse, itemsType, callback))
            return

    def _onGetCacheResponse(self, callback, resultID):
        if resultID < 0:
            if callback is not None:
                callback(resultID, None)
            return
        else:
            if callback is not None:
                callback(resultID, self._cache)
            return

    @property
    def _itemsStorage(self):
        return self._cache

    def _onGetItemsResponse(self, itemsType, callback, resultID):
        if resultID < 0:
            if callback is not None:
                callback(resultID, None)
            return
        else:
            if callback is not None:
                callback(resultID, self._itemsStorage.get(itemsType, None))
            return


def isFullSyncDiff(diff):
    return diff.get('prevRev', None) is None
