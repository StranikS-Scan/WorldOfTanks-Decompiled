# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/utils.py
from operator import sub
from copy import deepcopy
from constants import IS_CLIENT
from items import tankmen
from items.qualifiers import QUALIFIER_TYPE
from items.tankmen import MAX_SKILL_LEVEL, MIN_ROLE_LEVEL
from items.vehicles import VEHICLE_ATTRIBUTE_FACTORS, CAMOUFLAGE_KIND_INDICES
from VehicleDescrCrew import VehicleDescrCrew
from VehicleQualifiersApplier import VehicleQualifiersApplier

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
    return vehicleDescr.radio['distance'] * max(factors['radio/distance'], 0.0)


def getCircularVisionRadius(vehicleDescr, factors):
    return vehicleDescr.turret['circularVisionRadius'] * vehicleDescr.miscAttrs['circularVisionRadiusFactor'] * max(factors['circularVisionRadius'], 0.0)


def getReloadTime(vehicleDescr, factors):
    return vehicleDescr.gun['reloadTime'] * vehicleDescr.miscAttrs['gunReloadTimeFactor'] * max(factors['gun/reloadTime'], 0.0)


def getTurretRotationSpeed(vehicleDescr, factors):
    return vehicleDescr.turret['rotationSpeed'] * max(factors['turret/rotationSpeed'], 0.0)


def getGunRotationSpeed(vehicleDescr, factors):
    return vehicleDescr.gun['rotationSpeed'] * max(factors['gun/rotationSpeed'], 0.0)


def getGunAimingTime(vehicleDescr, factors):
    return vehicleDescr.gun['aimingTime'] * vehicleDescr.miscAttrs['gunAimingTimeFactor'] * max(factors['gun/aimingTime'], 0.0)


def getChassisRotationSpeed(vehicleDescr, factors):
    return vehicleDescr.chassis['rotationSpeed'] * max(factors['vehicle/rotationSpeed'], 0.0)


def getInvisibility(factors, baseInvisibility, isMoving):
    return (baseInvisibility[0 if isMoving else 1] + factors['invisibility'][0]) * factors['invisibility'][1]


if IS_CLIENT:
    CLIENT_VEHICLE_ATTRIBUTE_FACTORS = {'camouflage': 1.0,
     'shotDispersion': 1.0}
    CLIENT_VEHICLE_ATTRIBUTE_FACTORS.update(VEHICLE_ATTRIBUTE_FACTORS)

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
        return vehicleDescr.gun['shotDispersionAngle'] * shotDispersionFactor


    def getClientInvisibility(vehicleDescr, camouflageFactor, factors):
        camouflageKind = 0
        for camouflageIndex, camouflageName in CAMOUFLAGE_KIND_INDICES.iteritems():
            if vehicleDescr.camouflages[camouflageIndex][0] is not None:
                camouflageKind = camouflageIndex
                break

        baseInvisibility = vehicleDescr.computeBaseInvisibility(camouflageFactor, camouflageKind)
        return (getInvisibility(factors, baseInvisibility, True), getInvisibility(factors, baseInvisibility, False))


    def getCrewAffectedFactors(vehicleDescr, crewCompactDescrs):
        defaultCrewCompactDescrs = _replaceMissingTankmenWithDefaultOnes(vehicleDescr, crewCompactDescrs)
        defaultFactors = deepcopy(CLIENT_VEHICLE_ATTRIBUTE_FACTORS)
        updateVehicleAttrFactors(vehicleDescr, defaultCrewCompactDescrs, [], defaultFactors)
        result = {}
        for i, (tankmanCompactDescr, roles) in enumerate(zip(crewCompactDescrs, vehicleDescr.type.crewRoles)):
            backupedtankmanCompactDescr = defaultCrewCompactDescrs[i]
            defaultCrewCompactDescrs[i] = _generateTankman(vehicleDescr, roles, MIN_ROLE_LEVEL if tankmanCompactDescr is None else MAX_SKILL_LEVEL)
            tankmanAffectedFactors = deepcopy(CLIENT_VEHICLE_ATTRIBUTE_FACTORS)
            updateVehicleAttrFactors(vehicleDescr, defaultCrewCompactDescrs, [], tankmanAffectedFactors)
            changedFactors = _compareFactors(tankmanAffectedFactors, defaultFactors)
            if changedFactors:
                result[i] = changedFactors
            defaultCrewCompactDescrs[i] = backupedtankmanCompactDescr

        return result


    def _sumCrewLevelIncrease(eqs):
        return sum(filter(None, [ getattr(eq, 'crewLevelIncrease', None) for eq in eqs ]))


    def updateVehicleAttrFactors(vehicleDescr, crewCompactDescrs, eqs, factors):
        factors['crewLevelIncrease'] = _sumCrewLevelIncrease(eqs)
        mainSkillBonuses = VehicleQualifiersApplier({}, vehicleDescr)[QUALIFIER_TYPE.MAIN_SKILL]
        vehicleDescrCrew = VehicleDescrCrew(vehicleDescr, crewCompactDescrs, mainSkillBonuses)
        vehicleDescrCrew.onCollectFactors(factors)
        for eq in eqs:
            if eq is not None:
                eq.updateVehicleAttrFactors(factors)

        factors['camouflage'] = vehicleDescrCrew.camouflageFactor
        shotDispersionFactors = [1.0, 0.0]
        vehicleDescrCrew.onCollectShotDispersionFactors(shotDispersionFactors)
        factors['shotDispersion'] = shotDispersionFactors
        return
