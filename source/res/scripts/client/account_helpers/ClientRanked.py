# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/ClientRanked.py
from functools import partial
import AccountCommands
from shared_utils.account_helpers.diff_utils import synchronizeDicts
from debug_utils import LOG_DEBUG_DEV
import ranked_common

def _skipResponse(resultID, errorCode):
    LOG_DEBUG_DEV('_skipResponse', resultID, errorCode)


class ClientRanked(object):

    def __init__(self, syncData):
        self.__account = None
        self.__syncData = syncData
        self.__cache = {}
        self.__ignore = True
        return

    def setClientRank(self, clientRank, clientStep, callback=_skipResponse):
        self.__account._doCmdInt3(AccountCommands.CMD_SET_CLIENT_RANK, clientRank, clientStep, 0, lambda requestID, resultID, errorCode: callback(resultID, errorCode))

    def setClientMaxRank(self, clientRank, clientStep, callback=_skipResponse):
        self.__account._doCmdInt3(AccountCommands.CMD_SET_CLIENT_MAX_RANK, clientRank, clientStep, 0, lambda requestID, resultID, errorCode: callback(resultID, errorCode))

    def setClientVehRank(self, vehTypeCompDescr, clientRank, clientStep, callback=_skipResponse):
        self.__account._doCmdInt3(AccountCommands.CMD_SET_CLIENT_VEH_RANK, vehTypeCompDescr, clientRank, clientStep, lambda requestID, resultID, errorCode: callback(resultID, errorCode))

    def setClientShields(self, shieldsStatus, callback=_skipResponse):
        self.__account._doCmdIntArr(AccountCommands.CMD_SET_CLIENT_SHIELDS, shieldsStatus, lambda requestID, resultID, errorCode: callback(resultID, errorCode))

    def isEnabled(self):
        rankedConfig = self.__account.serverSettings['ranked_config']
        return rankedConfig is not None and rankedConfig.get('isEnabled', False)

    def getSeason(self):
        rankedConfig = self.__account.serverSettings['ranked_config']
        return ranked_common.getRankedSeason(rankedConfig)

    def getConfigs(self):
        rankedConfig = self.__account.serverSettings['ranked_config']
        cycleConfig = ranked_common.getCycleConfig(rankedConfig)
        return (rankedConfig, cycleConfig)

    def onAccountBecomePlayer(self):
        self.__ignore = False

    def onAccountBecomeNonPlayer(self):
        self.__ignore = True

    def setAccount(self, account):
        self.__account = account

    def synchronize(self, isFullSync, diff):
        for item in ('ranked',):
            itemDiff = diff.get(item, None)
            if itemDiff is not None:
                synchronizeDicts(itemDiff, self.__cache.setdefault(item, {}))

        return

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
                callback(resultID, self.__cache['ranked'].get(itemName, None))
            return
