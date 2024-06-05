# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/core/handler.py
import typing
import json
import zlib
import base64
import binascii
from functools import wraps, partial
import BigWorld
from Event import SafeEvent
from helpers import isPlayerAccount
from helpers.log.adapters import getWithContext
from shared_utils import safeCancelCallback
from uilogging.constants import DEFAULT_LOGGER_NAME, LogLevels
from uilogging.core.core_constants import LOGS_SEND_PERIOD, LOGS_FORCE_SEND_PERIOD, LOGS_MAX_QUEUE_SIZE, HTTP_DEFAULT_TIMEOUT, HTTP_OK_STATUS, HTTP_SESSION_EXPIRED, DEFAULT_COMPRESSION_LEVEL, FINAL_FLUSH_TIMEOUT, HttpHeaders
from uilogging.core.log import LogRecord
from uilogging.core.common import grouper
from uilogging.core.session import Session
if typing.TYPE_CHECKING:
    from uilogging.core.session import SessionData

def _ifDestroyed(result=None):

    def inner(function):

        @wraps(function)
        def wrapper(self, *args, **kwargs):
            if self.destroyed:
                self._logger.debug('Already destroyed. Skipping function call with result: %s.', result)
                return result
            return function(self, *args, **kwargs)

        return wrapper

    return inner


class Delayer(object):
    __slots__ = ('_callbackId', '_destroyed')

    def __init__(self, delay, func, *args, **kwargs):
        self._callbackId = BigWorld.callback(delay, partial(self._call, func, *args, **kwargs))
        self._destroyed = False

    def destroy(self):
        self._destroyed = True
        if self._callbackId is not None:
            safeCancelCallback(self._callbackId)
        self._callbackId = None
        return

    def _call(self, func, *args, **kwargs):
        self._callbackId = None
        delay = func(*args, **kwargs)
        if not self._destroyed and delay is not None and delay >= 0:
            self._callbackId = BigWorld.callback(delay, partial(self._call, func, *args, **kwargs))
        return


class FeatureSettings(object):
    __slots__ = ('feature', 'enabled', 'loglevel')

    def __init__(self, feature, enabled=True, params=None):
        self.feature = str(feature)
        self.enabled = enabled
        params = params or {}
        loglevel = params.get('loglevel')
        self.loglevel = loglevel if isinstance(loglevel, int) else LogLevels.NOTSET

    @property
    def params(self):
        return (self.feature, self.enabled, self.loglevel)

    def verifyLog(self, log):
        return False if log.feature != self.feature or not self.enabled or log.level < self.loglevel else True

    def __eq__(self, other):
        return self.params == other.params if isinstance(other, FeatureSettings) else False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return '<FeatureSettings: {}>'.format(self.params)

    def __repr__(self):
        return self.__str__()


class FeaturesSettings(object):

    def __init__(self):
        self._features = {}
        self._destroyed = False
        self._logger = getWithContext(DEFAULT_LOGGER_NAME, self)

    def update(self, rejected, accepted):
        for feature in set(accepted):
            _current = self._features.get(feature)
            if not _current:
                _new = FeatureSettings(feature, enabled=True, params=accepted[feature])
                self._features[feature] = _new
                self._logger.debug('Enabled %s.', _new)
            if _current.enabled:
                _new = FeatureSettings(feature, enabled=True, params=accepted[feature])
                if _current != _new:
                    self._features[feature] = _new
                    self._logger.debug('Changed %s.', _new)

        for feature in set(rejected):
            _settings = FeatureSettings(feature, enabled=False)
            self._features[feature] = _settings
            self._logger.debug('Rejected %s.', _settings)

    def verifyLog(self, log):
        settings = self._features.get(log.feature)
        return not settings or settings.verifyLog(log)

    def verifyFeature(self, feature):
        settings = self._features.get(feature)
        return not settings or settings.enabled

    def destroy(self):
        self._destroyed = True
        self._features.clear()
        self._logger.debug('Destroyed.')


