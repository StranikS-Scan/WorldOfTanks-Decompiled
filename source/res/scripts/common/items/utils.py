# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/utils.py
import copy
from operator import sub
from functools import partial
from typing import Any, Dict, Tuple
from constants import VEHICLE_TTC_ASPECTS
from debug_utils import *
from items import tankmen, ITEM_TYPES
from items import vehicles
from items.components.c11n_constants import CUSTOMIZATION_SLOTS_VEHICLE_PARTS
from items.tankmen import MAX_SKILL_LEVEL, MIN_ROLE_LEVEL, getSkillsConfig
from items.vehicles import vehicleAttributeFactors, VehicleDescriptor
from items.artefacts import StaticOptionalDevice, AdditiveBattleBooster
from items.components import component_constants
from account_shared import AmmoIterator
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
         basestring)):
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


def getClipTimeBetweenShots(vehicleDescr, factors):
    return vehicleDescr.gun.clip[1] * max(factors['gun/clipTimeBetweenShots'], 0.0)


def getChassisRotationSpeed(vehicleDescr, factors):
    return vehicleDescr.chassis.rotationSpeed * max(factors['vehicle/rotationSpeed'], 0.0) * max(vehicleDescr.miscAttrs['onMoveRotationSpeedFactor'], vehicleDescr.miscAttrs['onStillRotationSpeedFactor'])


def getInvisibility(vehicleDescr, factors, baseInvisibility, isMoving):
    baseValue = baseInvisibility[0 if isMoving else 1]
    additiveTerm = factors['invisibility'][0] + factors.get('invisibilityAdditiveTerm', 0.0) + vehicleDescr.miscAttrs['invisibilityBaseAdditive'] + vehicleDescr.miscAttrs['invisibilityAdditiveTerm']
    multFactor = factors['invisibility'][1] * factors.get('invisibilityMultFactor', 1.0)
    return (baseValue + additiveTerm) * multFactor


if IS_CLIENT:
    CLIENT_VEHICLE_ATTRIBUTE_FACTORS = {'camouflage': 1.0,
     'shotDispersion': 1.0,
     'dualAccuracyCoolingDelay': 1.0}
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
                originalFactor = original.get(factor, CLIENT_VEHICLE_ATTRIBUTE_FACTORS[factor])
                changedFactor = changed[factor]
                if originalFactor == changedFactor:
                    continue
                else:
                    result[factor] = originalFactor - changedFactor

        return result


    def getClientShotDispersion(vehicleDescr, shotDispersionFactor):
        gun = vehicleDescr.gun
        values = []
        if 'dualAccuracy' in gun.tags:
            values.append(gun.dualAccuracy.afterShotDispersionAngle)
        values.append(gun.shotDispersionAngle)
        return (value * vehicleDescr.miscAttrs['multShotDispersionFactor'] * shotDispersionFactor for value in values)


    def getClientCoolingDelay(vehicleDescr, factors):
        return float(vehicleDescr.gun.dualAccuracy.coolingDelay) * factors['dualAccuracyCoolingDelay']


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


    def updateAttrFactorsWithSplit(vehicleDescr, crewCompactDescrs, eqs, factors):
        extras = {}
        extraAspects = {VEHICLE_TTC_ASPECTS.WHEN_STILL: ('invisibility',)}
        for aspect in extraAspects.iterkeys():
            currFactors = copy.deepcopy(factors)
            updateVehicleAttrFactors(vehicleDescr, crewCompactDescrs, eqs, currFactors, aspect)
            for coefficient in extraAspects[aspect]:
                extras.setdefault(coefficient, {})[aspect] = currFactors[coefficient]

        updateVehicleAttrFactors(vehicleDescr, crewCompactDescrs, eqs, factors, VEHICLE_TTC_ASPECTS.DEFAULT)
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


    def updateVehicleAttrFactors(vehicleDescr, crewCompactDescrs, eqs, factors, aspect):
        from VehicleDescrCrew import VehicleDescrCrew
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
        if vehicleDescr.hasDualAccuracy:
            crewData = vehicleDescrCrew.collectDefaultCrewData()
            vehicleDescrCrew.extendSkillProcessor('dualAccuracyCoolingDelay', crewData, partial(_updateDualAccuracyCoolingDelay, factors=factors))
        multShotDispersionFactor = factors.get('multShotDispersionFactor', 1.0)
        shotDispersionFactors = [multShotDispersionFactor, 0.0]
        vehicleDescrCrew.onCollectShotDispersionFactors(shotDispersionFactors)
        factors['shotDispersion'] = shotDispersionFactors
        return


    def _updateDualAccuracyCoolingDelay(_, attr, factors):
        coolingDelayFactor = factors.get('dualAccuracyCoolingDelay', 1.0)
        factors['dualAccuracyCoolingDelay'] = coolingDelayFactor / attr.factor


