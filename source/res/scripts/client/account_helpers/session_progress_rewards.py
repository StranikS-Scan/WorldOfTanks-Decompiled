# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/session_progress_rewards.py
import AccountCommands
import typing
from functools import partial
from session_progress_rewards_common import SESSION_PROGRESS_REWARDS_PDATA_KEY
from shared_utils.account_helpers.diff_utils import synchronizeDicts
if typing.TYPE_CHECKING:
    from typing import Callable, Dict, Optional

class SessionProgressRewards(object):

    def __init__(self, syncData):
        self.__cache = {}
        self.__ignore = True
        self.__syncData = syncData

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
        if SESSION_PROGRESS_REWARDS_PDATA_KEY in diff:
            synchronizeDicts(diff[SESSION_PROGRESS_REWARDS_PDATA_KEY], self.__cache.setdefault(SESSION_PROGRESS_REWARDS_PDATA_KEY, {}))

    def __onGetCacheResponse(self, callback, resultID):
        if resultID < 0:
            if callback is not None:
                callback(resultID, None)
            return
        else:
            if callback is not None:
                callback(resultID, self.__cache)
            return
