# Embedded file name: scripts/client/gui/shared/utils/requesters/TokenRequester.py
import cPickle
import Account
import BigWorld
from adisp import async
from constants import REQUEST_COOLDOWN, TOKEN_TYPE
from debug_utils import LOG_CURRENT_EXCEPTION
from TokenResponse import TokenResponse
from ids_generators import SequenceIDGenerator

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
        return

    def clear(self):
        self.__callback = None
        repository = Account.g_accountRepository
        if repository:
            repository.onTokenReceived -= self.__onTokenReceived
        self.__lastResponse = None
        self.__requestID = 0
        return

    def getReqCoolDown(self):
        return getattr(REQUEST_COOLDOWN, TOKEN_TYPE.COOLDOWNS[self.__tokenType], 10.0)

    @async
    def request(self, callback = None):
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
            repository = Account.g_accountRepository
            if repository:
                repository.onTokenReceived += self.__onTokenReceived
            requester(self.__requestID, self.__tokenType)
            return

    def __onTokenReceived(self, requestID, tokenType, data):
        if self.__requestID != requestID or tokenType != self.__tokenType:
            return
        else:
            repository = Account.g_accountRepository
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
