# Embedded file name: scripts/common/UnitRoster.py
import struct
import nations
import constants
from items import vehicles
from constants import VEHICLE_CLASS_INDICES
_BAD_CLASS_INDEX = 16

class BaseUnitRoster:
    MAX_SLOTS = 15
    MAX_CLOSED_SLOTS = 0
    MAX_EMPTY_SLOTS = 0
    MAX_UNIT_ASSEMBLER_ARTY = 15
    SLOT_TYPE = None
    DEFAULT_SLOT_PACK = None
    MIN_UNIT_POINTS_SUM = 1
    MAX_UNIT_POINTS_SUM = 10 * MAX_SLOTS
    MAX_LEGIONARIES_COUNT = 0

    def __init__(self, slotDefs = {}, slotCount = None, packedRoster = ''):
        if self.SLOT_TYPE is None:
            raise NotImplementedError()
        if slotCount is None:
            slotCount = self.MAX_SLOTS
        if packedRoster:
            self.unpack(packedRoster)
            return
        elif slotDefs and isinstance(slotDefs, dict) and len(slotDefs) <= slotCount * 2 and min(slotDefs.iterkeys()) >= 0 and max(slotDefs.iterkeys()) < slotCount * 2:
            self.slots = dict(((i, self.SLOT_TYPE(**slotDef)) for i, slotDef in slotDefs.iteritems()))
            self.pack()
            return
        else:
            if slotCount:
                self.slots = dict(((i * 2, self.SLOT_TYPE()) for i in xrange(0, slotCount)))
            else:
                self.slots = {}
            self._packed = None
            return

    def __repr__(self):
        repr = '%s( slots len=%s' % (self.__class__.__name__, len(self.slots))
        for n, slot in self.slots.iteritems():
            repr += '\n    [%d] %s' % (n, slot)

        repr += '\n)'
        return repr

    def pack(self):
        slots = self.slots
        packed = struct.pack('<B', len(slots))
        for idx, slot in slots.iteritems():
            packed += struct.pack('<B', idx)
            packed += slot.pack()

        self._packed = packed
        return packed

    def unpack(self, packed):
        self.slots = {}
        slotsLen = struct.unpack_from('<B', packed)[0]
        unpacking = packed[1:]
        for i in range(0, slotsLen):
            slot = self.SLOT_TYPE()
            idx = struct.unpack_from('<B', unpacking)[0]
            unpacking = slot.unpack(unpacking[1:])
            self.slots[idx] = slot

        lengthDiff = len(packed) - len(unpacking)
        self._packed = packed[:lengthDiff]
        return unpacking

    def getPacked(self):
        return self._packed or self.pack()

    def isDefaultSlot(self, slot):
        return slot.pack() == self.DEFAULT_SLOT_PACK

    def checkVehicleList(self, vehTypeCompDescrList, unitSlotIdx = None):
        for vehTypeCompDescr in vehTypeCompDescrList:
            res, chosenSlotIdx = self.checkVehicle(vehTypeCompDescr, unitSlotIdx)
            if res:
                return True

        return False

    def matchVehicleList(self, vehTypeCompDescrList, unitSlotIdx = None):
        matchList = []
        for vehTypeCompDescr in vehTypeCompDescrList:
            res, chosenSlotIdx = self.checkVehicle(vehTypeCompDescr, unitSlotIdx)
            if res:
                matchList.append(vehTypeCompDescr)

        return matchList

    def matchVehicleListToSlotList(self, vehTypeCompDescrList, unitSlotIdxList = []):
        matchDict = {}
        for vehTypeCompDescr in vehTypeCompDescrList:
            slotList = []
            for idx in unitSlotIdxList:
                res, chosenSlotIdx = self.__checkVehicleForUnitSlot(vehTypeCompDescr, idx)
                if res:
                    slotList.append(chosenSlotIdx)

            if slotList:
                matchDict[vehTypeCompDescr] = slotList

        return matchDict

    def matchVehicleListByLevel(self, vehTypeCompDescrList):
        matchList = []
        for vehTypeCompDescr in vehTypeCompDescrList:
            if self.checkVehicleLevel(vehTypeCompDescr):
                matchList.append(vehTypeCompDescr)

        return matchList

    def checkVehicle(self, vehTypeCompDescr, unitSlotIdx = None):
        if unitSlotIdx is None:
            for i, slot in self.slots.iteritems():
                if slot.checkVehicle(vehTypeCompDescr):
                    return (True, i / 2)

        else:
            if isinstance(unitSlotIdx, int):
                return self.__checkVehicleForUnitSlot(vehTypeCompDescr, unitSlotIdx)
            for idx in unitSlotIdx:
                res, chosenSlotIdx = self.__checkVehicleForUnitSlot(vehTypeCompDescr, idx)
                if res:
                    return (res, chosenSlotIdx)

        return (False, None)

    def checkVehicleLevel(self, vehTypeCompDescr):
        vehType = vehicles.getVehicleType(vehTypeCompDescr)
        level = vehType.level
        if level < self.SLOT_TYPE.DEFAULT_LEVELS[0] or level > self.SLOT_TYPE.DEFAULT_LEVELS[1]:
            return False
        return True

    def getLegionariesMaxCount(self):
        return self.MAX_LEGIONARIES_COUNT

    def __checkVehicleForUnitSlot(self, vehTypeCompDescr, unitSlotIdx):
        for i in (0, 1):
            rosterSlotIdx = unitSlotIdx * 2 + i
            slot = self.slots.get(rosterSlotIdx)
            if slot and slot.checkVehicle(vehTypeCompDescr):
                return (True, unitSlotIdx)

        return (False, unitSlotIdx)


_DFLT_MASK = 255

