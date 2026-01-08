# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/shared_components.py
import copy
from functools import partial
import typing
import Math
import cPickle
from collections import namedtuple
from constants import IS_CLIENT, IS_WEB, IS_EDITOR, IS_BOT, HEATING_ZONES_GUN_STATE, DEBUFFS_TYPES
from debug_utils import LOG_WARNING
from items.components import component_constants, c11n_constants
from items.components import path_builder
from items.components.component_constants import KMH_TO_MS
from items.components.c11n_constants import AttachmentSize
from items.attributes_helpers import ALLOWED_STATIC_ATTRS
from soft_exception import SoftException
from wrapped_reflection_framework import ReflectionMetaclass, reflectedNamedTuple
from items import _xml, ITEM_TYPES
from math import radians
if IS_CLIENT:
    from helpers import i18n
elif IS_WEB or IS_BOT:
    from web_stubs import i18n
else:

    class i18n(object):

        @classmethod
        def makeString(cls, key):
            raise SoftException('Unexpected call "i18n.makeString"')


if typing.TYPE_CHECKING:
    from typing import Any, Dict, Tuple, List, Optional, Sequence
    from constants import VEHICLE_TTC_ASPECTS
    from items.vehicles import VehicleDescriptor
__all__ = ('MaterialInfo', 'DEFAULT_MATERIAL_INFO', 'EmblemSlot', 'LodSettings', 'NodesAndGroups', 'Camouflage', 'DEFAULT_CAMOUFLAGE', 'SwingingSettings', 'I18nComponent', 'DeviceHealth', 'ModelStatesPaths', 'RocketAccelerationParams', 'ImpulseData', 'MechanicsParams', 'RechargeableNitroParams', 'ConcentrationModeParams', 'ImprovedRammingParams', 'PowerModeParams', 'BattleFuryParams', 'PillboxSiegeModeParams', 'StationaryReloadParams', 'ExtraShotClipParams', 'AccuracyStacksParams', 'SecondaryGunParams', 'SupportWeaponParams', 'ChargeableBurstParams', 'ChargeShotParams', 'OverheatStacksParams', 'TargetDesignatorParams', 'StanceDanceParams', 'TemperatureGunThermalState', 'TemperatureGunThermalStates', 'TemperatureGunParams', 'OverheatGunParams', 'HeatingZonesGunParams', 'TargetDesignatorParams', 'StagedJetBoostersParams')
MaterialInfo = reflectedNamedTuple('MaterialInfo', ('kind', 'armor', 'extra', 'multipleExtra', 'vehicleDamageFactor', 'useArmorHomogenization', 'useHitAngle', 'useAntifragmentationLining', 'mayRicochet', 'collideOnceOnly', 'checkCaliberForRicochet', 'checkCaliberForHitAngleNorm', 'damageKind', 'chanceToHitByProjectile', 'chanceToHitByExplosion', 'continueTraceIfNoHit', 'tags'))
DEFAULT_MATERIAL_INFO = MaterialInfo(0, 0, None, False, 0.0, False, False, False, False, False, False, False, 0, 0.0, 0.0, False, frozenset())
EmblemSlot = reflectedNamedTuple('EmblemSlot', ('rayStart', 'rayEnd', 'rayUp', 'size', 'hideIfDamaged', 'type', 'isMirrored', 'isUVProportional', 'emblemId', 'slotId', 'applyToFabric', 'compatibleModels'))

class CustomizationSlotDescription(object):
    __metaclass__ = ReflectionMetaclass
    __slots__ = ('type', 'slotId', 'anchorPosition', 'anchorDirection', 'applyTo')

    def __init__(self, slotType='', slotId=0, anchorPosition=None, anchorDirection=None, applyTo=None, tags=None):
        self.type = slotType
        self.slotId = slotId
        self.anchorPosition = anchorPosition
        self.anchorDirection = anchorDirection
        self.applyTo = applyTo


class ProjectionDecalSlotDescription(object):
    __metaclass__ = ReflectionMetaclass
    __slots__ = ('type', 'slotId', 'position', 'rotation', 'scale', 'scaleFactors', 'doubleSided', 'hiddenForUser', 'canBeMirroredVertically', 'showOn', 'tags', 'clipAngle', 'compatibleModels', 'itemId', 'options', 'anchorShift', 'modificationOrder')

    def __init__(self, slotType='', slotId=0, position=None, rotation=None, scale=None, scaleFactors=c11n_constants.DEFAULT_DECAL_SCALE_FACTORS, doubleSided=False, hiddenForUser=False, canBeMirroredVertically=False, showOn=None, tags=None, clipAngle=c11n_constants.DEFAULT_DECAL_CLIP_ANGLE, compatibleModels=(c11n_constants.SLOT_DEFAULT_ALLOWED_MODEL,), itemId=None, options=c11n_constants.Options.NONE, anchorShift=c11n_constants.DEFAULT_DECAL_ANCHOR_SHIFT, modificationOrder=0):
        self.type = slotType
        self.slotId = slotId
        self.position = position
        self.rotation = rotation
        self.scale = scale
        self.scaleFactors = scaleFactors
        self.doubleSided = doubleSided
        self.hiddenForUser = hiddenForUser
        self.canBeMirroredVertically = canBeMirroredVertically
        self.showOn = showOn
        self.tags = tags or ()
        self.clipAngle = clipAngle
        self.compatibleModels = compatibleModels
        self.itemId = itemId
        self.options = options
        self.anchorShift = anchorShift
        self.modificationOrder = modificationOrder


class AttachmentSlotDescription(object):
    __metaclass__ = ReflectionMetaclass
    __slots__ = ('type', 'slotId', 'position', 'rotation', 'scale', 'attachNode', 'hiddenForUser', 'enableVisTunnel', 'applyType', 'size', 'hangerId', 'hangerRotation', 'compatibleModels')

    def __init__(self, slotType='', slotId=0, position=None, rotation=None, scale=None, attachNode=None, hiddenForUser=False, enableVisTunnel=False, applyType='', size='', hangerId=0, hangerRotation=None, compatibleModels=(c11n_constants.SLOT_DEFAULT_ALLOWED_MODEL,)):
        self.type = slotType
        self.slotId = slotId
        self.position = position
        self.rotation = rotation
        self.scale = scale
        self.attachNode = attachNode
        self.hiddenForUser = hiddenForUser
        self.enableVisTunnel = enableVisTunnel
        self.applyType = applyType
        self.size = size
        self.hangerId = hangerId
        self.hangerRotation = hangerRotation
        self.compatibleModels = compatibleModels

    @property
    def scaleFactorId(self):
        return AttachmentSize.ALL.index(self.size)


MiscSlot = reflectedNamedTuple('MiscSlot', ('type', 'slotId', 'position', 'rotation', 'attachNode'))
LodSettings = namedtuple('LodSettings', ('maxLodDistance', 'maxPriority'))
NodesAndGroups = reflectedNamedTuple('NodesAndGroups', ('nodes', 'groups', 'activePostmortem', 'lodSettings'))
Camouflage = reflectedNamedTuple('Camouflage', ('tiling', 'exclusionMask', 'density', 'aoTextureSize'))
DEFAULT_CAMOUFLAGE = Camouflage((1.0, 1.0, 0.0, 0.0), '', (1.0, 1.0), (1, 1))
EMPTY_CAMOUFLAGE = Camouflage(None, None, None, None)
SwingingSettings = reflectedNamedTuple('SwingingSettings', ('lodDist', 'sensitivityToImpulse', 'pitchParams', 'rollParams'))

class I18nString(object):
    __slots__ = ('__value', '__converted')

    def __init__(self, key):
        super(I18nString, self).__init__()
        self.__value = i18n.makeString(key)
        self.__converted = False

    @property
    def value(self):
        if not self.__converted:
            self.__value = i18n.makeString(self.__value)
            self.__converted = True
        return self.__value


class _I18nConvertedFlags(object):
    UNDEFINED = 0
    USER_STRING = 1
    SHORT_STRING = 2
    DESCRIPTION = 4
    SHORT_DESCRIPTION_SPECIAL = 8
    LONG_DESCRIPTION_SPECIAL = 16
    SHORT_FILTER_ALERT_SPECIAL = 18
    LONG_FILTER_ALERT_SPECIAL = 20


class I18nComponent(object):
    __slots__ = ('__userString', '__shortString', '__description', '__converted', '__shortDescriptionSpecial', '__longDescriptionSpecial', '__shortFilterAlertSpecial', '__longFilterAlertSpecial')

    def __init__(self, userStringKey, descriptionKey, shortStringKey='', shortDescriptionSpecialKey='', longDescriptionSpecialKey='', shortFilterAlertKey='', longFilterAlertKey=''):
        super(I18nComponent, self).__init__()
        self.__userString = userStringKey
        if shortStringKey:
            self.__shortString = shortStringKey
        else:
            self.__shortString = component_constants.EMPTY_STRING
        self.__description = descriptionKey
        self.__converted = _I18nConvertedFlags.UNDEFINED
        if shortDescriptionSpecialKey:
            self.__shortDescriptionSpecial = shortDescriptionSpecialKey
        else:
            self.__shortDescriptionSpecial = component_constants.EMPTY_STRING
        if longDescriptionSpecialKey:
            self.__longDescriptionSpecial = longDescriptionSpecialKey
        else:
            self.__longDescriptionSpecial = component_constants.EMPTY_STRING
        if shortFilterAlertKey:
            self.__longFilterAlertSpecial = shortFilterAlertKey
        else:
            self.__shortFilterAlertSpecial = component_constants.EMPTY_STRING
        if longFilterAlertKey:
            self.__longFilterAlertSpecial = longFilterAlertKey
        else:
            self.__longFilterAlertSpecial = component_constants.EMPTY_STRING

    @property
    def userString(self):
        if self.__converted & _I18nConvertedFlags.USER_STRING == 0:
            self.__userString = i18n.makeString(self.__userString)
            self.__converted |= _I18nConvertedFlags.USER_STRING
        return self.__userString

    @property
    def shortString(self):
        if self.__shortString and self.__converted & _I18nConvertedFlags.SHORT_STRING == 0:
            self.__shortString = i18n.makeString(self.__shortString)
            self.__converted |= _I18nConvertedFlags.SHORT_STRING
        return self.__shortString or self.userString

    @property
    def description(self):
        if self.__converted & _I18nConvertedFlags.DESCRIPTION == 0:
            self.__description = i18n.makeString(self.__description)
            self.__converted |= _I18nConvertedFlags.DESCRIPTION
        return self.__description

    @property
    def shortDescriptionSpecial(self):
        if self.__converted & _I18nConvertedFlags.SHORT_DESCRIPTION_SPECIAL == 0:
            self.__shortDescriptionSpecial = i18n.makeString(self.__shortDescriptionSpecial)
            self.__converted |= _I18nConvertedFlags.SHORT_DESCRIPTION_SPECIAL
        return self.__shortDescriptionSpecial

    @property
    def longDescriptionSpecial(self):
        if self.__converted & _I18nConvertedFlags.LONG_DESCRIPTION_SPECIAL == 0:
            self.__longDescriptionSpecial = i18n.makeString(self.__longDescriptionSpecial)
            self.__converted |= _I18nConvertedFlags.LONG_DESCRIPTION_SPECIAL
        return self.__longDescriptionSpecial

    @property
    def longFilterAlertSpecial(self):
        if self.__converted & _I18nConvertedFlags.LONG_FILTER_ALERT_SPECIAL == 0:
            self.__longFilterAlertSpecial = i18n.makeString(self.__longFilterAlertSpecial)
            self.__converted |= _I18nConvertedFlags.LONG_FILTER_ALERT_SPECIAL
        return self.__longFilterAlertSpecial

    @property
    def shortFilterAlertSpecial(self):
        if self.__converted & _I18nConvertedFlags.SHORT_FILTER_ALERT_SPECIAL == 0:
            self.__shortFilterAlertSpecial = i18n.makeString(self.__shortFilterAlertSpecial)
            self.__converted |= _I18nConvertedFlags.SHORT_FILTER_ALERT_SPECIAL
        return self.__shortFilterAlertSpecial


