# Embedded file name: scripts/client/messenger/storage/local_cache.py
import types
import Event
from account_helpers.settings_core.SettingsCache import g_settingsCache
from helpers.local_cache import FileLocalCache, PickleIO, CryptIO
_MESSENGER_CACHE_VERSION = 2
_MESSENGER_CACHE_MIN_REV = 1
_MESSENGER_CACHE_MAX_REV = 32767
_MESSENGER_CACHE_DIR = 'messenger_cache'

def _normalizeRev(rev):
    return max(min(int(rev), _MESSENGER_CACHE_MAX_REV), _MESSENGER_CACHE_MIN_REV)


class SimpleCachedStorage(object):
    __slots__ = ('onRestoredFromCache',)

    def __init__(self):
        super(SimpleCachedStorage, self).__init__()
        self.onRestoredFromCache = Event.Event()

    def init(self):
        pass

    def clear(self):
        pass

    def makeRecordInCache(self):
        return self._getCachedData()

    def restoreFromCache(self, record):
        if type(record) is not types.ListType:
            return
        restored = self._setCachedData(record)
        self.onRestoredFromCache(restored)

    def _getCachedData(self):
        raise NotImplemented

    def _setCachedData(self, data):
        raise NotImplemented


class RevCachedStorage(SimpleCachedStorage):
    __slots__ = ('__rev', '__isRevRqSent', '__record')

    def __init__(self):
        super(RevCachedStorage, self).__init__()
        self.__reset()

    def init(self):
        self.__reset()
        g_settingsCache.onSyncCompleted += self.__onSyncCompleted

    def clear(self):
        self.__reset()
        g_settingsCache.onSyncCompleted -= self.__onSyncCompleted
        super(RevCachedStorage, self).clear()

    def makeRecordInCache(self):
        if self.__rev:
            record = [self.__rev]
            record.extend(self._getCachedData())
        else:
            record = self.__record
        return record

    def restoreFromCache(self, record):
        if type(record) is not types.ListType:
            return
        else:
            self.__rev = self.__getServerRev()
            if self.__rev is None:
                self.__record = record
                return
            if not record:
                return
            prevRev = record.pop(0)
            if self.__rev == prevRev:
                self.__isRevRqSent = True
                restored = self._setCachedData(record)
                self.onRestoredFromCache(restored)
            self.__record = []
            return

    def nextRev(self):
        if self.__isRevRqSent:
            return
        else:
            if self.__rev is None:
                rev = _MESSENGER_CACHE_MIN_REV
            else:
                rev = _normalizeRev(self.__rev + 1)
            self.__isRevRqSent = True
            self.__setServerRev(rev)
            return

    def _getServerRevKey(self):
        raise NotImplementedError

    def __getServerRev(self):
        return g_settingsCache.getSetting(self._getServerRevKey(), None)

    def __setServerRev(self, rev):
        g_settingsCache.setSettings({self._getServerRevKey(): rev})

    def __reset(self):
        self.__rev = None
        self.__isRevRqSent = False
        self.__record = []
        return

    def __onSyncCompleted(self):
        rev = self.__getServerRev()
        if self.__record:
            if rev:
                self.restoreFromCache(self.__record)
            else:
                self.__setServerRev(_MESSENGER_CACHE_MIN_REV)
        elif rev:
            self.__rev = _normalizeRev(rev)


class StorageLocalCache(FileLocalCache):
    __slots__ = ('_cache',)

    def __init__(self, tags):
        super(StorageLocalCache, self).__init__(_MESSENGER_CACHE_DIR, tags, io=CryptIO(PickleIO()), async=True)
        self._cache = {}

    def clear(self):
        super(StorageLocalCache, self).clear()
        self._cache.clear()

    def addRecord(self, name, value):
        self._cache[name] = value

    def popRecord(self, name):
        return self._cache.pop(name, None)

    def _getCache(self):
        return (_MESSENGER_CACHE_VERSION, self._cache.copy())

    def _setCache(self, data):
        version, cache = data
        if version != _MESSENGER_CACHE_VERSION:
            return
        self._cache = cache
