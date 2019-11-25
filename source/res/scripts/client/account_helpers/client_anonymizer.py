# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/client_anonymizer.py
import logging
from functools import partial
import AccountCommands
from shared_utils.account_helpers.diff_utils import synchronizeDicts
_logger = logging.getLogger(__name__)
_ANONYMIZER_KEY = 'anonymizer'

def _printResponse(resultID, errorCode):
    _logger.debug('response: %s', (resultID, errorCode))


class ClientAnonymizer(object):

    def __init__(self, syncData):
        self.__syncData = syncData
        self.__account = None
        self.__cache = {}
        self.__ignore = True
        return

    def clear(self):
        if self.__cache:
            self.__cache.clear()

    def onAccountBecomePlayer(self):
        self.__ignore = False

    def onAccountBecomeNonPlayer(self):
        self.__ignore = True

    def setAccount(self, account):
        self.__account = account

    def setAnonymized(self, anonymized=True, callback=_printResponse):
        self.__account._doCmdIntArr(AccountCommands.CMD_SET_ANONYMIZER_STATE, [int(anonymized)], lambda requestID, resultID, errorCode: callback(resultID, errorCode))

    def synchronize(self, isFullSync, diff):
        _logger.debug('Synchronize Anonymizer')
        if isFullSync:
            self.clear()
        synchronizeDicts(diff.get(_ANONYMIZER_KEY, {}), self.__cache)
        _logger.debug('Anonymizer info: %s', self.__cache)

    def getCache(self, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, None)
            return
        else:
            self.__syncData.waitForSync(partial(self.__onGetCacheResponse, callback))
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