class I18nExposedComponent(I18nComponent):
    __slots__ = ('__userKey', '__descriptionKey', '__longDescriptionSpecialKey', '__name', '__shortDescriptionSpecialKey')

    def __init__(self, userStringKey, descriptionKey, longDescriptionSpecialKey='', name='', shortDescriptionSpecialKey=''):
        super(I18nExposedComponent, self).__init__(userStringKey, descriptionKey, longDescriptionSpecialKey=longDescriptionSpecialKey, shortDescriptionSpecialKey=shortDescriptionSpecialKey)
        self.__userKey = userStringKey
        self.__descriptionKey = descriptionKey
        self.__longDescriptionSpecialKey = longDescriptionSpecialKey
        self.__name = name
        self.__shortDescriptionSpecialKey = shortDescriptionSpecialKey

    @property
    def userKey(self):
        return self.__userKey

    @property
    def descriptionKey(self):
        return self.__descriptionKey

    @property
    def longDescriptionSpecialKey(self):
        return self.__longDescriptionSpecialKey

    @property
    def name(self):
        return self.__name

    @property
    def shortDescriptionSpecialKey(self):
        return self.__shortDescriptionSpecialKey


class DeviceHealth(object):
    __slots__ = ('maxHealth', 'repairCost', 'maxRegenHealth', 'healthRegenPerSec', 'healthBurnPerSec', 'chanceToHit', 'hysteresisHealth', 'invulnerable', 'repairSpeedLimiter', 'repairTime')

    def __init__(self, maxHealth, repairCost=component_constants.ZERO_FLOAT, maxRegenHealth=component_constants.ZERO_INT):
        super(DeviceHealth, self).__init__()
        self.repairTime = None
        self.maxHealth = maxHealth
        self.repairCost = repairCost
        self.maxRegenHealth = maxRegenHealth
        self.healthRegenPerSec = component_constants.ZERO_FLOAT
        self.hysteresisHealth = None
        self.healthBurnPerSec = component_constants.ZERO_FLOAT
        self.chanceToHit = None
        self.invulnerable = False
        self.repairSpeedLimiter = None
        return

    def __repr__(self):
        return 'DeviceHealth(maxHealth={}, repairCost={}, maxRegenHealth={}, healthRegenPerSec={}, hysteresisHealth={})'.format(self.maxHealth, self.repairCost, self.maxRegenHealth, self.healthRegenPerSec, self.hysteresisHealth)

    @property
    def maxRepairCost(self):
        return (self.maxHealth - self.maxRegenHealth) * self.repairCost


DEFAULT_DEVICE_HEALTH = DeviceHealth(1)

class ModelStatesPaths(object):
    __slots__ = ('__undamaged', '__destroyed', '__exploded')
    __metaclass__ = ReflectionMetaclass

    def __init__(self, undamaged, destroyed, exploded):
        super(ModelStatesPaths, self).__init__()
        self.__undamaged = tuple(path_builder.makeIndexes(undamaged))
        self.__destroyed = tuple(path_builder.makeIndexes(destroyed))
        self.__exploded = tuple(path_builder.makeIndexes(exploded))

    def __repr__(self):
        return 'ModelStatesPaths(undamaged={}, destroyed={}, exploded={})'.format(self.undamaged, self.destroyed, self.exploded)

    @property
    def undamaged(self):
        return path_builder.makePath(*self.__undamaged)

    @property
    def destroyed(self):
        return path_builder.makePath(*self.__destroyed)

    @property
    def exploded(self):
        return path_builder.makePath(*self.__exploded)

    if IS_EDITOR:

        def setUndamaged(self, value):
            self.__undamaged = tuple(path_builder.makeIndexes(value))

        def setDestroyed(self, value):
            self.__destroyed = tuple(path_builder.makeIndexes(value))

        def setExploded(self, value):
            self.__exploded = tuple(path_builder.makeIndexes(value))

    def getPathByStateName(self, stateName):
        path = getattr(self, stateName, None)
        if path is None:
            raise SoftException('State {} is not found'.format(stateName))
        return path


ImpulseData = namedtuple('ImpulseData', ('magnitude', 'applyPoint', 'duration'))

def readImpulseData(ctx, section, subsection='impulse'):
    impulseCtx, impulseSection = _xml.getSubSectionWithContext(ctx, section, subsection)
    impulse = ImpulseData(magnitude=_xml.readNonNegativeFloat(impulseCtx, impulseSection, 'magnitude'), applyPoint=_xml.readVector3(impulseCtx, impulseSection, 'applyPoint', component_constants.ZERO_VECTOR3), duration=_xml.readNonNegativeFloat(impulseCtx, impulseSection, 'duration'))
    return impulse


class RocketAccelerationParams(object):
    __slots__ = ('deployTime', 'reloadTime', 'reuseCount', 'duration', 'impulse', 'modifiers', 'kpi')

    def __init__(self, deployTime, reloadTime, reuseCount, duration, impulse, modifiers, kpi):
        self.deployTime = deployTime
        self.reloadTime = reloadTime
        self.reuseCount = reuseCount
        self.duration = duration
        self.impulse = impulse
        self.modifiers = modifiers
        self.kpi = kpi

    def __repr__(self):
        return 'deployTime={}, reloadTime={},reuseCount={}, duration={}, impulse={}, modifiers={}'.format(self.deployTime, self.reloadTime, self.reuseCount, self.duration, self.impulse, self.modifiers)


class MechanicsParams(object):
    __slots__ = ('__origin', 'modifiers')
    MECHANICS_NAME = None
    COMPONENT_TYPE_ID = None

    def __init__(self, modifiers=None):
        self.__origin = None
        self.modifiers = modifiers
        return

    @classmethod
    def getSubClasses(cls, uniqueParamNames=None):
        if uniqueParamNames is None:
            uniqueParamNames = set()
        paramsClasses = []
        for paramsCls in cls.__subclasses__():
            if paramsCls.MECHANICS_NAME is None:
                paramsClasses.extend(paramsCls.getSubClasses(uniqueParamNames))
            if paramsCls.MECHANICS_NAME not in uniqueParamNames:
                paramsClasses.append(paramsCls)
                uniqueParamNames.add(paramsCls.MECHANICS_NAME)

        return paramsClasses

    @classmethod
    def readMechanicsParams(cls, xmlCtx, section, readModifiers):
        if not cls.MECHANICS_NAME:
            return
        else:
            mechanicCtx, mechanicSection = _xml.getSubSectionWithContext(xmlCtx, section, cls.MECHANICS_NAME, throwIfMissing=False)
            if mechanicSection is None:
                return
            params = cls._readMechanicsParams(mechanicCtx, mechanicSection, readModifiers)
            return params

    def createMechanicsParamsOrigin(self):
        origin = self.__origin
        if origin:
            params = cPickle.loads(origin)
            params.__origin = origin
            return params
        else:
            return None
            return None

    def getMechanicsMiscAttributes(self):
        return self.getDefaultMechanicsMiscAttributes()

    @classmethod
    def getDefaultMechanicsMiscAttributes(cls):
        return {}

    def isActiveMechanics(self, vehicleDescriptor):
        return True

    def applyMiscAttrToMechanics(self, miscAttrs):
        for attr in self.getMechanicsMiscAttributes():
            self._applyMechanicsAttrs(attr, miscAttrs[attr])

    def applyDynModifiersToMechanics(self, dynModifiers):
        modifiers = self.modifiers
        if not dynModifiers or self.modifiers is None:
            return
        else:
            for modifier in dynModifiers:
                modifierFilter = modifier[4]
                if modifierFilter == self.MECHANICS_NAME:
                    modifiers.append(modifier)

            return

    def updateVehicleAttrFactorsForAspect(self, vehicleDescr, factors, aspect):
        pass

    @classmethod
    def _readMechanicsParams(cls, ctx, section, readModifiers):
        return None

    def _applyMechanicsAttrs(self, attr, value):
        pass

    def _saveOrigin(self):
        self.__origin = cPickle.dumps(self, -1)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, ', '.join(('{}={}'.format(slotName, getattr(self, slotName)) for slotName in self.__slots__ if not slotName.startswith('_'))))


class GunMechanicsParams(MechanicsParams):
    __slots__ = ('gunInstallationSlot',)
    COMPONENT_TYPE_ID = ITEM_TYPES.vehicleGun

    def __init__(self, modifiers=None):
        super(GunMechanicsParams, self).__init__(modifiers)
        self.gunInstallationSlot = None
        return

    def setGunInstallationSlot(self, gunInstallationSlot):
        self.gunInstallationSlot = gunInstallationSlot


