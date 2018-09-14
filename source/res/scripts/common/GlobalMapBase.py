# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/GlobalMapBase.py
import struct
import cPickle
from ops_pack import OpsUnpacker, packPascalString, unpackPascalString, initOpsFormatDef
from debug_utils import LOG_DEBUG_DEV, LOG_CURRENT_EXCEPTION

class GM_ERROR:
    WAIT_OK = -1
    OK = 0
    METHOD_COOLDOWN = 1
    BAD_METHOD = 2
    NO_CLAN = 3
    BATTLE_NOT_FOUND = 4
    UNIT_NOT_READY = 5


OK = GM_ERROR.OK
GM_ERROR_NAMES = dict([ (v, k) for k, v in GM_ERROR.__dict__.iteritems() if not k.startswith('_') ])

class GM_CLIENT_METHOD:
    SUBSCRIBE = 1
    UNSUBSCRIBE = 2
    JOIN_BATTLE = 3
    SET_DEV_MODE = 4
    KEEP_ALIVE = 5


class GM_OP:
    UNPACK_BATTLE = 1
    FINISH_BATTLE = 2
    REMOVE_BATTLE = 3
    UNPACK_BATTLE_UNIT = 4
    REMOVE_BATTLE_UNIT = 5
    ON_CLAN_RESTORED = 6


