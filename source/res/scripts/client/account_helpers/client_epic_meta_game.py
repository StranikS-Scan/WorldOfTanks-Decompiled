# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/client_epic_meta_game.py
from functools import partial
import AccountCommands
from debug_utils import LOG_DEBUG_DEV
from shared_utils.account_helpers.diff_utils import synchronizeDicts

def _skipResponse(resultID, errorCode):
    LOG_DEBUG_DEV('_skipResponse', resultID, errorCode)


class ClientEpicMetaGame(object):
    __DATA_KEY = 'epicMetaGame'

    def __init__(self, syncData):
        self.__account = None
        self.__syncData = syncData
        self.__cache = {}
        self.__ignore = True
        return

    def setSelectedAbilities(self, listOfAbilities, vehicleCD, callback=_skipResponse):
        self.__account._doCmdIntArr(AccountCommands.CMD_UPDATE_SELECTED_EPIC_META_ABILITY, listOfAbilities + [vehicleCD], lambda requestID, resultID, errorCode: callback(resultID, errorCode))

    def setSelectedAbilitiesVehsClass(self, listOfAbilities, vehicleCD, callback=_skipResponse):
        self.__account._doCmdIntArr(AccountCommands.CMD_UPDATE_SELECTED_EPIC_META_ABILITY_VEHICLES, listOfAbilities + [vehicleCD], lambda requestID, resultID, errorCode: callback(resultID, errorCode))

    def increaseAbility(self, abilityID, callback=_skipResponse):
        self.__account._doCmdInt(AccountCommands.CMD_INCREASE_EPIC_META_ABILITY, abilityID, lambda requestID, resultID, errorCode: callback(resultID, errorCode))

    def resetEpicMetaGame(self, metaLevel=0, abilityPoints=0, callback=_skipResponse):
        self.__account._doCmdInt2(AccountCommands.CMD_RESET_EPIC_META_GAME, metaLevel, abilityPoints, lambda requestID, resultID, errorCode: callback(resultID, errorCode))

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
