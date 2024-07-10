# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/attributes_helpers.py
from items import _xml
from typing import Dict, Tuple, Iterable, List, TYPE_CHECKING
if TYPE_CHECKING:
    import ResMgr
STATIC_ATTR_PREFIX = 'miscAttrs/'
DYNAMIC_ATTR_PREFIX = 'dynAttrs/'
AUTOSHOOT_ATTR_PREFIX = 'autoShootAttrs/'
ALLOWED_STATIC_ATTRS = {'additiveShotDispersionFactor',
 'ammoBayHealthFactor',
 'ammoBayReduceFineFactor',
 'antifragmentationLiningFactor',
 'armorSpallsDamageDevicesFactor',
 'backwardMaxSpeedKMHTerm',
 'centerRotationFwdSpeedFactor',
 'chassis/shotDispersionFactors/movement',
 'chassis/shotDispersionFactors/rotation',
 'isSetChassisMaxHealthAfterHysteresis',
 'chassisHealthFactor',
 'chassisRepairSpeedFactor',
 'circularVisionRadiusFactor',
 'circularVisionRadiusBaseFactor',
 'crewChanceToHitFactor',
 'crewLevelIncrease',
 'damageFactor',
 'deathZones/sensitivityFactor',
 'decreaseOwnSpottingTime',
 'demaskFoliageFactor',
 'demaskMovingFactor',
 'engineHealthFactor',
 'enginePowerFactor',
 'engineReduceFineFactor',
 'fireStartingChanceFactor',
 'forwardMaxSpeedKMHTerm',
 'fuelTankHealthFactor',
 'gun/shotDispersionFactors/afterShot',
 'gun/shotDispersionFactors/turretRotation',
 'gun/shotDispersionFactors/whileGunDamaged',
 'gunAimingTimeFactor',
 'gunHealthFactor',
 'gunReloadTimeFactor',
 'healthFactor',
 'increaseEnemySpottingTime',
 'invisibilityBaseAdditive',
 'invisibilityAdditiveTerm',
 'invisibilityMultFactor',
 'invisibilityFactorAtShot',
 'maxWeight',
 'multShotDispersionFactor',
 'onMoveRotationSpeedFactor',
 'onStillRotationSpeedFactor',
 'radioHealthFactor',
 'rammingFactor',
 'repairSpeedFactor',
 'repeatedStunDurationFactor',
 'rollingFrictionFactor',
 'stunResistanceDuration',
 'stunResistanceEffect',
 'surveyingDeviceHealthFactor',
 'turretRotationSpeed',
 'turretRotatorHealthFactor',
 'vehicleByChassisDamageFactor',
 'hullMaxHealth',
 'turretMaxHealth'}
ALLOWED_DYNAMIC_ATTRS = {'additiveShotDispersionFactor',
 'chassis/shotDispersionFactors/movement',
 'chassis/shotDispersionFactors/rotation',
 'circularVisionRadius',
 'crewChanceToHitFactor',
 'crewLevelIncrease',
 'crewRolesFactor',
 'damageFactor',
 'deathZones/sensitivityFactor',
 'engine/fireStartingChance',
 'engine/power',
 'enginePowerFactor',
 'gun/aimingTime',
 'gun/changeShell/reloadFactor',
 'gun/piercing',
 'gun/reloadTime',
 'gun/rotationSpeed',
 'gun/shotDispersionFactors/turretRotation',
 'healthBurnPerSecLossFraction',
 'healthFactor',
 'multShotDispersionFactor',
 'radio/distance',
 'ramming',
 'repairSpeed',
 'repeatedStunDurationFactor',
 'stunResistanceDuration',
 'stunResistanceEffect',
 'turret/rotationSpeed',
 'vehicle/maxSpeed',
 'vehicle/maxSpeed/forward',
 'vehicle/maxSpeed/backward',
 'vehicle/rotationSpeed',
 'vehicle/bkMaxSpeedBonus',
 'vehicle/fwMaxSpeedBonus'}
AUTOSHOOT_DYNAMIC_ATTRS = {'rate/multiplier', 'shotDispersionPerSecFactor', 'maxShotDispersionFactor'}
ALLOWED_ATTRS = {STATIC_ATTR_PREFIX: ALLOWED_STATIC_ATTRS,
 DYNAMIC_ATTR_PREFIX: ALLOWED_DYNAMIC_ATTRS,
 AUTOSHOOT_ATTR_PREFIX: AUTOSHOOT_DYNAMIC_ATTRS}
