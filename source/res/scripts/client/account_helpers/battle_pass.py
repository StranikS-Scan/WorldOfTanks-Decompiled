# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/battle_pass.py
import inspect
import logging
from functools import partial, wraps
import AccountCommands
from battle_pass_common import BATTLE_PASS_PDATA_KEY
from shared_utils.account_helpers.diff_utils import synchronizeDicts
_logger = logging.getLogger()

def _handleNonPlayerIgnoreState(func):
    callbackNdx = inspect.getargspec(func).args.index('callback')

    @wraps(func)
    def wrapped(self, *args, **kwargs):
        if self._ignore:
            callback = kwargs.get('callback', args[callbackNdx] if callbackNdx < len(args) else None)
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, None)
            return
        else:
            func(self, *args, **kwargs)
            return

    return wrapped


class BattlePassManager(object):

    def __init__(self, syncData, clientCommandsProxy):
        self.__syncData = syncData
        self.__cache = {}
        self.__commandsProxy = clientCommandsProxy
        self._ignore = True

    def onAccountBecomePlayer(self):
        self._ignore = False

    def onAccountBecomeNonPlayer(self):
        self._ignore = True

    def synchronize(self, isFullSync, diff):
        if isFullSync:
            self.__cache.clear()
        dataResetKey = (BATTLE_PASS_PDATA_KEY, '_r')
        if dataResetKey in diff:
            self.__cache[BATTLE_PASS_PDATA_KEY] = diff[dataResetKey]
        if BATTLE_PASS_PDATA_KEY in diff:
            synchronizeDicts(diff[BATTLE_PASS_PDATA_KEY], self.__cache.setdefault(BATTLE_PASS_PDATA_KEY, {}))

    def getCache(self, callback=None):
        if self._ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, None)
            return
        else:
            self.__syncData.waitForSync(partial(self.__onGetCacheResponse, callback))
            return

    @_handleNonPlayerIgnoreState
    def activateChapter(self, chapterID, seasonID, callback=None):
        self.__commandsProxy.perform(AccountCommands.CMD_SET_BATTLE_PASS_CHAPTER, seasonID, chapterID, _makeProxy(callback))

    def __onGetCacheResponse(self, callback, resultID):
        if resultID < 0:
            if callback is not None:
                callback(resultID, None)
            return
        else:
            if callback is not None:
                callback(resultID, self.__cache)
            return


def _makeProxy(callback):
    return (lambda requestID, resultID, errorStr, ext={}: callback(resultID)) if callback is not None else None
