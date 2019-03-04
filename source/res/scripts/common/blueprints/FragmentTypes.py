# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/blueprints/FragmentTypes.py
import nations
import typing
from items import vehicles, ITEM_TYPES
from random_utils import wchoices
from debug_utils import LOG_DEBUG_DEV
from . import g_cache, BlueprintsException, getAllResearchedVehicles
from BlueprintTypes import BlueprintTypes

class BlueprintFragment(object):
    __slots__ = ('nationID', 'vehTypeCD', 'total', 'isUniversal', 'getXPValueForFragments', 'makeIntCompDescr', 'getRequiredFragmentCounts', 'decayExtraFragments')
    FTYPE = BlueprintTypes.NONE
    nationID = property(lambda self: self.vehTypeCD >> 4 & 15)

    def __init__(self, vehTypeCD=0, total=0):
        self.vehTypeCD = vehTypeCD
        self.total = int(total)

    def getXPValueForFragments(self, count):
        pass

    def makeIntCompDescr(self, normalized=False):
        raise NotImplementedError

    def isUniversal(self):
        return False

    def getRequiredFragmentCounts(self, count=1):
        return {}

    def decayExtraFragments(self, count=1):
        return {}

    @staticmethod
    def fromIntFragmentCD(fragmentCD):
        myFragmentType = getFragmentType(fragmentCD)
        for cls in BlueprintFragment.__subclasses__():
            if myFragmentType == cls.FTYPE:
                return cls(ITEM_TYPES.vehicle + (fragmentCD & 65520))

        raise BlueprintsException('Invalid fragment compact descriptor', fragmentCD)


class NationalBlueprintFragment(BlueprintFragment):
    FTYPE = BlueprintTypes.NATIONAL

    @staticmethod
    def fromNation(nationNameOrId):
        nationID = nations.INDICES.get(nationNameOrId, -1) if type(nationNameOrId) is str else nationNameOrId
        return NationalBlueprintFragment(65280 + (nationID << 4) + ITEM_TYPES.vehicle)

    def __repr__(self):
        return 'nBPF:{}'.format(self.vehTypeCD >> 4 & 15)

    def isUniversal(self):
        return True

    def makeIntCompDescr(self, normalized=False):
        return ((self.vehTypeCD | 65280 if normalized else self.vehTypeCD) & 65520) + self.FTYPE


class VehicleBlueprintFragment(BlueprintFragment):
    FTYPE = BlueprintTypes.VEHICLE

    @staticmethod
    def fromVehicleType(vehNameOrTypeDescr):
        vehTypeCD = vehicles.makeVehicleTypeCompDescrByName(vehNameOrTypeDescr) if type(vehNameOrTypeDescr) is str else vehNameOrTypeDescr
        if vehTypeCD not in getAllResearchedVehicles():
            raise BlueprintsException('Cannot create blueprint for non-researched vehicle {}'.format(vehTypeCD))
        return VehicleBlueprintFragment(vehTypeCD)

    def __init__(self, vehTypeCD):
        super(VehicleBlueprintFragment, self).__init__(vehTypeCD)
        vehicleLevel = vehicles.getVehicleType(vehTypeCD).level
        availableLevels = g_cache.levels
        if vehicleLevel not in availableLevels:
            raise BlueprintsException('Invalid vehicle level for having blueprints')
        self.total, self.progressPerFragment, self.require, self.decays = availableLevels.get(vehicleLevel, (0,
         0,
         (0, 0),
         (0, 0)))
        LOG_DEBUG_DEV('[BPF] VehicleFragment: total={}, progress={}, require={}'.format(self.total, self.progressPerFragment, self.require))

    def __repr__(self):
        return 'vBPF:{}/{}'.format(self.vehTypeCD, self.total)

    @property
    def asNationalCD(self):
        return (self.vehTypeCD & 65520) + BlueprintTypes.NATIONAL

    @property
    def asIntelligenceDataCD(self):
        return (self.vehTypeCD & 65520) + BlueprintTypes.INTELLIGENCE_DATA

    def makeIntCompDescr(self, normalized=False):
        return (self.vehTypeCD & 65520) + self.FTYPE

    def getXPValueForFragments(self, count):
        return self.progressPerFragment * count if count < self.total else 1.0

    def getRequiredFragmentCounts(self, count=1):
        return dict(((t, count * r) for t, r in zip((self.asNationalCD, self.asIntelligenceDataCD), self.require)))

    def decayExtraFragments(self, count=1):
        evts = (self.asNationalCD, self.asIntelligenceDataCD)
        wghts = self.decays
        return wchoices(evts, wghts).ncounts(count) if any(wghts) else {}


class IntelligenceDataFragment(BlueprintFragment):
    FTYPE = BlueprintTypes.INTELLIGENCE_DATA
    nationID = property(lambda self: nations.NONE_INDEX)

    def makeIntCompDescr(self, normalized=False):
        return ((65521 if normalized else self.vehTypeCD) & 65520) + self.FTYPE

    def isUniversal(self):
        return True

    def __repr__(self):
        pass


def getFragmentType(ifragmentCD):
    if type(ifragmentCD) in (int, long):
        return ifragmentCD & 15
    raise BlueprintsException('Wrong fragment compact descriptor', ifragmentCD)


def fromIntFragmentCD(ifragmentCD):
    return BlueprintFragment.fromIntFragmentCD(ifragmentCD)


def toIntFragmentCD(fragment):
    return fragment.makeIntCompDescr()


def isValidFragment(maybeFragment, researchedVehicles=()):
    if type(maybeFragment) in (int, long):
        if maybeFragment & 15 == 1 and researchedVehicles:
            return maybeFragment in researchedVehicles
        else:
            return maybeFragment & 15 in BlueprintTypes.ALL
    return False


def isUniversalFragment(maybeFragment):
    return maybeFragment and maybeFragment & 15 in BlueprintTypes.UNIVERSAL if type(maybeFragment) in (int, long) else False


def isSimilar(fragmentTypeCD1, fragmentTypeCD2, strict=True):
    if strict:
        return fragmentTypeCD1 == fragmentTypeCD2
    if 15 & fragmentTypeCD1 == BlueprintTypes.VEHICLE:
        return isSimilar(fragmentTypeCD1, fragmentTypeCD2, True)
    if 15 & fragmentTypeCD1 == BlueprintTypes.NATIONAL:
        return isSimilar(fragmentTypeCD1 & 255, fragmentTypeCD2 & 255, True)
    return isSimilar(fragmentTypeCD1 & 15, fragmentTypeCD2 & 15, True) if 15 & fragmentTypeCD1 == BlueprintTypes.INTELLIGENCE_DATA else False
