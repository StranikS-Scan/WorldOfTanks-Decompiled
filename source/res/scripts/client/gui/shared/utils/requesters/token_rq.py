# Embedded file name: scripts/client/gui/shared/utils/requesters/token_rq.py
import cPickle
import Account
import BigWorld
from adisp import async
from constants import REQUEST_COOLDOWN, TOKEN_TYPE
from debug_utils import LOG_CURRENT_EXCEPTION
from ids_generators import SequenceIDGenerator
TOKEN_EXPIRED_TIME = 3000

class TokenResponse(object):
    __slots__ = ('_receivedAt', '_token', '_databaseID', '_error')

    def __init__(self, token = None, databaseID = 0L, error = None, **kwargs):
        super(TokenResponse, self).__init__()
        self._receivedAt = BigWorld.time()
        self._token = token
        self._databaseID = databaseID
        self._error = error

    def __repr__(self):
        return '{0}(receivedAt={1}, databaseID={2}, error={3})'.format(self.__class__.__name__, self._receivedAt, self._databaseID, self._error)

    def clear(self):
        self._receivedAt = 0
        self._token = None
        self._databaseID = 0L
        self._error = None
        return

    def isValid(self):
        return self._token and not self._error and BigWorld.time() < self._receivedAt + TOKEN_EXPIRED_TIME

    def getDatabaseID(self):
        return self._databaseID

    def getToken(self):
        return self._token

    def hasError(self):
        return self._error is not None

    def getError(self):
        return self._error


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
        self.__callback = callback
        if self.__cache and self.__lastResponse and self.__lastResponse.isValid():
            if callback:
                callback(self.__lastResponse)
            return
        self.__requestID = self.__idsGen.next()
        repository = Account.g_accountRepository
        if repository:
            repository.onTokenReceived += self.__onTokenReceived
        BigWorld.player().requestToken(self.__requestID, self.__tokenType)

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
