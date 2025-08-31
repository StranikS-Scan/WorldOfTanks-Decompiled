# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/blueprints/FragmentTypes.py
import nations
import typing
from backports.functools_lru_cache import lru_cache
from items import vehicles, ITEM_TYPES, ITEM_TYPE_NAMES
from items.vehicles import parseIntCompactDescr, makeIntCompactDescrByID
from random_utils import wchoices
from debug_utils import LOG_DEBUG_DEV, LOG_CODEPOINT_WARNING
from . import g_cache, BlueprintsException, getAllResearchedVehicles
from BlueprintTypes import BlueprintTypes
SPECIAL_VEHICLE_ID = 255

class BlueprintFragment(object):
    __slots__ = ('nationID', 'vehTypeCD', 'total')
    FTYPE = BlueprintTypes.NONE
    nationID = property(lambda self: parseIntCompactDescr(self.vehTypeCD)[1])

    def __init__(self, vehTypeCD=0, total=0, enableException=True):
        self.vehTypeCD = vehTypeCD
        self.total = int(total)

    def getXPValueForFragments(self, count):
        pass

    def makeIntCompDescr(self, normalized=False):
        return _makeIntFragmentCompDescr(self.vehTypeCD, self.FTYPE, normalized)

    def isUniversal(self):
        return False

    def getRequiredFragmentCounts(self, count=1):
        return {}

    def getRequiredIntelligenceDataCounts(self, count=1):
        return {}

    def decayExtraFragments(self, count=1):
        return {}

    @staticmethod
    def fromIntFragmentCD(fragmentCD, enableException=True):
        fType, nationID, innationID = _parseIntFragmentCompDescr(fragmentCD)
        for cls in BlueprintFragment.__subclasses__():
            if fType == cls.FTYPE:
                return cls(makeIntCompactDescrByID('vehicle', nationID, innationID), enableException)

        raise BlueprintsException('Invalid fragment compact descriptor', fragmentCD)


class NationalBlueprintFragment(BlueprintFragment):
    __slots__ = ()
    FTYPE = BlueprintTypes.NATIONAL

    @staticmethod
    @lru_cache(maxsize=len(nations.NAMES) * 2)
    def fromNation(nationNameOrId):
        nationID = nations.INDICES.get(nationNameOrId, -1) if type(nationNameOrId) is str else nationNameOrId
        return NationalBlueprintFragment(makeIntCompactDescrByID('vehicle', nationID, SPECIAL_VEHICLE_ID))

    def __repr__(self):
        return 'nBPF:{}'.format(_parseIntFragmentCompDescr(self.vehTypeCD)[1])

    def isUniversal(self):
        return True


class VehicleBlueprintFragment(BlueprintFragment):
    __slots__ = ('progressPerFragment', 'require', 'decays', 'nationalRequiredOptions')
    FTYPE = BlueprintTypes.VEHICLE

    @staticmethod
    def fromVehicleType(vehNameOrTypeDescr, enableException=True):
        vehTypeCD = vehicles.makeVehicleTypeCompDescrByName(vehNameOrTypeDescr) if type(vehNameOrTypeDescr) is str else vehNameOrTypeDescr
        if enableException and vehTypeCD not in getAllResearchedVehicles():
            raise BlueprintsException('Cannot create blueprint for non-researched vehicle {}'.format(vehTypeCD))
        return VehicleBlueprintFragment(vehTypeCD, enableException)

    def __init__(self, vehTypeCD, enableException=True):
        super(VehicleBlueprintFragment, self).__init__(vehTypeCD)
        vehicleLevel = vehicles.getVehicleType(vehTypeCD).level
        self.total, self.progressPerFragment, self.require, self.decays, _ = _getFragmentSpecs(vehTypeCD, enableException)
        self.nationalRequiredOptions = self.__getNationalRequiredOptions(self.nationID, vehicleLevel)
        LOG_DEBUG_DEV('[BPF] VehicleFragment: total={}, progress={}, require={}'.format(self.total, self.progressPerFragment, self.require))

    def __repr__(self):
        return 'vBPF:{}/{}'.format(self.vehTypeCD, self.total)

    @property
    def asNationalCD(self):
        return _makeIntFragmentCompDescr(self.vehTypeCD, BlueprintTypes.NATIONAL, False)

    @property
    def asIntelligenceDataCD(self):
        return _makeIntFragmentCompDescr(self.vehTypeCD, BlueprintTypes.INTELLIGENCE_DATA, False)

    def getXPValueForFragments(self, count):
        return self.progressPerFragment * count if count < self.total else 1.0

    def getRequiredFragmentCounts(self, count=1):
        return dict(((t, count * r) for t, r in zip((self.asNationalCD, self.asIntelligenceDataCD), self.require)))

    def getRequiredIntelligenceDataCounts(self, count=1):
        return {self.asIntelligenceDataCD: count * self.require[1]}

    def decayExtraFragments(self, count=1):
        evts = (self.asNationalCD, self.asIntelligenceDataCD)
        weights = self.decays
        return wchoices(evts, weights).ncounts(count) if any(weights) else {}

    @staticmethod
    @lru_cache(maxsize=256)
    def __getNationalRequiredOptions(nationID, vehicleLevel):
        availableLevels = g_cache.levels
        if vehicleLevel not in availableLevels:
            return {}
        _, _, require, _, allyConversionCoefs = availableLevels.get(vehicleLevel, (0,
         0,
         (0, 0),
         (0, 0),
         {}))
        allyConversionCoefs = allyConversionCoefs.get(nations.NATION_TO_ALLIANCE_IDS_MAP[nationID], {})
        nationalRequire = require[0]
        return {NationalBlueprintFragment.fromNation(nId).makeIntCompDescr():(round(allyConversionCoefs[nId] * nationalRequire) if nId != nationID else nationalRequire) for nId in allyConversionCoefs.iterkeys()}


