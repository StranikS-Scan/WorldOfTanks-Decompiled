# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/cache/web_cache.py
import os
import typing
import hashlib
import json
import logging
import urlparse
import itertools
from functools import partial
import BigWorld
from debug_utils import LOG_CURRENT_EXCEPTION
from Event import Event, EventManager
from shared_utils import safeCancelCallback
from helpers.web.app_storage import ApplicationStorage
from web.cache.web_downloader import WebDownloader
from web.web_external_cache import IWebExternalCache
_logger = logging.getLogger(__name__)
_WORKERS_LIMIT = 2

class CachePrefetchResult(object):
    SUCCESS = 0
    FAIL = -1
    CACHE_SYNC_TIMEOUT = -2
    MGR_SYNC_TIMEOUT = -3
    WRONG_CONFIG = -4
    CLOSED = -5
    BUSY = -6
    RESTART = -7
    ALL = (SUCCESS,
     FAIL,
     CACHE_SYNC_TIMEOUT,
     MGR_SYNC_TIMEOUT,
     WRONG_CONFIG,
     CLOSED,
     BUSY,
     RESTART)


class CacheStates(object):
    INITIALIZED = 1
    SYNCING = 2
    SYNCED = 3
    ALL = (INITIALIZED, SYNCING, SYNCED)


def generateKey(url):
    md = hashlib.md5()
    md.update(url)
    return md.hexdigest()


def createManifestRecord(appName, host, files, code='OK', description='SUCCESS'):
    return {'host': host,
     'status': {'code': code,
                'description': description},
     'files': list(files),
     'name': appName}