class RechargeableNitroParams(MechanicsParams):
    __slots__ = ('deployTime', 'reloadTime', 'duration', 'threshold', 'cooldown', 'addMaxSpeedForwardBonus', 'addRotationSpeedBonus', 'impulse')
    MECHANICS_NAME = 'rechargeableNitro'

    def __init__(self, deployTime, reloadTime, duration, cooldown, addMaxSpeedForwardBonus, addRotationSpeedBonus, impulse, modifiers, threshold=0):
        super(RechargeableNitroParams, self).__init__(modifiers)
        self.deployTime = deployTime
        self.reloadTime = reloadTime
        self.duration = duration
        self.threshold = threshold
        self.cooldown = cooldown
        self.addMaxSpeedForwardBonus = addMaxSpeedForwardBonus
        self.addRotationSpeedBonus = addRotationSpeedBonus
        self.impulse = impulse
        self._saveOrigin()

    @classmethod
    def _readMechanicsParams(cls, ctx, section, readModifiers):
        impulse = readImpulseData(ctx, section)
        modifiers = readModifiers(ctx, _xml.getSubsection(ctx, section, 'modifiers'))
        return cls(deployTime=_xml.readNonNegativeFloat(ctx, section, 'deployTime'), reloadTime=_xml.readPositiveFloat(ctx, section, 'reloadTime'), duration=_xml.readPositiveFloat(ctx, section, 'duration'), threshold=_xml.readPositiveFloat(ctx, section, 'threshold'), cooldown=_xml.readPositiveFloat(ctx, section, 'cooldown'), addMaxSpeedForwardBonus=_xml.readFloat(ctx, section, 'addMaxSpeedForwardBonus'), addRotationSpeedBonus=_xml.readFloat(ctx, section, 'addRotationSpeedBonus'), impulse=impulse, modifiers=modifiers)

    @classmethod
    def getDefaultMechanicsMiscAttributes(cls):
        return {'rechargeableNitro/duration': 0.0,
         'rechargeableNitro/reloadTime': 0.0,
         'rechargeableNitro/addMaxSpeedForwardBonus': 0.0,
         'rechargeableNitro/addRotationSpeedBonus': 0.0}

    def _applyMechanicsAttrs(self, attr, value):
        if attr == 'rechargeableNitro/duration':
            self.duration += value
        elif attr == 'rechargeableNitro/reloadTime':
            self.reloadTime += value
        elif attr == 'rechargeableNitro/addMaxSpeedForwardBonus':
            self.addMaxSpeedForwardBonus += value
            if self.addMaxSpeedForwardBonus or value:
                self.__applyMulModifier('dynAttrs/', 'vehicle/maxSpeed/forward', self.addMaxSpeedForwardBonus)
        elif attr == 'rechargeableNitro/addRotationSpeedBonus':
            self.addRotationSpeedBonus += value
            if self.addRotationSpeedBonus or value:
                self.__applyMulModifier('dynAttrs/', 'vehicle/rotationSpeed', self.addRotationSpeedBonus)

    def __applyMulModifier(self, modifierType, modifierName, bonusValue):
        mulValue = max(0.0, 1.0 + bonusValue)
        newModifier = ('mul',
         modifierType,
         modifierName,
         mulValue,
         'rechargeableNitro')
        foundIndex = None
        for idx, (opCode, modType, modName, _, _) in enumerate(self.modifiers):
            if opCode == 'mul' and modType == modifierType and modName == modifierName:
                foundIndex = idx
                break

        if foundIndex is not None:
            self.modifiers[foundIndex] = newModifier
        else:
            self.modifiers.append(newModifier)
        return

    def __repr__(self):
        return 'deployTime={}, reloadTime={}, duration={}, threshold={}, impulse={}, cooldown={}, addMaxSpeedForwardBonus={}, addRotationSpeedBonus={}, modifiers={}'.format(self.deployTime, self.reloadTime, self.duration, self.threshold, self.impulse, self.cooldown, self.addMaxSpeedForwardBonus, self.addRotationSpeedBonus, self.modifiers)


class ConcentrationModeParams(MechanicsParams):
    __slots__ = ('deployTime', 'reloadTime', 'duration')
    MECHANICS_NAME = 'concentrationMode'

    def __init__(self, deployTime, reloadTime, duration, modifiers):
        super(ConcentrationModeParams, self).__init__(modifiers)
        self.deployTime = deployTime
        self.reloadTime = reloadTime
        self.duration = duration
        self._saveOrigin()

    @classmethod
    def getDefaultMechanicsMiscAttributes(cls):
        return {'concentrationModeDeployTime': 0.0,
         'concentrationModeReloadTime': 0.0,
         'concentrationModeDuration': 0.0}

    @classmethod
    def _readMechanicsParams(cls, ctx, section, readModifiers):
        modifiers = readModifiers(ctx, _xml.getSubsection(ctx, section, 'modifiers'))
        return cls(deployTime=_xml.readPositiveFloat(ctx, section, 'deployTime'), reloadTime=_xml.readPositiveFloat(ctx, section, 'reloadTime'), duration=_xml.readPositiveFloat(ctx, section, 'duration'), modifiers=modifiers)

    def _applyMechanicsAttrs(self, attr, value):
        if attr == 'concentrationModeDeployTime':
            self.deployTime += value
        elif attr == 'concentrationModeReloadTime':
            self.reloadTime += value
        elif attr == 'concentrationModeDuration':
            self.duration += value


class ImprovedRammingParams(MechanicsParams):
    __slots__ = ('damageBonusStageSize', 'damageBonusBasicFactor', 'damageBonusChangeFactor', 'trackDamageBonusStageSize', 'trackDamageBonusBasicFactor', 'trackDamageBonusChangeFactor', 'reductionDamageBonusStageSize', 'reductionDamageBonusBasicFactor', 'reductionDamageBonusChangeFactor', 'damageValueToShowAnimation', 'effectSpeedThreshold')
    MECHANICS_NAME = 'improvedRamming'

    def __init__(self, damageBonusStageSize, damageBonusBasicFactor, damageBonusChangeFactor, trackDamageBonusStageSize, trackDamageBonusBasicFactor, trackDamageBonusChangeFactor, reductionDamageBonusStageSize, reductionDamageBonusBasicFactor, reductionDamageBonusChangeFactor, damageValueToShowAnimation, effectSpeedThreshold):
        super(ImprovedRammingParams, self).__init__()
        self.damageBonusStageSize = damageBonusStageSize
        self.damageBonusBasicFactor = damageBonusBasicFactor
        self.damageBonusChangeFactor = damageBonusChangeFactor
        self.trackDamageBonusStageSize = trackDamageBonusStageSize
        self.trackDamageBonusBasicFactor = trackDamageBonusBasicFactor
        self.trackDamageBonusChangeFactor = trackDamageBonusChangeFactor
        self.reductionDamageBonusStageSize = reductionDamageBonusStageSize
        self.reductionDamageBonusBasicFactor = reductionDamageBonusBasicFactor
        self.reductionDamageBonusChangeFactor = reductionDamageBonusChangeFactor
        self.damageValueToShowAnimation = damageValueToShowAnimation
        self.effectSpeedThreshold = effectSpeedThreshold
        self._saveOrigin()

    @classmethod
    def getDefaultMechanicsMiscAttributes(cls):
        return {'improvedRammingDamageBonus/basicFactor': 1.0,
         'improvedRammingTrackDamageBonus/basicFactor': 1.0,
         'improvedRammingDamageReductionBonus/basicFactor': 1.0}

    @classmethod
    def _readMechanicsParams(cls, ctx, section, readModifiers):
        _defaultStageSize = 10.0
        _defaultDamageToAnimation = 0
        _defaultSpeedToEffect = 30
        damageBonusStageSize = _xml.readNonNegativeFloat(ctx, section, 'damageBonusStageSize', _defaultStageSize)
        damageBonusBasicFactor = _xml.readNonNegativeFloat(ctx, section, 'damageBonusBasicFactor')
        damageBonusChangeFactor = _xml.readNonNegativeFloat(ctx, section, 'damageBonusChangeFactor')
        trackDamageBonusStageSize = _xml.readNonNegativeFloat(ctx, section, 'trackDamageBonusStageSize', _defaultStageSize)
        trackDamageBonusBasicFactor = _xml.readNonNegativeFloat(ctx, section, 'trackDamageBonusBasicFactor')
        trackDamageBonusChangeFactor = _xml.readNonNegativeFloat(ctx, section, 'trackDamageBonusChangeFactor')
        reductionDamageBonusStageSize = _xml.readNonNegativeFloat(ctx, section, 'reductionDamageBonusStageSize', _defaultStageSize)
        reductionDamageBonusBasicFactor = _xml.readNonNegativeFloat(ctx, section, 'reductionDamageBonusBasicFactor')
        reductionDamageBonusChangeFactor = _xml.readNonNegativeFloat(ctx, section, 'reductionDamageBonusChangeFactor')
        damageValueToShowAnimation = _xml.readNonNegativeInt(ctx, section, 'damageValueToShowAnimation', _defaultDamageToAnimation)
        effectSpeedThreshold = _xml.readNonNegativeInt(ctx, section, 'effectSpeedThreshold', _defaultSpeedToEffect)
        return cls(damageBonusStageSize=damageBonusStageSize * component_constants.KMH_TO_MS, damageBonusBasicFactor=damageBonusBasicFactor, damageBonusChangeFactor=damageBonusChangeFactor, trackDamageBonusStageSize=trackDamageBonusStageSize * component_constants.KMH_TO_MS, trackDamageBonusBasicFactor=trackDamageBonusBasicFactor, trackDamageBonusChangeFactor=trackDamageBonusChangeFactor, reductionDamageBonusStageSize=reductionDamageBonusStageSize * component_constants.KMH_TO_MS, reductionDamageBonusBasicFactor=reductionDamageBonusBasicFactor, reductionDamageBonusChangeFactor=reductionDamageBonusChangeFactor, damageValueToShowAnimation=damageValueToShowAnimation, effectSpeedThreshold=effectSpeedThreshold * component_constants.KMH_TO_MS)

    def _applyMechanicsAttrs(self, attr, value):
        if attr == 'improvedRammingDamageBonus/basicFactor':
            self.damageBonusBasicFactor *= value
        elif attr == 'improvedRammingTrackDamageBonus/basicFactor':
            self.trackDamageBonusBasicFactor *= value
        elif attr == 'improvedRammingDamageReductionBonus/basicFactor':
            self.reductionDamageBonusBasicFactor *= value