class IntelligenceDataFragment(BlueprintFragment):
    __slots__ = ()
    FTYPE = BlueprintTypes.INTELLIGENCE_DATA
    nationID = property(lambda self: nations.NONE_INDEX)

    def isUniversal(self):
        return True

    def __repr__(self):
        pass


def getFragmentType(ifragmentCD):
    if type(ifragmentCD) in (int, long):
        return _parseIntFragmentCompDescr(ifragmentCD)[0]
    raise BlueprintsException('Wrong fragment compact descriptor', ifragmentCD)


def fromIntFragmentCD(ifragmentCD, enableException=True):
    return BlueprintFragment.fromIntFragmentCD(ifragmentCD, enableException)


def toIntFragmentCD(fragment):
    return fragment.makeIntCompDescr(normalized=False)


def isValidFragment(maybeFragment, defaultUnlocks=()):
    if type(maybeFragment) in (int, long):
        fType = _parseIntFragmentCompDescr(maybeFragment)[0]
        if fType == BlueprintTypes.VEHICLE and defaultUnlocks:
            vehType = vehicles.getVehicleType(maybeFragment)
            if not vehType.isCollectorVehicle:
                return maybeFragment not in defaultUnlocks
        else:
            return fType in BlueprintTypes.ALL
    return False


def isUniversalFragment(maybeFragment):
    return _parseIntFragmentCompDescr(maybeFragment)[0] in BlueprintTypes.UNIVERSAL if type(maybeFragment) in (int, long) else False


def isSimilar(fragmentTypeCD1, fragmentTypeCD2, strict=True):
    if strict:
        return fragmentTypeCD1 == fragmentTypeCD2
    fType1 = getFragmentType(fragmentTypeCD1)
    fType2 = getFragmentType(fragmentTypeCD2)
    if fType1 == BlueprintTypes.VEHICLE:
        return fragmentTypeCD1 == fragmentTypeCD2
    if fType1 == BlueprintTypes.NATIONAL:
        _, nationID1, _ = _parseIntFragmentCompDescr(fragmentTypeCD1)
        _, nationID2, _ = _parseIntFragmentCompDescr(fragmentTypeCD2)
        return fType1 == fType2 and nationID1 == nationID2
    return fType1 == fType2 if fType1 == BlueprintTypes.INTELLIGENCE_DATA else False


@lru_cache(maxsize=512)
def normalizeFragment(ifragmentCD):
    fType, nationID, innationID = _parseIntFragmentCompDescr(ifragmentCD)
    vehTypeCD = makeIntCompactDescrByID('vehicle', nationID, innationID)
    return _makeIntFragmentCompDescr(vehTypeCD, fType, normalized=True)


@lru_cache(maxsize=512)
def _makeIntFragmentCompDescr(vehTypeCD, fType, normalized):
    _, nationID, innationID = _parseIntFragmentCompDescr(vehTypeCD)
    itemTypeName = ITEM_TYPE_NAMES[fType]
    if BlueprintTypes.INTELLIGENCE_DATA == fType:
        return makeIntCompactDescrByID(itemTypeName, nations.NONE_INDEX if normalized else nationID, SPECIAL_VEHICLE_ID if normalized else innationID)
    if BlueprintTypes.NATIONAL == fType:
        return makeIntCompactDescrByID(itemTypeName, nationID, SPECIAL_VEHICLE_ID if normalized else innationID)
    if BlueprintTypes.VEHICLE == fType:
        return makeIntCompactDescrByID(itemTypeName, nationID, innationID)
    LOG_CODEPOINT_WARNING(vehTypeCD, fType, normalized)


@lru_cache(maxsize=512)
def _parseIntFragmentCompDescr(fragmentCD):
    return parseIntCompactDescr(fragmentCD)


@lru_cache(maxsize=512)
def getFragmentSpecs(fragmentCD):
    fragmentCD = normalizeFragment(fragmentCD)
    isUniversal = isUniversalFragment(fragmentCD)
    total, _, _, _, _ = _getFragmentSpecs(fragmentCD)
    return (isUniversal, total)


@lru_cache(maxsize=512)
def _getFragmentSpecs(fragmentCD, enableException=True):
    total, progressPerFragment, require, decays, _ = (0,
     0,
     (0, 0),
     (0, 0),
     {})
    if getFragmentType(fragmentCD) == BlueprintTypes.VEHICLE:
        vehicleLevel = vehicles.getVehicleType(fragmentCD).level
        availableLevels = g_cache.levels
        LOG_DEBUG_DEV('_getFragmentSpecs vehicleLevel={}, availableLevels={}'.format(vehicleLevel, availableLevels))
        if enableException and vehicleLevel not in availableLevels:
            raise BlueprintsException('Invalid vehicle level for having blueprints')
        total, progressPerFragment, require, decays, _ = availableLevels.get(vehicleLevel, (0,
         0,
         (0, 0),
         (0, 0),
         {}))
    return (total,
     progressPerFragment,
     require,
     decays,
     _)