class WebExternalCache(IWebExternalCache):

    def __init__(self, cacheName, workersLimit=_WORKERS_LIMIT):
        self._cache = {}
        self._prefetchCnt = 0
        self._downloadedCnt = 0
        self._notDownloadedCnt = 0
        self._downloadedSize = 0
        self._storedCnt = 0
        self._notStoredCnt = 0
        self._startTime = 0
        self._downloader = WebDownloader(workersLimit)
        _logger.info('WebDownloader created. Workers: %r', workersLimit)
        self._storage = ApplicationStorage(cacheName, workersLimit)
        _logger.info('WebStorage created. Name: %s Workers: %r', cacheName, workersLimit)
        self._eventsManager = EventManager()
        self.onDownloadFinished = Event(self._eventsManager)

    def stopWorkers(self):
        self.__closeDownloader()
        if self._storage:
            self._storage.close()

    def close(self):
        self._cache = {}
        self.stopWorkers()
        self._storage = None
        _logger.info('WebStorage destroyed')
        self._eventsManager.clear()
        return

    def setPause(self, value):
        if self._downloader:
            self._downloader.setPause(value)

    def __closeDownloader(self):
        if self._downloader:
            self._downloader.close()
            self._downloader = None
            _logger.info('WebDownloader destroyed')
        return

    @property
    def rootDirPath(self):
        return self._storage.rootDirPath

    def load(self):
        loaded = self._storage.load()
        self._cache.update(loaded)

    def get(self, url):
        key = generateKey(url)
        if key in self._cache:
            res = self._cache[key]
            if self._storage.isFileExist(res):
                _logger.debug('Resource: %s found in cache as: %s', url, res)
                return res
            self._cache.pop(key)
        _logger.debug('Resource %s not found in cache and will be loaded from Web.', url)
        return None

    def getRelativePath(self, url):
        return self.getRelativeFromAbsolute(self.get(url))

    def getRelativeFromAbsolute(self, absolute):
        if absolute:
            try:
                return os.path.relpath(absolute, start=self.rootDirPath)
            except Exception:
                _logger.exception('Error while getting relative path from: %s, root: %s', absolute, self.rootDirPath)

        return None

    def loadCustomUrls(self, urls, appName):
        filesToDownload = {}
        for url in urls:
            key = generateKey(url)
            if key not in self._cache or not self._storage.isAppFileExist(appName, key):
                _logger.debug('Resource not found in cache. Download from web: %s', url)
                filesToDownload[url] = appName

        self._prefetchCnt += len(filesToDownload)
        if filesToDownload:
            if self._downloader is None:
                self._downloader = WebDownloader(_WORKERS_LIMIT)
            self._storage.restartWorker(_WORKERS_LIMIT)
            _logger.info('There are %r new files to download', len(filesToDownload))
            _logger.info('Start downloading...')
            for url, name in filesToDownload.iteritems():
                self._downloader.download(url, partial(self._onResourceLoaded, name))

        else:
            _logger.info('There are no new files to download')
            self.prefetchEnd()
        return

    def prefetchStart(self, url):
        self._startTime = BigWorld.timeExact()
        _logger.info('Web prefetch started...')
        if url is not None:
            _logger.info('Download manifest file: %s', url)
            self._downloader.downloadLowPriority(url, self.__onManifestLoaded)
        else:
            _logger.error('Manifest url not found in gui_settings.xml')
            self.prefetchEnd()
        return

    def prefetchEnd(self):
        self.stopWorkers()
        _logger.info('Web prefetch finished')
        _logger.info('Summary: Downloaded: %r / %r. Stored: %r / %r. Size: %r', self._downloadedCnt, self._prefetchCnt, self._storedCnt, self._prefetchCnt, self._downloadedSize)
        delta = BigWorld.timeExact() - self._startTime
        _logger.info('Total prefetch time: %r', delta)
        self.onDownloadFinished()

    def __onManifestLoaded(self, url, data):
        if data is not None:
            _logger.info('Manifest downloaded: %s', url)
            try:
                manifest = json.loads(data)
                self.update(manifest)
            except Exception:
                LOG_CURRENT_EXCEPTION()

        else:
            _logger.error('Manifest download error: %s', url)
            self.prefetchEnd()
        return

    def update(self, manifest):
        filesToDownload = {}
        try:
            unusedApps = self._storage.getApps()
            for data in manifest:
                appName = data['name']
                status = data['status']
                _logger.debug('Web status for: %s = %s : %s', appName, status['code'], status['description'])
                host = data['host']
                if appName in unusedApps:
                    unusedApps.remove(appName)
                unusedFiles = self._storage.getAppFiles(appName)
                files = data['files']
                for curfile in files:
                    url = urlparse.urljoin(host, curfile)
                    url = url.replace(' ', '%20')
                    key = generateKey(url)
                    if key not in self._cache or not self._storage.isAppFileExist(appName, key):
                        _logger.debug('Resource not found in cache. Download from web: %s', url)
                        filesToDownload[url] = appName
                    if key in unusedFiles:
                        unusedFiles.remove(key)

                for f in unusedFiles:
                    self._storage.removeAppFile(appName, f)

            for appName in unusedApps:
                self._storage.removeApp(appName)

        except KeyError:
            LOG_CURRENT_EXCEPTION()

        self._prefetchCnt = len(filesToDownload)
        if self._prefetchCnt > 0:
            _logger.info('There are %r new files in manifest', self._prefetchCnt)
            _logger.info('Start downloading...')
            for url, name in filesToDownload.iteritems():
                self._downloader.downloadLowPriority(url, partial(self._onResourceLoaded, name))

        else:
            _logger.info('There are no new files in manifest')
            self.prefetchEnd()

    def _onResourceLoaded(self, appName, url, data):
        if data is not None:
            key = generateKey(url)
            _logger.debug('Resource downloaded: %s size: %r', url, len(data))
            self._storage.addAppFile(appName, key, data, partial(self._onResourceStored, url, key))
            self._downloadedCnt += 1
            self._downloadedSize += len(data)
        else:
            _logger.warning('Resource download error: %s', url)
            self._notDownloadedCnt += 1
        self.__checkPrefetchEnd()
        return

    def _onResourceStored(self, url, key, filename, stored):
        if stored:
            self._cache[key] = filename
            _logger.debug('Resource: %s saved on disk as: %s', url, filename)
            self._storedCnt += 1
        else:
            _logger.error('Resource: %s writing error as: %s', url, filename)
            self._notStoredCnt += 1
        self.__checkPrefetchEnd()

    def __checkPrefetchEnd(self):
        if self._downloadedCnt + self._notDownloadedCnt == self._prefetchCnt:
            if self._storedCnt + self._notStoredCnt + self._notDownloadedCnt == self._prefetchCnt:
                self.prefetchEnd()


