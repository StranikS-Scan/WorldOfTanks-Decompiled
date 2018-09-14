# Embedded file name: scripts/client/gui/shared/utils/requesters/TokenRequester.py
import cPickle
from functools import partial
import BigWorld
from adisp import async
from constants import REQUEST_COOLDOWN, TOKEN_TYPE
from debug_utils import LOG_CURRENT_EXCEPTION
from TokenResponse import TokenResponse
from ids_generators import SequenceIDGenerator

def _getAccountRepository():
    import Account
    return Account.g_accountRepository


class TokenRequester(object):
    __idsGen = SequenceIDGenerator()

    def __init__(self, tokenType, wrapper = TokenResponse, cache = True):
        super(TokenRequester, self).__init__()
        if callable(wrapper):
            self.__wrapper = wrapper
        else:
            raise ValueError, 'Wrapper is invalid: {0}'.format(wrapper)
        self.__tokenType = tokenType
        self.__callback = None
        self.__lastResponse = None
        self.__requestID = 0
        self.__cache = cache
        self.__timeoutCbID = None
        return

    def isInProcess(self):
        return self.__callback is not None

    def clear(self):
        self.__callback = None
        repository = _getAccountRepository()
        if repository:
            repository.onTokenReceived -= self.__onTokenReceived
        self.__lastResponse = None
        self.__requestID = 0
        self.__clearTimeoutCb()
        return

    def getReqCoolDown(self):
        return getattr(REQUEST_COOLDOWN, TOKEN_TYPE.COOLDOWNS[self.__tokenType], 10.0)

    @async
    def request(self, timeout = None, callback = None):
        requester = getattr(BigWorld.player(), 'requestToken', None)
        if not requester or not callable(requester):
            if callback:
                callback(None)
            return
        elif self.__cache and self.__lastResponse and self.__lastResponse.isValid():
            if callback:
                callback(self.__lastResponse)
            return
        else:
            self.__callback = callback
            self.__requestID = self.__idsGen.next()
            if timeout:
                self.__loadTimeout(self.__requestID, self.__tokenType, max(timeout, 0.0))
            repository = _getAccountRepository()
            if repository:
                repository.onTokenReceived += self.__onTokenReceived
            requester(self.__requestID, self.__tokenType)
            return

    def __onTokenReceived(self, requestID, tokenType, data):
        if self.__requestID != requestID or tokenType != self.__tokenType:
            return
        else:
            repository = _getAccountRepository()
            if repository:
                repository.onTokenReceived -= self.__onTokenReceived
            try:
                self.__lastResponse = self.__wrapper(**cPickle.loads(data))
            except TypeError:
                LOG_CURRENT_EXCEPTION()

            self.__requestID = 0
            if self.__callback is not None:
                self.__callback(self.__lastResponse)
                self.__callback = None
            return

    def __clearTimeoutCb(self):
        if self.__timeoutCbID is not None:
            BigWorld.cancelCallback(self.__timeoutCbID)
            self.__timeoutCbID = None
        return

    def __loadTimeout(self, requestID, tokenType, timeout):
        self.__clearTimeoutCb()
        self.__timeoutCbID = BigWorld.callback(timeout, partial(self.__onTimeout, requestID, tokenType))

    def __onTimeout(self, requestID, tokenType):
        self.__clearTimeoutCb()
        self.__onTokenReceived(requestID, tokenType, cPickle.dumps({'error': 'TIMEOUT'}, -1))
