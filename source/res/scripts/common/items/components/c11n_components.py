# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/c11n_components.py
import items
import items.vehicles as iv
from items.components import shared_components
from items.components.c11n_constants import ApplyArea, SeasonType, ItemTags, CustomizationType, MAX_CAMOUFLAGE_PATTERN_SIZE, DecalType
from constants import IS_CELLAPP, IS_BASEAPP
if IS_CELLAPP or IS_BASEAPP:
    from typing import List, Dict, Type, Tuple, Optional, Union, TypeVar
    Item = TypeVar('TypeVar')

class BaseCustomizationItem(object):
    """Base class for all customization related xml items"""
    __slots__ = ('id', 'tags', 'filter', 'parentGroup', 'season', 'historical', 'i18n', 'priceGroup', 'requiredToken', 'priceGroupTags')
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

    @classmethod
    def makeIntDescr(cls, itemId):
        return items.makeIntCompactDescrByID('customizationItem', cls.itemType, itemId)

    @property
    def compactDescr(self):
        return self.makeIntDescr(self.id)

    @property
    def userString(self):
        return self.i18n.userString if self.i18n else ''

    @property
    def userKey(self):
        return self.i18n.userKey if self.i18n else ''

    @property
    def description(self):
        return self.i18n.description if self.i18n else ''


class PaintItem(BaseCustomizationItem):
    """Item used for custom colorization of vehicle regions and camouflage elements"""
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
        """Calculate total amount of paint required to color given parts
        
        :param parts: int bitmask from ApplyArea
        :returns: int value to use or None if paint can't be used for some of given parts
        """
        result = 0
        for i in ApplyArea.RANGE:
            if parts & i:
                if i not in self.usageCosts:
                    return None
                result += self.usageCosts[i]

        return result


class DecalItem(BaseCustomizationItem):
    """Item which can be placed in the slot of the vehicle board: inscriptions, emblems, etc."""
    itemType = CustomizationType.DECAL
    __slots__ = ('type', 'isMirrored', 'texture')
    allSlots = BaseCustomizationItem.__slots__ + __slots__

    def __init__(self, parentGroup=None):
        self.type = 0
        self.isMirrored = False
        self.texture = ''
        super(DecalItem, self).__init__(parentGroup)


class CamouflageItem(BaseCustomizationItem):
    """Static information about camouflage"""
    itemType = CustomizationType.CAMOUFLAGE
    __slots__ = ('palettes', 'compatibleParts', 'componentsCovering', 'invisibilityFactor', 'texture', 'tiling', 'scales')
    allSlots = BaseCustomizationItem.__slots__ + __slots__

    def __init__(self, parentGroup=None):
        self.compatibleParts = ApplyArea.CAMOUFLAGE_REGIONS_VALUE
        self.componentsCovering = 0
        self.palettes = []
        self.invisibilityFactor = 1.0
        self.texture = ''
        self.tiling = ()
        self.scales = (1.2, 1, 0.7)
        super(CamouflageItem, self).__init__(parentGroup)


class ModificationItem(BaseCustomizationItem):
    """Combination of effects applied to vehicle as single item: color quality, age, etc."""
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
    __slots__ = ('outfits', 'isRent', 'rentCount', 'texture')
    allSlots = BaseCustomizationItem.__slots__ + __slots__

    def __init__(self, parentGroup=None):
        self.outfits = {}
        self.isRent = False
        self.rentCount = 1
        self.texture = ''
        super(StyleItem, self).__init__(parentGroup)


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


