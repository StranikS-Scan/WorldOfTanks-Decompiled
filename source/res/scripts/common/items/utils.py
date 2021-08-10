# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/utils.py
import copy
from operator import sub
from typing import Any, Dict, Tuple
from VehicleDescrCrew import VehicleDescrCrew
from constants import VEHICLE_TTC_ASPECTS
from debug_utils import *
from items import tankmen
from items import vehicles
from items.tankmen import MAX_SKILL_LEVEL, MIN_ROLE_LEVEL
from items.vehicles import vehicleAttributeFactors, VehicleDescriptor
import ResMgr
__defaultGlossTexture = None

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
        descr = tankmen.getItemByCompactDescr(compDescr)
    return descr


def isItemWithCompactDescrExist(compDescr):
    itemTypeID, _, _ = vehicles.parseIntCompactDescr(compDescr)
    if itemTypeID in vehicles.VEHICLE_ITEM_TYPES:
        return vehicles.isItemWithCompactDescrExist(compDescr)
    else:
        return tankmen.isItemWithCompactDescrExist(compDescr)


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


def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def generateDefaultCrew(vehicleType, level):
    nationID, vehicleTypeID = vehicleType.id
    skills = ()
    passport = (nationID,
     False,
     False,
     0,
     0,
     0)
    res = []
    for roles in vehicleType.crewRoles:
        cd = tankmen.generateCompactDescr(passport, vehicleTypeID, roles[0], level, skills, level)
        res.append(tankmen.stripNonBattle(cd))

    return tuple(res)


def _generateTankman(vehicleDescr, roles, level):
    nationID, vehicleTypeID = vehicleDescr.type.id
    passport = (nationID,
     False,
     False,
     0,
     0,
     0)
    skills = ()
    return tankmen.stripNonBattle(tankmen.generateCompactDescr(passport, vehicleTypeID, roles[0], level, skills, level))


def _replaceMissingTankmenWithDefaultOnes(vehicleDescr, crewCompactDescrs, level=MAX_SKILL_LEVEL):
    result = []
    for tankmanCompactDescr, roles in zip(crewCompactDescrs, vehicleDescr.type.crewRoles):
        if tankmanCompactDescr is None:
            result.append(_generateTankman(vehicleDescr, roles, level))
        result.append(tankmanCompactDescr)

    return result


def getRadioDistance(vehicleDescr, factors):
    return vehicleDescr.radio.distance * max(factors['radio/distance'], 0.0)


def getCircularVisionRadius(vehicleDescr, factors):
    return vehicleDescr.turret.circularVisionRadius * vehicleDescr.miscAttrs['circularVisionRadiusBaseFactor'] * vehicleDescr.miscAttrs['circularVisionRadiusFactor'] * max(factors['circularVisionRadius'], 0.0)


def getFirstReloadTime(vehicleDescr, factors, ignoreRespawn=False):
    respawnReloadFactor = max(factors['respawnReloadTimeFactor'], 0.0)
    factor = vehicleDescr.miscAttrs['gunReloadTimeFactor'] * max(factors['gun/reloadTime'], 0.0)
    firstShellReload = vehicleDescr.gun.reloadTime
    if 'dualGun' in vehicleDescr.gun.tags:
        firstShellReload = vehicleDescr.gun.dualGun.reloadTimes[0]
    elif 'clip' in vehicleDescr.gun.tags and 'autoreload' in vehicleDescr.gun.tags:
        firstShellReload = vehicleDescr.gun.autoreload.reloadTime[-1]
    return firstShellReload * factor if ignoreRespawn else firstShellReload * factor * respawnReloadFactor


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
    additiveTerm = factors['invisibility'][0] + factors.get('invisibilityAdditiveTerm', 0.0) + vehicleDescr.miscAttrs['invisibilityBaseAdditive'] + vehicleDescr.miscAttrs['invisibilityAdditiveTerm']
    multFactor = factors['invisibility'][1]
    return (baseValue + additiveTerm) * multFactor


