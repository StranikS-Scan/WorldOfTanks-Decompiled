# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/comp7_storage.py
from functools import partial
import typing
import AccountCommands
from shared_utils.account_helpers.diff_utils import synchronizeDicts
if typing.TYPE_CHECKING:
    from typing import Callable, Dict, Optional

class Comp7Storage(object):
    PDATA_KEY = 'comp7'
    SKILL_KEY = 'selectedComp7Skill'
    BALANCE_VERSION_KEY = 'balanceVersion'

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

    def clear(self):
        if self.__cache:
            self.__cache.clear()

    def synchronize(self, isFullSync, diff):
        if isFullSync and self.__cache:
            self.__cache.clear()
        if self.PDATA_KEY in diff:
            newBalanceVersion = diff[self.PDATA_KEY].get(self.SKILL_KEY, {}).get(self.BALANCE_VERSION_KEY, 0)
            if self.__cache and newBalanceVersion > 0:
                prevBalanceVersion = self.__cache.get(self.SKILL_KEY, {}).get(self.BALANCE_VERSION_KEY, 0)
                if prevBalanceVersion != newBalanceVersion:
                    self.__cache.clear()
            synchronizeDicts(diff[self.PDATA_KEY].get(self.SKILL_KEY, {}), self.__cache.setdefault(self.SKILL_KEY, {}))

    def getVehicleSkill(self, vehInvID):
        return self.__cache.get(self.SKILL_KEY, {}).get(vehInvID, 0)

    def __onGetCacheResponse(self, callback, resultID):
        if resultID < 0:
            if callback is not None:
                callback(resultID, None)
            return
        else:
            if callback is not None:
                callback(resultID, self.__cache)
            return
