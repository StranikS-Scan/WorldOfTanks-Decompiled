# Embedded file name: scripts/client/gui/shared/local_cache.py
import base64
import shelve
from collections import defaultdict
from contextlib import contextmanager
import os
import cPickle
from threading import Lock, Thread
import types
import zlib
import BigWorld
import Event
from debug_utils import LOG_WARNING, LOG_CURRENT_EXCEPTION, LOG_ERROR

class CacheIO(object):

    def clear(self):
        pass

    def read(self, src):
        return src

    def write(self, dst):
        return dst


class RedirectIO(CacheIO):

    def __init__(self, redirect = None):
        super(CacheIO, self).__init__()
        self._redirect = redirect or CacheIO()

    def clear(self):
        if self._redirect is not None:
            self._redirect.clear()
        return

    def read(self, src):
        result = self._doRead(src)
        if not result:
            return result
        return self._redirect.read(result)

    def write(self, dst):
        result = self._redirect.write(dst)
        if not result:
            return result
        return self._doWrite(result)

    def _doRead(self, src):
        raise NotImplementedError

    def _doWrite(self, dst):
        raise NotImplementedError


@contextmanager
def _open_file(fileName, mode = 'r'):
    try:
        fd = open(fileName, mode)
    except IOError as error:
        LOG_CURRENT_EXCEPTION()
        yield (None, error)
    else:
        try:
            yield (fd, None)
        except:
            LOG_CURRENT_EXCEPTION()
        finally:
            fd.close()

    return


class _FileIO(RedirectIO):
    __internal = {}

    def __init__(self, filePath, redirect = None):
        super(_FileIO, self).__init__(redirect)
        self._filePath = filePath

    def _doRead(self, src):
        if not self._filePath:
            return
        elif self._filePath in _FileIO.__internal:
            LOG_WARNING('Gets cache from internal property', self._filePath)
            return _FileIO.__internal[self._filePath]
        elif not os.path.isfile(self._filePath):
            return
        else:
            with _open_file(self._filePath, 'rb') as fd, error:
                if fd:
                    src = fd.read()
                else:
                    LOG_WARNING('Can not read cache', self._filePath, error)
                    src = None
            return src

    def _doWrite(self, dst):
        if not self._filePath:
            return
        else:
            with _open_file(self._filePath, 'wb') as fd, error:
                if fd:
                    fd.write(dst)
                else:
                    LOG_WARNING('Can not write cache', self._filePath, error)
                    _FileIO.__internal[self._filePath] = dst
            return fd


class _ShelveIO(RedirectIO):

    def __init__(self, filePath):
        super(_ShelveIO, self).__init__()
        self._filePath = filePath
        self._db = None
        return

    def clear(self):
        if self._db is not None:
            self._db.close()
            self._db = None
        return

    def write(self, dst):
        self._doWrite(dst)

    def _doRead(self, src):
        if not self._filePath:
            return
        else:
            try:
                self._db = src = shelve.open(self._filePath, flag='c', writeback=True)
            except Exception as error:
                LOG_WARNING('Can not read cache', self._filePath, error)
                src = None

            return src

    def _doWrite(self, _):
        if not self._filePath:
            return None
        else:
            try:
                self._db.sync()
            except Exception as error:
                LOG_WARNING('Can not write cache', self._filePath, error)

            return None


_ioMutexes = defaultdict(Lock)

def _readWorker(uniqueID, io, callback):
    with _ioMutexes[uniqueID]:
        src = io.read('')
        callback(src)


def _writeWorker(uniqueID, io, dst):
    with _ioMutexes[uniqueID]:
        io.write(dst)


class _AsyncIO(RedirectIO):

    def __init__(self, uniqueID, redirect = None):
        super(_AsyncIO, self).__init__(redirect)
        self._uniqueID = uniqueID
        self.onRead = Event.Event()

    def clear(self):
        self.onRead.clear()
        super(_AsyncIO, self).clear()

    def read(self, src):
        t = Thread(target=_readWorker, args=(self._uniqueID, self._redirect, self.onRead))
        t.start()
        return ''

    def write(self, dst):
        t = Thread(target=_writeWorker, args=(self._uniqueID, self._redirect, dst))
        t.start()
        return ''


