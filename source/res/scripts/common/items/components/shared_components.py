# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/shared_components.py
from collections import namedtuple
from constants import IS_CLIENT, IS_WEB, IS_EDITOR, IS_BOT
from items.components import component_constants, c11n_constants
from items.components import path_builder
from items.components.c11n_constants import ApplyArea
from soft_exception import SoftException
from wrapped_reflection_framework import ReflectionMetaclass, reflectedNamedTuple
if IS_CLIENT:
    from helpers import i18n
elif IS_WEB or IS_BOT:
    from web_stubs import i18n
else:

    class i18n(object):

        @classmethod
        def makeString(cls, key):
            raise SoftException('Unexpected call "i18n.makeString"')


__all__ = ('MaterialInfo', 'DEFAULT_MATERIAL_INFO', 'EmblemSlot', 'LodSettings', 'NodesAndGroups', 'Camouflage', 'DEFAULT_CAMOUFLAGE', 'SwingingSettings', 'I18nComponent', 'DeviceHealth', 'ModelStatesPaths')
MaterialInfo = reflectedNamedTuple('MaterialInfo', ('kind', 'armor', 'extra', 'multipleExtra', 'vehicleDamageFactor', 'useArmorHomogenization', 'useHitAngle', 'useAntifragmentationLining', 'mayRicochet', 'collideOnceOnly', 'checkCaliberForRichet', 'checkCaliberForHitAngleNorm', 'damageKind', 'chanceToHitByProjectile', 'chanceToHitByExplosion', 'continueTraceIfNoHit'))
DEFAULT_MATERIAL_INFO = MaterialInfo(0, 0, None, False, 0.0, False, False, False, False, False, False, False, 0, 0.0, 0.0, False)
EmblemSlot = reflectedNamedTuple('EmblemSlot', ('rayStart', 'rayEnd', 'rayUp', 'size', 'hideIfDamaged', 'type', 'isMirrored', 'isUVProportional', 'emblemId', 'slotId', 'applyToFabric'))

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
    __slots__ = ('type', 'slotId', 'anchorPosition', 'anchorDirection', 'position', 'rotation', 'scale', 'scaleFactors', 'doubleSided', 'canBeMirroredVertically', 'showOn', 'tags', 'clipAngle', 'compatibleModels', 'itemId', 'options')

    def __init__(self, slotType='', slotId=0, anchorPosition=None, anchorDirection=None, position=None, rotation=None, scale=None, scaleFactors=c11n_constants.DEFAULT_DECAL_SCALE_FACTORS, doubleSided=False, canBeMirroredVertically=False, showOn=None, tags=None, clipAngle=c11n_constants.DEFAULT_DECAL_CLIP_ANGLE, compatibleModels=(c11n_constants.SLOT_DEFAULT_ALLOWED_MODEL,), itemId=None, options=c11n_constants.Options.NONE):
        self.type = slotType
        self.slotId = slotId
        self.anchorPosition = anchorPosition
        self.anchorDirection = anchorDirection
        self.position = position
        self.rotation = rotation
        self.scale = scale
        self.scaleFactors = scaleFactors
        self.doubleSided = doubleSided
        self.canBeMirroredVertically = canBeMirroredVertically
        self.showOn = showOn
        self.tags = tags or ()
        self.clipAngle = clipAngle
        self.compatibleModels = compatibleModels
        self.itemId = itemId
        self.options = options


MiscSlot = reflectedNamedTuple('MiscSlot', ('type', 'slotId', 'position', 'rotation', 'attachNode'))
LodSettings = namedtuple('LodSettings', ('maxLodDistance', 'maxPriority'))
NodesAndGroups = reflectedNamedTuple('NodesAndGroups', ('nodes', 'groups', 'activePostmortem', 'lodSettings'))
Camouflage = reflectedNamedTuple('Camouflage', ('tiling', 'exclusionMask', 'density', 'aoTextureSize'))
DEFAULT_CAMOUFLAGE = Camouflage(None, None, None, None)
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
    __slots__ = ('__userKey', '__descriptionKey', '__longDescriptionSpecialKey')

    def __init__(self, userStringKey, descriptionKey, longDescriptionSpecialKey=''):
        super(I18nExposedComponent, self).__init__(userStringKey, descriptionKey, longDescriptionSpecialKey=longDescriptionSpecialKey)
        self.__userKey = userStringKey
        self.__descriptionKey = descriptionKey
        self.__longDescriptionSpecialKey = longDescriptionSpecialKey

    @property
    def userKey(self):
        return self.__userKey

    @property
    def descriptionKey(self):
        return self.__descriptionKey

    @property
    def longDescriptionSpecialKey(self):
        return self.__longDescriptionSpecialKey


class DeviceHealth(object):
    __slots__ = ('maxHealth', 'repairCost', 'maxRegenHealth', 'healthRegenPerSec', 'healthBurnPerSec', 'chanceToHit', 'hysteresisHealth', 'invulnerable')

    def __init__(self, maxHealth, repairCost=component_constants.ZERO_FLOAT, maxRegenHealth=component_constants.ZERO_INT):
        super(DeviceHealth, self).__init__()
        self.maxHealth = maxHealth
        self.repairCost = repairCost
        self.maxRegenHealth = maxRegenHealth
        self.healthRegenPerSec = component_constants.ZERO_FLOAT
        self.healthBurnPerSec = component_constants.ZERO_FLOAT
        self.chanceToHit = None
        self.hysteresisHealth = None
        self.invulnerable = False
        return

    def __repr__(self):
        return 'DeviceHealth(maxHealth={}, repairCost={}, maxRegenHealth={})'.format(self.maxHealth, self.repairCost, self.maxRegenHealth)

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
