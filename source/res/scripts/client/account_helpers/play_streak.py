# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/play_streak.py
from functools import partial
import typing
import AccountCommands
from shared_utils.account_helpers.diff_utils import synchronizeDicts
if typing.TYPE_CHECKING:
    from typing import Callable, Dict, Optional
PS_PDATA_KEY = 'playStreak'

class PlayStreak(object):

    def __init__(self, syncData):
        self.__account = None
        self.__cache = {}
        self.__ignore = True
        self.__syncData = syncData
        return

    def setAccount(self, account):
        self.__account = account

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

    def synchronize(self, isFullSync, diff):
        if isFullSync and self.__cache:
            self.__cache.clear()
        if PS_PDATA_KEY in diff:
            synchronizeDicts(diff[PS_PDATA_KEY], self.__cache.setdefault(PS_PDATA_KEY, {}))

    def __onGetCacheResponse(self, callback, resultID):
        if resultID < 0:
            if callback is not None:
                callback(resultID, None)
            return
        else:
            if callback is not None:
                callback(resultID, self.__cache)
            return
