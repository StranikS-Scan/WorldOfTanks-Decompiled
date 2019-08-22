# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/ClientBattleRoyale.py
from functools import partial
import AccountCommands
from shared_utils.account_helpers.diff_utils import synchronizeDicts
from debug_utils import LOG_DEBUG_DEV
from helpers import time_utils
import season_common

def _skipResponse(resultID, errorCode):
    LOG_DEBUG_DEV('_skipResponse', resultID, errorCode)


class ClientBattleRoyale(object):

    def __init__(self, syncData):
        self.__account = None
        self.__syncData = syncData
        self.__cache = {}
        self.__ignore = True
        return

    def changeBRPoints(self, points, callback=_skipResponse):
        self.__account._doCmdInt3(AccountCommands.CMD_CHANGE_BR_POINTS, points, True, 0, lambda requestID, resultID, errorCode: callback(resultID, errorCode))

    def isEnabled(self):
        battleRoyaleConfig = self.__account.serverSettings['battle_royale_config']
        return battleRoyaleConfig is not None and battleRoyaleConfig.get('isEnabled', False)

    def getSeason(self):
        battleRoyaleConfig = self.__account.serverSettings['battle_royale_config']
        return season_common.getSeason(battleRoyaleConfig, time_utils.getCurrentLocalServerTimestamp())

    def getConfigs(self):
        battleRoyaleConfig = self.__account.serverSettings['battle_royale_config']
        cycleConfig = season_common.getActiveCycleConfig(battleRoyaleConfig, time_utils.getCurrentLocalServerTimestamp())
        return (battleRoyaleConfig, cycleConfig)

    def onAccountBecomePlayer(self):
        self.__ignore = False

    def onAccountBecomeNonPlayer(self):
        self.__ignore = True

    def setAccount(self, account):
        self.__account = account

    def synchronize(self, isFullSync, diff):
        for item in ('battleRoyale',):
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
                callback(resultID, self.__cache['battleRoyale'].get(itemName, None))
            return
