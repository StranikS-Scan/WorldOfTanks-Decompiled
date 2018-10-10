# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/battle_cache/__init__.py
import struct
import BigWorld
from debug_utils import LOG_DEBUG, LOG_WARNING, LOG_ERROR
from skeletons.gui.battle_session import IBattleClientCache
_CACHE_MAX_LENGTH = 4096
_RECORD_HEADER_FORMAT = 'HH'
_RECORD_HEADER_SIZE = struct.calcsize(_RECORD_HEADER_FORMAT)

class BattleClientCache(IBattleClientCache):

    def __init__(self):
        super(BattleClientCache, self).__init__()
        self.__chunks = {}
        self.__records = {}

    def getRecord(self, recordClass):
        rID = recordClass.getRecordID()
        if rID not in self.__records:
            record = recordClass(self)
            self._unpackRecord(record, self.__chunks.get(rID, None))
            self.__records[rID] = record
        else:
            record = self.__records[rID]
        return record

    def clear(self):
        for r in self.__records.itervalues():
            r.clear()

        self.__chunks = {}
        self.__records = {}

    def save(self):
        for r in self.__records.itervalues():
            chunk = self._packRecord(r)
            if chunk:
                self.__chunks[r.getRecordID()] = chunk
            self.__chunks.pop(r.getRecordID(), None)

        blob = ''.join(self.__chunks.itervalues())
        if len(blob) > _CACHE_MAX_LENGTH:
            LOG_ERROR('Could not store client cache on the server. Exceeded max size: {} > {}'.format(len(blob), _CACHE_MAX_LENGTH))
            return False
        else:
            player = BigWorld.player()
            if player is None or not hasattr(player, 'storeClientCtx'):
                LOG_DEBUG('Avatar.storeClientCtx not found', player)
                return False
            player.storeClientCtx(blob)
            return True

    def load(self):
        player = BigWorld.player()
        if player is None or not hasattr(player, 'clientCtx'):
            LOG_DEBUG('Avatar.clientCtx not found', player)
            return False
        else:
            blob = player.clientCtx
            status = True
            if blob:
                offset = 0
                while offset < len(blob):
                    recordID, recLength = self._unpackRecordHeader(offset, blob)
                    offset += _RECORD_HEADER_SIZE
                    if recLength > 0:
                        chunk = blob[offset:offset + recLength]
                        if recordID in self.__records:
                            self._unpackRecord(self.__records[recordID], chunk)
                        self.__chunks[recordID] = chunk
                    else:
                        if recordID in self.__records:
                            self.__records[recordID].clear()
                        self.__chunks.pop(recordID, None)
                    offset += recLength

            else:
                self.__chunks = {}
                for r in self.__records:
                    r.clear()

            return status

    @classmethod
    def _packRecord(cls, record):
        body = record.pack()
        header = struct.pack(_RECORD_HEADER_FORMAT, record.getRecordID(), len(body))
        return header + body

    @classmethod
    def _unpackRecordHeader(cls, offset, buf):
        try:
            recordID, recordLen = struct.unpack(_RECORD_HEADER_FORMAT, buf[offset:offset + _RECORD_HEADER_SIZE])
        except struct.error as e:
            LOG_WARNING('Could not unpack record header: ', buf[offset:offset + _RECORD_HEADER_SIZE], e)
            recordID = 0
            recordLen = 0

        return (recordID, recordLen)

    @classmethod
    def _unpackRecord(cls, record, chunk):
        status = True
        if chunk:
            try:
                record.unpack(chunk)
            except struct.error as e:
                status = False
                LOG_WARNING('Could not unpack the following record: ', chunk, e)

        else:
            record.clear()
        return status
