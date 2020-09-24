# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/offers/cache.py
import os
import logging
import itertools
import urlparse
from functools import partial
import BigWorld
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.offers import IOffersDataProvider
from web.cache.web_cache import WebExternalCache
_logger = logging.getLogger(__name__)
_DEFAULT_WORKERS_LIMIT = 2
_REQUEST_TIMEOUT = 300.0
_DEFAULT_SYNC_TIMEOUT = 180.0
_CDN_CACHE_DIR = 'offers_cache'
_CDN_WORKERS = 2

class CachePrefetchResult(object):
    SUCCESS = 0
    FAIL = -1
    CACHE_SYNC_TIMEOUT = -2
    MGR_SYNC_TIMEOUT = -3
    WRONG_CONFIG = -4
    CLOSED = -5
    BUSY = -6
    RESTART = -7


class CacheStates(object):
    INITIALIZED = 1
    SYNCING = 2
    SYNCED = 3


class ExternalCache(WebExternalCache):

    def __init__(self, cacheName, workersLimit):
        super(ExternalCache, self).__init__(cacheName, workersLimit)
        self._callback = None
        self._state = CacheStates.INITIALIZED
        self._timoutTimerID = None
        return

    @property
    def syncing(self):
        return self._state == CacheStates.SYNCING

    def prefetchStart(self, manifest, callback=None, timeout=0.0):
        if self._state == CacheStates.INITIALIZED:
            self._startTime = BigWorld.timeExact()
            self._callback = callback
            if not isinstance(manifest, list):
                _logger.error('Wrong manifest structure')
                self._prefetchEnd(CachePrefetchResult.WRONG_CONFIG)
            else:
                _logger.debug('Start syncing, timeout: %s', timeout)
                self._startSync(timeout)
                self.update(manifest)
        elif self._state == CacheStates.SYNCING:
            _logger.debug('Cache already syncing')
            if callable(callback):
                callback(CachePrefetchResult.BUSY)
        else:
            _logger.error('Cache already closed or synced')
            if callable(callback):
                callback(CachePrefetchResult.CLOSED)

    def prefetchEnd(self):
        result = CachePrefetchResult.SUCCESS
        if self._notDownloadedCnt or self._notStoredCnt:
            result = CachePrefetchResult.FAIL
        self._prefetchEnd(result)

    def getRelativePath(self, url):
        absolute = self.get(url)
        if absolute:
            try:
                return os.path.relpath(absolute, start=self.rootDirPath)
            except ValueError:
                _logger.error('Error while getting relative path from: %s, root: %s', absolute, self.rootDirPath)

    def close(self, reason=CachePrefetchResult.CLOSED):
        super(ExternalCache, self).close()
        self._cancelSync(reason)

    def _startSync(self, timeout=0.0):
        self._state = CacheStates.SYNCING
        if timeout > 0:
            self._timoutTimerID = BigWorld.callback(timeout, self._onTimeout)

    def _cancelSync(self, result):
        self._state = CacheStates.SYNCED
        if self._timoutTimerID is not None:
            BigWorld.cancelCallback(self._timoutTimerID)
            self._timoutTimerID = None
        if callable(self._callback):
            self._callback(result)
        self._callback = None
        return

    def _prefetchEnd(self, result):
        _logger.debug('Stopping sync with result: %s', result)
        super(ExternalCache, self).prefetchEnd()
        self._cancelSync(result)

    def _onTimeout(self, *args, **kwargs):
        self._timoutTimerID = None
        self._prefetchEnd(CachePrefetchResult.CACHE_SYNC_TIMEOUT)
        return

    def _onResourceLoaded(self, appName, url, data):
        if self._state != CacheStates.SYNCING:
            _logger.debug('Receive resource from: [%s], when stopped or destroyed (%s)', url, self._state)
            return
        return super(ExternalCache, self)._onResourceLoaded(appName, url, data)

    def _onResourceStored(self, url, key, filename, stored):
        if self._state != CacheStates.SYNCING:
            _logger.debug('Receive update request for: [%s], when stopped or destroyed (%s)', url, self._state)
            return
        return super(ExternalCache, self)._onResourceStored(url, key, filename, stored)


