# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/lobby_cdn_controller.py
import urlparse
import typing
import BigWorld
import Event
import logging
from gui.impl.utils.path import normalizeGfImagePath
from helpers import dependency
from skeletons.gui.game_control import ILobbyCdnController
from skeletons.gui.lobby_context import ILobbyContext
from dict2model import fields, schemas
from dict2model.models import Model
from web.cache.web_cache import BaseExternalCache, BaseExternalCacheManager, CachePrefetchResult, CacheStates, createManifestRecord
_logger = logging.getLogger('LobbyCdnCache')
if typing.TYPE_CHECKING:
    from typing import Any, Dict, List, Optional, Union

class ConfigModel(Model):
    __slots__ = ('images',)

    def __init__(self, images):
        super(ConfigModel, self).__init__()
        self.images = images

    def __repr__(self):
        return '<ConfigModel(images={})>'.format(len(self.images))


configSchema = schemas.Schema(fields={'images': fields.List(fieldOrSchema=fields.String(), required=True)}, modelClass=ConfigModel, checkUnknown=True)

class LobbyCdnCache(BaseExternalCache):
    __CDN_CACHE_DIR = 'lobby_cdn_cache'
    __CDN_WORKERS = 1
    __CONFIG_FILE = 'config.json'

    def __init__(self, externalBucketUrl):
        self.__externalBucketUrl = externalBucketUrl
        if externalBucketUrl:
            configUrl = '/'.join((externalBucketUrl, self.__CONFIG_FILE))
            self._EXTERNAL_CONFIG_URL = configUrl
        self.__config = None
        super(LobbyCdnCache, self).__init__(self.__CDN_CACHE_DIR, self.__CDN_WORKERS)
        return

    def _startSync(self, timeout=0.0):
        _logger.debug('Start syncing, timeout: %s', timeout)
        self._state = CacheStates.SYNCING
        if timeout > 0:
            self._timeoutTimerID = BigWorld.callback(timeout, self._onTimeout)
        if self._EXTERNAL_CONFIG_URL and self.__config is None:
            if not self._downloader or self._downloader.stopped:
                _logger.error('Config [%s] download error. Downloader not started.', self._EXTERNAL_CONFIG_URL)
                self._prefetchEnd(CachePrefetchResult.CLOSED)
                return
            self._downloader.downloadLowPriority(self._EXTERNAL_CONFIG_URL, self._onConfigLoaded)
        else:
            self._prepareToUpdate(config=None, manifest=None)
        return

    def _prepareToUpdate(self, config=None, manifest=None):
        if config is not None:
            self.__config = configSchema.deserialize(config, silent=True)
            if self.__config is None:
                _logger.exception('Wrong config structure.')
        if self.__config is None:
            return
        else:
            try:
                created = self._createManifest(self.__config)
            except Exception:
                _logger.exception('Can not create manifest.')
                created = None

            if not isinstance(created, list):
                _logger.warning('No manifest created.')
                self._prefetchEnd(CachePrefetchResult.WRONG_CONFIG)
                return
            try:
                self.update(list(manifest or []) + created)
            except Exception:
                _logger.exception('External cache can not be updated.')
                self._prefetchEnd(CachePrefetchResult.FAIL)

            return

    def _createManifest(self, config=None):
        _logger.debug('Creating manifest to download from config.')
        toDownloadByHosts = {}
        for image in config.images:
            url = '/'.join((self.__externalBucketUrl, image))
            parsedUrl = urlparse.urlparse(url)
            host = urlparse.urlunsplit((parsedUrl.scheme,
             parsedUrl.netloc,
             '',
             '',
             ''))
            toDownloadByHosts.setdefault(host, []).append(parsedUrl.path)

        return [ createManifestRecord(appName='images', host=host, files=relativeUrls) for host, relativeUrls in toDownloadByHosts.iteritems() ]


