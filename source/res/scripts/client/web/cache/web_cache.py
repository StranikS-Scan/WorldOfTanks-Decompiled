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

    def __init__(self, cacheName):
        self.__cache = {}
        self.__prefetchCnt = 0
        self.__downloadedCnt = 0
        self.__notDownloadedCnt = 0
        self.__downloadedSize = 0
        self.__storedCnt = 0
        self.__notStoredCnt = 0
        self.__startTime = 0
        self.__downloader = WebDownloader(_WORKERS_LIMIT)
        _logger.info('WebDownloader created. Workers: %r', _WORKERS_LIMIT)
        self.__storage = ApplicationStorage(cacheName, _WORKERS_LIMIT)
        _logger.info('WebStorage created. Name: %s Workers: %r', cacheName, _WORKERS_LIMIT)

    def close(self):
        self.__cache = {}
        self.__closeDownloader()
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
        self.__startTime = BigWorld.timeExact()
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
        self.__storage.stopWorker()
        _logger.info('Web prefetch finished')
        _logger.info('Summary: Downloaded: %r / %r. Stored: %r / %r. Size: %r', self.__downloadedCnt, self.__prefetchCnt, self.__storedCnt, self.__prefetchCnt, self.__downloadedSize)
        delta = BigWorld.timeExact() - self.__startTime
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

        self.__prefetchCnt = len(filesToDownload)
        if self.__prefetchCnt > 0:
            _logger.info('There are %r new files in manifest', self.__prefetchCnt)
            _logger.info('Start downloading...')
            for url, name in filesToDownload.iteritems():
                self.__downloader.download(url, partial(self.__onResourceLoaded, name))

        else:
            _logger.info('There are no new files in manifest')
            self.prefetchEnd()

    def __onResourceLoaded(self, appName, url, data):
        if data is not None:
            key = _generateKey(url)
            _logger.debug('Resource downloaded: %s size: %r', url, len(data))
            self.__storage.addAppFile(appName, key, data, partial(self.__onResourceStored, url, key))
            self.__downloadedCnt += 1
            self.__downloadedSize += len(data)
        else:
            _logger.error('Resource download error: %s', url)
            self.__notDownloadedCnt += 1
        self.__checkPrefetchEnd()
        return

    def __onResourceStored(self, url, key, filename, stored):
        if stored:
            self.__cache[key] = filename
            _logger.debug('Resource: %s saved on disk as: %s', url, filename)
            self.__storedCnt += 1
        else:
            _logger.error('Resource: %s writing error as: %s', url, filename)
            self.__notStoredCnt += 1
        self.__checkPrefetchEnd()

    def __checkPrefetchEnd(self):
        if self.__downloadedCnt + self.__notDownloadedCnt == self.__prefetchCnt:
            if self.__storedCnt + self.__notStoredCnt + self.__notDownloadedCnt == self.__prefetchCnt:
                self.prefetchEnd()