ALLOWED_ATTR_PREFIXES = set(ALLOWED_ATTRS.keys())

class MODIFIER_TYPE:
    MUL = 'mul'
    ADD = 'add'


def _parseAttrName(complexName):
    for attrPrefix in ALLOWED_ATTR_PREFIXES:
        if complexName.startswith(attrPrefix):
            return (attrPrefix, intern(complexName[len(attrPrefix):]))

    return (None, None)


def readModifiers(xmlCtx, section):
    xmlCtx = (xmlCtx, section.name)
    modifiers = []
    for opType, data in section.items():
        if opType not in (MODIFIER_TYPE.MUL, MODIFIER_TYPE.ADD):
            _xml.raiseWrongXml(xmlCtx, opType, 'Unknown operation type')
        name = data.readString('name')
        attrType, attrName = _parseAttrName(name)
        names = ALLOWED_ATTRS.get(attrType)
        if names is None:
            _xml.raiseWrongXml(xmlCtx, name, 'Unknown attribute type')
        if attrName not in names:
            _xml.raiseWrongXml(xmlCtx, name, 'Unknown attribute name')
        value = data.readFloat('value')
        modifiers.append((opType,
         attrType,
         attrName,
         value))

    return modifiers


def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


class SingleCollectorHelper(object):
    _EMPTY_CHECKER = {MODIFIER_TYPE.ADD: lambda value: isclose(value, 0.0),
     MODIFIER_TYPE.MUL: lambda value: isclose(value, 1.0)}
    _APPLIERS = {MODIFIER_TYPE.ADD: lambda currentValue, addValue: currentValue + addValue,
     MODIFIER_TYPE.MUL: lambda currentValue, addValue: currentValue * addValue}

    @staticmethod
    def isEmpty(opType, value):
        return SingleCollectorHelper._EMPTY_CHECKER[opType](value)

    @staticmethod
    def collect(total, modifiersList, attrPrefix):
        isEmpty = SingleCollectorHelper.isEmpty
        appliers = SingleCollectorHelper._APPLIERS
        for modifiers in modifiersList:
            for opType, attrType, attrName, value in modifiers:
                if attrType != attrPrefix:
                    continue
                if isEmpty(opType, value):
                    continue
                total[attrName] = appliers[opType](total[attrName], value)


class AggregatedCollectorHelper(object):
    _EMPTY_CHECKER = {MODIFIER_TYPE.ADD: lambda value: isclose(value, 0.0),
     MODIFIER_TYPE.MUL: lambda value: isclose(value, 0.0)}
    _MERGERS = {MODIFIER_TYPE.ADD: lambda currentValue, addValue: currentValue + addValue,
     MODIFIER_TYPE.MUL: lambda currentValue, addValue: currentValue + (addValue - 1)}
    _APPLIERS = {MODIFIER_TYPE.ADD: lambda currentValue, addValue: currentValue + addValue,
     MODIFIER_TYPE.MUL: lambda currentValue, addValue: currentValue * (addValue + 1)}

    @staticmethod
    def isEmpty(opType, value):
        return AggregatedCollectorHelper._EMPTY_CHECKER[opType](value)

    @staticmethod
    def collect(total, modifiersList, attrPrefix):
        uniqueAttrs = dict()
        mergers = AggregatedCollectorHelper._MERGERS
        for modifiers in modifiersList:
            for opType, attrType, attrName, value in modifiers:
                if attrType != attrPrefix:
                    continue
                key = (attrName, opType)
                uniqueAttrs[key] = mergers[opType](uniqueAttrs.get(key, 0.0), value)

        isEmpty = AggregatedCollectorHelper.isEmpty
        appliers = AggregatedCollectorHelper._APPLIERS
        for (attrName, opType), value in uniqueAttrs.iteritems():
            if isEmpty(opType, value):
                continue
            total[attrName] = appliers[opType](total[attrName], value)


def onCollectAttributes(total, modifiersList, attrPrefix, asAggregated):
    if asAggregated:
        AggregatedCollectorHelper.collect(total, modifiersList, attrPrefix)
    else:
        SingleCollectorHelper.collect(total, modifiersList, attrPrefix)