class ExternalCacheManager(object):

    def __init__(self, cacheName, workersLimit=_DEFAULT_WORKERS_LIMIT):
        self._cacheName = cacheName
        self._workersLimit = workersLimit
        self._cache = None
        self._callers = {}
        self._callersIDGen = itertools.count()
        return

    def destroy(self):
        self._destroyCache()
        self._sendResultToCallers(CachePrefetchResult.CLOSED)
        _logger.debug('[%s] manager destroyed', self._cacheName)

    def sync(self, callback=None, timeout=_DEFAULT_SYNC_TIMEOUT):
        self._registerCaller(callback, timeout)
        self._sync()

    def restart(self):
        if self._cache is not None and self._cache.syncing:
            _logger.debug('[%s] restarting cache sync', self._cacheName)
            self._cache.close(reason=CachePrefetchResult.RESTART)
            self._sync()
        return

    def get(self, url, relative=True):
        if self._cache is None:
            _logger.error('[%s] not initialized', self._cacheName)
            return ''
        else:
            if relative:
                path = self._cache.getRelativePath(url)
            else:
                path = self._cache.get(url)
            return path or ''

    def _sync(self):
        if self._cache is not None and self._cache.syncing:
            _logger.debug('[%s] already syncing', self._cacheName)
            return
        else:
            self._destroyCache()
            manifest = self._getManifest()
            if manifest is None:
                _logger.error('[%s] broken manifest', self._cacheName)
                self._onResponse(CachePrefetchResult.WRONG_CONFIG)
                return
            self._cache = ExternalCache(self._cacheName, self._workersLimit)
            _logger.debug('[%s] initialized', self._cacheName)
            try:
                self._cache.load()
            except:
                _logger.error('[%s] can not load files', self._cacheName)
                self._destroyCache()
                self._onResponse(CachePrefetchResult.FAIL)
                return

            self._cache.prefetchStart(manifest, callback=self._onResponse, timeout=_REQUEST_TIMEOUT)
            return

    def _destroyCache(self):
        if self._cache is not None:
            self._cache.close()
            _logger.debug('[%s] instance destroyed', self._cacheName)
            self._cache = None
        return

    def _sendResult(self, callerID, result):
        timerID, caller = self._callers.pop(callerID, (None, None))
        if timerID is not None:
            if result != CachePrefetchResult.MGR_SYNC_TIMEOUT:
                BigWorld.cancelCallback(timerID)
        else:
            _logger.error('[%s] caller wrong timer id', self._cacheName)
        if callable(caller):
            caller(result)
        else:
            _logger.error('[%s] caller %s not callable', self._cacheName, caller)
        return

    def _sendResultToCallers(self, result):
        for callerID in list(self._callers):
            self._sendResult(callerID, result)

    def _onResponse(self, result):
        if result == CachePrefetchResult.RESTART:
            _logger.debug('[%s] restart response', self._cacheName)
            return
        self._sendResultToCallers(result)

    def _onTimeout(self, callerID):
        _logger.debug('[%s] (%s) request timeout', callerID, self._cacheName)
        self._sendResult(callerID, CachePrefetchResult.MGR_SYNC_TIMEOUT)

    def _registerCaller(self, caller, timeout):
        if timeout <= 0:
            _logger.error('[%s] cache wrong sync timeout: %s. Using default: %s', self._cacheName, timeout, _DEFAULT_SYNC_TIMEOUT)
            timeout = _DEFAULT_SYNC_TIMEOUT
        if callable(caller):
            cID = self._callersIDGen.next()
            tID = BigWorld.callback(timeout, partial(self._onTimeout, cID))
            self._callers[cID] = (tID, caller)
        else:
            _logger.debug('[%s] cache sync caller %s not callable', self._cacheName, caller)

    def _getManifest(self):
        raise NotImplementedError


class CdnResourcesCache(ExternalCacheManager):
    _lobbyCtx = dependency.descriptor(ILobbyContext)
    _offersProvider = dependency.descriptor(IOffersDataProvider)

    def __init__(self):
        super(CdnResourcesCache, self).__init__(_CDN_CACHE_DIR, _CDN_WORKERS)
        self._cdnRootUrl = ''

    def get(self, cdnRelativePath, relative=True):
        url = urlparse.urljoin(self._cdnRootUrl, cdnRelativePath)
        return super(CdnResourcesCache, self).get(url, relative=relative)

    def _getManifest(self):
        url = self._lobbyCtx.getServerSettings().fileServer.getOffersRootUrl()
        if not isinstance(url, str):
            _logger.error('[%s] Broken url: %s. Check server settings', self._cacheName, url)
            url = ''
        if not url:
            return None
        else:
            if not url.endswith('/'):
                url += '/'
            self._cdnRootUrl = url
            root = urlparse.urlparse(self._cdnRootUrl)
            host = urlparse.urlunsplit((root.scheme,
             root.netloc,
             '',
             '',
             ''))
            resMap = {'localizations': set(),
             'images': set()}
            for offer in self._offersProvider.iAvailableOffers():
                resMap['localizations'].update({offer.cdnLocFilePath})
                resMap['images'].update({offer.cdnBannerLogoPath,
                 offer.cdnLogoPath,
                 offer.cdnGiftsBackgroundPath,
                 offer.cdnGiftsTokenImgPath})
                for gift in offer.availableGifts:
                    resMap['localizations'].update({gift.cdnLocFilePath})
                    resMap['images'].update({gift.cdnImagePath, gift.cdnIconPath})

            manifest = []
            for resName, filePaths in resMap.iteritems():
                record = {'host': host,
                 'status': {'code': 'OK',
                            'description': 'SUCCESS'},
                 'files': [ urlparse.urljoin(root.path, path) for path in filePaths if path ],
                 'name': resName}
                manifest.append(record)

            return manifest
