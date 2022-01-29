# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/lunar_ny/lunar_ny_account_helper.py
import logging
from functools import partial
import typing
import AccountCommands
from shared_utils.account_helpers.diff_utils import synchronizeDicts
from lunar_ny_common import settings_constants as const
if typing.TYPE_CHECKING:
    from typing import Callable
    from account_helpers.AccountSyncData import AccountSyncData
    from Account import _ClientCommandProxy
_logger = logging.getLogger(__name__)

class LunarNYAccountHelper(object):
    __slots__ = ('__syncData', '__commandProxy', '__cache', '__ignore')

    def __init__(self, syncData, commandProxy):
        self.__syncData = syncData
        self.__commandProxy = commandProxy
        self.__cache = {}
        self.__ignore = True

    def fillAlbumSlot(self, slotID, charmID, callback=None):
        if callback is None:
            callback = self.__stubOnResponse
        self.__commandProxy.perform(AccountCommands.CMD_LUNAR_NY_FILL_ALBUM_SLOT, slotID, charmID, callback)
        return

    def markSeenAllNewCharms(self, charmIDs, callback=None):
        if callback is None:
            callback = self.__stubOnResponse
        self.__commandProxy.perform(AccountCommands.CMD_LUNAR_NY_SEEN_ALL_CHARM, charmIDs, callback)
        return

    def onAccountBecomePlayer(self):
        self.__ignore = False

    def onAccountBecomeNonPlayer(self):
        self.__ignore = True

    def synchronize(self, isFullSync, diff):
        if isFullSync:
            self.__cache.clear()
        dataResetKey = (const.LUNAR_NY_PDATA_KEY, '_r')
        if dataResetKey in diff:
            itemDiff = diff[dataResetKey]
            synchronizeDicts(itemDiff, self.__cache)
        if const.LUNAR_NY_PDATA_KEY in diff:
            itemDiff = diff[const.LUNAR_NY_PDATA_KEY]
            synchronizeDicts(itemDiff, self.__cache)

    def getCache(self, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, None)
            return
        else:
            self.__syncData.waitForSync(partial(self.__onGetCacheResponse, callback))
            return

    def isSynchronized(self):
        return bool(self.__cache)

    def __onGetCacheResponse(self, callback, resultID):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, None)
            return
        elif resultID < 0:
            if callback is not None:
                callback(resultID, None)
            return
        else:
            if callback is not None:
                callback(resultID, self.__cache)
            return

    def __stubOnResponse(self, resultID, requestID, errorStr, errorMsg=None):
        if not AccountCommands.isCodeValid(requestID):
            _logger.error((errorStr, errorMsg))
