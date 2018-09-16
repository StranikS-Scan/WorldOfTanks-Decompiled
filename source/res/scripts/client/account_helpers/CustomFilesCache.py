# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/CustomFilesCache.py
import os
import time
import base64
import urllib2
import binascii
import threading
import random
import shelve as provider
from functools import partial
from Queue import Queue
import BigWorld
from debug_utils import LOG_WARNING, LOG_ERROR, LOG_CURRENT_EXCEPTION, LOG_DEBUG
from helpers import getFullClientVersion
from soft_exception import SoftException
_MIN_LIFE_TIME = 900
_MAX_LIFE_TIME = 86400
_LIFE_TIME_IN_MEMORY = 1200
_CACHE_VERSION = 2
_CLIENT_VERSION = None
_DEFAULT_REQUEST_TIMEOUT = 10

def _getClientVersion():
    global _CLIENT_VERSION
    if _CLIENT_VERSION is None:
        _CLIENT_VERSION = getFullClientVersion()
    return _CLIENT_VERSION


def _LOG_EXECUTING_TIME(startTime, methodName, deltaTime=0.1):
    finishTime = time.time()
    if finishTime - startTime > deltaTime:
        LOG_WARNING('Method "%s" takes too much time %s' % (methodName, finishTime - startTime))


def parseHttpTime(t):
    if t is None:
        return
    elif isinstance(t, int):
        return t
    else:
        if isinstance(t, str):
            try:
                parts = t.split()
                weekdays = ['mon',
                 'tue',
                 'wed',
                 'thu',
                 'fri',
                 'sat',
                 'sun']
                months = ['jan',
                 'feb',
                 'mar',
                 'apr',
                 'may',
                 'jun',
                 'jul',
                 'aug',
                 'sep',
                 'oct',
                 'nov',
                 'dec']
                tm_wday = weekdays.index(parts[0][:3].lower())
                tm_day = int(parts[1])
                tm_month = months.index(parts[2].lower()) + 1
                tm_year = int(parts[3])
                tm = parts[4].split(':')
                tm_hour = int(tm[0])
                tm_min = int(tm[1])
                tm_sec = int(tm[2])
                t = int(time.mktime((tm_year,
                 tm_month,
                 tm_day,
                 tm_hour,
                 tm_min,
                 tm_sec,
                 tm_wday,
                 0,
                 -1)))
            except Exception as e:
                LOG_ERROR(e, t)
                t = None

        return t


def makeHttpTime(dt):
    try:
        weekday = ['Mon',
         'Tue',
         'Wed',
         'Thu',
         'Fri',
         'Sat',
         'Sun'][dt.tm_wday]
        month = ['Jan',
         'Feb',
         'Mar',
         'Apr',
         'May',
         'Jun',
         'Jul',
         'Aug',
         'Sep',
         'Oct',
         'Nov',
         'Dec'][dt.tm_mon - 1]
        t = '%s, %02d %s %04d %02d:%02d:%02d GMT' % (weekday,
         dt.tm_mday,
         month,
         dt.tm_year,
         dt.tm_hour,
         dt.tm_min,
         dt.tm_sec)
    except Exception as e:
        LOG_ERROR(e, dt)
        t = None

    return t


def getSafeDstUTCTime():
    t = time.gmtime()
    return int(time.mktime((t.tm_year,
     t.tm_mon,
     t.tm_mday,
     t.tm_hour,
     t.tm_min,
     t.tm_sec,
     t.tm_wday,
     0,
     -1)))


class NotModifiedHandler(urllib2.BaseHandler):

    def http_error_304(self, req, fp, code, message, headers):
        addinfourl = urllib2.addinfourl(fp, headers, req.get_full_url())
        addinfourl.code = code
        return addinfourl


class CFC_OP_TYPE(object):
    DOWNLOAD = 1
    READ = 2
    WRITE = 3
    CHECK = 4