class PowerModeParams(MechanicsParams):
    __slots__ = ('modeThreshold', 'modeDuration', 'accelerationFactor', 'attenuationFactor', 'speedThreshold', 'gracePeriod', 'vehicleParams')
    MECHANICS_NAME = 'powerMode'
    DEFAULT_VEHICLE_PARAMS = {'vehicleSpeed': 1.0,
     'dispersion': 1.0,
     'rotationSpeed': 1.0,
     'enginePower': 1.0}

    def __init__(self, modeThreshold, modeDuration, accelerationFactor, attenuationFactor, speedThreshold, gracePeriod, vehicleParams):
        super(PowerModeParams, self).__init__()
        self.modeThreshold = modeThreshold
        self.modeDuration = modeDuration
        self.accelerationFactor = accelerationFactor
        self.attenuationFactor = attenuationFactor
        self.speedThreshold = speedThreshold
        self.gracePeriod = gracePeriod
        self.vehicleParams = dict(PowerModeParams.DEFAULT_VEHICLE_PARAMS, **vehicleParams)
        self._saveOrigin()

    @classmethod
    def getDefaultMechanicsMiscAttributes(cls):
        return {'powerMode/modeThreshold': 0.0,
         'powerMode/modeDuration': 0.0,
         'powerMode/speedThreshold': 0.0,
         'powerMode/gracePeriod': 0.0,
         'powerMode/accelerationFactor': 1.0,
         'powerMode/attenuationFactor': 1.0,
         'powerMode/vehicleSpeed': 1.0,
         'powerMode/rotationSpeed': 1.0,
         'powerMode/enginePower': 1.0,
         'powerMode/dispersion': 1.0}

    @classmethod
    def _readMechanicsParams(cls, ctx, section, readModifiers):
        modeThreshold = _xml.readPositiveFloat(ctx, section, 'modeThreshold')
        modeDuration = _xml.readPositiveFloat(ctx, section, 'modeDuration')
        accelerationFactor = _xml.readPositiveFloat(ctx, section, 'accelerationFactor', 1.0)
        attenuationFactor = _xml.readPositiveFloat(ctx, section, 'attenuationFactor', 1.0)
        speedThreshold = _xml.readPositiveFloat(ctx, section, 'speedThreshold', 0.0)
        gracePeriod = _xml.readPositiveFloat(ctx, section, 'gracePeriod', 0.0)
        vehicleParams = {}
        vehicleParamSection = section['vehicleParams']
        for paramName in vehicleParamSection.keys():
            vehicleParams[paramName] = vehicleParamSection.readFloat(paramName)

        return cls(modeThreshold=modeThreshold, modeDuration=modeDuration, accelerationFactor=accelerationFactor, attenuationFactor=attenuationFactor, speedThreshold=speedThreshold * component_constants.KMH_TO_MS, gracePeriod=gracePeriod, vehicleParams=vehicleParams)

    def _applyMechanicsAttrs(self, attr, value):
        if attr == 'powerMode/modeThreshold':
            self.modeThreshold += value
        elif attr == 'powerMode/modeDuration':
            self.modeDuration += value
        elif attr == 'powerMode/speedThreshold':
            self.speedThreshold += value * component_constants.KMH_TO_MS
        elif attr == 'powerMode/gracePeriod':
            self.gracePeriod += value
        elif attr == 'powerMode/accelerationFactor':
            self.accelerationFactor *= value
        elif attr == 'powerMode/attenuationFactor':
            self.attenuationFactor *= value
        elif attr == 'powerMode/vehicleSpeed':
            self.vehicleParams['vehicleSpeed'] *= value
        elif attr == 'powerMode/rotationSpeed':
            self.vehicleParams['rotationSpeed'] *= value
        elif attr == 'powerMode/enginePower':
            self.vehicleParams['enginePower'] *= value
        elif attr == 'powerMode/dispersion':
            self.vehicleParams['dispersion'] *= value


class BattleFuryParams(MechanicsParams):
    __slots__ = ('maxLevel', 'duration', 'reloadSpdBonus', 'gainPerHit', 'gainPerKill')
    MECHANICS_NAME = 'battleFury'

    def __init__(self, maxLevel, duration, reloadSpdBonus, gainPerHit, gainPerKill):
        super(BattleFuryParams, self).__init__()
        self.maxLevel = maxLevel
        self.duration = duration
        self.reloadSpdBonus = reloadSpdBonus
        self.gainPerHit = gainPerHit
        self.gainPerKill = gainPerKill
        self._saveOrigin()

    @classmethod
    def getDefaultMechanicsMiscAttributes(cls):
        return {'battleFury/gainPerKill': 0,
         'battleFury/duration': 0.0,
         'battleFury/reloadSpdBonus': 0.0}

    @classmethod
    def _readMechanicsParams(cls, ctx, section, readModifiers):
        maxLevel = _xml.readPositiveInt(ctx, section, 'maxLevel')
        duration = _xml.readPositiveFloat(ctx, section, 'duration')
        reloadSpdBonus = _xml.readNonNegativeFloat(ctx, section, 'reloadSpdBonus')
        gainPerHit = _xml.readNonNegativeInt(ctx, section, 'gainPerHit')
        gainPerKill = _xml.readNonNegativeInt(ctx, section, 'gainPerKill')
        return cls(maxLevel=maxLevel, duration=duration, reloadSpdBonus=reloadSpdBonus, gainPerHit=gainPerHit, gainPerKill=gainPerKill)

    def _applyMechanicsAttrs(self, attr, value):
        if attr == 'battleFury/gainPerKill':
            self.gainPerKill += value
        elif attr == 'battleFury/duration':
            self.duration += value
        elif attr == 'battleFury/reloadSpdBonus':
            self.reloadSpdBonus += value


class PillboxSiegeModeParams(MechanicsParams):
    __slots__ = ('switchDriveToPillboxTime', 'switchSiegeToPillboxTime', 'switchPillboxToSiegeTime', 'switchPillboxToDriveTime')
    MECHANICS_NAME = 'pillboxSiegeMode'

    def __init__(self, switchDriveToPillboxTime, switchSiegeToPillboxTime, switchPillboxToSiegeTime, switchPillboxToDriveTime, modifiers):
        super(PillboxSiegeModeParams, self).__init__(modifiers)
        self.switchDriveToPillboxTime = switchDriveToPillboxTime
        self.switchSiegeToPillboxTime = switchSiegeToPillboxTime
        self.switchPillboxToSiegeTime = switchPillboxToSiegeTime
        self.switchPillboxToDriveTime = switchPillboxToDriveTime
        self.modifiers = modifiers
        self._saveOrigin()

    @classmethod
    def getDefaultMechanicsMiscAttributes(cls):
        return {'pillboxSiegeMode/switchDriveToPillboxTime': 0.0,
         'pillboxSiegeMode/switchSiegeToPillboxTime': 0.0,
         'pillboxSiegeMode/switchPillboxToSiegeTime': 0.0,
         'pillboxSiegeMode/switchPillboxToDriveTime': 0.0}

    @classmethod
    def _readMechanicsParams(cls, ctx, section, readModifiers):
        switchDriveToPillboxTime = _xml.readNonNegativeFloat(ctx, section, 'switchDriveToPillboxTime')
        switchSiegeToPillboxTime = _xml.readNonNegativeFloat(ctx, section, 'switchSiegeToPillboxTime')
        switchPillboxToSiegeTime = _xml.readNonNegativeFloat(ctx, section, 'switchPillboxToSiegeTime')
        switchPillboxToDriveTime = _xml.readNonNegativeFloat(ctx, section, 'switchPillboxToDriveTime')
        modifiers = readModifiers(ctx, _xml.getSubsection(ctx, section, 'modifiers'))
        return cls(switchDriveToPillboxTime=switchDriveToPillboxTime, switchSiegeToPillboxTime=switchSiegeToPillboxTime, switchPillboxToSiegeTime=switchPillboxToSiegeTime, switchPillboxToDriveTime=switchPillboxToDriveTime, modifiers=modifiers)

    def _applyMechanicsAttrs(self, attr, value):
        if attr == 'pillboxSiegeMode/switchDriveToPillboxTime':
            self.switchDriveToPillboxTime += value
        elif attr == 'pillboxSiegeMode/switchSiegeToPillboxTime':
            self.switchSiegeToPillboxTime += value
        elif attr == 'pillboxSiegeMode/switchPillboxToSiegeTime':
            self.switchPillboxToSiegeTime += value
        elif attr == 'pillboxSiegeMode/switchPillboxToDriveTime':
            self.switchPillboxToDriveTime += value


class StationaryReloadParams(GunMechanicsParams):
    __slots__ = ('preparingSpeedFactor', 'finishingSpeedFactor', 'preparingDelay', 'finishingDelay', 'fixAngles')
    MECHANICS_NAME = 'stationaryReload'

    def __init__(self, preparingSpeedFactor, finishingSpeedFactor, preparingDelay, finishingDelay, fixAngles):
        super(StationaryReloadParams, self).__init__()
        self.preparingSpeedFactor = preparingSpeedFactor
        self.finishingSpeedFactor = finishingSpeedFactor
        self.preparingDelay = preparingDelay
        self.finishingDelay = finishingDelay
        self.fixAngles = fixAngles
        self._saveOrigin()

    @classmethod
    def getDefaultMechanicsMiscAttributes(cls):
        return {'stationaryReload/preparingDelayFactor': 1.0,
         'stationaryReload/finishingDelayFactor': 1.0}

    @classmethod
    def _readMechanicsParams(cls, ctx, section, readModifiers):
        return cls(preparingSpeedFactor=_xml.readNonNegativeFloat(ctx, section, 'preparingSpeedFactor'), finishingSpeedFactor=_xml.readNonNegativeFloat(ctx, section, 'finishingSpeedFactor'), preparingDelay=_xml.readNonNegativeFloat(ctx, section, 'preparingDelay'), finishingDelay=_xml.readNonNegativeFloat(ctx, section, 'finishingDelay'), fixAngles=tuple(map(radians, _xml.readVector2(ctx, section, 'fixAngles'))))

    def _applyMechanicsAttrs(self, attr, value):
        if attr == 'stationaryReload/preparingDelayFactor':
            self.preparingDelay *= value
            self.preparingSpeedFactor /= value
        elif attr == 'stationaryReload/finishingDelayFactor':
            self.finishingDelay *= value
            self.finishingSpeedFactor /= value


class ExtraShotClipParams(GunMechanicsParams):
    __slots__ = ('extraReloadTime',)
    MECHANICS_NAME = 'extraShotClip'

    def __init__(self, extraReloadTime):
        super(ExtraShotClipParams, self).__init__()
        self.extraReloadTime = extraReloadTime
        self._saveOrigin()

    @classmethod
    def getDefaultMechanicsMiscAttributes(cls):
        return {'gun/extraShotClip/extraReloadTime': 0.0}

    def isActiveMechanics(self, vehicleDescriptor):
        return 'clip' in vehicleDescriptor.gun.tags and vehicleDescriptor.gun.clip[0] > 1

    def updateVehicleAttrFactorsForAspect(self, vehicleDescr, factors, aspect):
        factors['gun/extraReloadTime'] += self.extraReloadTime

    @classmethod
    def _readMechanicsParams(cls, ctx, section, readModifiers):
        extraReloadTime = _xml.readNonNegativeFloat(ctx, section, 'extraReloadTime', 0.0)
        return cls(extraReloadTime=extraReloadTime)

    def _applyMechanicsAttrs(self, attr, value):
        if attr == 'gun/extraShotClip/extraReloadTime':
            self.extraReloadTime += value


