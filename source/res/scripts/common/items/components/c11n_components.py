# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/c11n_components.py
import items
import items.vehicles as iv
from items.components import shared_components
from soft_exception import SoftException
from items.components.c11n_constants import ApplyArea, SeasonType, Options, ItemTags, CustomizationType, MAX_CAMOUFLAGE_PATTERN_SIZE, DecalType, PROJECTION_DECALS_SCALE_ID_VALUES, MAX_USERS_PROJECTION_DECALS, CustomizationTypeNames, DecalTypeNames, ProjectionDecalFormTags, CUSTOMIZATION_SLOTS_VEHICLE_PARTS, PERSONAL_NUMBER_DIGITS_COUNT
from typing import List, Dict, Type, Tuple, Optional, Union, TypeVar, FrozenSet
from string import lower
Item = TypeVar('TypeVar')

class BaseCustomizationItem(object):
    __slots__ = ('id', 'tags', 'filter', 'parentGroup', 'season', 'historical', 'i18n', 'priceGroup', 'requiredToken', 'priceGroupTags', 'maxNumber')
    allSlots = __slots__
    itemType = 0

    def __init__(self, parentGroup=None):
        self.id = 0
        self.tags = frozenset()
        self.filter = None
        self.season = SeasonType.ALL
        self.historical = False
        self.i18n = None
        self.priceGroup = ''
        self.priceGroupTags = frozenset()
        self.requiredToken = ''
        self.maxNumber = 0
        if parentGroup and parentGroup.itemPrototype:
            for field in self.allSlots:
                setattr(self, field, getattr(parentGroup.itemPrototype, field))

        self.parentGroup = parentGroup
        return

    def matchVehicleType(self, vehTypeDescr):
        return not self.filter or self.filter.matchVehicleType(vehTypeDescr)

    def isVehicleBound(self):
        return ItemTags.VEHICLE_BOUND in self.tags

    def isUnlocked(self, tokens):
        return not self.requiredToken or tokens and self.requiredToken in tokens

    def isRare(self):
        return ItemTags.RARE in self.tags

    def isHiddenInUI(self):
        return ItemTags.HIDDEN_IN_UI in self.tags

    @property
    def isUnique(self):
        return self.maxNumber > 0

    @classmethod
    def makeIntDescr(cls, itemId):
        return items.makeIntCompactDescrByID('customizationItem', cls.itemType, itemId)

    @property
    def compactDescr(self):
        return self.__class__.makeIntDescr(self.id)

    @property
    def userString(self):
        return self.i18n.userString if self.i18n else ''

    @property
    def userKey(self):
        return self.i18n.userKey if self.i18n else ''

    @property
    def description(self):
        return self.i18n.description if self.i18n else ''

    @property
    def shortDescriptionSpecial(self):
        return self.i18n.shortDescriptionSpecial if self.i18n else ''

    @property
    def longDescriptionSpecial(self):
        return self.i18n.longDescriptionSpecial if self.i18n else ''


class PaintItem(BaseCustomizationItem):
    itemType = CustomizationType.PAINT
    __slots__ = ('color', 'usageCosts', 'gloss', 'metallic', 'texture')
    allSlots = BaseCustomizationItem.__slots__ + __slots__

    def __init__(self, parentGroup=None):
        self.color = 0
        self.usageCosts = {area:1 for area in ApplyArea.RANGE}
        self.gloss = 0.0
        self.metallic = 0.0
        self.texture = ''
        super(PaintItem, self).__init__(parentGroup)

    def getAmount(self, parts):
        result = 0
        for i in ApplyArea.RANGE:
            if parts & i:
                if i not in self.usageCosts:
                    return None
                result += self.usageCosts[i]

        return result


class DecalItem(BaseCustomizationItem):
    itemType = CustomizationType.DECAL
    __slots__ = ('type', 'canBeMirrored', 'texture')
    allSlots = BaseCustomizationItem.__slots__ + __slots__

    def __init__(self, parentGroup=None):
        self.type = 0
        self.canBeMirrored = False
        self.texture = ''
        super(DecalItem, self).__init__(parentGroup)