class PickleIO(RedirectIO):

    def _doRead(self, src):
        try:
            return cPickle.loads(src)
        except cPickle.PickleError as error:
            LOG_WARNING('Can not unpickle cache', error)
            return None

        return None

    def _doWrite(self, dst):
        try:
            return cPickle.dumps(dst, -1)
        except cPickle.PickleError as error:
            LOG_WARNING('Can not pickle cache', error)
            return None

        return None


class ZipIO(RedirectIO):

    def _doRead(self, src):
        try:
            return zlib.decompress(src)
        except zlib.error as error:
            LOG_WARNING('Can not decompress cache', error)
            return None

        return None

    def _doWrite(self, dst):
        try:
            return zlib.compress(dst)
        except zlib.error as error:
            LOG_WARNING('Can not compress cache', error)
            return None

        return None


class CryptIO(RedirectIO):

    def _doRead(self, src):
        return BigWorld.wg_ucpdata(src)

    def _doWrite(self, dst):
        return BigWorld.wg_cpdata(dst)


def makeFileLocalCachePath(space, tags, fileFormat = '.dat'):
    p = os.path
    prefsFilePath = unicode(BigWorld.wg_getPreferencesFilePath(), 'utf-8', errors='ignore')
    dirPath = p.join(p.dirname(prefsFilePath), space)
    try:
        if not os.path.isdir(dirPath):
            os.makedirs(dirPath)
    except:
        LOG_CURRENT_EXCEPTION()
        return ''

    tagsType = type(tags)
    if tagsType is types.TupleType:
        fileName = ';'.join(map(lambda item: str(item), tags))
    elif tagsType in types.StringTypes:
        fileName = tags
    else:
        LOG_ERROR('Type of tags can be string, unicode or tuple', tagsType, tags)
        return ''
    if fileFormat:
        fileFormat = '.{0:>s}'.format(fileFormat)
    else:
        fileFormat = ''
    return p.join(dirPath, '{0:>s}{1:>s}'.format(base64.b32encode(fileName), fileFormat))


class FileLocalCache(object):
    __internal = {}
    __slots__ = ('_io', 'onRead')

    def __init__(self, space, tags, io = None, async = False):
        super(FileLocalCache, self).__init__()
        filePath = makeFileLocalCachePath(space, tags)
        if io:
            self._io = _FileIO(filePath, io)
        else:
            self._io = _FileIO(filePath, PickleIO())
        if async:
            self._io = _AsyncIO(filePath, redirect=self._io)
            self._io.onRead += self._onRead
        self.onRead = Event.Event()

    def clear(self):
        self._io.clear()
        self.onRead.clear()

    def read(self):
        self._onRead(self._io.read(None))
        return

    def write(self):
        self._io.write(self._getCache())

    def _onRead(self, src):
        if src:
            self._setCache(src)
            BigWorld.callback(0, self.onRead)

    def _getCache(self):
        raise NotImplemented

    def _setCache(self, data):
        raise NotImplemented


class ShelfLocalCache(object):
    __slots__ = ('_io', '_cache', '_autoflush', 'onRead', '__flushCbID')

    def __init__(self, space, tags, autoflush = 0):
        super(ShelfLocalCache, self).__init__()
        filePath = makeFileLocalCachePath(space, tags, fileFormat='')
        self._io = _AsyncIO(filePath, redirect=_ShelveIO(filePath))
        self._io.onRead += self._onRead
        self._cache = None
        self._autoflush = autoflush
        self.__flushCbID = None
        if autoflush > 0:
            self.__loadFlushCb()
        self.onRead = Event.Event()
        return

    def clear(self):
        self.__clearFlushCb()
        self._cache = None
        self._io.clear()
        self.onRead.clear()
        return

    def read(self):
        self._io.read(None)
        return

    def write(self):
        self._io.write(None)
        return

    def _onRead(self, src):
        if src is not None:
            self._cache = src
            BigWorld.callback(0, self.onRead)
        return

    def __doFlush(self):
        self.write()
        self.__loadFlushCb()

    def __loadFlushCb(self):
        self.__clearFlushCb()
        if self.__flushCbID is None:
            self.__flushCbID = BigWorld.callback(self._autoflush, self.__doFlush)
        return

    def __clearFlushCb(self):
        if self.__flushCbID is not None:
            BigWorld.cancelCallback(self.__flushCbID)
            self.__flushCbID = None
        return
