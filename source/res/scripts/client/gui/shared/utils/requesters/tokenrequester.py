# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/TokenRequester.py
import logging
import time
import cPickle
from functools import partial
import BigWorld
from adisp import adisp_async, adisp_process
from constants import REQUEST_COOLDOWN, TOKEN_TYPE
from debug_utils import LOG_CURRENT_EXCEPTION
from TokenResponse import TokenResponse
from ids_generators import SequenceIDGenerator
from helpers import isPlayerAccount
_logger = logging.getLogger(__name__)

def _getAccountRepository():
    import Account
    return Account.g_accountRepository


_tokenRqs = {}

def getTokenRequester(tokenType):
    global _tokenRqs
    if tokenType not in _tokenRqs:
        _tokenRqs[tokenType] = TokenRequester(tokenType, cache=False)
    return _tokenRqs[tokenType]


def fini():
    for requester in _tokenRqs.itervalues():
        requester.clear()

    _tokenRqs.clear()


class TokenRequester(object):
    __idsGen = SequenceIDGenerator()

    def __init__(self, tokenType, wrapper=TokenResponse, cache=True):
        super(TokenRequester, self).__init__()
        if callable(wrapper):
            self.__wrapper = wrapper
        else:
            raise ValueError('Wrapper is invalid: {0}'.format(wrapper))
        self.__tokenType = tokenType
        self.__callback = None
        self.__lastResponse = None
        self.__requestID = 0
        self.__cache = cache
        self.__timeoutCbID = None
        self.__lastRequestTime = 0
        return

    def lastResponseDelta(self):
        return time.time() - self.__lastRequestTime

    def isInProcess(self):
        return self.__callback is not None

    def clear(self):
        self.__callback = None
        repository = _getAccountRepository()
        if repository:
            repository.onTokenReceived -= self._onTokenReceived
        self.__lastResponse = None
        self.__requestID = 0
        self.__clearTimeoutCb()
        return

    def getReqCoolDown(self):
        return getattr(REQUEST_COOLDOWN, TOKEN_TYPE.COOLDOWNS[self.__tokenType], 10.0)

    def canAllowRequest(self):
        return self.__tokenType != TOKEN_TYPE.WGNI if not isPlayerAccount() else True

    @adisp_async
    @adisp_process
    def request(self, timeout=None, callback=None, allowDelay=False):

        @adisp_async
        def wait(t, callback):
            BigWorld.callback(t, lambda : callback(None))

        yield lambda callback: callback(True)
        requester = self._getRequester()
        if not requester or not callable(requester):
            if callback:
                callback(None)
            return
        elif self.__cache and self.__lastResponse and self.__lastResponse.isValid():
            if callback:
                callback(self.__lastResponse)
            return
        else:
            delta = self.lastResponseDelta()
            if allowDelay and delta < self.getReqCoolDown():
                yield wait(self.getReqCoolDown() - delta)
            if requester != self._getRequester():
                _logger.warning('Request cancelled because requester has been changed')
                if callback:
                    callback(None)
                return
            self.__callback = callback
            self.__requestID = self.__idsGen.next()
            if timeout:
                self.__loadTimeout(self.__requestID, self.__tokenType, max(timeout, 0.0))
            repository = _getAccountRepository()
            if repository and self.canAllowRequest():
                repository.onTokenReceived += self._onTokenReceived
                requester(self.__requestID, self.__tokenType)
            elif self.__callback:
                self.__callback(None)
            return

    def _getRequester(self):
        return getattr(BigWorld.player(), 'requestToken', None)

    def _onTokenReceived(self, requestID, tokenType, data):
        if self.__requestID != requestID or tokenType != self.__tokenType:
            return
        else:
            repository = _getAccountRepository()
            if repository:
                repository.onTokenReceived -= self._onTokenReceived
            try:
                self.__lastResponse = self.__wrapper(**cPickle.loads(data))
            except TypeError:
                LOG_CURRENT_EXCEPTION()

            self.__requestID = 0
            if self.__callback is not None:
                callback = self.__callback
                self.__callback = None
                callback(self.__lastResponse)
            self.__lastRequestTime = time.time()
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
        self._onTokenReceived(requestID, tokenType, cPickle.dumps({'error': 'TIMEOUT'}, -1))
