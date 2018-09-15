# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/utils.py
import copy
from operator import sub
from constants import IS_CLIENT, VEHICLE_TTC_ASPECTS
from items import tankmen
from items.qualifiers import QUALIFIER_TYPE
from items.tankmen import MAX_SKILL_LEVEL, MIN_ROLE_LEVEL
from items.vehicles import CAMOUFLAGE_KIND_INDICES, __createAttributeFactors
from VehicleDescrCrew import VehicleDescrCrew
from VehicleQualifiersApplier import VehicleQualifiersApplier
from debug_utils import *
import copy

def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def generateDefaultCrew(vehicleType, level):
    assert 0 <= level <= tankmen.MAX_SKILL_LEVEL
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
    return vehicleDescr.turrets[0].turret.circularVisionRadius * vehicleDescr.miscAttrs['circularVisionRadiusFactor'] * max(factors['circularVisionRadius'], 0.0)


def getReloadTime(vehicleDescr, factors, index=0):
    return vehicleDescr.turrets[index].gun.reloadTime * vehicleDescr.miscAttrs['gunReloadTimeFactor'] * max(factors['turrets/{}/gun/reloadTime'.format(index)], 0.0)


def getTurretRotationSpeed(vehicleDescr, factors, index=0):
    return vehicleDescr.turrets[index].turret.rotationSpeed * max(factors['turrets/{}/rotationSpeed'.format(index)], 0.0)


def getGunRotationSpeed(vehicleDescr, factors, index=0):
    return vehicleDescr.turrets[index].gun.rotationSpeed * max(factors['turrets/{}/gun/rotationSpeed'.format(index)], 0.0)


def getGunAimingTime(vehicleDescr, factors, index=0):
    return vehicleDescr.turrets[index].gun.aimingTime * vehicleDescr.miscAttrs['gunAimingTimeFactor'] * max(factors['turrets/{}/gun/aimingTime'.format(index)], 0.0)


def getChassisRotationSpeed(vehicleDescr, factors):
    return vehicleDescr.chassis.rotationSpeed * max(factors['vehicle/rotationSpeed'], 0.0)


def getInvisibility(factors, baseInvisibility, isMoving):
    return (baseInvisibility[0 if isMoving else 1] + factors['invisibility'][0]) * factors['invisibility'][1]