def _makeBitMask(nameList, nameIndex):
    mask = 0
    if nameList:
        for name in nameList:
            index = nameIndex.get(name, -1)
            if index >= 0:
                mask |= 1 << index

    return mask or _DFLT_MASK


def _reprBitMask(bitMask, nameList):
    repr = ''
    if bitMask:
        for i, n in enumerate(nameList):
            if 1 << i & bitMask:
                repr += n + ','

    return repr


def reprBitMaskFromDict(bitMask, nameDict):
    repr = ''
    if bitMask:
        for nameMask, name in nameDict.iteritems():
            if nameMask & bitMask == nameMask and nameMask:
                repr += name + ','

    else:
        return nameDict.get(0, '')
    return repr


def buildNamesDict(constDefClass):
    ret = {}
    for k, v in constDefClass.__dict__.iteritems():
        if k[0] != '_':
            ret[v] = k

    return ret


def _vehType__repr__(self):
    return 'VehicleType( name=%r, id=%s, vehTypeCompDescr=%s, tags=%s, level=%s, description=%r )' % (self.name,
     str(self.id),
     self.compactDescr,
     str(self.tags),
     self.level,
     getattr(self, 'description', ''))


class BaseUnitRosterSlot(object):
    __EXACT_TYPE_PREFIX = '\x00'
    DEFAULT_LEVELS = (1, 10)
    DEFAULT_NATIONS = []
    DEFAULT_VEHICLE_CLASSES = []

    def __init__(self, vehTypeCompDescr = None, nationNames = None, levels = None, vehClassNames = None, packed = ''):
        if nationNames is None:
            nationNames = self.DEFAULT_NATIONS
        if levels is None:
            levels = self.DEFAULT_LEVELS
        if vehClassNames is None:
            vehClassNames = self.DEFAULT_VEHICLE_CLASSES
        if packed:
            self.unpack(packed)
            return
        else:
            self.vehTypeCompDescr = vehTypeCompDescr
            if vehTypeCompDescr is not None:
                return
            self.nationMask = _makeBitMask(nationNames, nations.INDICES)
            self.vehClassMask = _makeBitMask(vehClassNames, constants.VEHICLE_CLASS_INDICES)
            levelRange = xrange(self.DEFAULT_LEVELS[0], self.DEFAULT_LEVELS[1] + 1)
            if isinstance(levels, int) and levels in levelRange:
                self.levels = (levels, levels)
                return
            if isinstance(levels, tuple) and len(levels) == 2:
                if levels[0] in levelRange and levels[1] in levelRange:
                    self.levels = levels
                    return
            self.levels = self.DEFAULT_LEVELS
            return

    def __repr__(self):
        if self.vehTypeCompDescr is None:
            strNations = _reprBitMask(self.nationMask, nations.NAMES)
            strVehicles = _reprBitMask(self.vehClassMask, constants.VEHICLE_CLASSES)
            return '%s( levels=%s, nationMask=0x%02X, vehClassMask=0x%02X, nations=[%s], classes=[%s] )' % (self.__class__.__name__,
             self.levels,
             self.nationMask,
             self.vehClassMask,
             strNations,
             strVehicles)
        else:
            return 'RosterSlot( vehTypeCompDescr=%s ) -- packed:%r' % (self.vehTypeCompDescr, self.pack())

    _VEHICLE_MASKS = '<BHB'
    _VEHICLE_MASKS_SIZE = struct.calcsize(_VEHICLE_MASKS)
    _VEHICLE_TYPE = '<BH'
    _VEHICLE_TYPE_SIZE = struct.calcsize(_VEHICLE_TYPE)

    def pack(self):
        if self.vehTypeCompDescr is None:
            level0, level1 = self.levels
            levelMask = level0 - 1 & 15 | (level1 - 1 & 15) << 4
            return struct.pack(self._VEHICLE_MASKS, self.vehClassMask, self.nationMask, levelMask)
        else:
            return BaseUnitRosterSlot.__EXACT_TYPE_PREFIX + struct.pack('<H', self.vehTypeCompDescr)

    def unpack(self, packed):
        if packed[0] != BaseUnitRosterSlot.__EXACT_TYPE_PREFIX:
            self.vehTypeCompDescr = None
            self.vehClassMask, self.nationMask, levelMask = struct.unpack_from(self._VEHICLE_MASKS, packed)
            level0 = (levelMask & 15) + 1
            level1 = (levelMask >> 4 & 15) + 1
            self.levels = (level0, level1)
            return packed[self._VEHICLE_MASKS_SIZE:]
        else:
            self.__dict__.clear()
            self.vehTypeCompDescr = struct.unpack_from('<H', packed, 1)[0]
            return packed[self._VEHICLE_TYPE_SIZE:]

    @staticmethod
    def getPackSize(firstByte):
        if firstByte != BaseUnitRosterSlot.__EXACT_TYPE_PREFIX:
            return BaseUnitRosterSlot._VEHICLE_MASKS_SIZE
        return BaseUnitRosterSlot._VEHICLE_TYPE_SIZE

    def checkVehicle(self, vehTypeCompDescr):
        if self.vehTypeCompDescr is not None:
            return self.vehTypeCompDescr == vehTypeCompDescr
        vehType = vehicles.getVehicleType(vehTypeCompDescr)
        if not self.nationMask & 1 << vehType.id[0]:
            return False
        level = vehType.level
        if not (self.levels[0] <= level and level <= self.levels[1]):
            return False
        classTag = vehicles.getVehicleClass(vehTypeCompDescr)
        classIndex = VEHICLE_CLASS_INDICES.get(classTag, _BAD_CLASS_INDEX)
        if not self.vehClassMask & 1 << classIndex:
            return False
        else:
            return True


_DEFAULT_ROSTER_SLOT_PACK = BaseUnitRosterSlot().pack()