class AccuracyStacksParams(MechanicsParams):
    __slots__ = ('levelMax', 'levelInitial', 'levelAfterShot', 'aimLevelBonus', 'aimBonusCap', 'gainMaxSpd', 'gainTime', 'stabilizeBonus')
    MECHANICS_NAME = 'accuracyStacks'

    def __init__(self, levelMax, levelInitial, levelAfterShot, aimLevelBonus, aimBonusCap, gainMaxSpd, gainTime, stabilizeBonus):
        super(AccuracyStacksParams, self).__init__()
        self.levelMax = levelMax
        self.levelInitial = levelInitial
        self.levelAfterShot = levelAfterShot
        self.aimLevelBonus = aimLevelBonus
        self.aimBonusCap = aimBonusCap
        self.gainMaxSpd = gainMaxSpd
        self.gainTime = gainTime
        self.stabilizeBonus = stabilizeBonus
        self._saveOrigin()

    @classmethod
    def getDefaultMechanicsMiscAttributes(cls):
        return {'accuracyStacks/aimLevelBonus': 0.0,
         'accuracyStacks/gainMaxSpd': 0.0,
         'accuracyStacks/gainTime': 0.0,
         'accuracyStacks/stabilizeBonus': 0.0}

    @classmethod
    def _readMechanicsParams(cls, mechCtx, mechSection, readModifiers):
        levelMax = _xml.readPositiveInt(mechCtx, mechSection, 'levelMax')
        levelInitial = _xml.readNonNegativeInt(mechCtx, mechSection, 'levelInitial')
        levelAfterShot = _xml.readNonNegativeInt(mechCtx, mechSection, 'levelAfterShot')
        aimLevelBonus = _xml.readNonNegativeFloat(mechCtx, mechSection, 'aimLevelBonus')
        aimBonusCap = _xml.readNonNegativeFloat(mechCtx, mechSection, 'aimBonusCap', 0.99)
        gainMaxSpd = _xml.readNonNegativeFloat(mechCtx, mechSection, 'gainMaxSpd')
        gainTime = _xml.readPositiveFloat(mechCtx, mechSection, 'gainTime')
        stabilizeBonus = _xml.readNonNegativeFloat(mechCtx, mechSection, 'stabilizeBonus')
        return cls(levelMax=levelMax, levelInitial=levelInitial, levelAfterShot=levelAfterShot, aimLevelBonus=aimLevelBonus, aimBonusCap=aimBonusCap, gainMaxSpd=gainMaxSpd, gainTime=gainTime, stabilizeBonus=stabilizeBonus)

    def _applyMechanicsAttrs(self, attr, value):
        if attr == 'accuracyStacks/aimLevelBonus':
            self.aimLevelBonus += value
        elif attr == 'accuracyStacks/gainMaxSpd':
            self.gainMaxSpd += value
        elif attr == 'accuracyStacks/gainTime':
            self.gainTime += value
        elif attr == 'accuracyStacks/stabilizeBonus':
            self.stabilizeBonus += value


class SecondaryGunParams(GunMechanicsParams):
    __slots__ = ('initiationTime', 'dependentOnMainGun')
    __metaclass__ = ReflectionMetaclass
    MECHANICS_NAME = 'secondaryGun'

    def __init__(self, initiationTime, dependentOnMainGun):
        super(SecondaryGunParams, self).__init__()
        self.initiationTime = initiationTime
        self.dependentOnMainGun = dependentOnMainGun
        self._saveOrigin()

    @classmethod
    def getDefaultMechanicsMiscAttributes(cls):
        return cls._generateMechanicMiscAttributes()

    def getMechanicsMiscAttributes(self):
        return self._generateMechanicMiscAttributes(self.gunInstallationSlot.gun)

    def isActiveMechanics(self, vehicleDescriptor):
        gunInstallationSlot = self.gunInstallationSlot
        return not gunInstallationSlot.isMainInstallation() and 'secondaryGun' in gunInstallationSlot.gun.tags

    @classmethod
    def _readMechanicsParams(cls, ctx, section, readModifiers):
        return cls(initiationTime=_xml.readNonNegativeFloat(ctx, section, 'initiationTime'), dependentOnMainGun=_xml.readBool(ctx, section, 'dependentOnMainGun'))

    def _applyMechanicsAttrs(self, attr, value):
        if attr == 'secondaryGun/initiationTime':
            self.initiationTime *= value

    @staticmethod
    def _generateMechanicMiscAttributes(gunDescr=None):
        gunShotDispersionFactors = gunDescr.shotDispersionFactors if gunDescr else {}
        return {'secondaryGun/initiationTime': 1.0,
         'secondaryGunReloadTimeFactor': 1.0,
         'secondaryGunAimingTimeFactor': 1.0,
         'secondaryGun/invisibilityFactorAtShot': gunDescr.invisibilityFactorAtShot if gunDescr else 1.0,
         'secondaryGun/shotDispersionFactors/afterShot': gunShotDispersionFactors.get('afterShot', 1.0),
         'secondaryGun/shotDispersionFactors/whileGunDamaged': gunShotDispersionFactors.get('whileGunDamaged', 1.0),
         'secondaryGun/shotDispersionFactors/turretRotation': gunShotDispersionFactors.get('turretRotation', 0.0),
         'secondaryGunMultShotDispersionFactor': 1.0,
         'secondaryGunAdditiveShotDispersionFactor': 1.0}


class SupportWeaponParams(MechanicsParams):
    __slots__ = ()
    MECHANICS_NAME = 'supportWeapon'

    def __init__(self):
        super(SupportWeaponParams, self).__init__()
        self._saveOrigin()

    def isActiveMechanics(self, vehicleDescriptor):
        mechanicsParams = vehicleDescriptor.mechanicsParams
        return SecondaryGunParams.MECHANICS_NAME in mechanicsParams and mechanicsParams[SecondaryGunParams.MECHANICS_NAME].isActiveMechanics(vehicleDescriptor)

    @classmethod
    def _readMechanicsParams(cls, xmlCtx, section, readModifiers):
        return cls()


class ChargeableBurstParams(GunMechanicsParams):
    __slots__ = ('penetrationCount', 'burstDispersionFactor')
    MECHANICS_NAME = 'chargeableBurst'

    def __init__(self, penetrationCount, burstDispersionFactor, modifiers):
        super(ChargeableBurstParams, self).__init__(modifiers)
        self.penetrationCount = penetrationCount
        self.burstDispersionFactor = burstDispersionFactor
        self._saveOrigin()

    @classmethod
    def _readMechanicsParams(cls, ctx, section, readModifiers):
        penetrationCount = _xml.readNonNegativeInt(ctx, section, 'penetrationCount')
        burstDispersionFactor = _xml.readNonNegativeFloat(ctx, section, 'burstDispersionFactor')
        modifiers = readModifiers(ctx, _xml.getSubsection(ctx, section, 'modifiers'))
        return cls(penetrationCount=penetrationCount, burstDispersionFactor=burstDispersionFactor, modifiers=modifiers)

    @classmethod
    def getDefaultMechanicsMiscAttributes(cls):
        return {'chargeableBurst/penetrationCount': 0,
         'chargeableBurst/burstDispersionFactor': 1.0}

    def isActiveMechanics(self, vehicleDescriptor):
        return vehicleDescriptor.hasBurst

    def _applyMechanicsAttrs(self, attr, value):
        if attr == 'chargeableBurst/penetrationCount':
            self.penetrationCount += value
        if attr == 'chargeableBurst/burstDispersionFactor':
            self.burstDispersionFactor *= value


class ChargeShotParams(MechanicsParams):
    __slots__ = ('timePerLevel', 'damageFactorsPerLevel', 'maxLevel', 'shotBlockTime')
    MECHANICS_NAME = 'chargeShot'

    def __init__(self, timePerLevel, damageFactorsPerLevel, shotBlockTime):
        super(ChargeShotParams, self).__init__()
        self.timePerLevel = timePerLevel
        self.damageFactorsPerLevel = damageFactorsPerLevel
        self.maxLevel = len(timePerLevel) - 1
        self.shotBlockTime = shotBlockTime
        self._saveOrigin()

    @classmethod
    def _readMechanicsParams(cls, mechCtx, mechSection, readModifiers):
        timePerLevel = list(_xml.readTupleOfNonNegativeFloats(mechCtx, mechSection, 'timePerLevel'))
        damageFactorsPerLevel = list(_xml.readTupleOfNonNegativeFloats(mechCtx, mechSection, 'damageFactorsPerLevel'))
        shotBlockTime = _xml.readNonNegativeFloat(mechCtx, mechSection, 'shotBlockTime')
        return cls(timePerLevel, damageFactorsPerLevel, shotBlockTime)

    @classmethod
    def getDefaultMechanicsMiscAttributes(cls):
        return {'chargeShot/damageFactorLevel1': 0.0,
         'chargeShot/damageFactorLevel2': 0.0,
         'chargeShot/damageFactorLevel3': 0.0,
         'chargeShot/timeToShotBlock': 0.0,
         'chargeShot/shotBlockTime': 0.0}

    def _applyMechanicsAttrs(self, attr, value):
        if attr == 'chargeShot/damageFactorLevel1':
            self.damageFactorsPerLevel[1] += value
        elif attr == 'chargeShot/damageFactorLevel2':
            self.damageFactorsPerLevel[2] += value
        elif attr == 'chargeShot/damageFactorLevel3':
            self.damageFactorsPerLevel[3] += value
        elif attr == 'chargeShot/timeToShotBlock':
            self.timePerLevel[3] += value
        elif attr == 'chargeShot/shotBlockTime':
            self.shotBlockTime += value


