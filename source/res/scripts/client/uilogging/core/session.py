# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/core/session.py
import typing
import adisp
import wg_async
from BWUtil import AsyncReturn
from gui.wgcg.uilogging.contexts import UILoggingSessionCtx
from helpers import dependency, time_utils
from helpers.log.adapters import getWithContext
from ids_generators import SequenceIDGenerator
from skeletons.gui.web import IWebController
from soft_exception import SoftException
from uilogging.constants import DEFAULT_LOGGER_NAME
from uilogging.core.core_constants import LOGS_MAX_COUNT_PER_SEND, LOG_RECORD_MAX_PROPERTIES_COUNT, MAX_SESSION_GET_RETRIES, MIN_SESSION_LIFE_TIME, REQUEST_SESSION_TIMEOUT, RETRY_REQUEST_SESSION_DELAY
if typing.TYPE_CHECKING:
    from gui.wgcg.requests import WgcgRequestResponse
    from uilogging.core.log import LogRecord

class WaitingSessionData(SoftException):
    pass


class SessionData(object):
    __slots__ = ('__id', '__auth', '__logging')

    def __init__(self, sessionID, data):
        self.__id = sessionID
        self.__auth = data.get('auth') or {}
        self.__logging = data.get('logging') or {}

    @property
    def id(self):
        return self.__id

    @property
    def token(self):
        return self.__auth.get('token')

    @property
    def expiration(self):
        return self.__auth.get('expiration')

    @property
    def lifetime(self):
        expiration = self.expiration
        return None if expiration is None else expiration - time_utils.getServerUTCTime()

    @property
    def isExpired(self):
        lifetime = self.lifetime
        return False if lifetime is None else lifetime <= 0

    @property
    def maxLogsCount(self):
        return min(self.__logging.get('max_logs_count', 0), LOGS_MAX_COUNT_PER_SEND)

    @property
    def maxLogPropertiesCount(self):
        return min(self.__logging.get('max_log_properties_count', 0), LOG_RECORD_MAX_PROPERTIES_COUNT)

    @property
    def isValid(self):
        isValid = bool(self.url) and self.maxLogsCount >= 1 and self.maxLogPropertiesCount >= 1
        if not self.isExpired and self.expiration is not None:
            isValid = isValid and self.expiration - time_utils.getServerUTCTime() >= MIN_SESSION_LIFE_TIME
        return isValid

    @property
    def url(self):
        return self.__logging.get('url', '')

    def verifyLog(self, log):
        return len(log) <= self.maxLogPropertiesCount

    def __repr__(self):
        return '<SessionData>(id={}, lifetime={})'.format(self.id, self.lifetime)


class Session(object):
    webController = dependency.descriptor(IWebController)

    def __init__(self):
        self._requesting = False
        self._destroyed = False
        self._sessionData = None
        self._initialized = False
        self._idGen = SequenceIDGenerator()
        self._logger = getWithContext(DEFAULT_LOGGER_NAME, self)
        return

    def get(self):
        return self._sessionData

    def remove(self, sessionID):
        session = self.get()
        if session and session.id == sessionID:
            self._clear()
            self._logger.debug('Session=%s removed.', sessionID)

    def update(self):
        if self._requesting:
            return True
        if not self._destroyed and not self._isInitialized:
            self._update()
            return True
        return False

    @wg_async.wg_async
    def request(self):
        if self._destroyed:
            self._logger.debug('Ui logging session destroyed.')
            raise AsyncReturn(None)
        if self._requesting:
            raise WaitingSessionData('Session data request in progress.')
        if self._isInitialized:
            self._logger.debug('Return cached session data.')
            raise AsyncReturn(self._sessionData)
        if not self.webController.isStarted:
            self._logger.debug('Web controller not ready yet.')
            raise AsyncReturn(None)
        self._clear()
        self._requesting = True
        retries = MAX_SESSION_GET_RETRIES
        try:
            while True:
                sessionData, retry = yield wg_async.await_callback(self._getSessionData, REQUEST_SESSION_TIMEOUT)()
                if not retry:
                    self._sessionData = sessionData
                    break
                retries -= 1
                if retries <= 0:
                    self._sessionData = None
                    break
                yield wg_async.delay(RETRY_REQUEST_SESSION_DELAY)
                if self._destroyed:
                    break

        except wg_async.TimeoutError:
            self._logger.warning('Request session timout reached.')
            self._sessionData = None
        except wg_async.BrokenPromiseError:
            self._logger.debug('Promise was destroyed while waiting for result.')
            self._sessionData = None
        except Exception:
            self._logger.exception('Failed to get session data.')
            self._sessionData = None

        self._initialized = True
        self._requesting = False
        self._logger.debug('Session data %s received and saved.', self._sessionData)
        raise AsyncReturn(self._sessionData)
        return

    def destroy(self):
        self._destroyed = True
        self._clear()
        self._logger.debug('Destroyed.')

    @wg_async.wg_async
    def _update(self):
        self._logger.debug('Updating.')
        try:
            yield self.request()
        except WaitingSessionData:
            self._logger.debug('Already waiting session.')
        except wg_async.BrokenPromiseError:
            self._logger.debug('Promise was destroyed while waiting for result.')

        raise AsyncReturn(None)
        return

    @property
    def _isInitialized(self):
        return self._initialized and (not self._sessionData or not self._sessionData.isExpired)

    def _clear(self):
        self._initialized = False
        self._sessionData = None
        return

    @adisp.adisp_process
    def _getSessionData(self, callback):
        self._logger.debug('Request session data.')
        response = yield self.webController.sendRequest(ctx=UILoggingSessionCtx())
        self._logger.debug('Session response: %s', response)
        sessionData, retry = None, False
        if not self._destroyed:
            if response.isSuccess():
                if isinstance(response.data, dict):
                    data = SessionData(self._idGen.next(), response.data)
                    if data.isValid:
                        sessionData, retry = data, data.isExpired
                    else:
                        self._logger.warning('Invalid session data.')
                else:
                    self._logger.warning('Unsupported session response data type.')
            else:
                retry = True
        self._logger.debug('Session data: %s, retry: %s.', sessionData, retry)
        callback((sessionData, retry))
        return