class ProjectionDecalItem(BaseCustomizationItem):
    itemType = CustomizationType.PROJECTION_DECAL
    __slots__ = ('canBeMirrored', 'texture')
    allSlots = BaseCustomizationItem.__slots__ + __slots__

    def __init__(self, parentGroup=None):
        self.canBeMirrored = False
        self.texture = ''
        super(ProjectionDecalItem, self).__init__(parentGroup)


class CamouflageItem(BaseCustomizationItem):
    itemType = CustomizationType.CAMOUFLAGE
    __slots__ = ('palettes', 'compatibleParts', 'componentsCovering', 'invisibilityFactor', 'texture', 'tiling', 'scales', 'rotation')
    allSlots = BaseCustomizationItem.__slots__ + __slots__

    def __init__(self, parentGroup=None):
        self.compatibleParts = ApplyArea.CAMOUFLAGE_REGIONS_VALUE
        self.componentsCovering = 0
        self.palettes = []
        self.invisibilityFactor = 1.0
        self.texture = ''
        self.rotation = {'hull': 0.0,
         'turret': 0.0,
         'gun': 0.0}
        self.tiling = ()
        self.scales = (1.2, 1, 0.7)
        super(CamouflageItem, self).__init__(parentGroup)


class PersonalNumberItem(BaseCustomizationItem):
    itemType = CustomizationType.PERSONAL_NUMBER
    __prohibitedNumbers = ()
    __slots__ = ('compatibleParts', 'texture', 'previewTexture', 'fontInfo', 'isMirrored')
    allSlots = BaseCustomizationItem.__slots__ + __slots__

    def __init__(self, parentGroup=None):
        self.compatibleParts = ApplyArea.INSCRIPTION_REGIONS
        self.texture = ''
        self.previewTexture = ''
        self.fontInfo = None
        self.isMirrored = False
        super(PersonalNumberItem, self).__init__(parentGroup)
        return

    @classmethod
    def setProhibitedNumbers(cls, prohibitedNumbers):
        cls.__prohibitedNumbers = frozenset(prohibitedNumbers)

    @classmethod
    def getProhibitedNumbers(cls):
        return cls.__prohibitedNumbers


class ModificationItem(BaseCustomizationItem):
    itemType = CustomizationType.MODIFICATION
    __slots__ = ('effects', 'texture')
    allSlots = BaseCustomizationItem.__slots__ + __slots__

    def __init__(self, parentGroup=None):
        self.effects = {}
        self.texture = ''
        super(ModificationItem, self).__init__(parentGroup)

    def getEffectValue(self, type, default=0.0):
        return self.effects.get(type, default)


class StyleItem(BaseCustomizationItem):
    itemType = CustomizationType.STYLE
    __slots__ = ('outfits', 'isRent', 'rentCount', 'texture', 'modelsSet', 'textInfo')
    allSlots = BaseCustomizationItem.__slots__ + __slots__

    def __init__(self, parentGroup=None):
        self.outfits = {}
        self.isRent = False
        self.rentCount = 1
        self.texture = ''
        self.modelsSet = ''
        self.textInfo = ''
        super(StyleItem, self).__init__(parentGroup)

    def isVictim(self, color):
        return '{}Victim'.format(color) in self.tags


class InsigniaItem(BaseCustomizationItem):
    itemType = CustomizationType.INSIGNIA
    __slots__ = ('atlas', 'alphabet', 'texture', 'canBeMirrored')
    allSlots = BaseCustomizationItem.__slots__ + __slots__

    def __init__(self, parentGroup=None):
        self.atlas = ''
        self.alphabet = ''
        self.texture = ''
        self.canBeMirrored = False
        super(InsigniaItem, self).__init__(parentGroup)


class ItemGroup(object):
    itemType = CustomizationType.ITEM_GROUP
    __slots__ = ('itemPrototype',)

    def __init__(self, itemClass):
        self.itemPrototype = itemClass()
        super(ItemGroup, self).__init__()

    @property
    def id(self):
        return self.itemPrototype.id

    @classmethod
    def makeIntDescr(cls, itemId):
        return items.makeIntCompactDescrByID('customizationItem', cls.itemType, itemId)

    @property
    def compactDescr(self):
        return self.makeIntDescr(self.itemPrototype.id)