class BaseExternalCache(WebExternalCache):
    _EXTERNAL_CONFIG_URL = None
    _CONFIGS_DIR_NAME = None

    def __init__(self, cacheName, workersLimit):
        super(BaseExternalCache, self).__init__(cacheName, workersLimit)
        self._callback = None
        self._state = CacheStates.INITIALIZED
        self._timeoutTimerID = None
        return

    @property
    def syncing(self):
        return self._state == CacheStates.SYNCING

    def prefetchStart(self, callback=None, timeout=0.0):
        if self._state == CacheStates.INITIALIZED:
            self._startTime = BigWorld.timeExact()
            self._callback = callback
            self._startSync(timeout)
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

    def close(self, reason=CachePrefetchResult.CLOSED):
        super(BaseExternalCache, self).close()
        self._cancelSync(reason)

    def getLoaded(self):
        return dict(self._cache)

    def decodeConfig(self, url, rawConfig):
        _logger.debug('Decoding config: %s.', url)
        return json.loads(rawConfig)

    def _prepareToUpdate(self, config=None, manifest=None):
        try:
            created = self._createManifest(config)
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

    def _onConfigSaved(self, url, key, config, filename, stored):
        if not self.syncing:
            _logger.debug('Saved config from: [%s], when stopped or destroyed (%s).', url, self._state)
            return
        if not stored:
            _logger.error('Config: %s writing error: %s.', url, filename)
            self._prefetchEnd(CachePrefetchResult.FAIL)
            return
        self._cache[key] = filename
        _logger.debug('Config: %s saved on disk as: %s.', url, filename)
        parsedUrl = urlparse.urlparse(url)
        host = urlparse.urlunsplit((parsedUrl.scheme,
         parsedUrl.netloc,
         '',
         '',
         ''))
        filePath = parsedUrl.path[1:] if parsedUrl.path.startswith('/') else parsedUrl.path
        self._prepareToUpdate(config, [createManifestRecord(self._CONFIGS_DIR_NAME, host, [filePath])])

    def _onConfigLoaded(self, url, rawConfig):
        if not self.syncing:
            _logger.debug('Receive config from: [%s], when stopped or destroyed (%s).', url, self._state)
            return
        elif not url or rawConfig is None:
            _logger.error('Config [%s] download error.', url)
            self._prefetchEnd(CachePrefetchResult.FAIL)
            return
        else:
            try:
                config = self.decodeConfig(url, rawConfig)
            except Exception:
                _logger.exception('Config [%s] decoding error.', url)
                self._prefetchEnd(CachePrefetchResult.FAIL)
                return

            if self._CONFIGS_DIR_NAME:
                if not self._storage or self._storage.stopped:
                    _logger.error('Config [%s] save error. Storage not started.', url)
                    self._prefetchEnd(CachePrefetchResult.CLOSED)
                    return
                _logger.debug('Saving config [%s] to [%s].', url, self._CONFIGS_DIR_NAME)
                key = generateKey(url)
                self._storage.addAppFile(self._CONFIGS_DIR_NAME, key, rawConfig, partial(self._onConfigSaved, url, key, config))
            else:
                self._prepareToUpdate(config=config, manifest=None)
            return

    def _startSync(self, timeout=0.0):
        _logger.debug('Start syncing, timeout: %s', timeout)
        self._state = CacheStates.SYNCING
        if timeout > 0:
            self._timeoutTimerID = BigWorld.callback(timeout, self._onTimeout)
        if self._EXTERNAL_CONFIG_URL:
            if not self._downloader or self._downloader.stopped:
                _logger.error('Config [%s] download error. Downloader not started.', self._EXTERNAL_CONFIG_URL)
                self._prefetchEnd(CachePrefetchResult.CLOSED)
                return
            self._downloader.downloadLowPriority(self._EXTERNAL_CONFIG_URL, self._onConfigLoaded)
        else:
            self._prepareToUpdate(config=None, manifest=None)
        return

    def _cancelSync(self, result):
        self._state = CacheStates.SYNCED
        if self._timeoutTimerID is not None:
            safeCancelCallback(self._timeoutTimerID)
            self._timeoutTimerID = None
        if callable(self._callback):
            self._callback(result)
        self._callback = None
        return

    def _prefetchEnd(self, result):
        _logger.debug('Stopping sync with result: %s', result)
        super(BaseExternalCache, self).prefetchEnd()
        self._cancelSync(result)

    def _onTimeout(self, *args, **kwargs):
        self._timeoutTimerID = None
        self._prefetchEnd(CachePrefetchResult.CACHE_SYNC_TIMEOUT)
        return

    def _onResourceLoaded(self, appName, url, data):
        if not self.syncing:
            _logger.debug('Receive resource from: [%s], when stopped or destroyed (%s)', url, self._state)
            return
        return super(BaseExternalCache, self)._onResourceLoaded(appName, url, data)

    def _onResourceStored(self, url, key, filename, stored):
        if not self.syncing:
            _logger.debug('Receive save request for: [%s], when stopped or destroyed (%s)', url, self._state)
            return
        return super(BaseExternalCache, self)._onResourceStored(url, key, filename, stored)

    def _createManifest(self, config=None):
        raise NotImplementedError


