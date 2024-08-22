# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/ClientBadges.py
import logging
from functools import partial
import AccountCommands
_logger = logging.getLogger(__name__)

def _skipResponse(resultID, errorCode):
    _logger.debug('_skipResponse: code=%r, error=%r', resultID, errorCode)


class ClientBadges(object):

    def __init__(self, syncData):
        self.__account = None
        self.__syncData = syncData
        self.__cache = {}
        self.__ignore = True
        return

    def selectBadges(self, badgeList, callback=_skipResponse):
        self.__account._doCmdIntArr(AccountCommands.CMD_SELECT_BADGES, badgeList, callback)

    def onAccountBecomePlayer(self):
        self.__ignore = False

    def onAccountBecomeNonPlayer(self):
        self.__ignore = True

    def setAccount(self, account):
        self.__account = account

    def synchronize(self, isFullSync, diff):
        for item in ('badges',):
            itemDiff = diff.get(item, None)
            if itemDiff is not None:
                self.__cache[item] = itemDiff

        return

    def getCache(self, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, None)
            return
        else:
            self.__syncData.waitForSync(partial(self.__onGetCacheResponse, callback))
            return

    def get(self, item, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, None)
            return
        else:
            self.__syncData.waitForSync(partial(self.__onGetResponse, item, callback))
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

    def __onGetResponse(self, item, callback, resultID):
        if resultID < 0:
            if callback is not None:
                callback(resultID, None)
            return
        else:
            if callback is not None:
                callback(resultID, self.__cache.get(item))
            return