class LobbyCdnCacheMgr(BaseExternalCacheManager):
    __lobbyCtx = dependency.descriptor(ILobbyContext)
    _REQUEST_TIMEOUT = 30.0
    _DEFAULT_SYNC_TIMEOUT = 1200.0

    def __init__(self):
        super(LobbyCdnCacheMgr, self).__init__()
        self.onSynced = Event.Event()
        self._cache = None
        self._downloadResult = None
        self.__isStarted = False
        self.__toDownloadImages = []
        self.__bucketUrl = self.__getExternalBucketUrl()
        return

    def startSync(self, *args, **kwargs):
        self.__lobbyCtx.onServerSettingsChanged += self.__onServerSettingsChanged
        self.__update()
        _logger.debug('Sync started')

    def stopSync(self, *args, **kwargs):
        self.__lobbyCtx.onServerSettingsChanged -= self.__onServerSettingsChanged
        self._destroyCache()
        self.__isStarted = False
        _logger.debug('Sync stopped')

    def getPath(self, url):
        if self._cache is None:
            return
        else:
            fullUrl = '/'.join((self.__bucketUrl, url))
            return normalizeGfImagePath(self._cache.getRelativePath(fullUrl))

    def _createCache(self):
        return LobbyCdnCache(self.__bucketUrl)

    def __onServerSettingsChanged(self, *args, **kwargs):
        self.__bucketUrl = self.__getExternalBucketUrl()
        self.__update()

    def __update(self):
        if self.__isStarted:
            return
        if self.__bucketUrl:
            self.__isStarted = True
            _logger.debug('[ServerSettings] bucket url: %s selected.', self.__bucketUrl)
            self.__tryToDownload()

    def __getExternalBucketUrl(self):
        url = self.__lobbyCtx.getServerSettings().fileServer.getLobbyCdnContentBucketUrl()
        if not url:
            _logger.debug('External url not configured yet.')
            return None
        else:
            return url

    def __tryToDownload(self):
        if not self.__bucketUrl:
            _logger.debug('Not ready to sync yet.')
            return
        _logger.debug('Downloading cdn resources.')
        self.sync(self.__onSynced)

    def __onSynced(self, result):
        self._downloadResult = result
        if result == CachePrefetchResult.SUCCESS:
            _logger.debug('CachePrefetchResult is %s', result)
        else:
            _logger.warning('CachePrefetchResult is %s', result)
        self.onSynced()


class LobbyCdnController(ILobbyCdnController):
    MANDATORY_PREFIX = 'lobbycdn://'

    def __init__(self):
        super(LobbyCdnController, self).__init__()
        self.__em = Event.EventManager()
        self.onSynced = Event.Event(self.__em)
        self.__cdnCacheMgr = None
        return

    def resolveCdnImage(self, url):
        if not self.__cdnCacheMgr:
            return ''
        if not url.startswith(self.MANDATORY_PREFIX):
            _logger.error("Wrong cdn url prefix. Url must start with '%s'", self.MANDATORY_PREFIX)
        urlWithoutProtocol = url[len(self.MANDATORY_PREFIX):]
        return self.__cdnCacheMgr.getPath(urlWithoutProtocol) or ''

    def onLobbyInited(self, event):
        self.__cdnCacheMgr = LobbyCdnCacheMgr()
        self.__cdnCacheMgr.onSynced += self.__onSynced
        self.__cdnCacheMgr.startSync()

    def onDisconnected(self):
        if self.__cdnCacheMgr is not None:
            self.__cdnCacheMgr.onSynced -= self.__onSynced
            self.__cdnCacheMgr.stopSync()
        self.__em.clear()
        return

    def fini(self):
        if self.__cdnCacheMgr is not None:
            self.__cdnCacheMgr.onSynced -= self.__onSynced
            self.__cdnCacheMgr.stopSync()
        self.__em.clear()
        return

    def __onSynced(self):
        self.onSynced()
