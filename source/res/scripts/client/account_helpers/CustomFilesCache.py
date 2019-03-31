# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/CustomFilesCache.py
# Compiled at: 2011-11-28 20:03:54
import os
import time
import base64
import urllib2
import cPickle
import BigWorld
import binascii
import threading
from debug_utils import *
from functools import partial

class NotModifiedHandler(urllib2.BaseHandler):

    def http_error_304(self, req, fp, code, message, headers):
        addinfourl = urllib2.addinfourl(fp, headers, req.get_full_url())
        addinfourl.code = code
        return addinfourl


class DownloadTask(threading.Thread):

    def __init__(self, path, last_modified, url, callback):
        super(DownloadTask, self).__init__()
        self.__path = path
        self.__last_modified = last_modified
        self.__url = url
        self.__callback = callback

    def __download(self):
        try:
            try:
                fh = None
                file = None
                last_modified = None
                path = self.__path
                if path:
                    if not os.path.isdir(path):
                        return file
                    path = os.path.join(path, self.__url)
                    if not os.path.isfile(path):
                        return file
                    fh = open(path, 'rb')
                    file = fh.read()
                elif self.__last_modified:
                    req = urllib2.Request(self.__url)
                    req.add_header('If-Modified-Since', self.__last_modified)
                    opener = urllib2.build_opener(NotModifiedHandler())
                    fh = opener.open(req)
                    headers = fh.info()
                    if hasattr(fh, 'code') and fh.code == 304:
                        last_modified = self.__last_modified
                    elif hasattr(fh, 'code') and fh.code == 200:
                        last_modified = fh.info().getheader('Last-Modified')
                        file = fh.read()
                else:
                    fh = urllib2.urlopen(self.__url)
                    last_modified = fh.info().getheader('Last-Modified')
                    file = fh.read()
            except urllib2.HTTPError as e:
                LOG_WARNING('Http error. Code: %d, url: %s' % (e.code, self.__url))
            except urllib2.URLError as e:
                LOG_WARNING('Url error. Reason: %s, url: %s' % (str(e.reason), self.__url))
            except Exception as e:
                LOG_ERROR("Client couldn't download file.", e, self.__url)

        finally:
            if fh:
                fh.close()

        return (file, last_modified)

    def run(self):
        if self.__callback is None:
            return
        else:
            file, last_modified = self.__download()
            self.__callback(file, last_modified)
            self.__callback = None
            return


class WriteTask(threading.Thread):

    def __init__(self, path, name, data, callback):
        super(WriteTask, self).__init__()
        self.__path = path
        self.__name = name
        self.__data = data
        self.__callback = callback

    def __write(self):
        fh = None
        try:
            path = self.__path
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join(path, self.__name)
            fh = open(path, 'wb')
            cPickle.dump(self.__data, fh, -1)
        except:
            LOG_CURRENT_EXCEPTION()

        if fh:
            fh.close()
        return

    def run(self):
        if self.__callback is None:
            return
        else:
            self.__write()
            self.__callback()
            self.__callback = None
            return


class PostTask(threading.Thread):

    def __init__(self, callback):
        super(PostTask, self).__init__()
        self.__callback = callback

    def run(self):
        if self.__callback is None:
            return
        else:
            time.sleep(0.1)
            self.__callback()
            self.__callback = None
            return