class PriceGroup(object):
    itemType = CustomizationType.ITEM_GROUP
    __slots__ = ('price', 'notInShop', 'id', 'name', 'tags')

    def __init__(self):
        self.price = (0, 0, 0)
        self.name = None
        self.id = 0
        self.notInShop = False
        self.tags = []
        return

    @property
    def compactDescr(self):
        return items.makeIntCompactDescrByID('customizationItem', self.itemType, self.id)


class Font(object):
    itemType = CustomizationType.FONT
    __slots__ = ('id', 'texture', 'alphabet', 'mask')

    def __init__(self):
        self.id = 0
        self.texture = ''
        self.alphabet = ''
        self.mask = ''

    @property
    def compactDescr(self):
        return items.makeIntCompactDescrByID('customizationItem', self.itemType, self.id)


class VehicleFilter(object):

    class FilterNode(object):
        __slots__ = ('nations', 'levels', 'tags', 'vehicles')

        def __init__(self):
            self.nations = None
            self.levels = None
            self.tags = None
            self.vehicles = None
            return

        def __str__(self):
            result = []
            if self.nations:
                result.append(str(self.nations))
            if self.levels:
                result.append(str(self.levels))
            if self.vehicles:
                result.append(str(self.vehicles))
            if self.tags:
                result.append(str(self.tags))
            return '; '.join(result)

        def match(self, vehicleDescr):
            return self.matchVehicleType(vehicleDescr.type)

        def matchVehicleType(self, vehicleType):
            nationID = vehicleType.customizationNationID
            if self.nations and nationID not in self.nations:
                return False
            if self.levels and vehicleType.level not in self.levels:
                return False
            if self.vehicles and vehicleType.compactDescr not in self.vehicles:
                return False
            return False if self.tags and not self.tags < vehicleType.tags else True

    __slots__ = ('include', 'exclude')

    def __init__(self):
        super(VehicleFilter, self).__init__()
        self.include = []
        self.exclude = []

    def __str__(self):
        includes = map(lambda x: str(x), self.include)
        excludes = map(lambda x: str(x), self.exclude)
        result = []
        if includes:
            result.append('includes: ' + str(includes))
        if excludes:
            result.append('excludes: ' + str(excludes))
        return '; '.join(result)

    def match(self, vehicleDescr):
        include = not self.include or any((f.match(vehicleDescr) for f in self.include))
        return include and not (self.exclude and any((f.match(vehicleDescr) for f in self.exclude)))

    def matchVehicleType(self, vehicleType):
        include = not self.include or any((f.matchVehicleType(vehicleType) for f in self.include))
        return include and not (self.exclude and any((f.matchVehicleType(vehicleType) for f in self.exclude)))