class WorkerThread(threading.Thread):

    def __init__(self, queueLimit=60):
        super(WorkerThread, self).__init__()
        self.input_queue = Queue(queueLimit)
        self.__terminate = False
        self.isBusy = False

    def add_task(self, task):
        callback = task['callback']
        try:
            self.input_queue.put(task, block=False)
        except Exception:
            LOG_CURRENT_EXCEPTION()
            callback()

    def close(self):
        self.isBusy = False
        self.__terminate = True
        self.input_queue.put(None)
        return

    def run(self):
        while True:
            task = self.input_queue.get()
            if task is None:
                break
            if self.__terminate:
                break
            try:
                self.isBusy = True
                self.__run(**task)
            except Exception:
                LOG_CURRENT_EXCEPTION()

            self.isBusy = False
            self.input_queue.task_done()

        self.input_queue.task_done()
        return

    def __run(self, callback, **params):
        callback()


class ThreadPool(object):

    def __init__(self, workersLimit=8, queueLimit=60):
        num = max(2, workersLimit)
        self.__workers = []
        for _ in range(num):
            self.__workers.append(WorkerThread(queueLimit))

    def start(self):
        for w in self.__workers:
            w.start()

    def close(self):
        for w in self.__workers:
            w.close()

        self.__workers = []

    def add_task(self, task):
        if not self.__workers:
            return
        taskType = task['opType']
        if taskType in (CFC_OP_TYPE.WRITE, CFC_OP_TYPE.READ, CFC_OP_TYPE.CHECK):
            self.__workers[0].add_task(task)
        else:
            workers = self.__workers[1:]
            for w in workers:
                if w.isBusy:
                    continue
                w.add_task(task)
                return

            w = random.choice(workers)
            w.add_task(task)