class LogHandler(object):

    def __init__(self, playerID):
        self._destroyed = False
        self._playerID = playerID
        self._session = Session()
        self._features = FeaturesSettings()
        self._logs = []
        self._sender = None
        self._logsBatchWaitingTime = 0
        self.onDestroy = SafeEvent()
        self._logger = getWithContext(DEFAULT_LOGGER_NAME, self)
        return

    @property
    def destroyed(self):
        return self._destroyed

    @_ifDestroyed()
    def add(self, log):
        if len(self._logs) + 1 > LOGS_MAX_QUEUE_SIZE:
            self._logger.warning('Max logs queue size reached. Skipping [%s] log.', log.feature)
            return
        if not self._features.verifyLog(log):
            self._logger.debug('[%s] log skipped by features settings.', log.feature)
            return
        self._logs.append(log)
        self._logger.debug('[%s] log added. Logs count: %s.', log.feature, len(self._logs))
        if self._isPlayer:
            self._getSession()
            self._startSender()

    @_ifDestroyed()
    def logImmediately(self, log):
        session = self._getSession()
        if session is None:
            self._logger.warning('No session for immediate log.')
            return
        else:
            self._send(session, [log], wait=True)
            return

    @_ifDestroyed(False)
    def isFeatureEnabled(self, feature):
        return self._features.verifyFeature(feature)

    @_ifDestroyed(None)
    def getSessionLifetime(self):
        if not self._isPlayer:
            self._logger.debug('Getting session lifetime stopped. Player not account any more.')
            return None
        else:
            session = self._getSession()
            if session:
                return session.lifetime
            return None if self._destroyed else 0

    @_ifDestroyed(None)
    def startSender(self):
        self._startSender()

    def destroy(self, flush=False):
        self._logger.debug('Destroy in progress.')
        self._stopSender()
        self._logsBatchWaitingTime = 0
        self._destroyed = True
        session = self._session.get()
        if session and flush and self._logs:
            BigWorld.setFinalFlushURLRequestsTimeout(FINAL_FLUSH_TIMEOUT)
            for logs in grouper(self._logs, session.maxLogsCount):
                self._send(session, logs, wait=False)

        self._logs = []
        if self._session is not None:
            self._session.destroy()
            self._session = None
        if self._features is not None:
            self._features.destroy()
            self._features = None
        self.onDestroy()
        self.onDestroy.clear()
        self._logger.debug('Destroyed.')
        return

    @property
    def _isPlayer(self):
        return isPlayerAccount()

    def _getSession(self):
        return None if self._session.update() else self._session.get() or self.destroy()

    def _send(self, session, logs, wait=True):
        self._logger.debug('Sending %s logs from player=%s.', len(logs), self._playerID)
        logs = [ _log for _log in logs if session.verifyLog(_log) and self._features.verifyLog(_log) ]
        self._logger.debug('Filtered logs count: %s.', len(logs))
        if not logs:
            return
        else:
            try:
                jsonData = json.dumps([ _log.toDict() for _log in logs ])
                postData = base64.b64encode(zlib.compress(jsonData.encode('utf-8'), DEFAULT_COMPRESSION_LEVEL))
            except (binascii.Error,
             zlib.error,
             UnicodeError,
             TypeError,
             ValueError):
                self._logger.exception('Logs compression failed.')
                return

            headers = {HttpHeaders.CONTENT_TYPE.value: 'application/octet-stream',
             HttpHeaders.USER_ID.value: str(self._playerID)}
            if session.token is not None:
                headers[HttpHeaders.AUTH_TOKEN.value] = str(session.token)
            BigWorld.fetchURL(url=session.url, callback=partial(self._receive, session.id, logs) if wait else (lambda x: x), headers=headers, timeout=HTTP_DEFAULT_TIMEOUT, method='POST', postData=postData)
            return

    @_ifDestroyed()
    def _receive(self, sessionID, logs, response):
        self._logger.debug('Received response with code %s.', response.responseCode)
        if response.responseCode == HTTP_SESSION_EXPIRED:
            self._session.remove(sessionID)
            for log in logs:
                self.add(log)

            return
        elif response.responseCode != HTTP_OK_STATUS:
            self.destroy()
            return
        else:
            try:
                body = json.loads(response.body)
            except (TypeError, ValueError):
                body = {}

            rejected, accepted = body.get('rejected'), body.get('accepted')
            if rejected is None or accepted is None:
                self._logger.warning('Wrong response body structure.')
                self.destroy()
                return
            try:
                self._features.update(rejected, accepted)
            except Exception:
                self._logger.exception('Failed to update features.')
                self.destroy()

            return

    def _tryToSendBatch(self, incomplete=False):
        session, logsSent = self._getSession(), 0
        if session and self._logs and (incomplete or len(self._logs) >= session.maxLogsCount):
            logs = self._logs[:session.maxLogsCount]
            logsSent = len(logs)
            self._logs = self._logs[logsSent:]
            self._send(session, logs, wait=True)
        return logsSent > 0

    def _periodicSend(self):
        if self._destroyed or not self._logs or not self._isPlayer:
            self._stopSender()
            return None
        else:
            incomplete = self._logsBatchWaitingTime >= LOGS_FORCE_SEND_PERIOD
            if self._tryToSendBatch(incomplete=incomplete):
                self._logsBatchWaitingTime = 0
            else:
                self._logsBatchWaitingTime += LOGS_SEND_PERIOD
            return None if self._destroyed else LOGS_SEND_PERIOD

    def _startSender(self, *args, **kwargs):
        if self._sender is None and self._logs:
            self._sender = Delayer(LOGS_SEND_PERIOD, self._periodicSend)
            self._logger.debug('Sender started.')
        return

    def _stopSender(self):
        if self._sender is not None:
            self._sender.destroy()
            self._sender = None
            self._logger.debug('Sender stopped.')
        return