class OverheatStacksParams(MechanicsParams):
    __slots__ = ('levelMax', 'levelInc', 'levelDec', 'aimLevelBonus', 'dmgLevelBonus', 'gainMaxSpd', 'gainTime', 'delayTimerDuration', 'heatingTime', 'coolingTime', 'dmgBonus', 'aimBonus')
    MECHANICS_NAME = 'overheatStacks'

    def __init__(self, heatingTime, coolingTime, dmgBonus, aimBonus, gainMaxSpd, delayTimerDuration):
        super(OverheatStacksParams, self).__init__()
        self.levelMax = 255
        self.gainTime = 1.0
        self.gainMaxSpd = gainMaxSpd
        self.delayTimerDuration = delayTimerDuration
        self.heatingTime = heatingTime
        self.coolingTime = coolingTime
        self.dmgBonus = dmgBonus
        self.aimBonus = aimBonus
        self.configure()
        self._saveOrigin()

    def configure(self):
        self.levelInc = self.levelMax * self.gainTime / self.heatingTime
        self.levelDec = self.levelMax * self.gainTime / self.coolingTime
        self.dmgLevelBonus = (self.dmgBonus - 1) / self.levelMax
        self.aimLevelBonus = (self.aimBonus - 1) / self.levelMax
        self.aimLevelBonus = self.__clampAimLevelBonus(self.aimLevelBonus)

    @classmethod
    def getDefaultMechanicsMiscAttributes(cls):
        return {'overheatStacks/dmgBonusFactor': 1.0,
         'overheatStacks/aimBonusFactor': 1.0,
         'overheatStacks/gainMaxSpd': 0.0,
         'overheatStacks/totalTime': 0.0}

    @classmethod
    def _readMechanicsParams(cls, mechCtx, mechSection, _):
        heatingTime = _xml.readNonNegativeInt(mechCtx, mechSection, 'heatingTime', 0)
        coolingTime = _xml.readNonNegativeInt(mechCtx, mechSection, 'coolingTime', 0)
        dmgBonus = _xml.readNonNegativeFloat(mechCtx, mechSection, 'dmgBonus', 0.0)
        aimBonus = _xml.readNonNegativeFloat(mechCtx, mechSection, 'aimBonus', 0.0)
        gainMaxSpd = _xml.readNonNegativeFloat(mechCtx, mechSection, 'gainMaxSpd', 0.0)
        delayTimerDuration = _xml.readNonNegativeFloat(mechCtx, mechSection, 'delayTimerDuration', 0.0)
        return cls(heatingTime, coolingTime, dmgBonus, aimBonus, gainMaxSpd, delayTimerDuration)

    def _applyMechanicsAttrs(self, attr, value):
        if attr == 'overheatStacks/dmgBonusFactor':
            self.dmgBonus = max(0.0, self.dmgBonus + value - 1.0)
        elif attr == 'overheatStacks/aimBonusFactor':
            self.aimBonus = max(0.0, self.aimBonus + value - 1.0)
        elif attr == 'overheatStacks/gainMaxSpd':
            self.gainMaxSpd = max(0.0, self.gainMaxSpd + value)
        elif attr == 'overheatStacks/totalTime':
            self.heatingTime = max(1.0, self.heatingTime + value)

    def applyMiscAttrToMechanics(self, miscAttrs):
        super(OverheatStacksParams, self).applyMiscAttrToMechanics(miscAttrs)
        self.configure()

    @staticmethod
    def __clampAimLevelBonus(aimLevelBonus):
        res = min(0.99, max(0.0, aimLevelBonus))
        if res != aimLevelBonus:
            LOG_WARNING('[OverheatStacksParams] aimLevelBonus out of bounds (clamped, unclamped)', res, aimLevelBonus)
        return res


class TargetDesignatorParams(MechanicsParams):
    __slots__ = MechanicsParams.__slots__ + ('damageIncomeFactor', 'cooldownTime', 'deployTime', 'spottedMarkedTime', 'unspottedMarkedTime')
    MECHANICS_NAME = 'targetDesignator'

    def __init__(self, damageIncomeFactor, cooldownTime, deployTime, spottedMarkedTime, unspottedMarkedTime):
        super(TargetDesignatorParams, self).__init__()
        self.damageIncomeFactor = damageIncomeFactor
        self.cooldownTime = cooldownTime
        self.deployTime = deployTime
        self.spottedMarkedTime = spottedMarkedTime
        self.unspottedMarkedTime = unspottedMarkedTime
        self._saveOrigin()

    @classmethod
    def _readMechanicsParams(cls, mechCtx, mechSection, _):
        readFloat = partial(_xml.readNonNegativeFloat, mechCtx, mechSection)
        return cls(readFloat('damageIncomeFactor', 1.0), readFloat('cooldownTime', 1.0), readFloat('deployTime', 0.0), readFloat('spottedMarkedTime', 1.0), readFloat('unspottedMarkedTime', 1.0))

    @classmethod
    def getDefaultMechanicsMiscAttributes(cls):
        return {'targetDesignator/spottedMarkedTime': 0.0,
         'targetDesignator/cooldownTime': 0.0,
         'targetDesignator/deployTime': 0.0,
         'targetDesignator/damageIncome': 0.0}

    def _applyMechanicsAttrs(self, attr, value):
        if attr == 'targetDesignator/spottedMarkedTime':
            self.spottedMarkedTime = max(0, self.spottedMarkedTime + value)
        elif attr == 'targetDesignator/cooldownTime':
            self.cooldownTime = max(0, self.cooldownTime + value)
        elif attr == 'targetDesignator/deployTime':
            self.deployTime = max(0.0, self.deployTime + value)
        elif attr == 'targetDesignator/damageIncome':
            self.damageIncomeFactor = max(1.0, self.damageIncomeFactor + value)


