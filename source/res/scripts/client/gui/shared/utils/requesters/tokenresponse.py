# Embedded file name: scripts/client/gui/shared/utils/requesters/TokenResponse.py
import BigWorld
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
