# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/UnitRoster.py
import struct
import nations
from items import vehicles
from constants import VEHICLE_CLASSES, VEHICLE_CLASS_INDICES
_BAD_CLASS_INDEX = 16

class BaseUnitRoster:
    MAX_SLOTS = 15
    MAX_CLOSED_SLOTS = 0
    MAX_EMPTY_SLOTS = 0
    MAX_UNIT_ASSEMBLER_ARTY = MAX_SLOTS
    SLOT_TYPE = None
    DEFAULT_SLOT_PACK = None
    LIMITS_TYPE = None
    MIN_UNIT_POINTS_SUM = 1
    MAX_UNIT_POINTS_SUM = 10 * MAX_SLOTS
    MAX_LEGIONARIES_COUNT = 0
    MIN_VEHICLES = 1
    MAX_VEHICLES = 1

    def __init__(self, limitsDefs={}, slotDefs={}, slotCount=None, packedRoster=''):
        if self.SLOT_TYPE is None and self.LIMITS_TYPE is None:
            raise NotImplementedError()
        if packedRoster:
            self.unpack(packedRoster)
            return
        else:
            self.limits = self.LIMITS_TYPE(**limitsDefs)
            if slotCount is None:
                slotCount = self.limits.get('maxSlotCount', self.MAX_SLOTS)
            if slotDefs and isinstance(slotDefs, dict) and len(slotDefs) <= slotCount * 2 and min(slotDefs.iterkeys()) >= 0 and max(slotDefs.iterkeys()) < slotCount * 2:
                self.slots = dict(((i, self.SLOT_TYPE(**slotDef)) for i, slotDef in slotDefs.iteritems()))
                self.pack()
                return
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
        repr += '\n limits: %s' % self.limits
        return repr

    def pack(self):
        slots = self.slots
        packed = struct.pack('<B', len(slots))
        for idx, slot in slots.iteritems():
            packed += struct.pack('<B', idx)
            packed += slot.pack()

        packed += self.limits.pack()
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

        self.limits = self.LIMITS_TYPE()
        unpacking = self.limits.unpack(unpacking)
        lengthDiff = len(packed) - len(unpacking)
        self._packed = packed[:lengthDiff]
        return unpacking

    def getPacked(self):
        return self._packed or self.pack()

    def isDefaultSlot(self, slot):
        return slot.pack() == self.DEFAULT_SLOT_PACK

    def checkVehicleList(self, vehTypeCompDescrList, unitSlotIdx=None):
        for vehTypeCompDescr in vehTypeCompDescrList:
            res, chosenSlotIdx = self.checkVehicle(vehTypeCompDescr, unitSlotIdx)
            if res:
                return True

        return False

    def matchVehicleList(self, vehTypeCompDescrList, unitSlotIdx=None):
        matchList = []
        for vehTypeCompDescr in vehTypeCompDescrList:
            res, chosenSlotIdx = self.checkVehicle(vehTypeCompDescr, unitSlotIdx)
            if res:
                matchList.append(vehTypeCompDescr)

        return matchList

    def matchVehicleListToSlotList(self, vehTypeCompDescrList, unitSlotIdxList=[]):
        matchDict = {}
        for vehTypeCompDescr in vehTypeCompDescrList:
            if not self.limits.checkVehicle(vehTypeCompDescr):
                continue
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

    def checkVehicle(self, vehTypeCompDescr, unitSlotIdx=None):
        if not self.limits.checkVehicle(vehTypeCompDescr):
            return (False, unitSlotIdx)
        else:
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
        vehClass = vehicles.getVehicleClass(vehTypeCompDescr)
        vehClassIdx = VEHICLE_CLASS_INDICES[vehClass]
        vehLevel = vehicles.getVehicleType(vehTypeCompDescr).level
        if not self.limits.checkVehicleLevel(vehClassIdx, vehLevel):
            return False
        return False if not self.SLOT_TYPE.DEFAULT_LEVELS[0] <= vehLevel <= self.SLOT_TYPE.DEFAULT_LEVELS[1] else True

    def getLegionariesMaxCount(self):
        return self.MAX_LEGIONARIES_COUNT

    def __checkVehicleForUnitSlot(self, vehTypeCompDescr, unitSlotIdx):
        for i in (0, 1):
            rosterSlotIdx = unitSlotIdx * 2 + i
            slot = self.slots.get(rosterSlotIdx)
            if slot and slot.checkVehicle(vehTypeCompDescr):
                return (True, unitSlotIdx)

        return (False, unitSlotIdx)


