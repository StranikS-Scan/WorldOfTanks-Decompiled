# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/client_blueprints.py
import logging
from functools import partial
import AccountCommands
from shared_utils.account_helpers.diff_utils import synchronizeDicts
_logger = logging.getLogger(__name__)
_BLUEPRINT_KEY = 'blueprints'

class ClientBlueprints(object):

    def __init__(self, syncData=None):
        self.__account = None
        self.__ignore = True
        self.__syncData = syncData
        self.__cache = {}
        return

    def clear(self):
        self.__account = None
        self.__ignore = True
        self.__syncData = None
        if self.__cache:
            self.__cache.clear()
        return

    def setAccount(self, account):
        self.__account = account

    def onAccountBecomePlayer(self):
        self.__ignore = False

    def onAccountBecomeNonPlayer(self):
        self.__ignore = True

    def synchronize(self, isFullSync, diff):
        _logger.debug('Synchronize information about account blueprints')
        if isFullSync:
            self.__cache.clear()
        if _BLUEPRINT_KEY in diff:
            synchronizeDicts(diff[_BLUEPRINT_KEY], self.__cache)
        _logger.debug('User blueprints: %s', self.__cache)

    def getCache(self, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, None)
            return
        else:
            self.__syncData.waitForSync(partial(self.__onGetCacheResponse, callback))
            return

    def get(self, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, None)
            return
        else:
            self.__syncData.waitForSync(partial(self.__onGetResponse, callback))
            return

    def convertBlueprintFragment(self, fragmentTypeCD, position, requestedCount, callback):
        _logger.debug('Account.convertBlueprintFragment: fragmentTypeCD=%s', fragmentTypeCD)
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr: callback(resultID)
        else:
            proxy = None
        self.__account._doCmdInt3(AccountCommands.CMD_BPF_CONVERT_FRAGMENTS, requestedCount, fragmentTypeCD, position, proxy)
        return

    def markFragmentsAsSeen(self, fragmentCDs, callback):
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr: callback(resultID)
        else:
            proxy = None
        self.__account._doCmdIntArr(AccountCommands.CMD_BPF_MARK_FRAGMENTS_SEEN, fragmentCDs, proxy)
        return

    def __onGetCacheResponse(self, callback, resultID):
        _logger.debug('Blueprint cache was got')
        if resultID < 0:
            if callback is not None:
                callback(resultID, None)
            return
        else:
            if callback is not None:
                callback(resultID, {'cache': self.__cache})
            return

    def __onGetResponse(self, callback, resultID):
        if resultID < 0:
            if callback is not None:
                callback(resultID, None)
            return
        else:
            if callback is not None:
                callback(resultID, self.__cache.get(_BLUEPRINT_KEY, None))
            return
