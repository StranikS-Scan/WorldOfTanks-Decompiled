# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/cache/web_cache.py
import hashlib
import json
import logging
import urlparse
from functools import partial
import BigWorld
from debug_utils import LOG_CURRENT_EXCEPTION
from helpers.web.app_storage import ApplicationStorage
from web.cache.web_downloader import WebDownloader
from web.web_external_cache import IWebExternalCache
_logger = logging.getLogger(__name__)
_WORKERS_LIMIT = 2

def _generateKey(url):
    md = hashlib.md5()
    md.update(url)
    return md.hexdigest()


class WebExternalCache(IWebExternalCache):

    def __init__(self, cacheName, workersLimit=_WORKERS_LIMIT):
        self.__cache = {}
        self._prefetchCnt = 0
        self._downloadedCnt = 0
        self._notDownloadedCnt = 0
        self._downloadedSize = 0
        self._storedCnt = 0
        self._notStoredCnt = 0
        self._startTime = 0
        self.__downloader = WebDownloader(workersLimit)
        _logger.info('WebDownloader created. Workers: %r', workersLimit)
        self.__storage = ApplicationStorage(cacheName, workersLimit)
        _logger.info('WebStorage created. Name: %s Workers: %r', cacheName, workersLimit)

    def close(self):
        self.__cache = {}
        self.__closeDownloader()
        if self.__storage:
            self.__storage.close()
        self.__storage = None
        _logger.info('WebStorage destroyed')
        return

    def __closeDownloader(self):
        if self.__downloader:
            self.__downloader.close()
            self.__downloader = None
            _logger.info('WebDownloader destroyed')
        return

    @property
    def rootDirPath(self):
        return self.__storage.rootDirPath

    def load(self):
        loaded = self.__storage.load()
        self.__cache.update(loaded)

    def get(self, url):
        key = _generateKey(url)
        if key in self.__cache:
            res = self.__cache[key]
            if self.__storage.isFileExist(res):
                _logger.debug('Resource: %s found in cache as: %s', url, res)
                return res
            self.__cache.pop(key)
        _logger.debug('Resource %s not found in cache and will be loaded from Web.', url)
        return None

    def prefetchStart(self, url):
        self._startTime = BigWorld.timeExact()
        _logger.info('Web prefetch started...')
        if url is not None:
            _logger.info('Download manifest file: %s', url)
            self.__downloader.download(url, self.__onManifestLoaded)
        else:
            _logger.error('Manifest url not found in gui_settings.xml')
            self.prefetchEnd()
        return

    def prefetchEnd(self):
        self.__closeDownloader()
        if self.__storage:
            self.__storage.stopWorker()
        _logger.info('Web prefetch finished')
        _logger.info('Summary: Downloaded: %r / %r. Stored: %r / %r. Size: %r', self._downloadedCnt, self._prefetchCnt, self._storedCnt, self._prefetchCnt, self._downloadedSize)
        delta = BigWorld.timeExact() - self._startTime
        _logger.info('Total prefetch time: %r', delta)

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
            unusedApps = self.__storage.getApps()
            for data in manifest:
                appName = data['name']
                status = data['status']
                _logger.debug('Web status for: %s = %s : %s', appName, status['code'], status['description'])
                host = data['host']
                if appName in unusedApps:
                    unusedApps.remove(appName)
                unusedFiles = self.__storage.getAppFiles(appName)
                files = data['files']
                for curfile in files:
                    url = urlparse.urljoin(host, curfile)
                    key = _generateKey(url)
                    if key not in self.__cache or not self.__storage.isAppFileExist(appName, key):
                        _logger.debug('Resource not found in cache. Download from web: %s', url)
                        filesToDownload[url] = appName
                    if key in unusedFiles:
                        unusedFiles.remove(key)

                for f in unusedFiles:
                    self.__storage.removeAppFile(appName, f)

            for appName in unusedApps:
                self.__storage.removeApp(appName)

        except KeyError:
            LOG_CURRENT_EXCEPTION()

        self._prefetchCnt = len(filesToDownload)
        if self._prefetchCnt > 0:
            _logger.info('There are %r new files in manifest', self._prefetchCnt)
            _logger.info('Start downloading...')
            for url, name in filesToDownload.iteritems():
                self.__downloader.download(url, partial(self._onResourceLoaded, name))

        else:
            _logger.info('There are no new files in manifest')
            self.prefetchEnd()

    def _onResourceLoaded(self, appName, url, data):
        if data is not None:
            key = _generateKey(url)
            _logger.debug('Resource downloaded: %s size: %r', url, len(data))
            self.__storage.addAppFile(appName, key, data, partial(self._onResourceStored, url, key))
            self._downloadedCnt += 1
            self._downloadedSize += len(data)
        else:
            _logger.warning('Resource download error: %s', url)
            self._notDownloadedCnt += 1
        self.__checkPrefetchEnd()
        return

    def _onResourceStored(self, url, key, filename, stored):
        if stored:
            self.__cache[key] = filename
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