def getEditorOnlySection(section, createNewSection=False):
    editorOnlySection = section['editorOnly']
    if editorOnlySection is None and createNewSection:
        from items.writers.c11n_writers import findOrCreate
        editorOnlySection = findOrCreate(section, 'editorOnly')
    return editorOnlySection


def getDifferVehiclePartNames(newVehDescr, oldVehDescr):
    differPartNames = []
    for partName in CUSTOMIZATION_SLOTS_VEHICLE_PARTS:
        if getattr(newVehDescr, partName).compactDescr != getattr(oldVehDescr, partName).compactDescr:
            differPartNames.append(partName)

    if 'turret' in differPartNames:
        if 'gun' not in differPartNames:
            differPartNames.append('gun')
    elif 'gun' in differPartNames:
        differPartNames.append('turret')
    return differPartNames


def commanderTutorXpBonusFactorForCrew(crew, ammo, vehCompDescr):
    tutorLevel = component_constants.ZERO_FLOAT
    brotherhoodSum = 0.0
    vehDescriptor = VehicleDescriptor(compactDescr=vehCompDescr)
    for t in crew:
        if t.role == 'commander':
            tutorLevel = t.skillLevel('commander_tutor')
            if not tutorLevel:
                return component_constants.ZERO_FLOAT
            if not t.isOwnVehicleOrPremium(vehDescriptor.type):
                return component_constants.ZERO_FLOAT
            tutorLevel *= t.skillsEfficiency
        tmanBrotherhoodLevel = t.skillLevel('brotherhood') or 0
        brotherhoodSum += tmanBrotherhoodLevel * t.skillsEfficiency

    brotherhoodLevel = brotherhoodSum / (len(crew) * MAX_SKILL_LEVEL)
    skillsConfig = getSkillsConfig()
    brotherhoodBonus = brotherhoodLevel * skillsConfig.getSkill('brotherhood').crewLevelIncrease
    tutorLevel += brotherhoodBonus
    equipCrewLevelIncrease = component_constants.ZERO_FLOAT
    optionalDevCrewLevelIncrease = component_constants.ZERO_FLOAT
    cache = vehicles.g_cache
    optDev = set()
    for compDescr, count in AmmoIterator(ammo):
        itemTypeIdx, _, itemIdx = vehicles.parseIntCompactDescr(compDescr)
        if itemTypeIdx == ITEM_TYPES.optionalDevice:
            obj = cache.optionalDevices()[itemIdx]
            if isinstance(obj, StaticOptionalDevice):
                optionalDevCrewLevelIncrease += obj.getFactorValue(vehDescriptor, 'miscAttrs/crewLevelIncrease')
                optDev.add(obj)

    for compDescr, count in AmmoIterator(ammo):
        itemTypeIdx, _, itemIdx = vehicles.parseIntCompactDescr(compDescr)
        if itemTypeIdx == ITEM_TYPES.equipment:
            eqip = cache.equipments()[itemIdx]
            equipCrewLevelIncrease += getattr(eqip, 'crewLevelIncrease', component_constants.ZERO_FLOAT)
            if isinstance(eqip, AdditiveBattleBooster):
                for device in optDev:
                    levelParams = eqip.getLevelParamsForDevice(device)
                    if levelParams is not None and 'crewLevelIncrease' in levelParams:
                        equipCrewLevelIncrease += levelParams[1]
                        break

    tutorLevel += optionalDevCrewLevelIncrease
    tutorLevel += equipCrewLevelIncrease
    return tutorLevel * skillsConfig.getSkill('commander_tutor').xpBonusFactorPerLevel