class CustomFilesCache(object):

    def __init__(self, version=1):
        prefsFilePath = unicode(BigWorld.wg_getPreferencesFilePath(), 'utf-8', errors='ignore')
        self.__cacheDir = os.path.join(os.path.dirname(prefsFilePath), 'custom_data')
        self.__cacheDir = os.path.normpath(self.__cacheDir)
        self.__mutex = threading.Lock()
        self.__cache = {}
        self.__tasks = {}
        self.__syncID = 0
        self.__version = version
        self.__accessed_cache = {}
        self.__processed_cache = {}
        self.__readCache()
        self.__startTimer()

    def __startTimer(self):
        self.__timer = threading.Timer(60, self.__idle)
        self.__timer.start()

    def get(self, url, life_time, callback):
        if callback is None:
            return
        else:
            startDownload = True
            try:
                self.__mutex.acquire()
                processed_cache = self.__processed_cache
                if url in processed_cache:
                    startDownload = False
                processed_cache.setdefault(url, []).append(callback)
            finally:
                self.__mutex.release()

            if startDownload:
                self.__get(url, life_time)
            return

    def __get(self, url, life_time):
        try:
            ctime = int(time.time())
            hash = base64.b32encode(url)
            self.__mutex.acquire()
            cache = self.__cache
            accessed_cache = self.__accessed_cache
            if hash in cache:
                data = cache[hash]
                if data is None:
                    self.__readLocalFile(hash, url, life_time)
                else:
                    life_time_, creation_time, _, file, __, last_modified = data
                    if not life_time_ or abs(ctime - creation_time) <= life_time_:
                        accessed_cache[hash] = ctime
                        self.__postTask(url, file)
                    else:
                        self.__readRemoteFile(url, life_time, last_modified)
            else:
                self.__readRemoteFile(url, life_time, None)
        finally:
            self.__mutex.release()

        return

    def __idle(self):
        try:
            self.__mutex.acquire()
            cache = self.__cache
            accessed_cache = self.__accessed_cache
            ctime = int(time.time())
            for k, v in accessed_cache.items():
                if v and abs(ctime - v) >= 600:
                    cache[k] = None
                    accessed_cache.pop(k, None)

        finally:
            self.__mutex.release()

        self.__startTimer()
        return

    def __getNextSyncID(self):
        self.__syncID += 1
        if self.__syncID > 1000000:
            self.__syncID = 1
        return self.__syncID

    def __readLocalFile(self, hash, url, life_time):
        syncID = self.__getNextSyncID()
        downloader = DownloadTask(self.__cacheDir, None, hash, partial(self.__onReadLocalFile, url, life_time, syncID, hash))
        self.__tasks[syncID] = downloader
        downloader.start()
        return

    def __onReadLocalFile(self, url, life_time, syncID, hash, file, last_modified):
        del self.__tasks[syncID]
        data = None
        try:
            data = cPickle.loads(file)
            life_time_, _, crc, f, ver, __ = data
            if crc != binascii.crc32(f) or life_time != life_time_ or self.__version != ver:
                raise Exception, 'Invalid data.'
        except:
            data = None

        try:
            self.__mutex.acquire()
            cache = self.__cache
            if data:
                cache[hash] = data
            else:
                cache.pop(hash, None)
                self.__accessed_cache.pop(hash, None)
        finally:
            self.__mutex.release()

        self.__get(url, life_time)
        return

    def __readRemoteFile(self, url, life_time, modified_time):
        syncID = self.__getNextSyncID()
        downloader = DownloadTask(None, modified_time, url, partial(self.__onReadRemoteFile, life_time, syncID, url))
        self.__tasks[syncID] = downloader
        downloader.start()
        return

    def __onReadRemoteFile(self, life_time, syncID, url, file, last_modified):
        del self.__tasks[syncID]
        if file is None and last_modified is None:
            self.__postTask(url, file)
            return
        else:
            hash = base64.b32encode(url)
            ctime = int(time.time())
            try:
                self.__mutex.acquire()
                cache = self.__cache
                if file is None and last_modified is not None:
                    ____, _, crc, file, __, ___ = cache[hash]
                else:
                    crc = binascii.crc32(file)
                packet = (life_time,
                 ctime,
                 crc,
                 file,
                 self.__version,
                 last_modified)
                cache[hash] = packet
            finally:
                self.__mutex.release()

            self.__writeCache(hash, packet)
            self.__get(url, life_time)
            return

    def __readCache(self):
        try:
            cacheDir = self.__cacheDir
            if not os.path.isdir(cacheDir):
                os.makedirs(cacheDir)
        except:
            LOG_CURRENT_EXCEPTION()
            return

        try:
            try:
                self.__mutex.acquire()
                cache = self.__cache
                for name in os.listdir(cacheDir):
                    fullname = os.path.join(cacheDir, name)
                    if os.path.isfile(fullname):
                        cache[name] = None

            except:
                LOG_CURRENT_EXCEPTION()

        finally:
            self.__mutex.release()

        return

    def __writeCache(self, hash, packet):
        try:
            cacheDir = self.__cacheDir
            if not os.path.isdir(cacheDir):
                os.makedirs(cacheDir)
        except:
            LOG_CURRENT_EXCEPTION()
            return

        syncID = self.__getNextSyncID()
        writer = WriteTask(self.__cacheDir, hash, packet, partial(self.__onWriteCache, syncID))
        self.__tasks[syncID] = writer
        writer.start()

    def __onWriteCache(self, syncID):
        if syncID not in self.__tasks:
            return
        del self.__tasks[syncID]

    def __postTask(self, url, file):
        syncID = self.__getNextSyncID()
        post = PostTask(partial(self.__onPostTask, syncID, url, file))
        self.__tasks[syncID] = post
        post.start()

    def __onPostTask(self, syncID, url, file):
        if syncID not in self.__tasks:
            return
        del self.__tasks[syncID]
        try:
            self.__mutex.acquire()
            for cb in self.__processed_cache.pop(url, []):
                cb(url, file)

        finally:
            self.__mutex.release()