class StanceDanceParams(MechanicsParams):
    __slots__ = ('timeSwitchStance', 'maxEnergy', 'gainFightEnergyPoints', 'gainTurboEnergyPoints', 'gainEnergyTime', 'gainTurboEnergyBonusPoints', 'gainTurboEnergySpdLimitKmh', 'passiveFightEnergyBonusPerHit', 'passiveTurboFwdSpdBonusKmh', 'passiveTurboBkwdSpdBonusKmh', 'passiveTurboEnginePowerBonus', 'passiveTurboAccuracyDebuff', 'passiveTurboAimSpeedDebuff', 'passiveTurboStabilizeDebuff', 'passiveTurboAfterShotDispersionDebuff', 'activeFightCost', 'activeFightDuration', 'activeFightAccuracyBonus', 'activeFightAimSpeedBonus', 'activeFightStabilizeBonus', 'activeFightAfterShotDispersionBonus', 'activeFightReloadSpdBonus', 'activeTurboCost', 'activeTurboDuration', 'activeTurboFwdSpdBonusKmh', 'activeTurboBkwdSpdBonusKmh', 'activeTurboEnginePowerBonus', 'activeTurboRotationSpeedDebuff', 'activeTurboRammingDmgBonus', 'impulse')
    MECHANICS_NAME = 'stanceDance'

    def __init__(self, timeSwitchStance, maxEnergy, gainFightEnergyPoints, gainTurboEnergyPoints, gainEnergyTime, gainTurboEnergyBonusPoints, gainTurboEnergySpdLimitKmh, passiveFightEnergyBonusPerHit, passiveTurboFwdSpdBonusKmh, passiveTurboBkwdSpdBonusKmh, passiveTurboEnginePowerBonus, passiveTurboAccuracyDebuff, passiveTurboAimSpeedDebuff, passiveTurboStabilizeDebuff, passiveTurboAfterShotDispersionDebuff, activeFightCost, activeFightDuration, activeFightAccuracyBonus, activeFightAimSpeedBonus, activeFightStabilizeBonus, activeFightAfterShotDispersionBonus, activeFightReloadSpdBonus, activeTurboCost, activeTurboDuration, activeTurboFwdSpdBonusKmh, activeTurboBkwdSpdBonusKmh, activeTurboEnginePowerBonus, activeTurboRotationSpeedDebuff, activeTurboRammingDmgBonus, impulse):
        super(StanceDanceParams, self).__init__()
        self.timeSwitchStance = timeSwitchStance
        self.maxEnergy = maxEnergy
        self.gainFightEnergyPoints = gainFightEnergyPoints
        self.gainTurboEnergyPoints = gainTurboEnergyPoints
        self.gainEnergyTime = gainEnergyTime
        self.gainTurboEnergyBonusPoints = gainTurboEnergyBonusPoints
        self.gainTurboEnergySpdLimitKmh = gainTurboEnergySpdLimitKmh
        self.passiveFightEnergyBonusPerHit = passiveFightEnergyBonusPerHit
        self.passiveTurboFwdSpdBonusKmh = passiveTurboFwdSpdBonusKmh
        self.passiveTurboBkwdSpdBonusKmh = passiveTurboBkwdSpdBonusKmh
        self.passiveTurboEnginePowerBonus = passiveTurboEnginePowerBonus
        self.passiveTurboAccuracyDebuff = passiveTurboAccuracyDebuff
        self.passiveTurboAimSpeedDebuff = passiveTurboAimSpeedDebuff
        self.passiveTurboStabilizeDebuff = passiveTurboStabilizeDebuff
        self.passiveTurboAfterShotDispersionDebuff = passiveTurboAfterShotDispersionDebuff
        self.activeFightCost = activeFightCost
        self.activeFightDuration = activeFightDuration
        self.activeFightAccuracyBonus = activeFightAccuracyBonus
        self.activeFightAimSpeedBonus = activeFightAimSpeedBonus
        self.activeFightStabilizeBonus = activeFightStabilizeBonus
        self.activeFightAfterShotDispersionBonus = activeFightAfterShotDispersionBonus
        self.activeFightReloadSpdBonus = activeFightReloadSpdBonus
        self.activeTurboCost = activeTurboCost
        self.activeTurboDuration = activeTurboDuration
        self.activeTurboFwdSpdBonusKmh = activeTurboFwdSpdBonusKmh
        self.activeTurboBkwdSpdBonusKmh = activeTurboBkwdSpdBonusKmh
        self.activeTurboEnginePowerBonus = activeTurboEnginePowerBonus
        self.activeTurboRotationSpeedDebuff = activeTurboRotationSpeedDebuff
        self.activeTurboRammingDmgBonus = activeTurboRammingDmgBonus
        self.impulse = impulse
        self.modifiers = {}
        self._saveOrigin()

    @classmethod
    def _readMechanicsParams(cls, mechCtx, mechSection, readModifiers):
        timeSwitchStance = _xml.readNonNegativeFloat(mechCtx, mechSection, 'timeSwitchStance')
        maxEnergy = _xml.readNonNegativeFloat(mechCtx, mechSection, 'maxEnergy')
        gainFightEnergyPoints = _xml.readNonNegativeFloat(mechCtx, mechSection, 'gainFightEnergyPoints')
        gainTurboEnergyPoints = _xml.readNonNegativeFloat(mechCtx, mechSection, 'gainTurboEnergyPoints')
        gainEnergyTime = _xml.readNonNegativeFloat(mechCtx, mechSection, 'gainEnergyTime')
        gainTurboEnergyBonusPoints = _xml.readNonNegativeFloat(mechCtx, mechSection, 'gainTurboEnergyBonusPoints')
        gainTurboEnergySpdLimitKmh = _xml.readNonNegativeFloat(mechCtx, mechSection, 'gainTurboEnergySpdLimitKmh')
        passiveFightEnergyBonusPerHit = _xml.readNonNegativeFloat(mechCtx, mechSection, 'passiveFightEnergyBonusPerHit')
        passiveTurboFwdSpdBonusKmh = _xml.readNonNegativeFloat(mechCtx, mechSection, 'passiveTurboFwdSpdBonusKmh')
        passiveTurboBkwdSpdBonusKmh = _xml.readNonNegativeFloat(mechCtx, mechSection, 'passiveTurboBkwdSpdBonusKmh')
        passiveTurboEnginePowerBonus = _xml.readNonNegativeFloat(mechCtx, mechSection, 'passiveTurboEnginePowerBonus')
        passiveTurboAccuracyDebuff = _xml.readNonNegativeFloat(mechCtx, mechSection, 'passiveTurboAccuracyDebuff')
        passiveTurboAimSpeedDebuff = _xml.readNonNegativeFloat(mechCtx, mechSection, 'passiveTurboAimSpeedDebuff')
        passiveTurboStabilizeDebuff = _xml.readNonNegativeFloat(mechCtx, mechSection, 'passiveTurboStabilizeDebuff')
        passiveTurboAfterShotDispersionDebuff = _xml.readNonNegativeFloat(mechCtx, mechSection, 'passiveTurboAfterShotDispersionDebuff')
        activeFightCost = _xml.readNonNegativeFloat(mechCtx, mechSection, 'activeFightCost')
        activeFightDuration = _xml.readNonNegativeFloat(mechCtx, mechSection, 'activeFightDuration')
        activeFightAccuracyBonus = _xml.readNonNegativeFloat(mechCtx, mechSection, 'activeFightAccuracyBonus')
        activeFightAimSpeedBonus = _xml.readNonNegativeFloat(mechCtx, mechSection, 'activeFightAimSpeedBonus')
        activeFightStabilizeBonus = _xml.readNonNegativeFloat(mechCtx, mechSection, 'activeFightStabilizeBonus')
        activeFightAfterShotDispersionBonus = _xml.readNonNegativeFloat(mechCtx, mechSection, 'activeFightAfterShotDispersionBonus')
        activeFightReloadSpdBonus = _xml.readNonNegativeFloat(mechCtx, mechSection, 'activeFightReloadSpdBonus')
        activeTurboCost = _xml.readNonNegativeFloat(mechCtx, mechSection, 'activeTurboCost')
        activeTurboDuration = _xml.readNonNegativeFloat(mechCtx, mechSection, 'activeTurboDuration')
        activeTurboFwdSpdBonusKmh = _xml.readNonNegativeFloat(mechCtx, mechSection, 'activeTurboFwdSpdBonusKmh')
        activeTurboBkwdSpdBonusKmh = _xml.readNonNegativeFloat(mechCtx, mechSection, 'activeTurboBkwdSpdBonusKmh')
        activeTurboEnginePowerBonus = _xml.readNonNegativeFloat(mechCtx, mechSection, 'activeTurboEnginePowerBonus')
        activeTurboRotationSpeedDebuff = _xml.readNonNegativeFloat(mechCtx, mechSection, 'activeTurboRotationSpeedDebuff')
        activeTurboRammingDmgBonus = _xml.readNonNegativeFloat(mechCtx, mechSection, 'activeTurboRammingDmgBonus')
        impulse = readImpulseData(mechCtx, mechSection)
        return cls(timeSwitchStance=timeSwitchStance, maxEnergy=maxEnergy, gainFightEnergyPoints=gainFightEnergyPoints, gainTurboEnergyPoints=gainTurboEnergyPoints, gainEnergyTime=gainEnergyTime, gainTurboEnergyBonusPoints=gainTurboEnergyBonusPoints, gainTurboEnergySpdLimitKmh=gainTurboEnergySpdLimitKmh, passiveFightEnergyBonusPerHit=passiveFightEnergyBonusPerHit, passiveTurboFwdSpdBonusKmh=passiveTurboFwdSpdBonusKmh, passiveTurboBkwdSpdBonusKmh=passiveTurboBkwdSpdBonusKmh, passiveTurboEnginePowerBonus=passiveTurboEnginePowerBonus, passiveTurboAccuracyDebuff=passiveTurboAccuracyDebuff, passiveTurboAimSpeedDebuff=passiveTurboAimSpeedDebuff, passiveTurboStabilizeDebuff=passiveTurboStabilizeDebuff, passiveTurboAfterShotDispersionDebuff=passiveTurboAfterShotDispersionDebuff, activeFightCost=activeFightCost, activeFightDuration=activeFightDuration, activeFightAccuracyBonus=activeFightAccuracyBonus, activeFightAimSpeedBonus=activeFightAimSpeedBonus, activeFightStabilizeBonus=activeFightStabilizeBonus, activeFightAfterShotDispersionBonus=activeFightAfterShotDispersionBonus, activeFightReloadSpdBonus=activeFightReloadSpdBonus, activeTurboCost=activeTurboCost, activeTurboDuration=activeTurboDuration, activeTurboFwdSpdBonusKmh=activeTurboFwdSpdBonusKmh, activeTurboBkwdSpdBonusKmh=activeTurboBkwdSpdBonusKmh, activeTurboEnginePowerBonus=activeTurboEnginePowerBonus, activeTurboRotationSpeedDebuff=activeTurboRotationSpeedDebuff, activeTurboRammingDmgBonus=activeTurboRammingDmgBonus, impulse=impulse)

    @classmethod
    def getDefaultMechanicsMiscAttributes(cls):
        return {'stanceDance/gainFightEnergyPoints': 0.0,
         'stanceDance/gainFightEnergyPointsFactor': 1.0,
         'stanceDance/gainTurboEnergyPoints': 0.0,
         'stanceDance/gainTurboEnergyPointsFactor': 1.0,
         'stanceDance/activeFightDuration': 0.0,
         'stanceDance/activeTurboDuration': 0.0,
         'stanceDance/timeSwitchStance': 0.0}

    def _applyMechanicsAttrs(self, attr, value):
        if attr == 'stanceDance/gainFightEnergyPoints':
            self.gainFightEnergyPoints += value
        elif attr == 'stanceDance/gainFightEnergyPointsFactor':
            self.gainFightEnergyPoints *= value
        elif attr == 'stanceDance/gainTurboEnergyPoints':
            self.gainTurboEnergyPoints += value
        elif attr == 'stanceDance/gainTurboEnergyPointsFactor':
            self.gainTurboEnergyPoints *= value
        elif attr == 'stanceDance/activeFightDuration':
            self.activeFightDuration += value
        elif attr == 'stanceDance/activeTurboDuration':
            self.activeTurboDuration += value
        elif attr == 'stanceDance/timeSwitchStance':
            self.timeSwitchStance += value


class DebuffsParams(MechanicsParams):
    __slots__ = MechanicsParams.__slots__ + ('debuffs',)
    MECHANICS_NAME = 'reactiveDebuffs'

    def __init__(self, debuffs):
        super(DebuffsParams, self).__init__()
        self.debuffs = debuffs
        self._saveOrigin()

    @classmethod
    def _readMechanicsParams(cls, mechCtx, mechSection, readModifiers):
        debuffs = {}
        for debuff in mechSection.keys():
            debuffIdx = DEBUFFS_TYPES.getIdx(debuff)
            debuffs[debuffIdx] = readModifiers(mechCtx, mechSection[debuff])

        return cls(debuffs)


TemperatureGunThermalState = namedtuple('TemperatureGunThermalState', ['temperature', 'modifiers'])

class TemperatureGunThermalStates(object):
    __slots__ = ('states', 'thermalStateHysteresis')
    _MAX_THERMAL_STATES = 10

    def __init__(self, states, thermalStateHysteresis):
        self.states = states
        self.thermalStateHysteresis = thermalStateHysteresis

    def __eq__(self, other):
        return self.states == other.states and self.thermalStateHysteresis == other.thermalStateHysteresis if isinstance(other, TemperatureGunThermalStates) else False

    @classmethod
    def readThermalStates(cls, ctx, section, readModifiers, mechanicName):
        thermalStateHysteresis = _xml.readPositiveFloat(ctx, section, 'thermalStateHysteresis')
        states = []
        if not section.has_key('thermalStates'):
            _xml.raiseWrongXml(ctx, '', '[{}] Section <thermalStates> is missing!'.format(mechanicName))
        for tag, subsection in section['thermalStates'].items():
            if tag == 'state':
                maxTemperature = _xml.readPositiveFloat(ctx, subsection, 'maxTemperature')
                modifiers = readModifiers(ctx, _xml.getSubsection(ctx, subsection, 'modifiers'))
                state = TemperatureGunThermalState(temperature=maxTemperature, modifiers=modifiers)
                states.append(state)

        if not states:
            _xml.raiseWrongXml(ctx, '', '[{}] Section thermalStates should not be empty!'.format(mechanicName))
        if len(states) > cls._MAX_THERMAL_STATES:
            _xml.raiseWrongXml(ctx, '', '[{}] Section thermalStates should not have number of states > {}!'.format(mechanicName, cls._MAX_THERMAL_STATES))
        states.sort(key=lambda thermalState: thermalState.temperature)
        temperatureRanges = [0] + [ state.temperature for state in states ]
        minTempDiff = min((temperatureRanges[i + 1] - temperatureRanges[i] for i in xrange(len(temperatureRanges) - 1)))
        if minTempDiff < thermalStateHysteresis:
            _xml.raiseWrongXml(ctx, '', '[{}] <thermalStateHysteresis> must be within all temperature states!'.format(mechanicName))
        return cls(states=states, thermalStateHysteresis=thermalStateHysteresis)


