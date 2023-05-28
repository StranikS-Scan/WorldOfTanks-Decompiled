# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/referral_program.py
from functools import partial
import typing
import AccountCommands
from shared_utils.account_helpers.diff_utils import synchronizeDicts
if typing.TYPE_CHECKING:
    from typing import Callable, Dict, Optional
RP_PDATA_KEY = 'refProgram'

class ReferralProgram(object):

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
        if RP_PDATA_KEY in diff:
            synchronizeDicts(diff[RP_PDATA_KEY], self.__cache.setdefault(RP_PDATA_KEY, {}))

    def __onGetCacheResponse(self, callback, resultID):
        if resultID < 0:
            if callback is not None:
                callback(resultID, None)
            return
        else:
            if callback is not None:
                callback(resultID, self.__cache)
            return

    def collectRPPgbPoints(self, callback):
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr, ext={}: callback(requestID, resultID, errorStr)
        else:
            proxy = None
        self.__account._doCmdInt(AccountCommands.CMD_COLLECT_RP_PGB_POINTS, 0, proxy)
        return

    def incrementRecruitDelta(self, deltaInc, callback):
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr, ext={}: callback(requestID, resultID, errorStr)
        else:
            proxy = None
        self.__account._doCmdInt(AccountCommands.CMD_RP_INCREMENT_RECRUIT_DELTA, deltaInc, proxy)
        return

    def resetRecruitDelta(self, callback):
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr, ext={}: callback(requestID, resultID, errorStr)
        else:
            proxy = None
        self.__account._doCmdInt(AccountCommands.CMD_RP_RESET_RECRUIT_DELTA, 0, proxy)
        return
