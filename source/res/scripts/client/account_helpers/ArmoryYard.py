# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/ArmoryYard.py
from functools import partial
import AccountCommands
from shared_utils.account_helpers.diff_utils import synchronizeDicts
from debug_utils import LOG_DEBUG_DEV

def _skipResponse(resultID, errorCode):
    LOG_DEBUG_DEV('_skipResponse', resultID, errorCode)


class ArmoryYard(object):

    def __init__(self, syncData):
        self.__account = None
        self.__syncData = syncData
        self.__cache = {}
        self.__ignore = True
        return

    def onAccountBecomePlayer(self):
        self.__ignore = False

    def onAccountBecomeNonPlayer(self):
        self.__ignore = True

    def setAccount(self, account):
        self.__account = account

    def synchronize(self, isFullSync, diff):
        from armory_yard_constants import PDATA_KEY_ARMORY_YARD
        from armory_yard_constants import CURRENT_REROLL_PDATA_KEY, QUEST_CONDITION_OVERRIDE_PDATA_KEY
        dataResetKey = (PDATA_KEY_ARMORY_YARD, '_r')
        if dataResetKey in diff:
            self.__cache[PDATA_KEY_ARMORY_YARD] = diff[dataResetKey]
        if PDATA_KEY_ARMORY_YARD in diff:
            armoryDiff = diff[PDATA_KEY_ARMORY_YARD]
            synchronizeDicts(armoryDiff, self.__cache.setdefault(PDATA_KEY_ARMORY_YARD, {}))
            for specialDictKey in (CURRENT_REROLL_PDATA_KEY, QUEST_CONDITION_OVERRIDE_PDATA_KEY):
                if specialDictKey in armoryDiff and not armoryDiff[specialDictKey]:
                    self.__cache[PDATA_KEY_ARMORY_YARD][specialDictKey] = {}

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
                callback(resultID, self.__cache['armoryYard'].get(itemName, None))
            return
