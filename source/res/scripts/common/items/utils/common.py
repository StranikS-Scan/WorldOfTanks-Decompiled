# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/utils/common.py
import copy
from operator import sub
from typing import Any, Dict, Tuple, Optional, List, Type, TYPE_CHECKING
from items.VehicleDescrCrew import VehicleDescrCrew
from constants import VEHICLE_TTC_ASPECTS, SITUATIONAL_BONUSES
from debug_utils import *
from items import ITEM_TYPES, EQUIPMENT_TYPES
from items import vehicles
from items import detachment_customization
from items.vehicles import vehicleAttributeFactors, VehicleDescriptor
import ResMgr
from floating_point_utils import isclose
from soft_exception import SoftException
__defaultGlossTexture = None
if TYPE_CHECKING:
    from enum import Enum

def clamp(value, minVal, maxVal):
    return max(min(value, maxVal), minVal)


def getEnumNames(enum):
    return enum.__members__.keys()


def getEnumValues(enum):
    return enum.__members__.values()


def SoftAssert(condition, errorText):
    if not condition:
        raise SoftException(errorText)


def getDefaultGlossTexture():
    global __defaultGlossTexture
    if __defaultGlossTexture is None:
        section = ResMgr.openSection('resources.xml')
        if section is None:
            return
        __defaultGlossTexture = section.readString('gameplay/projDecalDefaultGM', '')
    return __defaultGlossTexture


def getItemDescrByCompactDescr(compDescr):
    itemTypeID, _, _ = vehicles.parseIntCompactDescr(compDescr)
    if itemTypeID in vehicles.VEHICLE_ITEM_TYPES:
        descr = vehicles.getItemByCompactDescr(compDescr)
    else:
        descr = detachment_customization.getItemByCompactDescr(compDescr)
    return descr


def isItemWithCompactDescrExist(compDescr):
    itemTypeID, _, _ = vehicles.parseIntCompactDescr(compDescr)
    if itemTypeID in vehicles.VEHICLE_ITEM_TYPES:
        return vehicles.isItemWithCompactDescrExist(compDescr)
    else:
        return detachment_customization.isItemWithCompactDescrExist(compDescr)


def _makeDefaultVehicleFactors(sample):
    default = {}
    for key, value in sample.iteritems():
        if value is None:
            default[key] = value
        if isinstance(value, (float,
         int,
         long,
         str)):
            default[key] = value
        if isinstance(value, (list, tuple)):
            default[key] = value[:]
        LOG_ERROR('Default value of vehicle attribute can not be resolved', key, value)

    return default


def makeDefaultVehicleAttributeFactors():
    return vehicleAttributeFactors()


def getRadioDistance(vehicleDescr, factors):
    return vehicleDescr.radio.distance * max(factors['radio/distance'], 0.0)


def getCircularVisionRadius(vehicleDescr, factors):
    return vehicleDescr.turret.circularVisionRadius * vehicleDescr.miscAttrs['circularVisionRadiusFactor'] * max(factors['circularVisionRadius'], 0.0)


def getReloadTime(vehicleDescr, factors):
    return vehicleDescr.gun.reloadTime * vehicleDescr.miscAttrs['gunReloadTimeFactor'] * max(factors['gun/reloadTime'], 0.0)


def getClipReloadTime(vehicleDescr, factors):
    if 'clip' in vehicleDescr.gun.tags:
        factor = vehicleDescr.miscAttrs['gunReloadTimeFactor'] * max(factors['gun/reloadTime'], 0.0)
        if 'autoreload' in vehicleDescr.gun.tags:
            return tuple((reloadTime * factor for reloadTime in vehicleDescr.gun.autoreload.reloadTime))
        else:
            return (vehicleDescr.gun.reloadTime * factor,)
    else:
        return (0.0,)


def getDualGunReloadTime(vehicleDescr, factors):
    if 'dualGun' in vehicleDescr.gun.tags:
        factor = vehicleDescr.miscAttrs['gunReloadTimeFactor'] * max(factors['gun/reloadTime'], 0.0)
        return tuple((reloadTime * factor for reloadTime in vehicleDescr.gun.dualGun.reloadTimes))
    else:
        return (0.0,)


