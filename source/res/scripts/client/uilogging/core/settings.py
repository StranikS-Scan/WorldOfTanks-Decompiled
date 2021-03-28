# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/core/settings.py
import logging
import typing
import json
from functools import partial
import BigWorld
import BattleReplay
from gui import GUI_SETTINGS
from Event import SafeEvent, EventManager
from wotdecorators import noexcept
from uilogging.core.common import createFeatureKey, getPlayerID
from uilogging.core.core_constants import SettingsStatuses, LogLevels, HTTP_OK_STATUS, HTTP_DEFAULT_TIMEOUT, HTTP_DEFAULT_HEADERS
_logger = logging.getLogger(__name__)

def _getGuiSettings():
    return GUI_SETTINGS.lookup('uiLogging') or {}


class LocalSettings(object):
    __slots__ = ('_settings', 'clientLog', 'logsQueueLimit', 'logUrl', 'settingsUrl', 'settingsTtl', 'enabled')

    def __init__(self):
        self._settings = _getGuiSettings()
        self.logUrl = self._settings.get('logUrl', '')
        self.settingsUrl = self._settings.get('settingsUrl', '')
        self.clientLog = self._settings.get('clientLog', False)
        self.logsQueueLimit = self._settings.get('logsQueueLimit', 0)
        self.settingsTtl = abs(self._settings.get('settingsTtl', 0)) * 60.0
        self.enabled = True if self.logUrl and self.settingsUrl else False


class Settings(object):
    __slots__ = ('status', 'loglevel', 'disabled')

    def __init__(self, status, loglevel=LogLevels.NOTSET):
        self.status = status
        self.loglevel = loglevel
        self.disabled = self.status == SettingsStatuses.DISABLED

    def __str__(self):
        return '<Settings: {}>'.format(self.toDict())

    def __repr__(self):
        return self.__str__()

    def toDict(self):
        return {'status': self.status,
         'disabled': self.disabled,
         'loglevel': self.loglevel}


class _WebSettings(object):
    REQUESTS_LIMIT = 5

    def __init__(self, url):
        self._url = url or ''
        self._cache = {}
        self._requestsCount = {}
        self._em = EventManager()
        self.onChanged = SafeEvent(self._em)

    def get(self, feature, group):
        key = createFeatureKey(feature, group)
        if key not in self._cache:
            return self._request(feature, group)
        settings = self._cache[key]
        _logger.debug('Getting web settings from cache: %s.', settings)
        return settings

    def clear(self):
        self._em.clear()
        self._cache.clear()
        self._requestsCount.clear()
        _logger.debug('Web settings container cleared.')

    def reset(self):
        for key in list(self._cache):
            if self._cache[key].status != SettingsStatuses.REQUESTED:
                self._pop(key)

    def _set(self, key, settings):
        self._cache[key] = settings
        _logger.debug('Web settings container updated: %s, %s.', key, settings)
        self.onChanged(key, settings)

    def _pop(self, key):
        self._cache.pop(key, None)
        _logger.debug('Web settings for %s deleted from container.', key)
        return

    def _request(self, feature, group):
        spaID = getPlayerID()
        if spaID is None or not feature or not group:
            return Settings(status=SettingsStatuses.DISABLED)
        else:
            key = createFeatureKey(feature, group)
            if self._requestsCount.get(key, 0) >= self.REQUESTS_LIMIT:
                settings = Settings(status=SettingsStatuses.DISABLED)
                _logger.debug('Requests feature %s web settings limit exceeded.', key)
                self._set(key, settings)
                self._requestsCount.pop(key, None)
                return settings
            postData = {'feature': feature,
             'spa_id': spaID}
            _logger.debug('Request web settings from %s with %s.', self._url, postData)
            settings = Settings(status=SettingsStatuses.REQUESTED)
            self._set(key, settings)
            self._requestsCount[key] = self._requestsCount.get(key, 0) + 1
            self._fetchURL(key, postData)
            return settings

    def _fetchURL(self, key, data):
        BigWorld.fetchURL(url=self._url, callback=partial(self._onResponse, key), headers=HTTP_DEFAULT_HEADERS, timeout=HTTP_DEFAULT_TIMEOUT, method='POST', postdata=json.dumps(data))

    @noexcept
    def _onResponse(self, key, response):
        _logger.debug('Received web settings for %s with code %s.', key, response.responseCode)
        if response.responseCode != HTTP_OK_STATUS:
            self._pop(key)
            return
        else:
            try:
                body = json.loads(response.body)
            except (TypeError, ValueError):
                _logger.warning('Can not load response body for %s.', key)
                body = {}

            data = body.get('data', {})
            feature = data.get('feature', '')
            group = data.get('group', 'default')
            if feature and group and key == createFeatureKey(feature, group):
                status = SettingsStatuses.ENABLED if data.get('send_logs') else SettingsStatuses.DISABLED
                self._set(key, Settings(status=status, loglevel=data.get('loglevel', LogLevels.NOTSET)))
                self._requestsCount.pop(key, None)
            else:
                _logger.warning('Received broken web settings %s for %s.', body, key)
                self._pop(key)
            return


class LoggingSettings(object):

    def __init__(self):
        self._local = LocalSettings()
        self._webService = _WebSettings(self._local.settingsUrl)
        self.url = self._local.logUrl
        self.clientLog = self._local.clientLog
        self.logsQueueLimit = self._local.logsQueueLimit
        self.ttl = self._local.settingsTtl
        self.onChanged = self._webService.onChanged

    def get(self, feature, group):
        if not self._local.enabled or BattleReplay.isPlaying():
            _logger.debug('Logging for %s disabled in local environment.', (feature, group))
            return Settings(status=SettingsStatuses.DISABLED)
        return self._webService.get(feature, group)

    def reset(self):
        self._webService.reset()

    def clear(self):
        self._webService.clear()