class TemperatureGunParams(GunMechanicsParams):
    __slots__ = ('thermalStates', 'heatingPerShot', 'coolingDelay', 'coolingPerSec')
    MECHANICS_NAME = 'temperatureGun'

    def __init__(self, thermalStates, heatingPerShot, coolingDelay, coolingPerSec):
        super(TemperatureGunParams, self).__init__()
        self.thermalStates = thermalStates
        self.heatingPerShot = heatingPerShot
        self.coolingDelay = coolingDelay
        self.coolingPerSec = coolingPerSec
        self._saveOrigin()

    @classmethod
    def getDefaultMechanicsMiscAttributes(cls):
        return {'temperatureGun/heatingPerShot': 0.0,
         'temperatureGun/coolingDelay': 0.0,
         'temperatureGun/coolingPerSec': 1.0}

    @property
    def maxTemperature(self):
        return self.thermalStates.states[-1].temperature

    @classmethod
    def _readMechanicsParams(cls, ctx, section, readModifiers):
        heatingPerShot = _xml.readPositiveFloat(ctx, section, 'heatingPerShot')
        coolingDelay = _xml.readPositiveFloat(ctx, section, 'coolingDelay')
        coolingPerSec = _xml.readPositiveFloat(ctx, section, 'coolingPerSec')
        thermalStates = TemperatureGunThermalStates.readThermalStates(ctx, section, readModifiers, cls.MECHANICS_NAME)
        return cls(thermalStates=thermalStates, heatingPerShot=heatingPerShot, coolingDelay=coolingDelay, coolingPerSec=coolingPerSec)

    def _applyMechanicsAttrs(self, attr, value):
        if attr == 'temperatureGun/heatingPerShot':
            self.heatingPerShot += value
        elif attr == 'temperatureGun/coolingDelay':
            self.coolingDelay += value
        elif attr == 'temperatureGun/coolingPerSec':
            self.coolingPerSec *= value


class OverheatGunParams(GunMechanicsParams):
    __slots__ = ('coolingPerSecFactor', 'tempOverheatOnThreshold', 'tempOverheatOffThreshold', 'tempOverheatWarnThreshold')
    MECHANICS_NAME = 'overheatGun'

    def __init__(self, coolingPerSecFactor, tempOverheatOnThreshold, tempOverheatOffThreshold, tempOverheatWarnThreshold):
        super(OverheatGunParams, self).__init__()
        self.coolingPerSecFactor = coolingPerSecFactor
        self.tempOverheatOnThreshold = tempOverheatOnThreshold
        self.tempOverheatOffThreshold = tempOverheatOffThreshold
        self.tempOverheatWarnThreshold = tempOverheatWarnThreshold
        self._saveOrigin()

    def isActiveMechanics(self, vehicleDescriptor):
        mechanicsParams = vehicleDescriptor.mechanicsParams
        return TemperatureGunParams.MECHANICS_NAME in mechanicsParams and mechanicsParams[TemperatureGunParams.MECHANICS_NAME].isActiveMechanics(vehicleDescriptor)

    @classmethod
    def getDefaultMechanicsMiscAttributes(cls):
        return {'overheatGun/coolingPerSecFactor': 1.0,
         'overheatGun/tempOverheatOnThreshold': 1.0,
         'overheatGun/tempOverheatOffThreshold': 1.0,
         'overheatGun/tempOverheatWarnThreshold': 1.0}

    @classmethod
    def _readMechanicsParams(cls, ctx, section, readModifiers):
        coolingPerSecFactor = _xml.readPositiveFloat(ctx, section, 'coolingPerSecFactor')
        tempOverheatOnThreshold = _xml.readPositiveFloat(ctx, section, 'tempOverheatOnThreshold')
        tempOverheatOffThreshold = _xml.readNonNegativeFloat(ctx, section, 'tempOverheatOffThreshold')
        tempOverheatWarnThreshold = _xml.readPositiveFloat(ctx, section, 'tempOverheatWarnThreshold', defaultValue=tempOverheatOnThreshold)
        if tempOverheatOffThreshold > tempOverheatOnThreshold:
            _xml.raiseWrongXml(ctx, '', '[OverheatGunParams] tempOverheatOffThreshold={} should not be > tempOverheatOnThreshold={}!'.format(tempOverheatOffThreshold, tempOverheatOnThreshold))
        return cls(coolingPerSecFactor=coolingPerSecFactor, tempOverheatOnThreshold=tempOverheatOnThreshold, tempOverheatOffThreshold=tempOverheatOffThreshold, tempOverheatWarnThreshold=tempOverheatWarnThreshold)

    def _applyMechanicsAttrs(self, attr, value):
        if attr == 'overheatGun/coolingPerSecFactor':
            self.coolingPerSecFactor *= value
        elif attr == 'overheatGun/tempOverheatOnThreshold':
            self.tempOverheatOnThreshold *= value
        elif attr == 'overheatGun/tempOverheatOffThreshold':
            self.tempOverheatOffThreshold *= value
        elif attr == 'overheatGun/tempOverheatWarnThreshold':
            self.tempOverheatWarnThreshold *= value


class HeatingZonesGunParams(GunMechanicsParams):
    __slots__ = ('zones',)
    MECHANICS_NAME = 'heatingZonesGun'
    ZONE_STATE = HEATING_ZONES_GUN_STATE

    def __init__(self, zones):
        super(HeatingZonesGunParams, self).__init__()
        self.zones = zones
        self._saveOrigin()

    def isActiveMechanics(self, vehicleDescriptor):
        mechanicsParams = vehicleDescriptor.mechanicsParams
        return TemperatureGunParams.MECHANICS_NAME in mechanicsParams and mechanicsParams[TemperatureGunParams.MECHANICS_NAME].isActiveMechanics(vehicleDescriptor)

    @classmethod
    def _readMechanicsParams(cls, ctx, section, readModifiers):
        zonesValues = map(float, _xml.readNonEmptyString(ctx, section, 'zones').split())
        if any((zoneValue < 0.0 for zoneValue in zonesValues)):
            _xml.raiseWrongXml(ctx, '', "[{}] Invalid zones values: all zones values should be non negative '{}'".format(cls.__name__, zonesValues))
        zonesCount = len(zonesValues)
        statesCount = len(cls.ZONE_STATE.__slots__)
        if zonesCount != statesCount:
            _xml.raiseWrongXml(ctx, '', '[{}] Invalid zones count: expected: {}, got: {}'.format(cls.__name__, statesCount, zonesCount))
        if any((zonesValues[idx] > zonesValues[idx + 1] for idx in xrange(zonesCount - 1))):
            _xml.raiseWrongXml(ctx, '', '[{}] Invalid zones: zone value should be not less than previous one'.format(cls.__name__, zonesValues))
        return cls([ (getattr(cls.ZONE_STATE, stateName), zoneValue) for stateName, zoneValue in zip(sorted(cls.ZONE_STATE.__slots__, key=cls.ZONE_STATE.__dict__.get), zonesValues) ])


class StagedJetBoostersParams(MechanicsParams):
    __slots__ = ('deployTime', 'reloadTime', 'reuseCount', 'duration', 'impulse', 'impulseSpeedLimits', 'modifiers', 'customRotationPoints')
    MECHANICS_NAME = 'stagedJetBoosters'

    def __init__(self, deployTime, reloadTime, reuseCount, duration, impulse, impulseSpeedLimits, modifiers, customRotationPoints):
        super(StagedJetBoostersParams, self).__init__(modifiers)
        self.deployTime = deployTime
        self.reloadTime = reloadTime
        self.reuseCount = reuseCount
        self.duration = duration
        self.impulse = impulse
        self.impulseSpeedLimits = impulseSpeedLimits
        self.modifiers = modifiers
        self.customRotationPoints = customRotationPoints
        self._saveOrigin()

    @classmethod
    def _readMechanicsParams(cls, ctx, section, readModifiers):
        modifiers = readModifiers(ctx, _xml.getSubsection(ctx, section, 'modifiers'))
        impulse = None
        if section.has_key('impulse'):
            impulse = readImpulseData(ctx, section)
        speedLimits = None
        if section.has_key('impulseSpeedLimits'):
            speedLimits = _xml.readVector2(ctx, section, 'impulseSpeedLimits')
            speedLimits *= KMH_TO_MS
        return cls(deployTime=_xml.readNonNegativeFloat(ctx, section, 'deployTime'), reloadTime=_xml.readNonNegativeFloat(ctx, section, 'reloadTime'), reuseCount=_xml.readInt(ctx, section, 'reuseCount', minVal=-1), duration=_xml.readNonNegativeFloat(ctx, section, 'duration'), impulse=impulse, impulseSpeedLimits=speedLimits, modifiers=modifiers, customRotationPoints=cls._readCustomRotationPoints(ctx, section))

    @classmethod
    def _readCustomRotationPoints(cls, ctx, section):
        if not section.has_key('customRotationPoints'):
            return None
        else:

            def readPoints(ctx, section, subsectionName):
                subCtx, subSection = _xml.getSubSectionWithContext(ctx, section, subsectionName)
                return {'speed': _xml.readFloat(subCtx, subSection, 'speed') * KMH_TO_MS,
                 'leftPoint': _xml.readVector3(subCtx, subSection, 'leftPoint'),
                 'rightPoint': _xml.readVector3(subCtx, subSection, 'rightPoint')}

            pointsCtx, pointsSection = _xml.getSubSectionWithContext(ctx, section, 'customRotationPoints')
            return {'min': readPoints(pointsCtx, pointsSection, 'minSpeedPoints'),
             'max': readPoints(pointsCtx, pointsSection, 'maxSpeedPoints'),
             'changeRailDirection': _xml.readBool(pointsCtx, pointsSection, 'changeRailDirection')}

    @classmethod
    def getDefaultMechanicsMiscAttributes(cls):
        return {'stagedJetBoosters/deployTime': 0.0,
         'stagedJetBoosters/reloadTime': 0.0,
         'stagedJetBoosters/reuseCount': 0.0,
         'stagedJetBoosters/duration': 0.0}

    def _applyMechanicsAttrs(self, attr, value):
        if attr == 'stagedJetBoosters/deployTime':
            self.deployTime += value
        elif attr == 'stagedJetBoosters/reloadTime':
            self.reloadTime += value
        elif attr == 'stagedJetBoosters/reuseCount':
            self.reuseCount += value
        elif attr == 'stagedJetBoosters/duration':
            self.duration += value


def addMechanicsParamsAttrs(attrsSet):
    for paramsCls in MechanicsParams.getSubClasses():
        attrsSet.update(paramsCls.getDefaultMechanicsMiscAttributes())


addMechanicsParamsAttrs(ALLOWED_STATIC_ATTRS)
MECHANIC_NAME_TO_IDX = {mechanicParams.MECHANICS_NAME:index for index, mechanicParams in enumerate(MechanicsParams.getSubClasses())}
ObjectSlot = reflectedNamedTuple('ObjectSlot', ('name', 'type', 'position', 'rotation'))
