# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/tokens.py
from __future__ import absolute_import
from functools import partial
import AccountCommands
from shared_utils.account_helpers.diff_utils import synchronizeDicts
from debug_utils import deprecated

def _getProxy(callback):
    return (lambda requestID, resultID, errorStr, ext=None: callback(resultID, errorStr, ext if ext is not None else {})) if callback is not None else None


class Tokens(object):

    def __init__(self, syncData, commandProxy):
        self.__account = None
        self.__syncData = syncData
        self.__commandProxy = commandProxy
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
        if isFullSync:
            self.__cache.clear()
        for item in ('tokens', 'lootBoxes'):
            itemDiff = diff.get(item, None)
            if itemDiff is not None:
                synchronizeDicts(itemDiff, self.__cache.setdefault(item, {}))

        return

    def getCache(self, callback=None):
        self.__syncData.waitForSync(partial(self.__onGetCacheResponse, callback))

    def openLootBox(self, boxID, count, callback):
        self.__account._doCmdInt2(AccountCommands.CMD_LOOTBOX_OPEN, boxID, count, _getProxy(callback))

    @deprecated
    def getInfoLootBox(self, boxIDs, callback):
        self.__account._doCmdIntArr(AccountCommands.CMD_LOOTBOX_GETINFO, boxIDs, _getProxy(callback))

    def resetLootBoxStatistics(self, boxIDs, callback):
        self.__account._doCmdIntArr(AccountCommands.CMD_LOOTBOX_RESET_STATS, boxIDs, _getProxy(callback))

    def rerollBox(self, boxID, callback):
        self.__commandProxy.perform(AccountCommands.CMD_LOOTBOX_REROLL, boxID, _getProxy(callback))

    def acceptBoxRerollRewards(self, boxID, callback):
        self.__commandProxy.perform(AccountCommands.CMD_LOOTBOX_ACCEPT_REWARD, boxID, _getProxy(callback))

    def __onGetCacheResponse(self, callback, resultID):
        if resultID < 0:
            if callback is not None:
                callback(resultID, None)
            return
        else:
            if callback is not None:
                callback(resultID, self.__cache)
            return

    def getToken(self, tokenID):
        cache = self.__cache
        return cache['tokens'].get(tokenID) if cache and 'tokens' in cache else None
