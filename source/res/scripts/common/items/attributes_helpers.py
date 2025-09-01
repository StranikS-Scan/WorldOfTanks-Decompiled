# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/attributes_helpers.py
from items import _xml
from typing import Dict, Tuple, Iterable, List, TYPE_CHECKING
if TYPE_CHECKING:
    import ResMgr
STATIC_ATTR_PREFIX = 'miscAttrs/'
DYNAMIC_ATTR_PREFIX = 'dynAttrs/'
DESCR_MODIFY_ATTR_PREFIX = 'descrAttrs/'
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
 'increaseCircularVisionRadius',
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
 'penaltyToDamagedSurveyingDevice',
 'gun/reloadTime',
 'gun/rotationSpeed',
 'gun/shotDispersionFactors/turretRotation',
 'healthBurnPerSecLossFraction',
 'healthFactor',
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
 'vehicle/fwMaxSpeedBonus',
 'multShotDispersionFactor',
 'gun/shotDispersionFactors/afterShot',
 'hull_aiming/pitch/wheelsCorrectionSpeedFactor',
 'improvedRammingDamageBonus/basicFactor',
 'improvedRammingDamageBonus/changeFactor',
 'improvedRammingTrackDamageBonus/basicFactor',
 'improvedRammingTrackDamageBonus/changeFactor',
 'improvedRammingDamageReductionBonus/basicFactor',
 'improvedRammingDamageReductionBonus/changeFactor'}
AUTOSHOOT_DYNAMIC_ATTRS = {'rate/multiplier', 'shotDispersionPerSecFactor', 'maxShotDispersionFactor'}

class DescrModifyAttrsCheker(object):

    def __contains__(self, item):
        from descr_modify_attrs import checkAttrName
        return checkAttrName(item)


ALLOWED_ATTRS = {STATIC_ATTR_PREFIX: ALLOWED_STATIC_ATTRS,
 DYNAMIC_ATTR_PREFIX: ALLOWED_DYNAMIC_ATTRS,
 AUTOSHOOT_ATTR_PREFIX: AUTOSHOOT_DYNAMIC_ATTRS,
 DESCR_MODIFY_ATTR_PREFIX: DescrModifyAttrsCheker()}
ALLOWED_ATTR_PREFIXES = set(ALLOWED_ATTRS.keys())

class MODIFIER_TYPE:
    MUL = 'mul'
    ADD = 'add'
    SET = 'set'


class MODIFIER_FILTER_TYPE:
    COMMON = 'common'
    DEFAULT = 'default'
    SIEGE = 'siege'


def _parseAttrName(complexName):
    for attrPrefix in ALLOWED_ATTR_PREFIXES:
        if complexName.startswith(attrPrefix):
            return (attrPrefix, intern(complexName[len(attrPrefix):]))

    return (None, None)


def readModifiers(xmlCtx, section):
    xmlCtx = (xmlCtx, section.name)
    modifiers = []
    for opType, data in section.items():
        if opType not in (MODIFIER_TYPE.MUL, MODIFIER_TYPE.ADD, MODIFIER_TYPE.SET):
            _xml.raiseWrongXml(xmlCtx, opType, 'Unknown operation type')
        name = data.readString('name')
        filterName = data.readString('filter') or MODIFIER_FILTER_TYPE.COMMON
        attrType, attrName = _parseAttrName(name)
        names = ALLOWED_ATTRS.get(attrType)
        if opType == MODIFIER_TYPE.SET and attrType != DESCR_MODIFY_ATTR_PREFIX:
            _xml.raiseWrongXml(xmlCtx, opType, 'Set not supported just for {}'.format(attrType))
        if names is None:
            _xml.raiseWrongXml(xmlCtx, name, 'Unknown attribute type')
        if attrName not in names:
            _xml.raiseWrongXml(xmlCtx, name, 'Unknown attribute name')
        value = data.readFloat('value')
        modifiers.append((opType,
         attrType,
         attrName,
         value,
         filterName))

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
    def collect(total, modifiersList, attrPrefix, filter=None):
        isEmpty = SingleCollectorHelper.isEmpty
        appliers = SingleCollectorHelper._APPLIERS
        for modifiers in modifiersList:
            for opType, attrType, attrName, value, modifierFilter in modifiers:
                if filter and modifierFilter not in filter:
                    continue
                if attrType != attrPrefix:
                    continue
                if isEmpty(opType, value):
                    continue
                total[attrName] = appliers[opType](total.get(attrName, 0), value)


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
    def collect(total, modifiersList, attrPrefix, filter=None):
        uniqueAttrs = dict()
        mergers = AggregatedCollectorHelper._MERGERS
        for modifiers in modifiersList:
            for opType, attrType, attrName, value, modifierFilter in modifiers:
                if filter and modifierFilter not in filter:
                    continue
                if attrType != attrPrefix:
                    continue
                key = (attrName, opType)
                uniqueAttrs[key] = mergers[opType](uniqueAttrs.get(key, 0.0), value)

        isEmpty = AggregatedCollectorHelper.isEmpty
        appliers = AggregatedCollectorHelper._APPLIERS
        for (attrName, opType), value in uniqueAttrs.iteritems():
            if isEmpty(opType, value):
                continue
            total[attrName] = appliers[opType](total.get(attrName, 0), value)


def onCollectAttributes(total, modifiersList, attrPrefix, asAggregated, filter=None):
    if asAggregated:
        AggregatedCollectorHelper.collect(total, modifiersList, attrPrefix, filter)
    else:
        SingleCollectorHelper.collect(total, modifiersList, attrPrefix, filter)
