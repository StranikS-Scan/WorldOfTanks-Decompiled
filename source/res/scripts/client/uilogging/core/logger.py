# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/core/logger.py
import logging
import typing
import json
from functools import wraps
import BigWorld
import constants
from helpers import time_utils, dependency
from skeletons.connection_mgr import IConnectionManager
from skeletons.ui_logging import IUILoggingCore
from wotdecorators import noexcept, noexceptReturn
from uilogging.core.common import createFeatureKey, getPlayerID, getClientBuildVersion
from uilogging.core.settings import LoggingSettings, Settings
from uilogging.core.core_constants import HTTP_DEFAULT_HEADERS, HTTP_DEFAULT_TIMEOUT, LogLevels, SettingsStatuses
_logger = logging.getLogger(__name__)

def _ifNotReady(result=None):

    def inner(function):

        @wraps(function)
        def wrapper(self, *args, **kwargs):
            if not self.ready:
                _logger.warning('UI logging not ready yet.')
                return result
            return function(self, *args, **kwargs)

        return wrapper

    return inner


class LogRecord(object):
    __slots__ = ('feature', 'group', 'action', 'level', 'time', 'params')

    def __init__(self, feature, group, action, level, params):
        self.feature = str(feature)
        self.group = str(group)
        self.action = str(action)
        self.level = int(level)
        self.params = dict(params)
        _time = time_utils.getServerUTCTime()
        self.time = int(_time) if self.params.pop('__intTime__', False) else _time

    def __str__(self):
        return '<Log: {}, {}, {}, {}, {}>'.format(self.feature, self.group, self.action, self.level, self.time)

    def __repr__(self):
        return self.__str__()

    @property
    def broken(self):
        return False if self.feature and self.group and self.action else True


class _Queue(object):

    def __init__(self, limit):
        self._queue = {}
        self._limit = limit

    def add(self, log):
        key = createFeatureKey(log.feature, log.group)
        queue = self._queue.setdefault(key, [])
        if self._limit and len(queue) >= self._limit:
            _logger.error('Too much logs in queue: %s. New logs ignored.', key)
        else:
            queue.append(log)
            _logger.debug('Enqueue log: %s', log)

    def pop(self, key):
        return self._queue.pop(key, [])

    def clear(self):
        if self._queue:
            _logger.warning('Clear waiting logs: %s.', self._queue.keys())
            self._queue.clear()
        _logger.debug('Logs queue cleared.')


class _HTTPLogger(object):

    def __init__(self, url, clientLog=False):
        self._url = url
        self._clientLog = clientLog

    def send(self, log):
        data = self._createPostData(log)
        if not data:
            return
        self._fetchURL(data)
        if self._clientLog:
            _logger.info('Send to %s log data: %s.', self._url, data)

    def _fetchURL(self, data):
        BigWorld.fetchURL(url=self._url, callback=lambda x: x, headers=HTTP_DEFAULT_HEADERS, timeout=HTTP_DEFAULT_TIMEOUT, method='POST', postdata=json.dumps(data))

    @staticmethod
    def _createPostData(log):
        playerID = getPlayerID()
        if playerID is None:
            return
        else:
            data = {'account_id': playerID,
             'client_version': getClientBuildVersion(),
             'key': log.group,
             'loglevel': log.level,
             'time_spent': log.params.pop('timeSpent', 0),
             'action': log.action,
             'realm': constants.CURRENT_REALM,
             'feature': 'feature:{}'.format(log.feature),
             'time': log.time}
            duplicates = set(data) & set(log.params)
            if duplicates:
                _logger.error('Reserved keys: %s in additional log params.', duplicates)
                return
            data.update(log.params)
            return data


class UILoggingCore(IUILoggingCore):
    _connMgr = dependency.descriptor(IConnectionManager)

    def __init__(self):
        self._settings = LoggingSettings()
        self._queue = _Queue(limit=self._settings.logsQueueLimit)
        self._logger = _HTTPLogger(url=self._settings.url, clientLog=self._settings.clientLog)
        self._ready = False
        self._settingTtlTimerId = None
        return

    def init(self):
        self._connMgr.onConnected += self._start
        self._connMgr.onDisconnected += self._stop

    def fini(self):
        self._stop()
        self._connMgr.onConnected -= self._start
        self._connMgr.onDisconnected -= self._stop
        _logger.debug('UILoggingCore destroyed.')

    @noexceptReturn(Settings(SettingsStatuses.DISABLED))
    @_ifNotReady(Settings(SettingsStatuses.DISABLED))
    def getSettings(self, feature, group):
        _logger.debug('Get settings for: %s.', (feature, group))
        return self._settings.get(feature=feature, group=group)

    @noexcept
    @_ifNotReady()
    def log(self, feature, group, action, loglevel=LogLevels.INFO, **params):
        log = LogRecord(feature=feature, group=group, action=action, level=loglevel, params=params)
        _logger.debug('Trying to send log: %s.', log)
        if self._validate(log):
            self._logger.send(log)

    @property
    def ready(self):
        return self._ready

    def _start(self):
        self._settings.clear()
        self._settings.onChanged += self._onSettingsChanged
        self._startResetSettingsTimer()
        self._ready = True
        _logger.debug('UILoggingCore started.')

    def _stop(self):
        self._ready = False
        self._settings.onChanged -= self._onSettingsChanged
        self._queue.clear()
        self._settings.clear()
        self._stopResetSettingsTimer()
        _logger.debug('UILoggingCore stopped.')

    def _validate(self, log):
        if log.broken:
            _logger.warning('Broken log: %s', log)
            return False
        settings = self._settings.get(feature=log.feature, group=log.group)
        if settings.status == SettingsStatuses.DISABLED:
            _logger.debug('UI logging disabled for log: %s', log)
            return False
        if settings.status == SettingsStatuses.REQUESTED:
            self._queue.add(log)
            return False
        if settings.loglevel > log.level:
            _logger.debug('Skip log: %s by level: %s', log, settings.loglevel)
            return False
        return True

    def _onSettingsChanged(self, key, settings):
        _logger.debug('Settings for key: %s changed: %s', key, settings)
        if settings.status != SettingsStatuses.REQUESTED:
            logs = self._queue.pop(key)
            if settings.status == SettingsStatuses.ENABLED:
                for log in logs:
                    self._logger.send(log)

    @noexcept
    def _startResetSettingsTimer(self):
        self._stopResetSettingsTimer()
        self._settings.reset()
        if self._settings.ttl:
            self._settingTtlTimerId = BigWorld.callback(self._settings.ttl, self._startResetSettingsTimer)
        _logger.debug('UILoggingCore settings ttl: %s timer: %s.', self._settings.ttl, self._settingTtlTimerId)

    @noexcept
    def _stopResetSettingsTimer(self):
        if self._settingTtlTimerId is not None:
            BigWorld.cancelCallback(self._settingTtlTimerId)
            self._settingTtlTimerId = None
            _logger.debug('UILoggingCore settings ttl timer destroyed.')
        return
