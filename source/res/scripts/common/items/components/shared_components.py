# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/shared_components.py
from collections import namedtuple
from constants import IS_CLIENT, IS_WEB
from items.components import component_constants
from items.components import path_builder
from soft_exception import SoftException
if IS_CLIENT:
    from helpers import i18n
elif IS_WEB:
    from web_stubs import i18n
else:

    class i18n(object):

        @classmethod
        def makeString(cls, key):
            raise SoftException('Unexpected call "i18n.makeString"')


__all__ = ('MaterialInfo', 'DEFAULT_MATERIAL_INFO', 'EmblemSlot', 'LodSettings', 'NodesAndGroups', 'Camouflage', 'DEFAULT_CAMOUFLAGE', 'SwingingSettings', 'I18nComponent', 'DeviceHealth', 'ModelStatesPaths')
MaterialInfo = namedtuple('MaterialInfo', ('kind', 'armor', 'extra', 'multipleExtra', 'vehicleDamageFactor', 'useArmorHomogenization', 'useHitAngle', 'useAntifragmentationLining', 'mayRicochet', 'collideOnceOnly', 'checkCaliberForRichet', 'checkCaliberForHitAngleNorm', 'damageKind', 'chanceToHitByProjectile', 'chanceToHitByExplosion', 'continueTraceIfNoHit'))
DEFAULT_MATERIAL_INFO = MaterialInfo(0, 0, None, False, 0.0, False, False, False, False, False, False, False, 0, 0.0, 0.0, False)
EmblemSlot = namedtuple('EmblemSlot', ('rayStart', 'rayEnd', 'rayUp', 'size', 'hideIfDamaged', 'type', 'isMirrored', 'isUVProportional', 'emblemId', 'slotId', 'applyToFabric'))
CustomizationSlotDescription = namedtuple('CustomizationSlotDescription', ('type', 'slotId', 'anchorPosition', 'anchorDirection', 'applyTo', 'position', 'rotation', 'scale', 'scaleFactors', 'doubleSided', 'showOn', 'tags', 'parentSlotId', 'clipAngle'))
LodSettings = namedtuple('LodSettings', ('maxLodDistance', 'maxPriority'))
NodesAndGroups = namedtuple('NodesAndGroups', ('nodes', 'groups', 'activePostmortem', 'lodSettings'))
Camouflage = namedtuple('Camouflage', ('tiling', 'exclusionMask'))
DEFAULT_CAMOUFLAGE = Camouflage(None, None)
SwingingSettings = namedtuple('SwingingSettings', ('lodDist', 'sensitivityToImpulse', 'pitchParams', 'rollParams'))

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


class I18nComponent(object):
    __slots__ = ('__userString', '__shortString', '__description', '__converted', '__shortDescriptionSpecial', '__longDescriptionSpecial')

    def __init__(self, userStringKey, descriptionKey, shortStringKey='', shortDescriptionSpecialKey='', longDescriptionSpecialKey=''):
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


class I18nExposedComponent(I18nComponent):
    __slots__ = ('__userKey', '__shortKey', '__descriptionKey')

    def __init__(self, userStringKey, descriptionKey, shortStringKey=''):
        super(I18nExposedComponent, self).__init__(userStringKey, descriptionKey, shortStringKey='')
        self.__userKey = userStringKey
        self.__descriptionKey = descriptionKey
        self.__shortKey = shortStringKey

    @property
    def userKey(self):
        return self.__userKey

    @property
    def descriptionKey(self):
        return self.__descriptionKey

    @property
    def shortKey(self):
        return self.__shortKey


class DeviceHealth(object):
    __slots__ = ('maxHealth', 'repairCost', 'maxRegenHealth', 'healthRegenPerSec', 'healthBurnPerSec', 'chanceToHit', 'hysteresisHealth')

    def __init__(self, maxHealth, repairCost=component_constants.ZERO_FLOAT, maxRegenHealth=component_constants.ZERO_INT):
        super(DeviceHealth, self).__init__()
        self.maxHealth = maxHealth
        self.repairCost = repairCost
        self.maxRegenHealth = maxRegenHealth
        self.healthRegenPerSec = component_constants.ZERO_FLOAT
        self.healthBurnPerSec = component_constants.ZERO_FLOAT
        self.chanceToHit = None
        self.hysteresisHealth = None
        return

    def __repr__(self):
        return 'DeviceHealth(maxHealth={}, repairCost={}, maxRegenHealth={})'.format(self.maxHealth, self.repairCost, self.maxRegenHealth)

    @property
    def maxRepairCost(self):
        return (self.maxHealth - self.maxRegenHealth) * self.repairCost


DEFAULT_DEVICE_HEALTH = DeviceHealth(1)

class ModelStatesPaths(object):
    __slots__ = ('__undamaged', '__destroyed', '__exploded')

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

    def getPathByStateName(self, stateName):
        path = getattr(self, stateName, None)
        if path is None:
            raise SoftException('State {} is not found'.format(stateName))
        return path