class CustomizationCache(object):
    __slots__ = ('paints', 'camouflages', 'decals', 'projection_decals', 'modifications', 'levels', 'itemToPriceGroup', 'priceGroups', 'priceGroupNames', 'insignias', 'styles', 'defaultColors', 'itemTypes', 'priceGroupTags', '__victimStyles', 'personal_numbers', 'fonts')

    def __init__(self):
        self.priceGroupTags = {}
        self.paints = {}
        self.camouflages = {}
        self.decals = {}
        self.projection_decals = {}
        self.personal_numbers = {}
        self.modifications = {}
        self.itemToPriceGroup = {}
        self.priceGroups = {}
        self.priceGroupNames = {}
        self.styles = {}
        self.insignias = {}
        self.defaultColors = {}
        self.fonts = {}
        self.__victimStyles = {}
        self.itemTypes = {CustomizationType.MODIFICATION: self.modifications,
         CustomizationType.STYLE: self.styles,
         CustomizationType.DECAL: self.decals,
         CustomizationType.CAMOUFLAGE: self.camouflages,
         CustomizationType.PERSONAL_NUMBER: self.personal_numbers,
         CustomizationType.PAINT: self.paints,
         CustomizationType.PROJECTION_DECAL: self.projection_decals,
         CustomizationType.INSIGNIA: self.insignias}
        super(CustomizationCache, self).__init__()

    def isVehicleBound(self, itemId):
        if isinstance(itemId, int):
            itemType, inTypeId = splitIntDescr(itemId)
        else:
            itemType, inTypeId = itemId
        if itemType not in self.itemTypes:
            raise SoftException('Incorrect item type', itemId)
        if inTypeId not in self.itemTypes[itemType]:
            raise SoftException('Item not found in cache', itemId)
        return ItemTags.VEHICLE_BOUND in self.itemTypes[itemType][inTypeId].tags

    def splitByVehicleBound(self, itemsDict, vehType):
        itemsToOperate = {k:(v, vehType if self.isVehicleBound(k) or v < 0 else 0) for k, v in itemsDict.iteritems() if v != 0}
        return itemsToOperate

    def getVictimStyles(self, hunting, vehType):
        if not self.__victimStyles:
            self.__victimStyles[''] = {}
            stylesByColor = self.__victimStyles.setdefault
            for style in self.styles.itervalues():
                for tag in style.tags:
                    if tag.endswith('Victim'):
                        stylesByColor(tag[:-6], []).append(style)

        return [ s for s in self.__victimStyles.get(hunting, []) if s.matchVehicleType(vehType) ]

    def validateOutfit(self, vehDescr, outfit, tokens=None, season=SeasonType.ALL):
        try:
            projectionDecalsCount = len(outfit.projection_decals)
            if projectionDecalsCount > MAX_USERS_PROJECTION_DECALS:
                raise SoftException('projection decals quantity {} greater than acceptable'.format(projectionDecalsCount))
            vehType = vehDescr.type
            usedParents = set()
            for itemType in CustomizationType.RANGE:
                typeName = lower(CustomizationTypeNames[itemType])
                componentsAttrName = '{}s'.format(typeName)
                components = getattr(outfit, componentsAttrName, None)
                if not components:
                    continue
                storage = getattr(self, componentsAttrName)
                for component in components:
                    componentId = component.id if not isinstance(component, int) else component
                    item = storage.get(componentId, None)
                    if item is None:
                        raise SoftException('{} {} not found'.format(typeName, componentId))
                    _validateItem(typeName, item, season, tokens, vehType)
                    if itemType in CustomizationType._APPLIED_TO_TYPES:
                        _validateApplyTo(component, item)
                        if itemType == CustomizationType.CAMOUFLAGE:
                            _validateCamouflage(component, item)
                        elif itemType == CustomizationType.PERSONAL_NUMBER:
                            _validatePersonalNumber(component)
                    if itemType == CustomizationType.PROJECTION_DECAL:
                        _validateProjectionDecal(component, item, vehDescr, usedParents)

        except SoftException as ex:
            return (False, ex.message)

        return (True, '')


def _validateItem(typeName, item, season, tokens, vehType):
    if not item.matchVehicleType(vehType):
        raise SoftException('{} {} incompatible vehicle {}'.format(typeName, item.id, vehType))
    if not item.season & season:
        raise SoftException('{} {} incompatible season {}'.format(typeName, item.id, season))
    if not item.isUnlocked(tokens):
        raise SoftException('{} {} locked'.format(typeName, item.id))


def _validateApplyTo(component, item):
    itemType = item.itemType
    typeName = CustomizationTypeNames[itemType]
    if itemType == CustomizationType.DECAL:
        typeName = DecalTypeNames[item.type]
    appliedTo = component.appliedTo
    if not appliedTo:
        raise SoftException('{} {} wrong appliedTo {}'.format(lower(typeName), component.id, appliedTo))
    region = getattr(ApplyArea, '{}_REGIONS_VALUE'.format(typeName))
    if appliedTo & region != appliedTo:
        raise SoftException('{} {} wrong user apply area {}'.format(lower(typeName), component.id, appliedTo))
    if itemType == CustomizationType.PAINT:
        if item.getAmount(appliedTo) is None:
            raise SoftException('{} {} incompatible appliedTo {}'.format(lower(typeName), component.id, appliedTo))
    elif itemType == CustomizationType.CAMOUFLAGE:
        if item.componentsCovering and appliedTo != item.componentsCovering:
            raise SoftException('camouflage {} wrong covering'.format(item.id))
        compatibleParts = item.compatibleParts
        if appliedTo & compatibleParts != appliedTo:
            raise SoftException('camouflage {} wrong appliedTo {}'.format(component.id, appliedTo))
    return


