# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/tokens.py
from functools import partial
import AccountCommands
from shared_utils.account_helpers.diff_utils import synchronizeDicts

class Tokens(object):

    def __init__(self, syncData, commandProxy):
        self.__syncData = syncData
        self.__commandProxy = commandProxy
        self.__cache = {}
        self.__ignore = True

    def onAccountBecomePlayer(self):
        self.__ignore = False

    def onAccountBecomeNonPlayer(self):
        self.__ignore = True

    def synchronize(self, isFullSync, diff):
        if isFullSync:
            self.__cache.clear()
        for item in ('tokens', 'lootBoxes'):
            itemDiff = diff.get(item, None)
            if itemDiff is not None:
                synchronizeDicts(itemDiff, self.__cache.setdefault(item, {}))

        return

    def getCache(self, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, None)
        else:
            self.__syncData.waitForSync(partial(self.__onGetCacheResponse, callback))
        return

    def openLootBox(self, boxID, count, callback):
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr, ext=None: callback(resultID, errorStr, ext)
        else:
            proxy = None
        self.__commandProxy.perform(AccountCommands.CMD_LOOTBOX_OPEN, boxID, count, proxy)
        return

    def openLootBoxBySender(self, boxID, count, senderID, callback):
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr, ext=None: callback(resultID, errorStr, ext)
        else:
            proxy = None
        self.__commandProxy.perform(AccountCommands.CMD_LOOTBOX_OPEN_BY_SENDER, boxID, count, senderID, proxy)
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

    def getToken(self, tokenID):
        return self.__cache['tokens'].get(tokenID, None) if self.__cache and 'tokens' in self.__cache else None