def getTurretRotationSpeed(vehicleDescr, factors):
    return vehicleDescr.turret.rotationSpeed * getTurretRotationSpeedFactor(vehicleDescr, factors)


def getTurretRotationSpeedFactor(vehicleDescr, factors):
    return max(factors['turret/rotationSpeed'], 0.0) * vehicleDescr.miscAttrs['turretRotationSpeed']


def getGunRotationSpeed(vehicleDescr, factors):
    return vehicleDescr.gun.rotationSpeed * max(factors['gun/rotationSpeed'], 0.0)


def getGunAimingTime(vehicleDescr, factors):
    return vehicleDescr.gun.aimingTime * vehicleDescr.miscAttrs['gunAimingTimeFactor'] * max(factors['gun/aimingTime'], 0.0)


def getChassisRotationSpeed(vehicleDescr, factors):
    return vehicleDescr.chassis.rotationSpeed * max(factors['vehicle/rotationSpeed'], 0.0) * max(vehicleDescr.miscAttrs['onMoveRotationSpeedFactor'], vehicleDescr.miscAttrs['onStillRotationSpeedFactor'])


def getInvisibility(vehicleDescr, factors, baseInvisibility, isMoving):
    baseValue = baseInvisibility[0 if isMoving else 1]
    additiveTerm = factors['invisibility'][0] + vehicleDescr.miscAttrs['invisibilityAdditiveTerm']
    multFactor = factors['invisibility'][1]
    return (baseValue + additiveTerm) * multFactor


def isBattleBooster(compDescr):
    itemTypeIdx, _, eqID = vehicles.parseIntCompactDescr(compDescr)
    if itemTypeIdx == ITEM_TYPES.equipment:
        equipment = vehicles.g_cache.equipments().get(eqID)
        if equipment and equipment.equipmentType == EQUIPMENT_TYPES.battleBoosters:
            return True
    return False


def isCrewBattleBooster(compDescr):
    itemTypeIdx, _, eqID = vehicles.parseIntCompactDescr(compDescr)
    if itemTypeIdx == ITEM_TYPES.equipment:
        equipment = vehicles.g_cache.equipments().get(eqID)
        if equipment and equipment.equipmentType == EQUIPMENT_TYPES.battleBoosters and 'crewSkillBattleBooster' in equipment.tags:
            return True
    return False


def spliceCompDescr(compDescr, offset, size):
    return (compDescr[offset:offset + size], offset + size)


def setBit(mask, bits, subBit=None, positive=True):
    selectedBit = bits
    if subBit is not None:
        selectedBit = 1 << getZeroBitsCount(bits) + subBit
    if positive:
        return mask | selectedBit
    else:
        return mask & ~selectedBit
        return


def getBit(mask, bits, subBit=None):
    if subBit is None:
        return isBitSet(mask, bits)
    else:
        zeroBitsCount = getZeroBitsCount(bits)
        return isBitSet(mask & bits, 1 << zeroBitsCount + subBit)
        return


def getSubBits(mask, bits):
    return (mask & bits) >> getZeroBitsCount(bits)


def isBitSet(mask, bit):
    return mask & bit > 0


def getZeroBitsCount(val):
    res = 0
    while val & 1 == 0:
        res += 1
        val /= 2

    return res


def bitsCount(val):
    count = 0
    while val:
        val &= val - 1
        count += 1

    return count


