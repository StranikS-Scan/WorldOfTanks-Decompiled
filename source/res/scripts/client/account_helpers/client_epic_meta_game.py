# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/client_epic_meta_game.py
from functools import partial
import AccountCommands
from debug_utils import LOG_DEBUG_DEV
from shared_utils.account_helpers.diff_utils import synchronizeDicts

def skipResponse(resultID, errorCode):
    LOG_DEBUG_DEV('skipResponse', resultID, errorCode)


class ClientEpicMetaGame(object):
    __DATA_KEY = 'epicMetaGame'

    def __init__(self, syncData):
        self.__account = None
        self.__syncData = syncData
        self.__cache = {}
        self.__ignore = True
        return

    def getStoredDiscount(self):
        return self.__cache[self.__DATA_KEY].get('freeEpicDiscount', {})

    def onAccountBecomePlayer(self):
        self.__ignore = False

    def onAccountBecomeNonPlayer(self):
        self.__ignore = True

    def setAccount(self, account):
        self.__account = account

    def synchronize(self, isFullSync, diff):
        if isFullSync:
            self.__cache.clear()
        dataResetKey = (self.__DATA_KEY, '_r')
        if dataResetKey in diff:
            self.__cache[self.__DATA_KEY] = diff[dataResetKey]
        if self.__DATA_KEY in diff:
            synchronizeDicts(diff[self.__DATA_KEY], self.__cache.setdefault(self.__DATA_KEY, {}))

    def getCache(self, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, None)
            return
        else:
            self.__syncData.waitForSync(partial(self.__onGetCacheResponse, callback))
            return

    def get(self, itemName, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, None)
            return
        else:
            self.__syncData.waitForSync(partial(self.__onGetResponse, itemName, callback))
            return

    def __onGetCacheResponse(self, callback, resultID):
        if resultID < 0:
            if callback is not None:
                callback(resultID, None)
            return
        else:
            if callback is not None:
                callback(resultID, self.__cache)
            return

    def __onGetResponse(self, itemName, callback, resultID):
        if resultID < 0:
            if callback is not None:
                callback(resultID, None)
            return
        else:
            if callback is not None:
                callback(resultID, self.__cache[self.__DATA_KEY].get(itemName, None))
            return
