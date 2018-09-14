# Embedded file name: scripts/client/account_helpers/CustomFilesCache.py
import os
import time
import base64
import urllib2
import cPickle
import BigWorld
import binascii
import threading
import BigWorld
from debug_utils import *
from functools import partial
from helpers import getFullClientVersion
from Queue import Queue
import shelve as provider
import random
_MIN_LIFE_TIME = 15 * 60
_MAX_LIFE_TIME = 24 * 60 * 60
_LIFE_TIME_IN_MEMORY = 20 * 60
_CACHE_VERSION = 2
_CLIENT_VERSION = getFullClientVersion()

def _LOG_EXECUTING_TIME(startTime, methodName, deltaTime = 0.1):
    finishTime = time.time()
    if finishTime - startTime > deltaTime:
        LOG_WARNING('Method "%s" takes too much time %s' % (methodName, finishTime - startTime))


def parseHttpTime(t):
    if t is None:
        return
    elif type(t) == int:
        return t
    else:
        if type(t) == str:
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


class CFC_OP_TYPE():
    DOWNLOAD = 1
    READ = 2
    WRITE = 3
    CHECK = 4


class WorkerThread(threading.Thread):

    def __init__(self):
        super(WorkerThread, self).__init__()
        self.input_queue = Queue(60)
        self.__terminate = False
        self.isBusy = False

    def add_task(self, task):
        callback = task['callback']
        try:
            self.input_queue.put(task, block=False)
        except:
            callback(None, None, None)

        return

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
                type = task['opType']
                if type == CFC_OP_TYPE.DOWNLOAD:
                    self.__run_download(**task)
                elif type == CFC_OP_TYPE.READ:
                    self.__run_read(**task)
                elif type == CFC_OP_TYPE.WRITE:
                    self.__run_write(**task)
                elif type == CFC_OP_TYPE.CHECK:
                    self.__run_check(**task)
            except:
                LOG_CURRENT_EXCEPTION()

            self.isBusy = False
            self.input_queue.task_done()

        self.input_queue.task_done()
        return

    def __run_download(self, url, modified_time, callback, **params):
        startTime = time.time()
        try:
            fh = file = None
            last_modified = expires = None
            req = urllib2.Request(url)
            req.add_header('User-Agent', _CLIENT_VERSION)
            if modified_time and type(modified_time) == str:
                req.add_header('If-Modified-Since', modified_time)
                opener = urllib2.build_opener(NotModifiedHandler())
                fh = opener.open(req, timeout=10)
                headers = fh.info()
                if hasattr(fh, 'code'):
                    code = fh.code
                    if code in (304, 200):
                        info = fh.info()
                        last_modified = info.getheader('Last-Modified')
                        expires = info.getheader('Expires')
                    if code == 200:
                        file = fh.read()
            else:
                opener = urllib2.build_opener(urllib2.BaseHandler())
                fh = opener.open(req, timeout=10)
                info = fh.info()
                last_modified = info.getheader('Last-Modified')
                expires = info.getheader('Expires')
                file = fh.read()
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
            LOG_WARNING('Url error. Reason: %s, url: %s' % (str(e.reason), url))
        except Exception as e:
            LOG_ERROR("Client couldn't download file.", e, url)
        finally:
            if fh:
                fh.close()

        _LOG_EXECUTING_TIME(startTime, '__run_download', 10.0)
        callback(file, last_modified, expires)
        return

    def __run_read(self, name, db, callback, **params):
        file = None
        try:
            startTime = time.time()
            if db is not None and db.has_key(name):
                file = db[name]
            _LOG_EXECUTING_TIME(startTime, '__run_read')
        except Exception as e:
            LOG_WARNING("Client couldn't read file.", e, name)

        callback(file, None, None)
        return

    def __run_write(self, name, data, db, callback, **params):
        try:
            startTime = time.time()
            if db is not None:
                db[name] = data
            _LOG_EXECUTING_TIME(startTime, '__run_write', 5.0)
        except:
            LOG_CURRENT_EXCEPTION()

        callback(None, None, None)
        return

    def __run_check(self, name, db, callback, **params):
        res = False
        try:
            startTime = time.time()
            if db is not None:
                res = db.has_key(name)
            _LOG_EXECUTING_TIME(startTime, '__run_check')
        except:
            LOG_CURRENT_EXCEPTION()

        callback(res, None, None)
        return


