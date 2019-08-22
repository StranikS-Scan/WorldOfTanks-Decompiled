# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/battle_cache/cache_records.py
import struct
import weakref
from debug_utils import LOG_ERROR
from gui.battle_control.battle_constants import CACHE_RECORDS_IDS
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_IGNORE_LIST_SIZE_FORMAT = '<B'
_IGNORE_LIST_FORMAT = '{}L'
_IGNORE_LIST_RECORD_FORMAT = _IGNORE_LIST_SIZE_FORMAT + _IGNORE_LIST_FORMAT
_IGNORE_LIST_SIZE_LEN = struct.calcsize(_IGNORE_LIST_SIZE_FORMAT)
_MODULE_LIST_SIZE_FORMAT = '<B'
_MODULE_LIST_FORMAT = '{}i'
_MODULE_LIST_RECORD_FORMAT = _MODULE_LIST_SIZE_FORMAT + _MODULE_LIST_FORMAT
_MODULE_LIST_SIZE_LEN = struct.calcsize(_MODULE_LIST_SIZE_FORMAT)

class AbstractCacheRecord(object):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, cache):
        super(AbstractCacheRecord, self).__init__()
        self.__cache = weakref.proxy(cache)

    @classmethod
    def get(cls):
        return cls.sessionProvider.battleCache.getRecord(cls)

    @classmethod
    def getRecordID(cls):
        raise NotImplementedError

    def unpack(self, record):
        raise NotImplementedError

    def pack(self):
        raise NotImplementedError

    def clear(self):
        pass

    def save(self):
        return self.__cache.save()

    def load(self):
        return self.__cache.load()


class TmpBRProgressionCacheRecord(AbstractCacheRecord):

    def __init__(self, cache):
        super(TmpBRProgressionCacheRecord, self).__init__(cache)
        self._selectedModules = set()

    @classmethod
    def getRecordID(cls):
        return CACHE_RECORDS_IDS.TMP_PROGRESSION

    def addModule(self, value):
        if value not in self._selectedModules:
            self._selectedModules.add(value)
            return True
        return False

    def getModules(self):
        return self._selectedModules

    def pack(self):
        modulesCount = len(self._selectedModules)
        return struct.pack(_MODULE_LIST_RECORD_FORMAT.format(modulesCount), modulesCount, *self._selectedModules)

    def unpack(self, record):
        if record:
            try:
                modulesCount = struct.unpack(_IGNORE_LIST_SIZE_FORMAT, record[:_MODULE_LIST_SIZE_LEN])[0]
                if modulesCount > 0:
                    self._selectedModules = set(struct.unpack_from(_IGNORE_LIST_FORMAT.format(modulesCount), record, offset=_MODULE_LIST_SIZE_LEN))
            except struct.error as e:
                LOG_ERROR('Could not unpack the following record: ', record, e)

        else:
            self._selectedModules.clear()


class TmpIgnoredCacheRecord(AbstractCacheRecord):

    def __init__(self, cache):
        super(TmpIgnoredCacheRecord, self).__init__(cache)
        self._ignoredIDs = set()

    @classmethod
    def getRecordID(cls):
        return CACHE_RECORDS_IDS.TMP_IGNORED

    def unpack(self, record):
        if record:
            try:
                ignoredCount = struct.unpack(_IGNORE_LIST_SIZE_FORMAT, record[:_IGNORE_LIST_SIZE_LEN])[0]
                if ignoredCount > 0:
                    self._ignoredIDs = set(struct.unpack_from(_IGNORE_LIST_FORMAT.format(ignoredCount), record, offset=_IGNORE_LIST_SIZE_LEN))
            except struct.error as e:
                LOG_ERROR('Could not unpack the following record: ', record, e)

        else:
            self._ignoredIDs.clear()

    def pack(self):
        ignoredCount = len(self._ignoredIDs)
        return struct.pack(_IGNORE_LIST_RECORD_FORMAT.format(ignoredCount), ignoredCount, *self._ignoredIDs)

    def clear(self):
        self._ignoredIDs.clear()

    def addToTmpIgnored(self, accDBID):
        if accDBID not in self._ignoredIDs:
            self._ignoredIDs.add(accDBID)
            return True
        return False

    def removeTmpIgnored(self, accDBID):
        if accDBID in self._ignoredIDs:
            self._ignoredIDs.discard(accDBID)
            return True
        return False

    def isTmpIgnored(self, accDBID):
        return accDBID in self._ignoredIDs

    def getTmpIgnored(self):
        return set(self._ignoredIDs)
