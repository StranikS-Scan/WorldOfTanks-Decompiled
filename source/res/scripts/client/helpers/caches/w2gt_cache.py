# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/caches/w2gt_cache.py
from helpers.local_cache import FileLocalCache

class W2gtCache(FileLocalCache):
    _VERSION = 1
    _PROGRESS = 'progress'

    def __init__(self):
        super(W2gtCache, self).__init__('w2gt_cache', ('w2gt_tips', W2gtCache._VERSION), isAsync=False)
        self.__cache = {}
        self.__cachedRequests = set()

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, data):
        self.__cache[key] = data

    def saveProgress(self, arenaUniqueID, playerID, data):
        self.__cache[self._PROGRESS] = {playerID: {arenaUniqueID: data}}

    def getProgress(self, arenaUniqueID, playerID):
        return self.get(self._PROGRESS, {}).get(playerID, {}).get(arenaUniqueID, {})

    def saveRequest(self, key):
        self.__cachedRequests.add(key)

    def isRequestSaved(self, key):
        return key in self.__cachedRequests

    def getData(self):
        return self.__cache

    def clear(self):
        self.__cache = None
        self.__cachedRequests = None
        super(W2gtCache, self).clear()
        return

    def get(self, key, default=None):
        return self.__cache.get(key, default)

    def _getCache(self):
        return self.__cache

    def _setCache(self, data):
        if isinstance(data, dict):
            self.__cache = data