def _makeBitMask(nameList, nameIndex, power=8):
    mask = 0
    if nameList:
        for name in nameList:
            index = nameIndex.get(name, -1)
            if index >= 0:
                mask |= 1 << index

    _DFLT_MASK = (1 << power) - 1
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
    NATION_MASK_POWER = 16
    VEH_CLASS_MASK_POWER = 8

    def __init__(self, vehTypeCompDescr=None, nationNames=None, levels=None, vehClassNames=None, packed=''):
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
            self.nationMask = _makeBitMask(nationNames, nations.INDICES, self.NATION_MASK_POWER)
            self.vehClassMask = _makeBitMask(vehClassNames, VEHICLE_CLASS_INDICES, self.VEH_CLASS_MASK_POWER)
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
            strVehicles = _reprBitMask(self.vehClassMask, VEHICLE_CLASSES)
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

    def isNationMaskFull(self):
        return self.nationMask == _makeBitMask(self.DEFAULT_NATIONS, nations.INDICES, self.NATION_MASK_POWER)

    def isVehClassMaskFull(self):
        return self.vehClassMask == _makeBitMask(self.DEFAULT_VEHICLE_CLASSES, VEHICLE_CLASS_INDICES, self.VEH_CLASS_MASK_POWER)

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
        return BaseUnitRosterSlot._VEHICLE_MASKS_SIZE if firstByte != BaseUnitRosterSlot.__EXACT_TYPE_PREFIX else BaseUnitRosterSlot._VEHICLE_TYPE_SIZE

    def checkVehicle(self, vehTypeCompDescr):
        if self.vehTypeCompDescr is not None:
            return self.vehTypeCompDescr == vehTypeCompDescr
        else:
            vehType = vehicles.getVehicleType(vehTypeCompDescr)
            if not self.nationMask & 1 << vehType.id[0]:
                return False
            level = vehType.level
            if not (self.levels[0] <= level and level <= self.levels[1]):
                return False
            classTag = vehicles.getVehicleClass(vehTypeCompDescr)
            classIndex = VEHICLE_CLASS_INDICES.get(classTag, _BAD_CLASS_INDEX)
            return False if not self.vehClassMask & 1 << classIndex else True


_DEFAULT_ROSTER_SLOT_PACK = BaseUnitRosterSlot().pack()