if IS_CLIENT:
    CLIENT_VEHICLE_ATTRIBUTE_FACTORS = {'camouflage': 1.0,
     'shotDispersion': 1.0}
    CLIENT_VEHICLE_ATTRIBUTE_FACTORS.update(vehicleAttributeFactors())

    class TTCVehicleDescrCrew(VehicleDescrCrew):

        def _buildFactors(self):
            crewMasteryIgnored = self._perksController.getCrewMasteryIgnored()
            if crewMasteryIgnored:
                self._affectingFactors['crewMasteryFactor'] = 0
                self._miscAttrsCrewMastery = 0
            super(TTCVehicleDescrCrew, self)._buildFactors()


    def makeDefaultClientVehicleAttributeFactors():
        return _makeDefaultVehicleFactors(CLIENT_VEHICLE_ATTRIBUTE_FACTORS)


    def _isFactor(a):
        return isinstance(a, (int, long, float))


    def _comparableFactors(original, changed):
        if all((isinstance(x, list) for x in (original, changed))):
            return all((_isFactor(a) and _isFactor(b) for a, b in zip(original, changed)))
        else:
            return _isFactor(original) and _isFactor(changed)


    def _compareFactors(original, changed):
        result = {}
        for factor in original.iterkeys():
            if not _comparableFactors(original[factor], changed[factor]):
                continue
            if all((isinstance(x, list) for x in (original[factor], changed[factor]))):
                if not all(map(isclose, original[factor], changed[factor])):
                    result[factor] = map(sub, original[factor], changed[factor])
            if not isclose(original[factor], changed[factor]):
                result[factor] = original.get(factor, CLIENT_VEHICLE_ATTRIBUTE_FACTORS[factor]) - changed[factor]

        return result


    def getClientShotDispersion(vehicleDescr, shotDispersionFactor):
        return vehicleDescr.gun.shotDispersionAngle * vehicleDescr.miscAttrs['multShotDispersionFactor'] * shotDispersionFactor


    def getClientInvisibility(vehicleDescr, vehicle, camouflageFactor, factors):
        camouflageId = None
        camouflage = vehicle.getBonusCamo()
        if camouflage is not None:
            camouflageId = camouflage.id
        baseInvisibility = vehicleDescr.computeBaseInvisibility(camouflageId, camouflageFactor)
        invisibilityFactors = factors['invisibility']
        factors['invisibility'] = invisibilityFactors[VEHICLE_TTC_ASPECTS.DEFAULT]
        moving = getInvisibility(vehicleDescr, factors, baseInvisibility, True)
        factors['invisibility'] = invisibilityFactors[VEHICLE_TTC_ASPECTS.WHEN_STILL]
        still = getInvisibility(vehicleDescr, factors, baseInvisibility, False)
        factors['invisibility'] = invisibilityFactors
        return (moving, still)


    def updateAttrFactorsWithSplit(vehicleDescr, detachmentDescr, eqs, factors, perksController=None, ignoreSituational=False):
        extras = {}
        extraAspects = {VEHICLE_TTC_ASPECTS.WHEN_STILL: ('invisibility',)}
        for aspect in extraAspects.iterkeys():
            currFactors = copy.deepcopy(factors)
            updateVehicleAttrFactors(vehicleDescr, detachmentDescr, perksController, eqs, currFactors, aspect, ignoreSituational)
            for coefficient in extraAspects[aspect]:
                extras.setdefault(coefficient, {})[aspect] = currFactors[coefficient]

        updateVehicleAttrFactors(vehicleDescr, detachmentDescr, perksController, eqs, factors, VEHICLE_TTC_ASPECTS.DEFAULT, ignoreSituational)
        for coefficientName, coefficientValue in extras.iteritems():
            coefficientValue[VEHICLE_TTC_ASPECTS.DEFAULT] = factors[coefficientName]
            factors[coefficientName] = coefficientValue


    def updateVehicleAttrFactors(vehicleDescr, detachmentDescr, perksController, eqs, factors, aspect, ignoreSituational=False):
        for eq in eqs:
            if eq is not None:
                if ignoreSituational and vehicles.getBonusID(eq.itemTypeName, eq.name) in SITUATIONAL_BONUSES:
                    continue
                eq.updateVehicleAttrFactorsForAspect(vehicleDescr, factors, aspect)

        vehicleDescr.applyOptDevFactorsForAspect(factors, aspect, ignoreSituational)
        if perksController and aspect == VEHICLE_TTC_ASPECTS.DEFAULT:
            perksController.onCollectFactors(factors)
        vehicleDescrCrew = TTCVehicleDescrCrew(vehicleDescr, perksController)
        vehicleDescrCrew.onCollectFactors(factors, defaultdict(int))
        shotDispersionFactors = [1.0, 0.0]
        vehicleDescrCrew.onCollectShotDispersionFactors(shotDispersionFactors)
        factors['shotDispersion'] = shotDispersionFactors
        return