class GlobalMapBase(OpsUnpacker):
    _opsFormatDefs = initOpsFormatDef({GM_OP.UNPACK_BATTLE: ('', '_unpackBattle'),
     GM_OP.FINISH_BATTLE: ('q', '_finishBattle'),
     GM_OP.REMOVE_BATTLE: ('q', '_removeBattle'),
     GM_OP.UNPACK_BATTLE_UNIT: ('', '_unpackBattleUnit'),
     GM_OP.REMOVE_BATTLE_UNIT: ('q', '_removeBattleUnit')})
    FORMAT_HEADER = '<ii'
    SIZE_HEADER = struct.calcsize(FORMAT_HEADER)
    FORMAT_ADD_BATTLE_HEADER = '<qHii?'
    SIZE_ADD_BATTLE_HEADER = struct.calcsize(FORMAT_ADD_BATTLE_HEADER)
    FORMAT_ADD_BATTLE_UNIT_HEADER = '<qh'
    SIZE_ADD_BATTLE_UNIT_HEADER = struct.calcsize(FORMAT_ADD_BATTLE_UNIT_HEADER)

    def __init__(self):
        self._empty()

    def _empty(self):
        self.battles = {}
        self.battleUnits = {}
        self._dirty = False
        self._packed = ' '

    def __repr__(self):
        s = ''
        if self.battles:
            s += 'battles(%s)' % len(self.battles)
            for key, args in self.battles.iteritems():
                s += '\n  [%s] %s' % (key, args)

        if self.battleUnits:
            s += '\n battleUnits(%s)' % len(self.battleUnits)
        return s

    def _persist(self):
        pass

    def pack(self, isForced=False):
        if not self._dirty and not isForced:
            return self._packed
        self._dirty = False
        if self.battles:
            packed = struct.pack(self.FORMAT_HEADER, len(self.battles), len(self.battleUnits))
            fmt = self.FORMAT_ADD_BATTLE_HEADER
            for battleID, data in self.battles.iteritems():
                peripheryID = data['peripheryID']
                createTime = data['createTime']
                startTime = data['startTime']
                isFinished = data['isFinished']
                localizedData = packPascalString(cPickle.dumps(data['localizedData'], -1))
                packed += struct.pack(fmt, battleID, peripheryID, createTime, startTime, isFinished)
                packed += localizedData

            fmt = self.FORMAT_ADD_BATTLE_UNIT_HEADER
            for battleID, unitStr in self.battleUnits.iteritems():
                packed += struct.pack(fmt, battleID, len(unitStr))
                packed += unitStr

            self._packed = packed
        else:
            self._empty()
        self._persist()
        return self._packed

    def unpack(self, packedData):
        self._packed = packedData
        if len(packedData) <= 1:
            self._empty()
            return
        lenBattles, lenBattleUnits = struct.unpack_from(self.FORMAT_HEADER, packedData)
        self.battles = {}
        offset = self.SIZE_HEADER
        sz = self.SIZE_ADD_BATTLE_HEADER
        fmt = self.FORMAT_ADD_BATTLE_HEADER
        for i in xrange(lenBattles):
            battleID, peripheryID, createTime, startTime, isFinished = struct.unpack_from(fmt, packedData, offset)
            localizedDataStr, localizedDataLen = unpackPascalString(packedData, offset + sz)
            localizedData = cPickle.loads(localizedDataStr)
            offset += sz + localizedDataLen
            self.battles[battleID] = {'peripheryID': peripheryID,
             'createTime': createTime,
             'startTime': startTime,
             'isFinished': isFinished,
             'localizedData': localizedData}

        self.battleUnits = {}
        sz = self.SIZE_ADD_BATTLE_UNIT_HEADER
        fmt = self.FORMAT_ADD_BATTLE_UNIT_HEADER
        for i in xrange(lenBattleUnits):
            battleID, unitStrLen = struct.unpack_from(fmt, packedData, offset)
            offset += sz
            unitStr = packedData[offset:offset + unitStrLen]
            offset += unitStrLen
            self.battleUnits[battleID] = unitStr

        assert offset == len(packedData)

    def serialize(self):
        return {} if not self.battles else dict(battles=self.battles)

    def deserialize(self, pdata):
        if not isinstance(pdata, dict) or not pdata:
            self._empty()
            return
        self._dirty = True
        self.battles = pdata['battles']
        self.battleUnits = {}
        try:
            self.pack()
        except Exception as e:
            LOG_CURRENT_EXCEPTION()
            LOG_DEBUG_DEV('GlobalMapBase.self: %s' % repr(self))
            raise e

    def _addBattle(self, battleID, peripheryID, createTime, startTime, localizedData):
        self.battles[battleID] = {'peripheryID': peripheryID,
         'createTime': createTime,
         'startTime': startTime,
         'isFinished': False,
         'localizedData': localizedData}
        packedData = struct.pack(self.FORMAT_ADD_BATTLE_HEADER, battleID, peripheryID, createTime, startTime, False)
        packedData += packPascalString(cPickle.dumps(localizedData, -1))
        self._appendOp(GM_OP.UNPACK_BATTLE, packedData)

    def _unpackBattle(self, packedData):
        battleID, peripheryID, createTime, startTime, isFinished = struct.unpack_from(self.FORMAT_ADD_BATTLE_HEADER, packedData)
        localizedDataStr, localizedDataStrLen = unpackPascalString(packedData, self.SIZE_ADD_BATTLE_HEADER)
        self.battles[battleID] = {'peripheryID': peripheryID,
         'createTime': createTime,
         'startTime': startTime,
         'isFinished': isFinished,
         'localizedData': cPickle.loads(localizedDataStr)}
        return packedData[self.SIZE_ADD_BATTLE_HEADER + localizedDataStrLen:]

    def _finishBattle(self, battleID):
        if battleID in self.battles:
            self.battles[battleID]['isFinished'] = True
            self.battleUnits.pop(battleID, None)
            self.storeOp(GM_OP.FINISH_BATTLE, battleID)
        return

    def _removeBattle(self, battleID):
        self.battles.pop(battleID, None)
        self.battleUnits.pop(battleID, None)
        self.storeOp(GM_OP.REMOVE_BATTLE, battleID)
        return

    def _addBattleUnit(self, battleID, strUnitUpdate):
        self.battleUnits[battleID] = strUnitUpdate
        packedData = struct.pack(self.FORMAT_ADD_BATTLE_UNIT_HEADER, battleID, len(strUnitUpdate))
        packedData += strUnitUpdate
        self._appendOp(GM_OP.UNPACK_BATTLE_UNIT, packedData)

    def _unpackBattleUnit(self, packedData):
        battleID, unitStrLen = struct.unpack_from(self.FORMAT_ADD_BATTLE_UNIT_HEADER, packedData)
        begin, end = self.SIZE_ADD_BATTLE_UNIT_HEADER, self.SIZE_ADD_BATTLE_UNIT_HEADER + unitStrLen
        self.battleUnits[battleID] = packedData[begin:end]
        return packedData[end:]

    def _removeBattleUnit(self, battleID):
        self.battleUnits.pop(battleID, None)
        self.storeOp(GM_OP.REMOVE_BATTLE_UNIT, battleID)
        return