if IS_CLIENT:
    CLIENT_SPECIFIC_VEHICLE_ATTRIBUTE_FACTORS = {'camouflage': 1.0,
     'shotDispersion': 1.0}

    def _clientsVehicleAttributeFactors(defaultFactors):
        ret = copy.deepcopy(CLIENT_SPECIFIC_VEHICLE_ATTRIBUTE_FACTORS)
        ret.update(defaultFactors)
        return ret


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
            originalFactor = original[factor]
            changedFactor = changed[factor]
            if not _comparableFactors(originalFactor, changedFactor):
                continue
            if all((isinstance(x, list) for x in (originalFactor, changedFactor))):
                if not all(map(isclose, originalFactor, changedFactor)):
                    result[factor] = map(sub, originalFactor, changedFactor)
            if not isclose(originalFactor, changedFactor):
                result[factor] = originalFactor - changedFactor

        return result


    def getClientShotDispersion(vehicleDescr, shotDispersionFactor):
        return vehicleDescr.turrets[0].gun.shotDispersionAngle * shotDispersionFactor


    def getClientShotDispersion_Secondary(vehicleDescr, shotDispersionFactor):
        return vehicleDescr.turrets[1].gun.shotDispersionAngle * shotDispersionFactor


    def getClientInvisibility(vehicleDescr, camouflageFactor, factors):
        camouflageKind = 0
        for camouflageIndex, camouflageName in CAMOUFLAGE_KIND_INDICES.iteritems():
            if vehicleDescr.camouflages[camouflageIndex][0] is not None:
                camouflageKind = camouflageIndex
                break

        baseInvisibility = vehicleDescr.computeBaseInvisibility(camouflageFactor, camouflageKind)
        invisibilityFactors = factors['invisibility']
        factors['invisibility'] = invisibilityFactors[VEHICLE_TTC_ASPECTS.DEFAULT]
        moving = getInvisibility(factors, baseInvisibility, True)
        factors['invisibility'] = invisibilityFactors[VEHICLE_TTC_ASPECTS.WHEN_STILL]
        still = getInvisibility(factors, baseInvisibility, False)
        factors['invisibility'] = invisibilityFactors
        return (moving, still)


    def updateAttrFactorsWithSplit(vehicleDescr, crewCompactDescrs, eqs, factors):
        extras = {}
        extraAspects = {VEHICLE_TTC_ASPECTS.WHEN_STILL: ('invisibility',)}
        updateVehicleAttrFactors(vehicleDescr, crewCompactDescrs, eqs, factors, VEHICLE_TTC_ASPECTS.DEFAULT)
        for aspect in extraAspects.iterkeys():
            currFactors = copy.deepcopy(factors)
            updateVehicleAttrFactors(vehicleDescr, crewCompactDescrs, eqs, currFactors, aspect)
            for coefficient in extraAspects[aspect]:
                if coefficient in currFactors:
                    extras.setdefault(coefficient, {})[aspect] = currFactors[coefficient]

        for coefficientName, coefficientValue in extras.iteritems():
            coefficientValue[VEHICLE_TTC_ASPECTS.DEFAULT] = factors[coefficientName]
            factors[coefficientName] = coefficientValue


    def getCrewAffectedFactors(vehicleDescr, crewCompactDescrs):
        turretCount = len(vehicleDescr.turrets)
        defaultCrewCompactDescrs = _replaceMissingTankmenWithDefaultOnes(vehicleDescr, crewCompactDescrs)
        defaultVehicleFactors = _clientsVehicleAttributeFactors(vehicleDescr.type.createAttributeFactors())
        defaultFactors = copy.deepcopy(defaultVehicleFactors)
        updateAttrFactorsWithSplit(vehicleDescr, defaultCrewCompactDescrs, [], defaultFactors)
        result = {}
        for i, (tankmanCompactDescr, roles) in enumerate(zip(crewCompactDescrs, vehicleDescr.type.crewRoles)):
            backupedtankmanCompactDescr = defaultCrewCompactDescrs[i]
            defaultCrewCompactDescrs[i] = _generateTankman(vehicleDescr, roles, MIN_ROLE_LEVEL if tankmanCompactDescr is None else MAX_SKILL_LEVEL)
            tankmanAffectedFactors = copy.deepcopy(defaultVehicleFactors)
            updateAttrFactorsWithSplit(vehicleDescr, defaultCrewCompactDescrs, [], tankmanAffectedFactors)
            changedFactors = _compareFactors(tankmanAffectedFactors, defaultFactors)
            if changedFactors:
                result[i] = changedFactors
            defaultCrewCompactDescrs[i] = backupedtankmanCompactDescr

        return result


    def _sumCrewLevelIncrease(eqs):
        return sum(filter(None, [ getattr(eq, 'crewLevelIncrease', None) for eq in eqs ]))


    def updateVehicleAttrFactors(vehicleDescr, crewCompactDescrs, eqs, factors, aspect):
        factors['crewLevelIncrease'] = _sumCrewLevelIncrease(eqs)
        for eq in eqs:
            if eq is not None:
                eq.updateVehicleAttrFactors(vehicleDescr, factors, aspect)

        for device in vehicleDescr.optionalDevices:
            if device is not None:
                device.updateVehicleAttrFactors(vehicleDescr, factors, aspect)

        mainSkillBonuses = VehicleQualifiersApplier({}, vehicleDescr)[QUALIFIER_TYPE.MAIN_SKILL]
        vehicleDescrCrew = VehicleDescrCrew(vehicleDescr, crewCompactDescrs, mainSkillBonuses)
        for eq in eqs:
            if eq is not None and 'crewSkillBattleBooster' in eq.tags:
                vehicleDescrCrew.boostSkillBy(eq)

        vehicleDescrCrew.onCollectFactors(factors)
        factors['camouflage'] = vehicleDescrCrew.camouflageFactor
        shotDispersionFactors = [1.0, 0.0]
        vehicleDescrCrew.onCollectShotDispersionFactors(shotDispersionFactors)
        for i in range(len(vehicleDescr.turrets)):
            factors['turrets/{}/shotDispersion'.format(i)] = shotDispersionFactors

        return
