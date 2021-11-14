# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/gift_system.py
import logging
import typing
from functools import partial
import AccountCommands
from gui.gift_system.wrappers import GiftsHistoryData
from shared_utils import makeTupleByDict
from shared_utils.account_helpers.diff_utils import synchronizeDicts
_logger = logging.getLogger(__name__)
_CACHE_DIFF_KEY = 'cache'
_GIFT_SYSTEM_KEY = 'giftsData'

def _packEventHistoryData(eventExt):
    return makeTupleByDict(GiftsHistoryData, {'aggregated': eventExt,
     'detailed': []})


class _RequestHistoryProxy(object):

    def __init__(self, reqEventIds, callback):
        self.__reqEventIds = reqEventIds
        self.__callback = callback

    def __call__(self, requestID, resultID, errorStr, ext=None):
        ext = ext if ext is not None else {}
        for eventID in self.__reqEventIds:
            ext[eventID] = _packEventHistoryData(ext[eventID]) if eventID in ext else None

        self.__callback((resultID >= AccountCommands.RES_SUCCESS, ext))
        return


class GiftSystem(object):

    def __init__(self, syncData, commandsProxy):
        self.__cache = {}
        self.__ignore = True
        self.__syncData = syncData
        self.__commandsProxy = commandsProxy

    def onAccountBecomePlayer(self):
        self.__ignore = False

    def onAccountBecomeNonPlayer(self):
        self.__ignore = True

    def getCache(self, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, None)
            return
        else:
            self.__syncData.waitForSync(partial(self.__onGetCacheResponse, callback))
            return

    def requestGiftsHistory(self, reqEventIds, callback):
        proxy = _RequestHistoryProxy(reqEventIds, callback)
        self.__commandsProxy.perform(AccountCommands.CMD_SYNC_GIFTS, reqEventIds, proxy)

    def synchronize(self, isFullSync, diff):
        _logger.debug('Synchronize gift system')
        if isFullSync and self.__cache:
            self.__cache.clear()
        if _CACHE_DIFF_KEY in diff and _GIFT_SYSTEM_KEY in diff[_CACHE_DIFF_KEY]:
            synchronizeDicts(diff[_CACHE_DIFF_KEY][_GIFT_SYSTEM_KEY], self.__cache)
        _logger.debug('Gift system info: %s', self.__cache)

    def __onGetCacheResponse(self, callback, resultID):
        if resultID < 0:
            if callback is not None:
                callback(resultID, None)
            return
        else:
            if callback is not None:
                callback(resultID, self.__cache)
            return
