# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/battle_pass.py
import logging
from functools import partial
import AccountCommands
import BigWorld
from shared_utils.account_helpers.diff_utils import synchronizeDicts
_logger = logging.getLogger()

def selectProgressionStyle(styleID, callback):
    BigWorld.player()._doCmdInt(AccountCommands.CMD_ADD_BATTLE_PASS_PROGRESSION_STYLE, styleID, callback)


class BattlePassManager(object):
    __DATA_KEY = 'battlePass'

    def __init__(self, syncData, clientCommandsProxy):
        self.__syncData = syncData
        self.__cache = {}
        self.__ignore = True
        self.__commandsProxy = clientCommandsProxy

    def onAccountBecomePlayer(self):
        self.__ignore = False

    def onAccountBecomeNonPlayer(self):
        self.__ignore = True

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

    def __onGetCacheResponse(self, callback, resultID):
        if resultID < 0:
            if callback is not None:
                callback(resultID, None)
            return
        else:
            if callback is not None:
                callback(resultID, self.__cache)
            return