class CustomFilesCache(object):

    def __init__(self, cacheFolder):
        prefsFilePath = unicode(BigWorld.wg_getPreferencesFilePath(), 'utf-8', errors='ignore')
        self.__cacheDir = os.path.join(os.path.dirname(prefsFilePath), cacheFolder)
        self.__cacheDir = os.path.normpath(self.__cacheDir)
        self.__mutex = threading.RLock()
        self.__cache = {}
        self.__accessedCache = {}
        self.__processedCache = {}
        self.__written_cache = set()
        self.__db = None
        self.__prepareCache()
        self.__worker = ThreadPool()
        self.__worker.start()
        self.__startTimer()
        return

    def close(self):
        self.__worker.close()
        self.__cache = {}
        self.__accessedCache = {}
        self.__processedCache = {}
        self.__written_cache = set()
        if self.__timer is not None:
            BigWorld.cancelCallback(self.__timer)
            self.__timer = None
        if self.__db is not None:
            startTime = time.time()
            try:
                self.__db.close()
            except Exception:
                LOG_CURRENT_EXCEPTION()

            _LOG_EXECUTING_TIME(startTime, 'close')
            self.__db = None
        return

    def __startTimer(self):
        self.__timer = BigWorld.callback(60, self.__idle)

    def get(self, url, callback, showImmediately=False, headers=None):
        if callback is None:
            return
        else:
            startDownload = True
            if url in self.__processedCache:
                startDownload = False
            self.__processedCache.setdefault(url, []).append(callback)
            if startDownload:
                self.__get(url, showImmediately, False, headers)
            return

    def __get(self, url, showImmediately, checkedInCache, headers=None):
        try:
            ctime = getSafeDstUTCTime()
            file_hash = base64.b32encode(url)
            self.__mutex.acquire()
            cache = self.__cache
            if file_hash in cache:
                data = cache[file_hash]
                if data is None:
                    LOG_DEBUG('readLocalFile, there is no file in memory.', url)
                    self.__readLocalFile(url, showImmediately)
                else:
                    self.__accessedCache[file_hash] = ctime
                    expires, _, _, remote_file, _, last_modified = data
                    expires = parseHttpTime(expires)
                    if expires is None:
                        LOG_ERROR('Unable to parse expires time.', url)
                        self.__postTask(url, None, True)
                        return
                    if ctime - _MIN_LIFE_TIME <= expires <= ctime + _MAX_LIFE_TIME + _MIN_LIFE_TIME:
                        LOG_DEBUG('postTask, Sends file to requester.', url, last_modified, data[0])
                        self.__postTask(url, remote_file, True)
                    else:
                        if showImmediately:
                            LOG_DEBUG('postTask, Do not release callbacks. Sends file to requester.', url, last_modified, data[0])
                            self.__postTask(url, remote_file, False)
                        LOG_DEBUG('readRemoteFile, there is file in cache, check last_modified field.', url, last_modified, data[0])
                        self.__readRemoteFile(url, last_modified, showImmediately, headers)
            elif checkedInCache:
                LOG_DEBUG('readRemoteFile, there is no file in cache.', url)
                self.__readRemoteFile(url, None, False, headers)
            else:
                LOG_DEBUG('checkFile. Checking file in cache.', url, showImmediately)
                self.__checkFile(url, showImmediately, headers)
        finally:
            self.__mutex.release()

        return

    def __idle(self):
        try:
            self.__mutex.acquire()
            cache = self.__cache
            accessed_cache = self.__accessedCache
            ctime = getSafeDstUTCTime()
            for k, v in accessed_cache.items():
                if v and abs(ctime - v) >= _LIFE_TIME_IN_MEMORY:
                    cache[k] = None
                    accessed_cache.pop(k, None)
                    LOG_DEBUG('Idle. Removing old file from memory.', k)

        finally:
            self.__mutex.release()

        self.__startTimer()
        return

    def __readLocalFile(self, url, showImmediately):
        task = {'opType': CFC_OP_TYPE.READ,
         'callback': partial(self.__onReadLocalFile, url, showImmediately)}
        self.__worker.add_task(task)

    def __onReadLocalFile(self, url, showImmediately):
        remote_file = None
        key = base64.b32encode(url)
        try:
            startTime = time.time()
            if self.__db is not None and self.__db.has_key(key):
                remote_file = self.__db[key]
            _LOG_EXECUTING_TIME(startTime, '__onReadLocalFile')
        except Exception as e:
            LOG_WARNING("Client couldn't read file.", e, key)

        try:
            crc, f, ver = remote_file[2:5]
            if crc != binascii.crc32(f) or _CACHE_VERSION != ver:
                LOG_DEBUG('Old file was found.', url)
                raise SoftException('Invalid data.')
        except Exception:
            remote_file = None

        try:
            self.__mutex.acquire()
            cache = self.__cache
            if remote_file is not None:
                cache[key] = remote_file
            else:
                cache.pop(key, None)
                self.__accessedCache.pop(key, None)
        finally:
            self.__mutex.release()

        self.__get(url, showImmediately, True)
        return

    def __checkFile(self, url, showImmediately, headers=None):
        task = {'opType': CFC_OP_TYPE.CHECK,
         'callback': partial(self.__onCheckFile, url, showImmediately, headers)}
        self.__worker.add_task(task)

    def __onCheckFile(self, url, showImmediately, headers):
        res = False
        name = base64.b32encode(url)
        try:
            startTime = time.time()
            if self.__db is not None:
                res = self.__db.has_key(name)
            _LOG_EXECUTING_TIME(startTime, '__onCheckFile')
        except Exception:
            LOG_CURRENT_EXCEPTION()

        if res:
            try:
                self.__mutex.acquire()
                self.__cache[name] = None
            finally:
                self.__mutex.release()

        self.__get(url, showImmediately, True, headers)
        return

    def __readRemoteFile(self, url, modified_time, showImmediately, headers):
        task = {'opType': CFC_OP_TYPE.DOWNLOAD,
         'callback': partial(self.__onReadRemoteFile, url, showImmediately, modified_time, headers)}
        self.__worker.add_task(task)

    def __onReadRemoteFile(self, url, showImmediately, modified_time, headers):
        startTime = time.time()
        try:
            try:
                fh = remote_file = None
                last_modified = expires = None
                req = urllib2.Request(url)
                req.add_header('User-Agent', _getClientVersion())
                headers = headers or {}
                for name, value in headers.iteritems():
                    req.add_header(name, value)

                if modified_time and isinstance(modified_time, str):
                    req.add_header('If-Modified-Since', modified_time)
                    opener = urllib2.build_opener(NotModifiedHandler())
                    fh = opener.open(req, timeout=_DEFAULT_REQUEST_TIMEOUT)
                    headers = fh.info()
                    if hasattr(fh, 'code'):
                        code = fh.code
                        if code in (304, 200):
                            info = fh.info()
                            last_modified = info.getheader('Last-Modified')
                            expires = info.getheader('Expires')
                        if code == 200:
                            remote_file = fh.read()
                else:
                    opener = urllib2.build_opener(urllib2.BaseHandler())
                    fh = opener.open(req, timeout=_DEFAULT_REQUEST_TIMEOUT)
                    info = fh.info()
                    last_modified = info.getheader('Last-Modified')
                    expires = info.getheader('Expires')
                    remote_file = fh.read()
                if expires is None:
                    expires = makeHttpTime(time.gmtime())
                else:
                    ctime = getSafeDstUTCTime()
                    expiresTmp = parseHttpTime(expires)
                    if expiresTmp > ctime + _MAX_LIFE_TIME or expiresTmp < ctime:
                        expires = makeHttpTime(time.gmtime(time.time() + _MAX_LIFE_TIME))
            except urllib2.HTTPError as e:
                LOG_WARNING('Http error. Code: %d, url: %s' % (e.code, url))
            except urllib2.URLError as e:
                LOG_WARNING('Url error. Reason: %s, url: %s' % (str(e.reason) if isinstance(e.reason, basestring) else 'unknown', url))
            except ValueError as e:
                LOG_WARNING('Value error. Reason: %s, url: %s' % (e, url))
            except Exception as e:
                LOG_ERROR("Client couldn't download file.", e, url)

        finally:
            if fh:
                fh.close()

        _LOG_EXECUTING_TIME(startTime, '__onReadRemoteFile', 10.0)
        if remote_file is None and last_modified is None:
            if showImmediately:
                LOG_DEBUG('__onReadRemoteFile, Error occurred. Release callbacks.', url)
                self.__processedCache.pop(url, None)
            else:
                self.__postTask(url, None, True)
            return
        else:
            file_hash = base64.b32encode(url)
            ctime = getSafeDstUTCTime()
            fileChanged = False
            try:
                self.__mutex.acquire()
                cache = self.__cache
                if remote_file is None and last_modified is not None:
                    value = cache.get(file_hash, None)
                    if value is None:
                        LOG_WARNING('File is expected in cache, but there is no file')
                        self.__postTask(url, None, True)
                        return
                    crc, remote_file = value[2:4]
                else:
                    crc = binascii.crc32(remote_file)
                    fileChanged = True
                packet = (expires,
                 ctime,
                 crc,
                 remote_file,
                 _CACHE_VERSION,
                 last_modified)
                cache[file_hash] = packet
            finally:
                self.__mutex.release()

            LOG_DEBUG('writeCache', url, last_modified, expires)
            self.__writeCache(file_hash, packet)
            if showImmediately and not fileChanged:
                LOG_DEBUG('__onReadRemoteFile, showImmediately = True. Release callbacks.', url)
                self.__processedCache.pop(url, None)
            else:
                self.__get(url, False, True)
            return

    def __prepareCache(self):
        try:
            cacheDir = self.__cacheDir
            if not os.path.isdir(cacheDir):
                os.makedirs(cacheDir)
            filename = os.path.join(cacheDir, 'icons')
            self.__db = provider.open(filename, flag='c', writeback=True)
        except Exception:
            LOG_CURRENT_EXCEPTION()

    def __writeCache(self, name, packet):
        if name in self.__written_cache:
            return
        self.__written_cache.add(name)
        task = {'opType': CFC_OP_TYPE.WRITE,
         'callback': partial(self.__onWriteCache, name, packet)}
        self.__worker.add_task(task)

    def __onWriteCache(self, name, packet):
        try:
            startTime = time.time()
            if self.__db is not None:
                self.__db[name] = packet
            _LOG_EXECUTING_TIME(startTime, '__onWriteCache', 5.0)
        except Exception:
            LOG_CURRENT_EXCEPTION()

        self.__written_cache.discard(name)
        return

    def __postTask(self, url, remote_file, invokeAndReleaseCallbacks):
        BigWorld.callback(0.001, partial(self.__onPostTask, url, invokeAndReleaseCallbacks, remote_file))

    def __onPostTask(self, url, invokeAndReleaseCallbacks, remote_file):
        if invokeAndReleaseCallbacks:
            cbs = self.__processedCache.pop(url, [])
        else:
            cbs = self.__processedCache.get(url, [])
        for cb in cbs:
            cb(url, remote_file)