class VehicleFilter(object):
    """
    Filter testing if VehicleDescriptor satisfies given condition.
    
    Condition is based on list of include and exclude predicates.
    Vehicle must pass at least 1 include predicate and no exclude conditions
    """

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
    """
    Class storing all data parsed from customization xml files.
    """
    __slots__ = ('paints', 'camouflages', 'decals', 'modifications', 'levels', 'itemToPriceGroup', 'priceGroups', 'priceGroupNames', 'styles', 'defaultColors', 'itemTypes', 'priceGroupTags')

    def __init__(self):
        self.priceGroupTags = {}
        self.paints = {}
        self.camouflages = {}
        self.decals = {}
        self.modifications = {}
        self.itemToPriceGroup = {}
        self.priceGroups = {}
        self.priceGroupNames = {}
        self.styles = {}
        self.defaultColors = {}
        self.itemTypes = {CustomizationType.MODIFICATION: self.modifications,
         CustomizationType.STYLE: self.styles,
         CustomizationType.DECAL: self.decals,
         CustomizationType.CAMOUFLAGE: self.camouflages,
         CustomizationType.PAINT: self.paints}
        super(CustomizationCache, self).__init__()

    def isVehicleBound(self, itemId):
        """Check if item can be remounted to another vehicle."""
        itemType, inTypeId = splitIntDescr(itemId)
        if itemType not in self.itemTypes:
            raise ValueError('Incorrect item type', itemId)
        if inTypeId not in self.itemTypes[itemType]:
            raise ValueError('Item not found in cache', itemId)
        return ItemTags.VEHICLE_BOUND in self.itemTypes[itemType][inTypeId].tags

    def splitByVehicleBound(self, itemsDict, vehType):
        """Splits of selling items by vehicle bound tag and adds vehType where required """
        itemsToOperate = {k:(v, vehType if self.isVehicleBound(k) or v < 0 else 0) for k, v in itemsDict.iteritems() if v != 0}
        return itemsToOperate

    def validateOutfit(self, vehTypeDescr, outfitDescr, tokens=None, season=SeasonType.ALL):
        """Validate if every item in customization outfit is compatible with vehicle"""

        def validateItem(name, storage, itemId):
            item = storage.get(itemId, None)
            if item is None:
                return (False, '{} {} not found'.format(name, itemId))
            elif not item.matchVehicleType(vehTypeDescr):
                return (False, '{} {} incompatible vehicle'.format(name, itemId))
            elif not item.season & season:
                return (False, '{} {} incompatible season'.format(name, itemId))
            else:
                return (False, '{} {} locked'.format(name, itemId)) if not item.isUnlocked(tokens) else (True, item)

        for p in outfitDescr.paints:
            valid, paint = validateItem('paint', self.paints, p.id)
            if not valid:
                return (valid, paint)
            if paint.getAmount(p.appliedTo) is None:
                return (False, 'paint {} incompatible appliedTo'.format(paint.id))
            if p.appliedTo & ApplyArea.USER_PAINT_ALLOWED_REGIONS_VALUE != p.appliedTo:
                return (False, 'paint {} wrong user apply area'.format(paint.id))

        for d in outfitDescr.decals:
            valid, decal = validateItem('decal', self.decals, d.id)
            if not valid:
                return (valid, decal)
            if decal.type == DecalType.EMBLEM:
                if d.appliedTo & ApplyArea.EMBLEM_REGIONS_VALUE != d.appliedTo:
                    return (False, 'emblem {} wrong appliedTo {}'.format(d.id, d.appliedTo))
            if decal.type == DecalType.INSCRIPTION:
                if d.appliedTo & ApplyArea.INSCRIPTION_REGIONS_VALUE != d.appliedTo:
                    return (False, 'inscription {} wrong appliedTo {}'.format(d.id, d.appliedTo))

        for ce in outfitDescr.camouflages:
            valid, camo = validateItem('camouflage', self.camouflages, ce.id)
            if not valid:
                return (valid, camo)
            at = ce.appliedTo
            if camo.componentsCovering and at != camo.componentsCovering:
                return (False, 'camouflage {} wrong covering'.format(camo.id))
            cp = camo.compatibleParts
            if at & cp != at:
                return (False, 'camouflage {} wrong appliedTo {}'.format(camo.id, at))
            if ce.patternSize < 0 or ce.patternSize > MAX_CAMOUFLAGE_PATTERN_SIZE:
                return (False, 'camouflage has wrong pattern size {}'.format(ce.patternSize))
            if ce.palette < 0 or ce.palette >= len(camo.palettes):
                return (False, 'camouflage {} has wrong palette number {}'.format(ce.id, ce.palette))

        for m in outfitDescr.modifications:
            valid, mod = validateItem('modification', self.modifications, m)
            if not valid:
                return (valid, mod)

        return (True, '')


def splitIntDescr(intDescr):
    """Split int item descriptor to (customizationType, itemId) tuple."""
    itemType, customizationType, id = items.parseIntCompactDescr(intDescr)
    if itemType != 12 or customizationType not in CustomizationType.RANGE:
        raise ValueError('intDescr is not correct customization item int descriptor', intDescr)
    return (customizationType, id)
