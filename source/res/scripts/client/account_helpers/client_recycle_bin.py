# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/client_recycle_bin.py
from functools import partial
import AccountCommands
from shared_utils.account_helpers.diff_utils import synchronizeDicts

class ClientRecycleBin(object):

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
        if isFullSync:
            self.__cache.clear()
        recycleBinFull = diff.get(('recycleBin', '_r'), {})
        if recycleBinFull:
            self.__cache = dict(recycleBinFull)
        for item in ('recycleBin',):
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

    def getItems(self, itemsType, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, None)
            return
        else:
            self.__syncData.waitForSync(partial(self.__onGetItemsResponse, itemsType, callback))
            return

    def restoreTankman(self, tmanInvID, groupID, groupSize, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errStr='', ext=None: callback(resultID, errStr, ext)
            else:
                proxy = None
            arr = [tmanInvID, groupID, groupSize]
            self.__account._doCmdIntArr(AccountCommands.CMD_TMAN_RESTORE, arr, proxy)
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

    def __onGetItemsResponse(self, itemsType, callback, resultID):
        if resultID < 0:
            if callback is not None:
                callback(resultID, None)
            return
        else:
            if callback is not None:
                callback(resultID, self.__cache.get(itemsType, None))
            return
