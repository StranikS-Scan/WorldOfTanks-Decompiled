# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/arena_component_system/arena_sync_object.py
from collections import defaultdict
from debug_utils import LOG_ERROR
from shared_utils.account_helpers.diff_utils import synchronizeDicts

class AttributeDict(dict):

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            LOG_ERROR('sync data object has no key: ', item)


class ArenaSyncObject(object):
    EVENT_TYPE_DELIMITER = '.'

    def __init__(self):
        self.__cache = AttributeDict()
        self.__callbacks = defaultdict(list)

    def __getattr__(self, item):
        try:
            return self.__cache[item]
        except KeyError:
            LOG_ERROR('sync data object has no key: ', item)

    def synchronize(self, isFullSync, diff):
        if isFullSync:
            self.__cache.clear()
        changeList = {}
        changeList[''] = diff
        synchronizeDicts(diff, self.__cache, '', changeList, AttributeDict)
        self.__processChangeList(changeList)

    def addCallback(self, syncEntryID, callback):
        if callback not in self.__callbacks:
            self.__callbacks[callback] = []
        if syncEntryID not in self.__callbacks[callback]:
            self.__callbacks[callback].append(syncEntryID)
        if not syncEntryID:
            if self.__cache:
                callback(self.__cache)
        else:
            entry = self.__cache.get(syncEntryID)
            if entry is not None:
                callback(entry)
        return

    def removeCallback(self, syncEntryID, callback):
        if callback in self.__callbacks:
            if syncEntryID in self.__callbacks[callback]:
                self.__callbacks[callback].remove(syncEntryID)
            if not self.__callbacks[callback]:
                del self.__callbacks[callback]

    def getData(self, key):
        keyList = key.split(self.EVENT_TYPE_DELIMITER)
        if not keyList:
            return None
        else:
            cache = self.__cache
            for item in keyList:
                cache = cache.__getattr__(item)

            return cache

    def __processChangeList(self, changeList):
        for handler, diffpaths in self.__callbacks.iteritems():
            for diffpath in diffpaths:
                isFire, args = self.__processDiffPath(diffpath, changeList)
                if isFire:
                    handler(args)
                    break

    def __processDiffPath(self, diffpath, changeList):
        diff_ptr = changeList
        return (False, None) if diffpath not in diff_ptr else (True, diff_ptr[diffpath])