if IS_CLIENT:
    CLIENT_VEHICLE_ATTRIBUTE_FACTORS = {'camouflage': 1.0,
     'shotDispersion': 1.0}
    CLIENT_VEHICLE_ATTRIBUTE_FACTORS.update(vehicleAttributeFactors())

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
        baseInvisibility = vehicleDescr.computeBaseInvisibility(camouflageFactor, camouflageId)
        invisibilityFactors = factors['invisibility']
        factors['invisibility'] = invisibilityFactors[VEHICLE_TTC_ASPECTS.DEFAULT]
        moving = getInvisibility(vehicleDescr, factors, baseInvisibility, True)
        factors['invisibility'] = invisibilityFactors[VEHICLE_TTC_ASPECTS.WHEN_STILL]
        still = getInvisibility(vehicleDescr, factors, baseInvisibility, False)
        factors['invisibility'] = invisibilityFactors
        return (moving, still)


    def updateAttrFactorsWithSplit(vehicleDescr, crewCompactDescrs, eqs, factors, perksController=None):
        extras = {}
        extraAspects = {VEHICLE_TTC_ASPECTS.WHEN_STILL: ('invisibility',)}
        for aspect in extraAspects.iterkeys():
            currFactors = copy.deepcopy(factors)
            updateVehicleAttrFactors(vehicleDescr, perksController, crewCompactDescrs, eqs, currFactors, aspect)
            for coefficient in extraAspects[aspect]:
                extras.setdefault(coefficient, {})[aspect] = currFactors[coefficient]

        updateVehicleAttrFactors(vehicleDescr, perksController, crewCompactDescrs, eqs, factors, VEHICLE_TTC_ASPECTS.DEFAULT)
        for coefficientName, coefficientValue in extras.iteritems():
            coefficientValue[VEHICLE_TTC_ASPECTS.DEFAULT] = factors[coefficientName]
            factors[coefficientName] = coefficientValue


    def getCrewAffectedFactors(vehicleDescr, crewCompactDescrs):
        defaultCrewCompactDescrs = _replaceMissingTankmenWithDefaultOnes(vehicleDescr, crewCompactDescrs)
        defaultFactors = makeDefaultClientVehicleAttributeFactors()
        updateAttrFactorsWithSplit(vehicleDescr, defaultCrewCompactDescrs, [], defaultFactors)
        result = {}
        for i, (tankmanCompactDescr, roles) in enumerate(zip(crewCompactDescrs, vehicleDescr.type.crewRoles)):
            backupedtankmanCompactDescr = defaultCrewCompactDescrs[i]
            defaultCrewCompactDescrs[i] = _generateTankman(vehicleDescr, roles, MIN_ROLE_LEVEL if tankmanCompactDescr is None else MAX_SKILL_LEVEL)
            tankmanAffectedFactors = makeDefaultClientVehicleAttributeFactors()
            updateAttrFactorsWithSplit(vehicleDescr, defaultCrewCompactDescrs, [], tankmanAffectedFactors)
            changedFactors = _compareFactors(tankmanAffectedFactors, defaultFactors)
            if changedFactors:
                result[i] = changedFactors
            defaultCrewCompactDescrs[i] = backupedtankmanCompactDescr

        return result


    def _sumCrewLevelIncrease(eqs):
        return sum(filter(None, [ getattr(eq, 'crewLevelIncrease', None) for eq in eqs ]))


    def updateVehicleAttrFactors(vehicleDescr, perksController, crewCompactDescrs, eqs, factors, aspect):
        factors['crewLevelIncrease'] = _sumCrewLevelIncrease(eqs)
        for eq in eqs:
            if eq is not None:
                eq.updateVehicleAttrFactorsForAspect(vehicleDescr, factors, aspect)

        vehicleDescr.applyOptDevFactorsForAspect(factors, aspect)
        vehicleDescrCrew = VehicleDescrCrew(vehicleDescr, crewCompactDescrs)
        for eq in eqs:
            if eq is not None and 'crewSkillBattleBooster' in eq.tags:
                vehicleDescrCrew.boostSkillBy(eq)

        vehicleDescrCrew.onCollectFactors(factors)
        factors['camouflage'] = vehicleDescrCrew.camouflageFactor
        if perksController and aspect == VEHICLE_TTC_ASPECTS.DEFAULT:
            perksController.onCollectFactors(factors)
        shotDispersionFactors = [1.0, 0.0]
        vehicleDescrCrew.onCollectShotDispersionFactors(shotDispersionFactors)
        factors['shotDispersion'] = shotDispersionFactors
        return