class ThreadPool():

    def __init__(self, num = 8):
        num = max(2, num)
        self.__workers = []
        for i in range(num):
            self.__workers.append(WorkerThread())

    def start(self):
        for w in self.__workers:
            w.start()

    def close(self):
        for w in self.__workers:
            w.close()

        self.__workers = []

    def add_task(self, task):
        if len(self.__workers) == 0:
            return
        type = task['opType']
        if type in (CFC_OP_TYPE.WRITE, CFC_OP_TYPE.READ, CFC_OP_TYPE.CHECK):
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

    def __init__(self):
        prefsFilePath = unicode(BigWorld.wg_getPreferencesFilePath(), 'utf-8', errors='ignore')
        self.__cacheDir = os.path.join(os.path.dirname(prefsFilePath), 'custom_data')
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
            except:
                LOG_CURRENT_EXCEPTION()

            _LOG_EXECUTING_TIME(startTime, 'close')
            self.__db = None
        return

    def __startTimer(self):
        self.__timer = BigWorld.callback(60, self.__idle)

    def get(self, url, callback, showImmediately = False):
        if callback is None:
            return
        else:
            startDownload = True
            if url in self.__processedCache:
                startDownload = False
            self.__processedCache.setdefault(url, []).append(callback)
            if startDownload:
                self.__get(url, showImmediately, False)
            return

    def __get(self, url, showImmediately, checkedInCache):
        try:
            ctime = getSafeDstUTCTime()
            hash = base64.b32encode(url)
            self.__mutex.acquire()
            cache = self.__cache
            if hash in cache:
                data = cache[hash]
                if data is None:
                    LOG_DEBUG('readLocalFile, there is no file in memory.', url)
                    self.__readLocalFile(url, showImmediately)
                else:
                    self.__accessedCache[hash] = ctime
                    expires, creation_time, _, file, _, last_modified = data
                    expires = parseHttpTime(expires)
                    if expires is None:
                        LOG_ERROR('Unable to parse expires time.', url)
                        self.__postTask(url, None, True)
                        return
                    if ctime - _MIN_LIFE_TIME <= expires <= ctime + _MAX_LIFE_TIME + _MIN_LIFE_TIME:
                        LOG_DEBUG('postTask, Sends file to requester.', url, last_modified, data[0])
                        self.__postTask(url, file, True)
                    else:
                        if showImmediately:
                            LOG_DEBUG('postTask, Do not release callbacks. Sends file to requester.', url, last_modified, data[0])
                            self.__postTask(url, file, False)
                        LOG_DEBUG('readRemoteFile, there is file in cache, check last_modified field.', url, last_modified, data[0])
                        self.__readRemoteFile(url, last_modified, showImmediately)
            elif checkedInCache:
                LOG_DEBUG('readRemoteFile, there is no file in cache.', url)
                self.__readRemoteFile(url, None, False)
            else:
                LOG_DEBUG('checkFile. Checking file in cache.', url, showImmediately)
                self.__checkFile(url, showImmediately)
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
         'db': self.__db,
         'name': base64.b32encode(url),
         'callback': partial(self.__onReadLocalFile, url, showImmediately)}
        self.__worker.add_task(task)

    def __onReadLocalFile(self, url, showImmediately, file, d1, d2):
        data = file
        try:
            crc, f, ver = data[2:5]
            if crc != binascii.crc32(f) or _CACHE_VERSION != ver:
                LOG_DEBUG('Old file was found.', url)
                raise Exception, 'Invalid data.'
        except:
            data = None

        try:
            hash = base64.b32encode(url)
            self.__mutex.acquire()
            cache = self.__cache
            if data is not None:
                cache[hash] = data
            else:
                cache.pop(hash, None)
                self.__accessedCache.pop(hash, None)
        finally:
            self.__mutex.release()

        self.__get(url, showImmediately, True)
        return

    def __checkFile(self, url, showImmediately):
        task = {'opType': CFC_OP_TYPE.CHECK,
         'db': self.__db,
         'name': base64.b32encode(url),
         'callback': partial(self.__onCheckFile, url, showImmediately)}
        self.__worker.add_task(task)

    def __onCheckFile(self, url, showImmediately, res, d1, d2):
        if res is None:
            self.__postTask(url, None, True)
            return
        else:
            if res:
                try:
                    hash = base64.b32encode(url)
                    self.__mutex.acquire()
                    self.__cache[hash] = None
                finally:
                    self.__mutex.release()

            self.__get(url, showImmediately, True)
            return

    def __readRemoteFile(self, url, modified_time, showImmediately):
        task = {'opType': CFC_OP_TYPE.DOWNLOAD,
         'url': url,
         'modified_time': modified_time,
         'callback': partial(self.__onReadRemoteFile, url, showImmediately)}
        self.__worker.add_task(task)

    def __onReadRemoteFile(self, url, showImmediately, file, last_modified, expires):
        if file is None and last_modified is None:
            if showImmediately:
                LOG_DEBUG('__onReadRemoteFile, Error occurred. Release callbacks.', url)
                self.__processedCache.pop(url, None)
            else:
                self.__postTask(url, None, True)
            return
        else:
            hash = base64.b32encode(url)
            ctime = getSafeDstUTCTime()
            fileChanged = False
            try:
                self.__mutex.acquire()
                cache = self.__cache
                if file is None and last_modified is not None:
                    value = cache.get(hash, None)
                    if value is None:
                        LOG_WARNING('File is expected in cache, but there is no file')
                        self.__postTask(url, None, True)
                        return
                    crc, file = value[2:4]
                else:
                    crc = binascii.crc32(file)
                    fileChanged = True
                packet = (expires,
                 ctime,
                 crc,
                 file,
                 _CACHE_VERSION,
                 last_modified)
                cache[hash] = packet
            finally:
                self.__mutex.release()

            LOG_DEBUG('writeCache', url, last_modified, expires)
            self.__writeCache(hash, packet)
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
        except:
            LOG_CURRENT_EXCEPTION()

    def __writeCache(self, name, packet):
        if name in self.__written_cache:
            return
        self.__written_cache.add(name)
        task = {'opType': CFC_OP_TYPE.WRITE,
         'db': self.__db,
         'name': name,
         'data': packet,
         'callback': partial(self.__onWriteCache, name)}
        self.__worker.add_task(task)

    def __onWriteCache(self, name, d1, d2, d3):
        self.__written_cache.discard(name)

    def __postTask(self, url, file, invokeAndReleaseCallbacks):
        BigWorld.callback(0.001, partial(self.__onPostTask, url, invokeAndReleaseCallbacks, file))

    def __onPostTask(self, url, invokeAndReleaseCallbacks, file):
        if invokeAndReleaseCallbacks:
            cbs = self.__processedCache.pop(url, [])
        else:
            cbs = self.__processedCache.get(url, [])
        for cb in cbs:
            cb(url, file)
