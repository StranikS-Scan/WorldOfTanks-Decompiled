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

class AbstractCacheRecord(object):
    """
    An abstract class of cached data. Declares common interface and represents methods to
    update/extract cached data on the server. All derived classes must provide a way to restore
    cached data from the pickled string (through unpack method), to build pickled string
    from data to be cached on the server (pack method) and provide unique record ID.
    
    Note: all derived classes should be listed in the _CACHE_RECORDS map!
    
    Note: all derived classes represent data and should not contain subscriptions and other
    complicate logic (such logic should be placed into the controllers).
    
    Note: remember about security and do NOT cache private data!
    """
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, cache):
        super(AbstractCacheRecord, self).__init__()
        self.__cache = weakref.proxy(cache)

    @classmethod
    def get(cls):
        """
        Returns instance of cache record.
        :return: AbstractCacheRecord derived instance
        """
        return cls.sessionProvider.battleCache.getRecord(cls)

    @classmethod
    def getRecordID(cls):
        """
        Gets unique record ID (int)
        :return: int
        """
        raise NotImplementedError

    def unpack(self, record):
        """
        Unpacks data cached on the server by the given pickled string.
        
        :param record: A pickled string representing cached data.
        :return: True if the record is unpacked correctly, otherwise False.
        """
        raise NotImplementedError

    def pack(self):
        """
        Packs data to the pickled string to be stored on the server.
        
        :return: A pickled string representing cached data.
        """
        raise NotImplementedError

    def clear(self):
        """
        Clears inner state.
        """
        pass

    def save(self):
        """
        Pushes inner state to the server storage.
        
        :return: True if data has been cached on the server, False otherwise.
        """
        return self.__cache.save()

    def load(self):
        """
        Loads cached data from the server and updates inner state.
        
        :return: True if data has been extracted from the server, False otherwise.
        """
        return self.__cache.load()


class TmpIgnoredCacheRecord(AbstractCacheRecord):
    """
    Represents cache of accounts IDs which are in temporary ignore list
    (USER_TAG.IGNORED_TMP).
    
    Note: record size: min = 1, max = 14 * 4 + 1 = 57 bytes
         (see unpack description, 14 - max count of allies)
    """

    def __init__(self, cache):
        super(TmpIgnoredCacheRecord, self).__init__(cache)
        self._ignoredIDs = set()

    @classmethod
    def getRecordID(cls):
        return CACHE_RECORDS_IDS.TMP_IGNORED

    def unpack(self, record):
        """
        Unpack binary data. Data has  the following format: [IGNORED_COUNT, IGNORED_ITEMS], where
        IGNORED_COUNT - count of ignored players (byte), IGNORED_ITEMS - sequence of
        account IDs(IGNORED_COUNT * long(int32)).
        
        :param record: binary data to be unpacked.
        """
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
        """
        Pack set of ignored account IDs.
        
        :return: packed data in binary format.
        """
        ignoredCount = len(self._ignoredIDs)
        return struct.pack(_IGNORE_LIST_RECORD_FORMAT.format(ignoredCount), ignoredCount, *self._ignoredIDs)

    def clear(self):
        """
        Clears cache.
        """
        self._ignoredIDs.clear()

    def addToTmpIgnored(self, accDBID):
        """
        Adds the given account to the ignore list.
        
        :param accDBID: long, account ID.
        :return: True if the cache has been updated, False otherwise.
        """
        if accDBID not in self._ignoredIDs:
            self._ignoredIDs.add(accDBID)
            return True
        return False

    def removeTmpIgnored(self, accDBID):
        """
        Removes player with the given account ID from the ignore list.
        
        :param accDBID: long, account ID.
        :return: True if the cache has been updated, False otherwise.
        """
        if accDBID in self._ignoredIDs:
            self._ignoredIDs.discard(accDBID)
            return True
        return False

    def isTmpIgnored(self, accDBID):
        """
        Returns True if the given ID is in cache, False otherwise.
        
        :param accDBID: long, account ID.
        """
        return accDBID in self._ignoredIDs

    def getTmpIgnored(self):
        """
        Gets IDs of players which are in the tmp ignore list.
        
        :return: set of byte
        """
        return set(self._ignoredIDs)
