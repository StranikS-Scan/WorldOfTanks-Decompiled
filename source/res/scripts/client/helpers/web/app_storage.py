# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/web/app_storage.py
import os
import shutil
import logging
from functools import partial
import BigWorld
from helpers import threads
from helpers.web.storage import IStorage
from debug_utils import LOG_CURRENT_EXCEPTION
from soft_exception import SoftException
from external_strings_utils import unicode_from_utf8
_logger = logging.getLogger(__name__)
_CACHE_WARNING_GAP_IN_MB = 500

def _expectDir(path):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
        elif not os.path.isdir(path):
            raise SoftException('path "{}" exists, but it is not a directory'.format(path))
    except (IOError, OSError, SoftException):
        LOG_CURRENT_EXCEPTION()
        raise


class _WriteFileJob(threads.Job):

    def __init__(self, filename, data, callback):
        super(_WriteFileJob, self).__init__()
        self.__filename = filename
        self.__data = data
        self.__callback = callback

    def doWork(self, worker):
        stored = False
        try:
            try:
                dirPath = os.path.dirname(self.__filename)
                _expectDir(dirPath)
                with open(self.__filename, 'wb') as f:
                    f.write(self.__data)
                    stored = True
            except (IOError, OSError):
                LOG_CURRENT_EXCEPTION()

        finally:
            BigWorld.callback(0.0, partial(self.__callback, self.__filename, stored))


class AsynchFileStorage(IStorage):

    def __init__(self, name, worker):
        _expectDir(name)
        self.__name = name
        self.__worker = worker

    def close(self):
        self.__name = None
        self.__worker = None
        return

    def add(self, name, data, callback):
        filename = os.path.join(self.__name, name)
        self.__write(filename, data, callback)

    def remove(self, name):
        filename = os.path.join(self.__name, name)
        os.remove(filename)

    def isStored(self, name):
        filename = os.path.join(self.__name, name)
        return os.path.isfile(filename)

    def getAll(self):
        files = []
        if os.path.isdir(self.__name):
            files = [ f for f in os.listdir(self.__name) if os.path.isfile(os.path.join(self.__name, f)) ]
        return files

    def setWorker(self, worker):
        self.__worker = worker

    def __write(self, filename, data, callback):
        self.__worker.putJob(_WriteFileJob(filename, data, callback))


class ApplicationStorage(object):

    def __init__(self, name, workersLimit, queueLimit=threads.INFINITE_QUEUE_SIZE):
        prefsPath = unicode_from_utf8(BigWorld.wg_getPreferencesFilePath())[1]
        self._prefsDirPath = os.path.normpath(os.path.dirname(prefsPath))
        self.__cacheDir = os.path.normpath(os.path.join(self._prefsDirPath, name))
        _expectDir(self.__cacheDir)
        self.__worker = threads.ThreadPool(workersLimit, queueLimit)
        self.__worker.start()
        self.__db = {}

    def close(self):
        for i in self.__db.itervalues():
            i.close()

        self.__db = {}
        self.__cacheDir = {}
        self.stopWorker()

    def stopWorker(self):
        if self.__worker:
            self.__worker.stop()
            self.__worker = None
        return

    def restartWorker(self, workersLimit, queueLimit=threads.INFINITE_QUEUE_SIZE):
        if self.__worker is None:
            self.__worker = threads.ThreadPool(workersLimit, queueLimit)
            self.__worker.start()
            for storage in self.__db.itervalues():
                storage.setWorker(self.__worker)

        return

    @property
    def rootDirPath(self):
        return self._prefsDirPath

    def load(self):
        cache = {}
        cacheSize = 0
        _logger.info('WebCache start loading from disk...')
        dirs = os.listdir(self.__cacheDir)
        for entry in dirs:
            curdir = os.path.join(self.__cacheDir, entry)
            if os.path.isdir(curdir):
                subdirs = os.listdir(curdir)
                for subentry in subdirs:
                    subdir = os.path.join(curdir, subentry)
                    if os.path.isfile(subdir):
                        cacheSize += os.path.getsize(subdir)
                        cache[subentry] = subdir
                        continue
                    if os.path.isdir(subdir):
                        shutil.rmtree(subdir, True)

                if not os.listdir(curdir):
                    os.rmdir(curdir)
                self.addApp(entry)
                continue
            if os.path.isfile(curdir):
                os.remove(curdir)

        cacheSizeInMb = cacheSize / 1024 / 1024
        if cacheSizeInMb > 0:
            _logger.log(logging.WARNING if cacheSizeInMb > _CACHE_WARNING_GAP_IN_MB else logging.INFO, 'WebCache size on disk: %.1f Mb', cacheSizeInMb)
        else:
            _logger.info('WebCache is empty')
        _logger.info('WebCache loading finished')
        return cache

    def getApp(self, appName):
        return self.addApp(appName)

    def addApp(self, appName):
        if appName not in self.__db:
            folder = os.path.join(self.__cacheDir, appName)
            self.__db[appName] = AsynchFileStorage(folder, self.__worker)
        return self.__db[appName]

    def removeApp(self, appName):
        if appName in self.__db:
            app = self.__db.pop(appName)
            app.close()
        shutil.rmtree(os.path.join(self.__cacheDir, appName), True)

    def getApps(self):
        return set(self.__db.keys())

    def addAppFile(self, appName, key, data, callback):
        app = self.getApp(appName)
        app.add(key, data, callback)

    def removeAppFile(self, appName, filename):
        return self.__db[appName].remove(filename)

    def getAppFiles(self, appName):
        files = []
        if appName in self.__db:
            files = self.__db[appName].getAll()
        return set(files)

    def isAppFileExist(self, appName, filename):
        return self.__db[appName].isStored(filename) if appName in self.__db else False

    def isFileExist(self, filename):
        return os.path.isfile(filename)