class BaseUnitRosterLimits(object):
    _ROSTER_LIMIT_NAMES = ['maxSlotCount',
     'maxEmptySlotCount',
     'totalLevelLimits',
     'vehicleLevelLimits',
     'vehicleLevelLimitsByClass',
     'vehicleClasses',
     'vehicleNations',
     'vehicleTypes']
    _ROSTER_LIMIT_INDICES = dict(((x[1], x[0]) for x in enumerate(_ROSTER_LIMIT_NAMES)))
    _LIMITS_PACK_FORMAT = {'maxSlotCount': ('<B', 1),
     'maxEmptySlotCount': ('<B', 1),
     'totalLevelLimits': ('<2H', 4),
     'vehicleLevelLimits': ('<2H', 4),
     'vehicleLevelLimitsByClass': (('<B', 1), ('<B2H', 5)),
     'vehicleClasses': ('<B', 1),
     'vehicleNations': ('<H', 2),
     'vehicleTypes': (('<H', 2), ('<H2B', 4))}

    def __init__(self, **limitsDefs):
        assert all((key in self._ROSTER_LIMIT_NAMES for key in limitsDefs.iterkeys()))
        limits = self.limits = {key:value for key, value in limitsDefs.iteritems() if value is not None}
        if not limits:
            self.mask = 0
            return
        else:
            self.mask = _makeBitMask(limits.keys(), self._ROSTER_LIMIT_INDICES)
            vehicleLevelLimitsByClass = limits.pop('vehicleLevelLimitsByClass', None)
            if vehicleLevelLimitsByClass is not None:
                limits['vehicleLevelLimitsByClass'] = {VEHICLE_CLASS_INDICES[key]:value for key, value in vehicleLevelLimitsByClass.iteritems()}
            vehicleClasses = limits.pop('vehicleClasses', None)
            if vehicleClasses is not None:
                limits['vehicleClasses'] = _makeBitMask(vehicleClasses, VEHICLE_CLASS_INDICES)
            vehicleNations = limits.pop('vehicleNations', None)
            if vehicleNations is not None:
                limits['vehicleNations'] = _makeBitMask(vehicleNations, nations.INDICES, 16)
            return

    def __repr__(self):
        return str(self.limits) if self.mask != 0 else 'NO LIMITS'

    def _packLimit(self, limitName):
        limitValue = self.limits.get(limitName)
        if limitValue is None:
            return ''
        else:
            packFormat = self._LIMITS_PACK_FORMAT[limitName]
            if limitName in ('vehicleLevelLimitsByClass', 'vehicleTypes'):
                (lenFormat, _), (limitFormat, _) = packFormat
                packed = struct.pack(lenFormat, len(limitValue))
                for key, (lowerBound, upperBound) in limitValue.iteritems():
                    packed += struct.pack(limitFormat, key, lowerBound, upperBound)

                return packed
            isTuple = limitName in ('totalLevelLimits', 'vehicleLevelLimits')
            return struct.pack(packFormat[0], *(limitValue if isTuple else (limitValue,)))
            return

    def pack(self):
        mask = self.mask
        packed = struct.pack('<H', mask)
        if mask != 0:
            for limitName in self._ROSTER_LIMIT_NAMES:
                packed += self._packLimit(limitName)

        return packed

    def _unpackLimit(self, limitName, packed):
        limits = self.limits
        packFormat = self._LIMITS_PACK_FORMAT[limitName]
        if limitName in ('vehicleLevelLimitsByClass', 'vehicleTypes'):
            (lenFormat, lenSize), (limitFormat, limitSize) = packFormat
            length = struct.unpack_from(lenFormat, packed)[0]
            packed = packed[lenSize:]
            subLimits = limits[limitName] = {}
            for idx in xrange(length):
                key, lowerBound, upperBound = struct.unpack_from(limitFormat, packed)
                subLimits[key] = (lowerBound, upperBound)
                packed = packed[limitSize:]

            return packed
        else:
            limitValue = struct.unpack_from(packFormat[0], packed)
            isTuple = limitName in ('totalLevelLimits', 'vehicleLevelLimits')
            limits[limitName] = limitValue if isTuple else limitValue[0]
            return packed[packFormat[1]:]

    def unpack(self, packed):
        mask = self.mask = struct.unpack_from('<H', packed)[0]
        packed = packed[2:]
        if mask == 0:
            return packed
        for limitName in self._ROSTER_LIMIT_NAMES:
            if 1 << self._ROSTER_LIMIT_INDICES[limitName] & mask:
                packed = self._unpackLimit(limitName, packed)

        return packed

    def get(self, limitName, defaultValue=None):
        assert limitName in self._ROSTER_LIMIT_NAMES
        return defaultValue if self.mask == 0 else self.limits.get(limitName, defaultValue)

    def checkVehicleLevel(self, vehicleClassIdx, vehicleLevel):
        if self.mask == 0:
            return True
        vehicleLevelLimitsByClass = self.limits.get('vehicleLevelLimitsByClass', None)
        if vehicleLevelLimitsByClass is not None:
            vehicleLevelClassLimits = vehicleLevelLimitsByClass.get(vehicleClassIdx, None)
            if vehicleLevelClassLimits is not None:
                return vehicleLevelClassLimits[0] <= vehicleLevel <= vehicleLevelClassLimits[1]
        vehicleLevelLimits = self.limits.get('vehicleLevelLimits', None)
        if vehicleLevelLimits is not None:
            return vehicleLevelLimits[0] <= vehicleLevel <= vehicleLevelLimits[1]
        else:
            return True

    def _checkVehicleClass(self, vehicleClassIdx):
        vehicleClasses = self.limits.get('vehicleClasses', 0)
        return True if vehicleClasses == 0 else vehicleClasses & 1 << vehicleClassIdx

    def _checkVehicleNation(self, vehicleNationIdx):
        vehicleNations = self.limits.get('vehicleNations', 0)
        return True if vehicleNations == 0 else vehicleNations & 1 << vehicleNationIdx

    def _checkVehicleType(self, vehTypeCompDescr):
        vehicleTypes = self.limits.get('vehicleTypes', None)
        return True if vehicleTypes is None else vehTypeCompDescr in vehicleTypes

    def checkVehicle(self, vehTypeCompDescr):
        if self.mask == 0:
            return True
        if not self._checkVehicleType(vehTypeCompDescr):
            return False
        vehType = vehicles.getVehicleType(vehTypeCompDescr)
        if not self._checkVehicleNation(vehType.id[0]):
            return False
        vehClass = vehicles.getVehicleClass(vehTypeCompDescr)
        vehClassIdx = VEHICLE_CLASS_INDICES[vehClass]
        if not self._checkVehicleClass(vehClassIdx):
            return False
        vehLevel = vehType.level
        return False if not self.checkVehicleLevel(vehClassIdx, vehLevel) else True