def _validateCamouflage(component, item):
    if component.patternSize < 0 or component.patternSize > MAX_CAMOUFLAGE_PATTERN_SIZE:
        raise SoftException('camouflage has wrong pattern size {}'.format(component.patternSize))
    if component.palette < 0 or component.palette >= len(item.palettes):
        raise SoftException('camouflage {} has wrong palette number {}'.format(component.id, component.palette))


def _validateProjectionDecal(component, item, vehDescr, usedParents):
    options = component.options
    if options & Options.PROJECTION_DECALS_ALLOWED_OPTIONS_VALUE != options:
        raise SoftException('projection decal {} wrong options {}'.format(component.id, options))
    if component.scaleFactorId not in PROJECTION_DECALS_SCALE_ID_VALUES:
        raise SoftException('projection decal {} wrong scaleFactorId {}'.format(component.id, component.scaleFactorId))
    slotId = component.slotId
    slotParams = getVehicleProjectionDecalSlotParams(vehDescr, slotId)
    if slotParams is None:
        raise SoftException('projection decal {} wrong slotId = {}. VehType = {}'.format(component.id, slotId, vehDescr.type))
    parentSlotId = slotParams.parentSlotId if slotParams.parentSlotId is not None else slotId
    if parentSlotId in usedParents:
        raise SoftException('projection decal {} slot {} already used. VehType = {}'.format(component.id, parentSlotId, vehDescr.type))
    usedParents.add(parentSlotId)
    if options & Options.MIRRORED and not item.canBeMirrored:
        raise SoftException('projection decal {} wrong mirrored option'.format(component.id))
    slotFormFactors = set([ tag for tag in slotParams.tags if tag.startswith(ProjectionDecalFormTags.PREFIX) ])
    if slotFormFactors and ProjectionDecalFormTags.ANY not in slotFormFactors:
        formfactor = next((tag for tag in item.tags if tag.startswith(ProjectionDecalFormTags.PREFIX)), '')
        if not formfactor:
            raise SoftException('projection decal {} wrong XML. formfactor is missing'.format(component.id, formfactor))
        if formfactor not in slotFormFactors:
            raise SoftException('projection decal {} wrong formfactor {}'.format(component.id, formfactor))
    return


def _validatePersonalNumber(component):
    number = component.number
    if not number or len(number) != PERSONAL_NUMBER_DIGITS_COUNT:
        raise SoftException('personal number {} has wrong number {}'.format(component.id, number))
    if not isPersonalNumberAllowed(number):
        raise SoftException('number {} of personal number {} is prohibited'.format(number, component.id))


def splitIntDescr(intDescr):
    itemType, customizationType, id = items.parseIntCompactDescr(intDescr)
    if itemType != 12 or customizationType not in CustomizationType.RANGE:
        raise SoftException('intDescr is not correct customization item int descriptor', intDescr)
    return (customizationType, id)


def validateCustomizationEnabled(gameParams):
    return gameParams['misc_settings']['isCustomizationEnabled']


def validateCustomizationTypeEnabled(gameParams, customizationType):
    return CustomizationTypeNames[customizationType] not in gameParams['misc_settings']['disabledCustomizations']


def getVehicleProjectionDecalSlotParams(vehicleDescr, vehicleSlotId, partNames=CUSTOMIZATION_SLOTS_VEHICLE_PARTS):
    slotTypeName = 'projectionDecal'
    for partName in partNames:
        for vehicleSlot in getattr(vehicleDescr, partName).slotsAnchors:
            if vehicleSlot.type != slotTypeName or vehicleSlot.slotId != vehicleSlotId:
                continue
            return vehicleSlot

    return None


def isPersonalNumberAllowed(personalNumber):
    return personalNumber not in PersonalNumberItem.getProhibitedNumbers()
