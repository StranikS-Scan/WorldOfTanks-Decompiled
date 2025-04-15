# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/HistoricalBattles.py
from functools import partial
from Event import Event
import AccountCommands
from shared_utils.account_helpers.diff_utils import synchronizeDicts
from debug_utils import LOG_DEBUG_DEV
from historical_battles_common.hb_constants import PDATA_KEY_HISTORICAL_BATTLES

def _skipResponse(resultID, errorCode):
    LOG_DEBUG_DEV('_skipResponse', resultID, errorCode)


class HistoricalBattles(object):

    def __init__(self, syncData):
        self.__account = None
        self.__syncData = syncData
        self.__cache = {}
        self.__ignore = True
        self.onHBDataChanged = Event()
        return

    def onAccountBecomePlayer(self):
        self.__ignore = False

    def onAccountBecomeNonPlayer(self):
        self.__ignore = True

    def setAccount(self, account):
        self.__account = account

    def synchronize(self, isFullSync, diff):
        dataChanged = False
        dataResetKey = (PDATA_KEY_HISTORICAL_BATTLES, '_r')
        if dataResetKey in diff:
            self.__cache[PDATA_KEY_HISTORICAL_BATTLES] = diff[dataResetKey]
            dataChanged = True
        if PDATA_KEY_HISTORICAL_BATTLES in diff:
            synchronizeDicts(diff[PDATA_KEY_HISTORICAL_BATTLES], self.__cache.setdefault(PDATA_KEY_HISTORICAL_BATTLES, {}))
            dataChanged = True
        if not isFullSync and dataChanged:
            self.onHBDataChanged()

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
                callback(resultID, self.__cache[PDATA_KEY_HISTORICAL_BATTLES].get(itemName, None))
            return