class BaseExternalCacheManager(object):
    _REQUEST_TIMEOUT = 180.0
    _DEFAULT_SYNC_TIMEOUT = _REQUEST_TIMEOUT

    def __init__(self):
        self._cache = None
        self._callers = {}
        self._callersIDGen = itertools.count()
        return

    @property
    def isSyncing(self):
        return self._cache is not None and self._cache.syncing

    def destroy(self):
        self._destroyCache()
        self._sendResultToCallers(CachePrefetchResult.CLOSED)
        _logger.debug('External cache manager destroyed.')

    def load(self):
        if self.isSyncing:
            _logger.debug('Can not load. External cache is syncing.')
            return None
        else:
            loaded = self._load()
            if self._cache:
                self._cache.stopWorkers()
            return loaded

    def sync(self, callback=None, timeout=None):
        self._registerCaller(callback, timeout=timeout or self._DEFAULT_SYNC_TIMEOUT)
        self._sync()

    def restart(self):
        if self.isSyncing:
            _logger.debug('External cache manager restarting.')
            self._cache.close(reason=CachePrefetchResult.RESTART)
            self._sync()

    def get(self, url, relative=True):
        if self._cache is None:
            _logger.error('External cache not initialized.')
            return ''
        else:
            if relative:
                path = self._cache.getRelativePath(url)
            else:
                path = self._cache.get(url)
            return path or ''

    def _sync(self):
        if self.isSyncing:
            _logger.debug('External cache already syncing.')
            return
        else:
            self._destroyCache()
            self._cache = self._createCacheInstance()
            if not self._cache:
                self._onResponse(CachePrefetchResult.FAIL)
                return
            _logger.debug('External cache initialized.')
            loaded = self._load()
            if loaded is None:
                self._destroyCache()
                self._onResponse(CachePrefetchResult.FAIL)
                return
            self._cache.prefetchStart(callback=self._onResponse, timeout=self._REQUEST_TIMEOUT)
            return

    def _destroyCache(self):
        if self._cache is not None:
            self._cache.close()
            _logger.debug('External cache instance destroyed.')
            self._cache = None
        return

    def _sendResult(self, callerID, result):
        timerID, caller = self._callers.pop(callerID, (None, None))
        if timerID is not None:
            if result != CachePrefetchResult.MGR_SYNC_TIMEOUT:
                safeCancelCallback(timerID)
        else:
            _logger.error('External cache manager caller wrong timer id.')
        if callable(caller):
            caller(result)
        else:
            _logger.error('External cache manager caller %s not callable', caller)
        return

    def _sendResultToCallers(self, result):
        for callerID in list(self._callers):
            self._sendResult(callerID, result)

    def _onResponse(self, result):
        if result == CachePrefetchResult.RESTART:
            _logger.debug('External cache manager got restart response.')
            return
        self._sendResultToCallers(result)

    def _onTimeout(self, callerID):
        _logger.debug('External cache manager caller (%s) request timeout.', callerID)
        self._sendResult(callerID, CachePrefetchResult.MGR_SYNC_TIMEOUT)

    def _registerCaller(self, caller, timeout):
        if timeout <= 0:
            _logger.error('External cache manager wrong sync timeout: %s. Using default: %s.', timeout, self._DEFAULT_SYNC_TIMEOUT)
            timeout = self._DEFAULT_SYNC_TIMEOUT
        if callable(caller):
            cID = self._callersIDGen.next()
            tID = BigWorld.callback(timeout, partial(self._onTimeout, cID))
            self._callers[cID] = (tID, caller)
        else:
            _logger.debug('External cache manager sync caller %s not callable.', caller)

    def _load(self):
        loaded = None
        if self._cache is None:
            self._cache = self._createCacheInstance()
        if self._cache is not None:
            if not self._cache.syncing:
                try:
                    self._cache.load()
                    loaded = self._cache.getLoaded()
                except Exception:
                    _logger.exception('External cache can not load files.')

            else:
                _logger.warning('External cache can not load files while syncing.')
        else:
            _logger.warning('External cache not initialized.')
        return loaded

    def _createCacheInstance(self):
        cache = None
        try:
            cache = self._createCache()
        except Exception:
            _logger.exception('Can not create external cache instance.')

        return cache

    def _createCache(self):
        raise NotImplementedError
