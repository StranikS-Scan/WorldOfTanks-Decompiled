# Embedded file name: scripts/client/gui/shared/RemoteDataDownloader.py
import time
import httplib
import base64
import threading
from functools import partial
from collections import namedtuple
from debug_utils import LOG_DEBUG
from helpers import threads, getFullClientVersion, http, time_utils, local_cache
_CLIENT_VERSION = getFullClientVersion()
_TIMEOUT = 10.0
_REMOTE_DATA_CACHE_VERSION = 1

class LIFE_TIME(object):
    MIN = time_utils.QUARTER_HOUR
    MAX = time_utils.ONE_DAY

    @classmethod
    def isExpired(cls, expires):
        ct = time_utils.getCurrentTimestamp()
        return not ct <= expires <= ct + cls.MAX


class _HttpOpenPageJob(threads.Job):

    def __init__(self, page, lastModified, callback):
        super(_HttpOpenPageJob, self).__init__()
        self.__page = page
        self.__lastModified = lastModified
        self.__callback = callback

    def doWork(self, worker):
        response = http.openPage(worker.getConnection(), self.__page, self.__lastModified)
        if response.willClose():
            worker.closeConnection()
        self.__callback(response.getData(), response.getLastModified(), response.getExpires())


class _HttpOpenUrlJob(threads.Job):

    def __init__(self, url, lastModified, callback):
        super(_HttpOpenUrlJob, self).__init__()
        self.__url = url
        self.__lastModified = lastModified
        self.__callback = callback

    def doWork(self, worker):
        response = http.openUrl(self.__url, self.__lastModified)
        self.__callback(response.getData(), response.getLastModified(), response.getExpires())


class _HttpConnectionWorker(threads.Worker):

    def __init__(self, jobsQueue, host):
        super(_HttpConnectionWorker, self).__init__(jobsQueue)
        self.__host = host
        self.__conn = None
        return

    def terminate(self):
        super(_HttpConnectionWorker, self).terminate()
        self.closeConnection()

    def closeConnection(self):
        if self.__conn is not None:
            self.__conn.close()
            self.__conn = None
            LOG_DEBUG('Http connection has been closed', self.__conn)
        return

    def getConnection(self):
        if self.__conn is not None and self.__conn.sock is not None:
            self.closeConnection()
        if self.__conn is None:
            self.__conn = httplib.HTTPConnection(self.__host, timeout=_TIMEOUT)
            self.__conn.set_debuglevel(1)
            LOG_DEBUG('Http connection creating', self.__host, self.__conn)
        return self.__conn


class _HttpHostDownloader(threads.ThreadPool):

    def __init__(self, host, workersLimit):
        super(_HttpHostDownloader, self).__init__(workersLimit)
        self._host = host

    def _createNewWorker(self):
        return _HttpConnectionWorker(self._jobs, self._host)


class _LocalCache(local_cache.ShelfLocalCache):

    class _Record(namedtuple('_Record', ['data',
     'lastModified',
     'expires',
     'requestTime'])):

        def __repr__(self):
            return '_Record(data=%s, lastModified=%s, expires=%s, requestTime=%s)' % (type(self.data),
             self.lastModified,
             self.expires,
             self.requestTime)

    def __init__(self):
        super(_LocalCache, self).__init__('external_cache', ('data',), autoflush=60)

    def get(self, tags):
        return self._get(self._makeKey(tags))

    def has(self, tags):
        return self._makeKey(tags) in self._cache

    def put(self, tags, data, lastModified, expires):
        return self._put(self._makeKey(tags), data, lastModified, expires)

    def update(self, tags, data, lastModified, expires):
        key = self._makeKey(tags)
        if data is None and key in self._cache:
            data = self._get(key).data
        self._put(key, data, lastModified, expires)
        return

    def _get(self, key):
        if key in self._cache:
            return self._Record(*self._cache[key])
        else:
            return None

    def _put(self, key, data, lastModified, expires):
        self._cache[key] = (data,
         lastModified,
         expires,
         time_utils.getCurrentTimestamp())

    @classmethod
    def _makeKey(cls, tags):
        return base64.b32encode(':'.join(map(str, tags)))


class _RemoteDataDownloader(object):

    def __init__(self):
        self.__storageCache = None
        self.__lock = threading.RLock()
        self._pools = {'clans': _HttpHostDownloader('ce-ct.worldoftanks.net', 3),
         'clubs': _HttpHostDownloader('ce-ct.worldoftanks.net', 3),
         'custom': threads.ThreadPool(workersLimit=2)}
        return

    def start(self):
        self.__storageCache = _LocalCache()
        self.__storageCache.onRead += self.__cache_onRead
        self.__storageCache.read()

    def stop(self):
        if self.__storageCache is not None:
            self.__storageCache.onRead -= self.__cache_onRead
            self.__storageCache.clear()
        for pool in self._pools.itervalues():
            pool.stop()

        return

    def getClanVehicleDecal(self, clanDbID, callback):
        return self.__getRemoteFileByConnection('clans', '/dcont/clans/emblems/%d/emblem_64x64_tank.png' % clanDbID, callback)

    def getClanEmblem32x32(self, clanDbID, callback):
        return self.__getRemoteFileByConnection('clans', '/dcont/clans/emblems/%d/emblem_32x32.png' % clanDbID, callback)

    def getClanEmblem64x64(self, clanDbID, callback):
        return self.__getRemoteFileByConnection('clans', '/dcont/clans/emblems/%d/emblem_64x64.png' % clanDbID, callback)

    def getClubEmblem32x32(self, clubDbID, callback):
        return self.__getRemoteFileByConnection('clubs', '/dcont/clans/emblems/%d/emblem_32x32.png' % clubDbID, callback)

    def getClubEmblem64x64(self, clubDbID, callback):
        return self.__getRemoteFileByConnection('clubs', '/dcont/clans/emblems/%d/emblem_64x64.png' % clubDbID, callback)

    def getUrlData(self, url, callback):
        return self.__getRemoteFile('custom', url, callback, _HttpOpenUrlJob)

    def __getFromCache(self, poolName, page):
        with self.__lock:
            record = self.__storageCache.get((poolName, page))
            if record is not None:
                return (record, LIFE_TIME.isExpired(record.expires))
        return (None, True)

    def __getRemoteFileByConnection(self, poolName, page, callback):
        return self.__getRemoteFile(poolName, page, callback, _HttpOpenPageJob)

    def __getRemoteFile(self, poolName, page, callback, jobType):
        record, needToInvalidate = self.__getFromCache(poolName, page)
        if needToInvalidate:
            if record is not None:
                lastModified = record.lastModified
            else:
                lastModified = None
            self._pools[poolName]._putJob(jobType(page, lastModified, partial(self.__onResponseReceived, poolName, page, callback)))
        else:
            callback(record.data)
        return

    def __onResponseReceived(self, poolName, page, callback, data, lastModified, expires):
        if expires is None:
            expires = time.time()
        elif LIFE_TIME.isExpired(expires):
            expires = time.time() + LIFE_TIME.MAX
        if lastModified is not None:
            with self.__lock:
                self.__storageCache.update((poolName, page), data, lastModified, expires)
        callback(data)
        return

    def __cache_onRead(self):
        if not self.__storageCache:
            return
        for pool in self._pools.itervalues():
            pool.start()


g_remoteCache = _RemoteDataDownloader()
