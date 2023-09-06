# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/collection/resources/cdn/cache.py
import urlparse
import typing
import BigWorld
from gui.collection import loggers
from gui.collection.resources.cdn.config import createConfigModel
from gui.collection.resources.cdn.models import CdnCacheParamsModel, ImageModel
from helpers import dependency
from shared_utils import first
from skeletons.gui.game_control import ICollectionsSystemController
from skeletons.gui.lobby_context import ILobbyContext
from web.cache.web_cache import BaseExternalCache, BaseExternalCacheManager, CachePrefetchResult, CacheStates, createManifestRecord
_logger = loggers.getCdnCacheLogger()
if typing.TYPE_CHECKING:
    from typing import Any, Dict, List, Optional, Union
    from gui.collection.resources.cdn.models import ConfigModel
_g_config = None

def _getConfig():
    global _g_config
    return _g_config


def _updateConfig(config):
    global _g_config
    if _g_config is None and config is not None:
        _g_config = createConfigModel(config)
    return


class CollectionsCdnCache(BaseExternalCache):
    __collectionsSystem = dependency.descriptor(ICollectionsSystemController)
    __CDN_CACHE_DIR = 'collections_cache'
    __CDN_WORKERS = 16

    def __init__(self, externalConfigUrl, toDownloadImages):
        self._EXTERNAL_CONFIG_URL = externalConfigUrl
        self.__toDownloadImages = toDownloadImages
        super(CollectionsCdnCache, self).__init__(self.__CDN_CACHE_DIR, self.__CDN_WORKERS)

    def getImages(self, imagesIDs):
        config = _getConfig()
        if config is None:
            _logger.warning('Config does not exist')
            return []
        else:
            return [ i for i in config.images if i.id in imagesIDs ]

    def _startSync(self, timeout=0.0):
        _logger.debug('Start syncing, timeout: %s', timeout)
        self._state = CacheStates.SYNCING
        if timeout > 0:
            self._timeoutTimerID = BigWorld.callback(timeout, self._onTimeout)
        if self._EXTERNAL_CONFIG_URL and _getConfig() is None:
            if not self._downloader or self._downloader.stopped:
                _logger.error('Config [%s] download error. Downloader not started.', self._EXTERNAL_CONFIG_URL)
                self._prefetchEnd(CachePrefetchResult.CLOSED)
                return
            self._downloader.downloadLowPriority(self._EXTERNAL_CONFIG_URL, self._onConfigLoaded)
        else:
            self._prepareToUpdate(config=None, manifest=None)
        return

    def _prepareToUpdate(self, config=None, manifest=None):
        _updateConfig(config)
        try:
            created = self._createManifest(_getConfig())
        except Exception:
            _logger.exception('Can not create manifest.')
            created = None

        if not isinstance(created, list):
            _logger.warning('No manifest created.')
            self._prefetchEnd(CachePrefetchResult.WRONG_CONFIG)
            return
        else:
            try:
                self.update(list(manifest or []) + created)
            except Exception:
                _logger.exception('External cache can not be updated.')
                self._prefetchEnd(CachePrefetchResult.FAIL)

            return

    def _createManifest(self, config=None):
        _logger.debug('Creating manifest to download from config.')
        existingUrls = []
        for image in config.images:
            if image.isDownloaded(self):
                existingUrls.append(image.url)

        toDownloadUrls = []
        for image in self.__toDownloadImages:
            urls = [ i.url for i in config.images if i.id == image.id ]
            if urls:
                toDownloadUrls.append(first(urls))

        toDownloadByHosts = {}
        for url in existingUrls + toDownloadUrls:
            parsedUrl = urlparse.urlparse(url)
            host = urlparse.urlunsplit((parsedUrl.scheme,
             parsedUrl.netloc,
             '',
             '',
             ''))
            toDownloadByHosts.setdefault(host, []).append(parsedUrl.path)

        self.__toDownloadImages = []
        return [ createManifestRecord(appName='images', host=host, files=relativeUrls) for host, relativeUrls in toDownloadByHosts.iteritems() ]


class CollectionsCdnCacheMgr(BaseExternalCacheManager):
    __lobbyCtx = dependency.descriptor(ILobbyContext)
    _REQUEST_TIMEOUT = 30.0
    _DEFAULT_SYNC_TIMEOUT = 1200.0

    def __init__(self):
        super(CollectionsCdnCacheMgr, self).__init__()
        self._cache = None
        self._downloadResult = None
        self.__cacheParams = CdnCacheParamsModel()
        self.__toDownloadImages = []
        return

    def startSync(self, *args, **kwargs):
        self.__lobbyCtx.onServerSettingsChanged += self.__onServerSettingsChanged
        self.__update()
        _logger.debug('Sync started')

    def stopSync(self, *args, **kwargs):
        self.__lobbyCtx.onServerSettingsChanged -= self.__onServerSettingsChanged
        self.__cacheParams.reset()
        self._destroyCache()
        _logger.debug('Sync stopped')

    def _createCache(self):
        return CollectionsCdnCache(self.__cacheParams.configUrl, self.__toDownloadImages)

    def getImagesPaths(self, imagesIDs, callback=None):
        self.__toDownloadImages = self._cache.getImages(imagesIDs)

        def onSynced(result):
            isOk = result == CachePrefetchResult.SUCCESS
            message = 'CachePrefetchResult is {}'.format(result)
            (_logger.debug if isOk else _logger.warning)(message)
            if self._cache is not None:
                downloadedImages = self._cache.getImages(imagesIDs)
            else:
                _logger.warning('Cache was not created')
                downloadedImages = []
            callback(isOk, self.__packImages(downloadedImages))
            self.__toDownloadImages = []
            return

        self.sync(onSynced)

    def __packImages(self, images):
        packed = {}
        for image in images:
            packed.setdefault(image.group, {})
            packed[image.group].setdefault(image.sub, {})
            packed[image.group][image.sub][image.name] = image.getGFPath(self._cache)

        return packed

    def __onServerSettingsChanged(self, *args, **kwargs):
        self.__update()

    def __update(self):
        if self.__cacheParams.isReady:
            return
        configUrl = self.__getExternalConfigUrl()
        if configUrl:
            self.__cacheParams.configUrl = configUrl
            _logger.debug('[ServerSettings] config url: %s selected.', configUrl)
            self.__tryToDownload()

    def __getExternalConfigUrl(self):
        url = self.__lobbyCtx.getServerSettings().fileServer.getCollectionsContentConfigUrl()
        if not url:
            _logger.debug('External url not configured yet.')
            return None
        else:
            return url

    def __tryToDownload(self):
        if not self.__cacheParams.isReady:
            _logger.debug('Not ready to sync yet.')
            return
        _logger.debug('Downloading cdn resources.')
        self.sync(self.__onSynced)

    def __onSynced(self, result):
        self._downloadResult = result
        _logger.debug('Got sync result: [%s].', result)
