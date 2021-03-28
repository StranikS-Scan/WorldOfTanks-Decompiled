# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/c11n_components.py
import itertools
from backports.functools_lru_cache import lru_cache
import Math
import items
import items.vehicles as iv
import nations
from debug_utils import LOG_CURRENT_EXCEPTION
from items import vehicles
from items.components import shared_components
from soft_exception import SoftException
from items.components.c11n_constants import ApplyArea, SeasonType, Options, ItemTags, CustomizationType, MAX_CAMOUFLAGE_PATTERN_SIZE, DecalType, HIDDEN_CAMOUFLAGE_ID, PROJECTION_DECALS_SCALE_ID_VALUES, MAX_USERS_PROJECTION_DECALS, CustomizationTypeNames, DecalTypeNames, CustomizationNamesToTypes, ProjectionDecalFormTags, CUSTOMIZATION_SLOTS_VEHICLE_PARTS, CamouflageTilingType, HIDDEN_FOR_USER_TAG, SLOT_TYPE_NAMES, EMPTY_ITEM_ID, SLOT_DEFAULT_ALLOWED_MODEL, EDITING_STYLE_REASONS
from typing import List, Dict, Type, Tuple, Optional, TypeVar, FrozenSet, Set
from string import lower, upper
from copy import deepcopy
from wrapped_reflection_framework import ReflectionMetaclass
from constants import IS_EDITOR, ARENA_BONUS_TYPE_NAMES
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
if IS_EDITOR:
    from editor_copy import edCopy
Item = TypeVar('TypeVar')

class BaseCustomizationItem(object):
    __metaclass__ = ReflectionMetaclass
    __slots__ = ('id', 'tags', 'filter', 'parentGroup', 'season', 'historical', 'i18n', 'priceGroup', 'requiredToken', 'priceGroupTags', 'maxNumber', 'texture', 'progression')
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
        self.texture = ''
        self.progression = None
        copyBaseValue = (lambda x: x) if not IS_EDITOR else edCopy
        if parentGroup and parentGroup.itemPrototype:
            for field in self.allSlots:
                if hasattr(parentGroup.itemPrototype, field):
                    value = getattr(parentGroup.itemPrototype, field)
                    setattr(self, field, copyBaseValue(value))

        self.parentGroup = parentGroup
        return

    def _copy(self, newItem):
        newItem.id = self.id
        newItem.tags = deepcopy(self.tags)
        newItem.filter = deepcopy(self.filter)
        newItem.season = self.season
        newItem.historical = self.historical
        newItem.i18n = deepcopy(self.i18n)
        newItem.priceGroup = deepcopy(self.priceGroup)
        newItem.priceGroupTags = deepcopy(self.priceGroupTags)
        newItem.requiredToken = deepcopy(self.requiredToken)
        newItem.maxNumber = self.maxNumber
        newItem.texture = deepcopy(self.texture)
        newItem.progression = deepcopy(self.progression)
        newItem.parentGroup = self.parentGroup

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

    def isProgressive(self):
        return self.progression is not None

    @property
    def isUnique(self):
        return self.maxNumber > 0

    @property
    def isStyleOnly(self):
        return ItemTags.STYLE_ONLY in self.tags

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
        description = self.i18n.description
        return description if self.i18n else ''

    @property
    def shortDescriptionSpecial(self):
        shortDescriptionSpecial = self.i18n.shortDescriptionSpecial
        return shortDescriptionSpecial if self.i18n else ''

    @property
    def longDescriptionSpecial(self):
        longDescriptionSpecial = self.i18n.longDescriptionSpecial
        return longDescriptionSpecial if self.i18n else ''


class PaintItem(BaseCustomizationItem):
    __metaclass__ = ReflectionMetaclass
    itemType = CustomizationType.PAINT
    __slots__ = ('color', 'usageCosts', 'gloss', 'metallic')
    allSlots = BaseCustomizationItem.__slots__ + __slots__

    def __init__(self, parentGroup=None):
        self.color = 0
        self.usageCosts = {area:1 for area in ApplyArea.RANGE}
        self.gloss = 0.0
        self.metallic = 0.0
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
    __metaclass__ = ReflectionMetaclass
    itemType = CustomizationType.DECAL
    __slots__ = ('type', 'canBeMirrored')
    allSlots = BaseCustomizationItem.__slots__ + __slots__

    def __init__(self, parentGroup=None):
        self.type = 0
        self.canBeMirrored = False
        super(DecalItem, self).__init__(parentGroup)


class ProjectionDecalItem(BaseCustomizationItem):
    __metaclass__ = ReflectionMetaclass
    itemType = CustomizationType.PROJECTION_DECAL
    __slots__ = ('canBeMirroredHorizontally', 'glossTexture')
    allSlots = BaseCustomizationItem.__slots__ + __slots__

    def __init__(self, parentGroup=None):
        self.canBeMirroredHorizontally = False
        self.glossTexture = ''
        super(ProjectionDecalItem, self).__init__(parentGroup)

    @property
    def canBeMirroredVertically(self):
        return ItemTags.DISABLE_VERTICAL_MIRROR not in self.tags

    @property
    def canBeMirroredOnlyVertically(self):
        return ItemTags.ONLY_VERTICAL_MIRROR in self.tags


class CamouflageItem(BaseCustomizationItem):
    __metaclass__ = ReflectionMetaclass
    itemType = CustomizationType.CAMOUFLAGE
    __slots__ = ('palettes', 'compatibleParts', 'componentsCovering', 'invisibilityFactor', 'tiling', 'tilingSettings', 'scales', 'rotation', 'glossMetallicSettings')
    allSlots = BaseCustomizationItem.__slots__ + __slots__

    def __init__(self, parentGroup=None):
        self.compatibleParts = ApplyArea.CAMOUFLAGE_REGIONS_VALUE
        self.componentsCovering = 0
        self.palettes = []
        self.invisibilityFactor = 1.0
        self.rotation = {'hull': 0.0,
         'turret': 0.0,
         'gun': 0.0}
        self.tiling = {}
        self.tilingSettings = (CamouflageTilingType.LEGACY, None, None)
        self.scales = (1.2, 1, 0.7)
        self.glossMetallicSettings = {'glossMetallicMap': '',
         'gloss': Math.Vector4(0.0),
         'metallic': Math.Vector4(0.0)}
        super(CamouflageItem, self).__init__(parentGroup)
        return

    def __deepcopy__(self, memodict={}):
        newItem = type(self)()
        newItem.compatibleParts = self.compatibleParts
        newItem.componentsCovering = self.componentsCovering
        newItem.palettes = deepcopy(self.palettes)
        newItem.invisibilityFactor = self.invisibilityFactor
        newItem.rotation = deepcopy(self.rotation)
        newItem.tiling = deepcopy(self.tiling)
        newItem.tilingSettings = deepcopy(self.tilingSettings)
        newItem.scales = self.scales
        super(CamouflageItem, self)._copy(newItem)
        return newItem


class PersonalNumberItem(BaseCustomizationItem):
    __metaclass__ = ReflectionMetaclass
    itemType = CustomizationType.PERSONAL_NUMBER
    __prohibitedNumbers = ()
    __slots__ = ('compatibleParts', 'digitsCount', 'previewTexture', 'fontInfo', 'isMirrored')
    allSlots = BaseCustomizationItem.__slots__ + __slots__

    def __init__(self, parentGroup=None):
        self.compatibleParts = ApplyArea.INSCRIPTION_REGIONS
        self.digitsCount = 3
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


class SequenceItem(BaseCustomizationItem):
    itemType = CustomizationType.SEQUENCE
    __slots__ = ('sequenceName',)
    allSlots = BaseCustomizationItem.__slots__ + __slots__

    def __init__(self, parentGroup=None):
        self.sequenceName = None
        super(SequenceItem, self).__init__(parentGroup)
        return


class AttachmentItem(BaseCustomizationItem):
    itemType = CustomizationType.ATTACHMENT
    __slots__ = ('modelName', 'sequenceId', 'attachmentLogic', 'initialVisibility')
    allSlots = BaseCustomizationItem.__slots__ + __slots__

    def __init__(self, parentGroup=None):
        self.modelName = None
        self.sequenceId = None
        self.attachmentLogic = None
        self.initialVisibility = True
        super(AttachmentItem, self).__init__(parentGroup)
        return


class ModificationItem(BaseCustomizationItem):
    __metaclass__ = ReflectionMetaclass
    itemType = CustomizationType.MODIFICATION
    __slots__ = ('effects',)
    allSlots = BaseCustomizationItem.__slots__ + __slots__

    def __init__(self, parentGroup=None):
        self.effects = {}
        super(ModificationItem, self).__init__(parentGroup)

    def getEffectValue(self, type, default=0.0):
        return self.effects.get(type, default)


class StyleItem(BaseCustomizationItem):
    __metaclass__ = ReflectionMetaclass
    itemType = CustomizationType.STYLE
    __slots__ = ('outfits', 'isRent', 'rentCount', 'modelsSet', 'isEditable', 'alternateItems', 'itemsFilters', '_changeableSlotTypes', 'styleProgressions', 'dependencies', 'dependenciesAncestors')
    allSlots = BaseCustomizationItem.__slots__ + __slots__

    def __init__(self, parentGroup=None):
        self.outfits = {}
        self.isRent = False
        self.rentCount = 1
        self.modelsSet = ''
        self.isEditable = False
        self.alternateItems = {}
        self.itemsFilters = {}
        self.dependencies = {}
        self.dependenciesAncestors = {}
        self._changeableSlotTypes = None
        self.styleProgressions = {}
        super(StyleItem, self).__init__(parentGroup)
        return

    def isVictim(self, color):
        return '{}Victim'.format(color) in self.tags

    def isItemInstallable(self, item):
        if not self.isEditable:
            return False
        elif self.historical and not item.historical:
            return False
        elif item.id in self.alternateItems.get(item.itemType, ()):
            return True
        else:
            itemFilter = self.itemsFilters.get(item.itemType)
            return False if itemFilter is None else itemFilter.match(item)

    @property
    def changeableSlotTypes(self):
        if self._changeableSlotTypes is None:
            c11nChecker = lambda i: self.isItemInstallable(i)
            emblemChecker = lambda i: self.isItemInstallable(i) and i.type == DecalType.EMBLEM
            inscriptionChecker = lambda i: self.isItemInstallable(i) and i.type == DecalType.INSCRIPTION
            _C11N_TYPES_CHECK_DATA = ((CustomizationType.MODIFICATION, c11nChecker, None),
             (CustomizationType.CAMOUFLAGE, c11nChecker, None),
             (CustomizationType.PAINT, c11nChecker, None),
             (CustomizationType.PROJECTION_DECAL, c11nChecker, None),
             (CustomizationType.PERSONAL_NUMBER, c11nChecker, None),
             (CustomizationType.DECAL, emblemChecker, DecalType.EMBLEM),
             (CustomizationType.DECAL, inscriptionChecker, DecalType.INSCRIPTION))
            customizationCache = vehicles.g_cache.customization20()
            slotTypes = set()
            for c11nType, checker, decalType in _C11N_TYPES_CHECK_DATA:
                for item in customizationCache.itemTypes[c11nType].itervalues():
                    if item.id == EMPTY_ITEM_ID:
                        continue
                    if checker(item):
                        slotTypes.add(getSlotType(c11nType, decalType))
                        break

            self._changeableSlotTypes = slotTypes
        return self._changeableSlotTypes

    @property
    def clearableSlotTypes(self):
        return set(SLOT_TYPE_NAMES.EDITABLE_STYLE_DELETABLE).intersection(self.changeableSlotTypes)

    @property
    def isProgression(self):
        return ItemTags.STYLE_PROGRESSION in self.tags

    @property
    def hasDependent(self):
        return bool(self.dependencies)


class InsigniaItem(BaseCustomizationItem):
    __metaclass__ = ReflectionMetaclass
    itemType = CustomizationType.INSIGNIA
    __slots__ = ('atlas', 'alphabet', 'canBeMirrored')
    allSlots = BaseCustomizationItem.__slots__ + __slots__

    def __init__(self, parentGroup=None):
        self.atlas = ''
        self.alphabet = ''
        self.canBeMirrored = False
        super(InsigniaItem, self).__init__(parentGroup)


class ItemGroup(object):
    __metaclass__ = ReflectionMetaclass
    itemType = CustomizationType.ITEM_GROUP
    __slots__ = ('itemPrototype', 'name')

    def __init__(self, itemClass):
        self.itemPrototype = itemClass()
        self.name = ''
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
    __metaclass__ = ReflectionMetaclass
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


if IS_EDITOR:
    CUSTOMIZATION_TYPES = {CustomizationType.MODIFICATION: ModificationItem,
     CustomizationType.STYLE: StyleItem,
     CustomizationType.DECAL: DecalItem,
     CustomizationType.CAMOUFLAGE: CamouflageItem,
     CustomizationType.PERSONAL_NUMBER: PersonalNumberItem,
     CustomizationType.PAINT: PaintItem,
     CustomizationType.PROJECTION_DECAL: ProjectionDecalItem,
     CustomizationType.INSIGNIA: InsigniaItem,
     CustomizationType.SEQUENCE: SequenceItem,
     CustomizationType.FONT: Font,
     CustomizationType.ATTACHMENT: AttachmentItem}
    CUSTOMIZATION_CLASSES = {v:k for k, v in CUSTOMIZATION_TYPES.items()}

class _Filter(object):
    __slots__ = ('include', 'exclude')

    def __init__(self):
        super(_Filter, self).__init__()
        self.include = []
        self.exclude = []

    def __deepcopy__(self, memodict={}):
        newItem = type(self)()
        newItem.include = deepcopy(self.include)
        newItem.exclude = deepcopy(self.exclude)
        return newItem

    def __str__(self):
        includes = map(lambda x: str(x), self.include)
        excludes = map(lambda x: str(x), self.exclude)
        result = []
        if includes:
            result.append('includes: ' + str(includes))
        if excludes:
            result.append('excludes: ' + str(excludes))
        return '; '.join(result)

    def match(self, item):
        raise NotImplementedError


class VehicleFilter(_Filter):
    __metaclass__ = ReflectionMetaclass

    class FilterNode(object):
        __metaclass__ = ReflectionMetaclass
        __slots__ = ('nations', 'levels', 'tags', 'vehicles')

        def __init__(self):
            self.nations = None
            self.levels = None
            self.tags = None
            self.vehicles = None
            return

        def __deepcopy__(self, memodict={}):
            newItem = type(self)()
            newItem.nations = deepcopy(self.nations)
            newItem.levels = deepcopy(self.levels)
            newItem.vehicles = deepcopy(self.vehicles)
            newItem.tags = deepcopy(self.tags)
            return newItem

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

    def match(self, vehicleDescr):
        include = not self.include or any((f.match(vehicleDescr) for f in self.include))
        return include and not (self.exclude and any((f.match(vehicleDescr) for f in self.exclude)))

    def matchVehicleType(self, vehicleType):
        include = not self.include or any((f.matchVehicleType(vehicleType) for f in self.include))
        return include and not (self.exclude and any((f.matchVehicleType(vehicleType) for f in self.exclude)))


class ItemsFilter(_Filter):
    __metaclass__ = ReflectionMetaclass

    class FilterNode(object):
        __slots__ = ('ids', 'itemGroupNames', 'tags', 'types', 'historical')

        def __init__(self):
            self.ids = None
            self.itemGroupNames = None
            self.tags = None
            self.types = None
            self.historical = None
            return

        def __str__(self):
            result = []
            if self.ids is not None:
                result.append(str(self.ids))
            if self.itemGroupNames is not None:
                result.append(str(self.itemGroupNames))
            if self.tags is not None:
                result.append(str(self.tags))
            if self.types is not None:
                result.append(str(self.types))
            if self.historical is not None:
                result.append(str(self.historical))
            return '; '.join(result)

        def matchItem(self, item):
            if self.ids is not None and item.id not in self.ids:
                return False
            elif self.itemGroupNames is not None and item.parentGroup.name not in self.itemGroupNames:
                return False
            elif self.tags is not None and not self.tags < item.tags:
                return False
            elif self.types is not None and item.itemType == CustomizationType.DECAL and item.type not in self.types:
                return False
            else:
                return False if self.historical is not None and item.historical != self.historical else True

    def match(self, item):
        include = not self.include or any((f.matchItem(item) for f in self.include))
        return include and not (self.exclude and any((f.matchItem(item) for f in self.exclude)))


class ProgressForCustomization(object):
    __slots__ = ('autobound', 'levels', 'autoGrantCount', 'bonusTypes', 'priceGroup', 'defaultLvl')

    def __init__(self):
        super(ProgressForCustomization, self).__init__()
        self.autobound = False
        self.levels = {}
        self.autoGrantCount = 0
        self.bonusTypes = set()
        self.priceGroup = ''
        self.defaultLvl = 0

    def __deepcopy__(self, memodict={}):
        newItem = type(self)()
        newItem.autobound = self.autobound
        newItem.levels = deepcopy(self.levels)
        newItem.autoGrantCount = self.autoGrantCount
        newItem.priceGroup = self.priceGroup
        newItem.defaultLvl = self.defaultLvl
        return newItem

    def __str__(self):
        result = {'autobound': self.autobound,
         'levels': self.levels,
         'autoGrantCount': self.autoGrantCount,
         'bonusTypes': self.bonusTypes,
         'priceGroup': self.priceGroup,
         'defaultLvl': self.defaultLvl}
        return str(result)


class CustomizationCache(object):
    __metaclass__ = ReflectionMetaclass
    __slots__ = ('paints', 'camouflages', 'decals', 'projection_decals', 'modifications', 'levels', 'itemToPriceGroup', 'priceGroups', 'priceGroupNames', 'insignias', 'styles', 'defaultColors', 'defaultInsignias', 'itemTypes', 'priceGroupTags', '__victimStyles', 'personal_numbers', 'fonts', 'sequences', 'attachments', 'customizationWithProgression', 'itemGroupByProgressionBonusType', '__vehicleCanMayIncludeCustomization', 'topVehiclesByNation')

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
        self.defaultInsignias = {}
        self.defaultColors = {}
        self.fonts = {}
        self.sequences = {}
        self.attachments = {}
        self.__victimStyles = {}
        self.customizationWithProgression = {}
        self.itemGroupByProgressionBonusType = {arenaTypeID:list() for arenaTypeID in ARENA_BONUS_TYPE_NAMES.values() if ARENA_BONUS_TYPE_CAPS.checkAny(arenaTypeID, ARENA_BONUS_TYPE_CAPS.CUSTOMIZATION_PROGRESSION)}
        self.__vehicleCanMayIncludeCustomization = {}
        self.topVehiclesByNation = {}
        self.itemTypes = {CustomizationType.MODIFICATION: self.modifications,
         CustomizationType.STYLE: self.styles,
         CustomizationType.DECAL: self.decals,
         CustomizationType.CAMOUFLAGE: self.camouflages,
         CustomizationType.PERSONAL_NUMBER: self.personal_numbers,
         CustomizationType.PAINT: self.paints,
         CustomizationType.PROJECTION_DECAL: self.projection_decals,
         CustomizationType.INSIGNIA: self.insignias,
         CustomizationType.SEQUENCE: self.sequences,
         CustomizationType.ATTACHMENT: self.attachments}
        super(CustomizationCache, self).__init__()

    def getVehiclesCanMayInclude(self, item):
        vehsCanUseItem = self.__vehicleCanMayIncludeCustomization.get(item.compactDescr)
        if vehsCanUseItem is None:
            vehsCanUseItem = []
            for nationID in nations.INDICES.itervalues():
                for descr in iv.g_list.getList(nationID).itervalues():
                    vehCD = descr.compactDescr
                    if item.matchVehicleType(iv.getVehicleType(vehCD)):
                        vehsCanUseItem.append(vehCD)

            self.__vehicleCanMayIncludeCustomization[item.compactDescr] = vehsCanUseItem
        return vehsCanUseItem

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

    def validateOutfit(self, vehDescr, outfit, progressionStorage, tokens=None, season=SeasonType.ALL):
        usedStyle = None
        try:
            vehType = vehDescr.type
            styleID = outfit.styleId
            if styleID != 0:
                usedStyle = self.styles.get(styleID, None)
                if usedStyle is None:
                    raise SoftException('Wrong styleId {} '.format(styleID))
                if not usedStyle.matchVehicleType(vehType):
                    raise SoftException('style {} is incompatible with vehicle {}'.format(styleID, vehDescr.name))
                if usedStyle.isProgressive():
                    if usedStyle.progression.defaultLvl > outfit.styleProgressionLevel > len(usedStyle.progression.levels):
                        raise SoftException('Progression style {} level out of limits'.format(styleID))
                projectionDecalsCount = len(outfit.projection_decals)
                if projectionDecalsCount > MAX_USERS_PROJECTION_DECALS:
                    raise SoftException('projection decals quantity {} greater than acceptable'.format(projectionDecalsCount))
                for itemType in CustomizationType.FULL_RANGE:
                    typeName = lower(CustomizationTypeNames[itemType])
                    componentsAttrName = '{}s'.format(typeName)
                    components = getattr(outfit, componentsAttrName, None)
                    if not components:
                        continue
                    elif usedStyle is not None and not usedStyle.isEditable:
                        raise SoftException("Style {} can't contain extra items in outfit".format(styleID))
                    if itemType in CustomizationType.STYLE_ONLY_RANGE and components:
                        raise SoftException("Outfit can't contain style-only items: {}".format(components))
                    storage = getattr(self, componentsAttrName)
                    if usedStyle is not None:
                        baseOutfit = usedStyle.outfits.get(season)
                        if not baseOutfit:
                            raise SoftException("Style {} hasn't base outfit for season {}".format(styleID, season))
                        baseComponents = getattr(baseOutfit, componentsAttrName, None)
                    for component in components:
                        componentId = component.id if not isinstance(component, int) else component
                        item = storage.get(componentId, None)
                        if componentId != EMPTY_ITEM_ID:
                            if item is None:
                                raise SoftException('{} {} not found'.format(typeName, componentId))
                            _validateItem(typeName, item, season, tokens, vehType, styleID)
                            if item.isProgressive():
                                _validateProgression(component, item, progressionStorage, vehType)
                            if itemType in CustomizationType.APPLIED_TO_TYPES:
                                _validateApplyTo(component, item)
                                if itemType == CustomizationType.CAMOUFLAGE:
                                    _validateCamouflage(component, item)
                                elif itemType == CustomizationType.PERSONAL_NUMBER:
                                    _validatePersonalNumber(component, item)
                            elif itemType == CustomizationType.PROJECTION_DECAL:
                                _validateProjectionDecal(component, item, vehDescr, usedStyle)
                        if usedStyle is not None and usedStyle.isEditable:
                            _validateEditableStyle(componentId, typeName, itemType, component, item, usedStyle, outfit, vehDescr, baseComponents, season)

                usedStyle is not None and usedStyle.isEditable and _validateDependencies(outfit, usedStyle, vehDescr, season)
        except SoftException as ex:
            return (False, ex.message)

        return (True, '')

    def adjustProgression--- This code section failed: ---

 894       0	LOAD_GLOBAL       'False'
           3	STORE_FAST        'force'

 895       6	LOAD_GLOBAL       'CustomizationType'
           9	LOAD_ATTR         'RANGE'
          12	STORE_FAST        'itemTypes'

 896      15	LOAD_FAST         'itemForce'
          18	LOAD_CONST        ''
          21	COMPARE_OP        'is not'
          24	POP_JUMP_IF_FALSE '48'

 897      27	LOAD_GLOBAL       'True'
          30	STORE_FAST        'force'

 898      33	LOAD_FAST         'itemForce'
          36	LOAD_ATTR         'itemType'
          39	BUILD_SET_1       ''
          42	STORE_FAST        'itemTypes'
          45	JUMP_FORWARD      '48'
        48_0	COME_FROM         '45'

 900      48	SETUP_LOOP        '322'
          51	LOAD_FAST         'itemTypes'
          54	GET_ITER          ''
          55	FOR_ITER          '321'
          58	STORE_FAST        'itemType'

 901      61	LOAD_GLOBAL       'lower'
          64	LOAD_GLOBAL       'CustomizationTypeNames'
          67	LOAD_FAST         'itemType'
          70	BINARY_SUBSCR     ''
          71	CALL_FUNCTION_1   ''
          74	STORE_FAST        'typeName'

 902      77	LOAD_CONST        '{}s'
          80	LOAD_ATTR         'format'
          83	LOAD_FAST         'typeName'
          86	CALL_FUNCTION_1   ''
          89	STORE_FAST        'componentsAttrName'

 903      92	LOAD_GLOBAL       'getattr'
          95	LOAD_FAST         'outfit'
          98	LOAD_FAST         'componentsAttrName'
         101	LOAD_CONST        ''
         104	CALL_FUNCTION_3   ''
         107	STORE_FAST        'components'

 905     110	LOAD_FAST         'components'
         113	POP_JUMP_IF_TRUE  '122'

 906     116	CONTINUE          '55'
         119	JUMP_FORWARD      '122'
       122_0	COME_FROM         '119'

 908     122	LOAD_GLOBAL       'getattr'
         125	LOAD_FAST         'self'
         128	LOAD_FAST         'componentsAttrName'
         131	CALL_FUNCTION_2   ''
         134	STORE_FAST        'storage'

 910     137	SETUP_LOOP        '318'
         140	LOAD_FAST         'components'
         143	GET_ITER          ''
         144	FOR_ITER          '317'
         147	STORE_FAST        'component'

 911     150	LOAD_FAST         'itemType'
         153	LOAD_GLOBAL       'CustomizationType'
         156	LOAD_ATTR         'CAMOUFLAGE'
         159	COMPARE_OP        '=='
         162	POP_JUMP_IF_FALSE '186'
         165	LOAD_FAST         'component'
         168	LOAD_ATTR         'id'
         171	LOAD_GLOBAL       'HIDDEN_CAMOUFLAGE_ID'
         174	COMPARE_OP        '=='
       177_0	COME_FROM         '162'
         177	POP_JUMP_IF_FALSE '186'

 912     180	CONTINUE          '144'
         183	JUMP_FORWARD      '186'
       186_0	COME_FROM         '183'

 914     186	SETUP_EXCEPT      '290'

 916     189	LOAD_GLOBAL       'isinstance'
         192	LOAD_FAST         'component'
         195	LOAD_GLOBAL       'int'
         198	CALL_FUNCTION_2   ''
         201	POP_JUMP_IF_FALSE '210'

 917     204	CONTINUE_LOOP     '144'
         207	JUMP_FORWARD      '210'
       210_0	COME_FROM         '207'

 919     210	LOAD_FAST         'force'
         213	POP_JUMP_IF_FALSE '240'
         216	LOAD_FAST         'itemForce'
         219	LOAD_ATTR         'id'
         222	LOAD_FAST         'component'
         225	LOAD_ATTR         'id'
         228	COMPARE_OP        '!='
       231_0	COME_FROM         '213'
         231	POP_JUMP_IF_FALSE '240'

 920     234	CONTINUE_LOOP     '144'
         237	JUMP_FORWARD      '240'
       240_0	COME_FROM         '237'

 922     240	LOAD_FAST         'storage'
         243	LOAD_ATTR         'get'
         246	LOAD_FAST         'component'
         249	LOAD_ATTR         'id'
         252	CALL_FUNCTION_1   ''
         255	STORE_FAST        'item'

 923     258	LOAD_GLOBAL       '_adjustProgression'
         261	LOAD_FAST         'component'
         264	LOAD_FAST         'vehTypeCompDescr'
         267	LOAD_FAST         'item'
         270	LOAD_FAST         'progressionStorage'
         273	LOAD_CONST        'progressionLevel'
         276	LOAD_CONST        'force'

 924     279	LOAD_FAST         'force'
         282	CALL_FUNCTION_261 ''
         285	POP_TOP           ''
         286	POP_BLOCK         ''
         287	JUMP_BACK         '144'
       290_0	COME_FROM         '186'

 925     290	DUP_TOP           ''
         291	LOAD_GLOBAL       'SoftException'
         294	COMPARE_OP        'exception match'
         297	POP_JUMP_IF_FALSE '313'
         300	POP_TOP           ''
         301	POP_TOP           ''
         302	POP_TOP           ''

 926     303	LOAD_GLOBAL       'LOG_CURRENT_EXCEPTION'
         306	CALL_FUNCTION_0   ''
         309	POP_TOP           ''
         310	JUMP_BACK         '144'
         313	END_FINALLY       ''
       314_0	COME_FROM         '313'
         314	JUMP_BACK         '144'
         317	POP_BLOCK         ''
       318_0	COME_FROM         '137'
         318	JUMP_BACK         '55'
         321	POP_BLOCK         ''
       322_0	COME_FROM         '48'

 928     322	SETUP_EXCEPT      '445'

 929     325	LOAD_GLOBAL       'CustomizationType'
         328	LOAD_ATTR         'STYLE'
         331	LOAD_FAST         'itemTypes'
         334	COMPARE_OP        'in'
         337	POP_JUMP_IF_FALSE '441'

 930     340	LOAD_FAST         'outfit'
         343	LOAD_ATTR         'styleId'
         346	LOAD_CONST        0
         349	COMPARE_OP        '!='
         352	POP_JUMP_IF_FALSE '441'
         355	LOAD_FAST         'force'
         358	POP_JUMP_IF_FALSE '379'
         361	LOAD_FAST         'outfit'
         364	LOAD_ATTR         'styleId'
         367	LOAD_FAST         'itemForce'
         370	LOAD_ATTR         'id'
         373	COMPARE_OP        '=='
       376_0	COME_FROM         '358'
         376	POP_JUMP_IF_TRUE  '386'
         379	LOAD_FAST         'force'
         382	UNARY_NOT         ''
       383_0	COME_FROM         '337'
       383_1	COME_FROM         '352'
       383_2	COME_FROM         '376'
         383	POP_JUMP_IF_FALSE '441'

 931     386	LOAD_FAST         'self'
         389	LOAD_ATTR         'styles'
         392	LOAD_ATTR         'get'
         395	LOAD_FAST         'outfit'
         398	LOAD_ATTR         'styleId'
         401	CALL_FUNCTION_1   ''
         404	STORE_FAST        'item'

 932     407	LOAD_GLOBAL       '_adjustProgression'
         410	LOAD_FAST         'outfit'
         413	LOAD_FAST         'vehTypeCompDescr'
         416	LOAD_FAST         'item'
         419	LOAD_FAST         'progressionStorage'
         422	LOAD_CONST        'styleProgressionLevel'
         425	LOAD_CONST        'force'

 933     428	LOAD_FAST         'force'
         431	CALL_FUNCTION_261 ''
         434	POP_TOP           ''
         435	JUMP_ABSOLUTE     '441'
         438	JUMP_FORWARD      '441'
       441_0	COME_FROM         '438'
         441	POP_BLOCK         ''
         442	JUMP_FORWARD      '469'
       445_0	COME_FROM         '322'

 934     445	DUP_TOP           ''
         446	LOAD_GLOBAL       'SoftException'
         449	COMPARE_OP        'exception match'
         452	POP_JUMP_IF_FALSE '468'
         455	POP_TOP           ''
         456	POP_TOP           ''
         457	POP_TOP           ''

 935     458	LOAD_GLOBAL       'LOG_CURRENT_EXCEPTION'
         461	CALL_FUNCTION_0   ''
         464	POP_TOP           ''
         465	JUMP_FORWARD      '469'
         468	END_FINALLY       ''
       469_0	COME_FROM         '442'
       469_1	COME_FROM         '468'
         469	LOAD_CONST        ''
         472	RETURN_VALUE      ''

Syntax error at or near 'JUMP_FORWARD' token at offset 438


class EditingStyleReason(object):

    def __init__(self, reson):
        self.reason = reson

    def __nonzero__(self):
        return self.reason in EDITING_STYLE_REASONS.ENABLED


def _adjustProgression(component, vehTypeCD, item, progressionStorage, attr, force=False):
    if item is None:
        raise SoftException('Missing customization item for component: {}'.format(component))
    if not item.isProgressive():
        return
    else:
        if not hasattr(component, attr):
            raise SoftException('Missing progression level for component: {}'.format(component))
        if not force and getattr(component, attr):
            return
        if not item.progression.autobound:
            vehTypeCD = 0
        level = progressionStorage.get(item.itemType, {}).get(item.id, {}).get(vehTypeCD, {}).get('level')
        if level is None:
            raise SoftException('missing progression for item: {} at vehicle: {}'.format(item.id, vehTypeCD))
        setattr(component, attr, level)
        return


def _validateItem(typeName, item, season, tokens, vehType, styleID):
    if not item.matchVehicleType(vehType):
        raise SoftException('{} {} incompatible vehicle {}'.format(typeName, item.id, vehType))
    if not item.season & season:
        raise SoftException('{} {} incompatible season {}'.format(typeName, item.id, season))
    if not item.isUnlocked(tokens):
        raise SoftException('{} {} locked'.format(typeName, item.id))
    if vehType.progressionDecalsOnly and not item.isProgressive() and ItemTags.NATIONAL_EMBLEM not in item.tags:
        raise SoftException('{} can have only progression customization'.format(vehType))
    if styleID == 0 and item.isStyleOnly:
        raise SoftException("styleOnly {} {} can't be used with custom style".format(typeName, item.id, vehType))


def _validateProgression(component, item, progressionStorage, vehType):
    level = getattr(component, 'progressionLevel', None)
    if level is None:
        raise SoftException('missing progression level for component:'.format(component.id))
    vehTypeCD = vehType.compactDescr if item.progression.autobound else 0
    achievedLevel = progressionStorage.get(item.itemType, {}).get(item.id, {}).get(vehTypeCD, {}).get('level')
    if achievedLevel is None:
        raise SoftException('missing progression for item: {} at vehicle: {}'.format(item.id, vehTypeCD))
    if not 0 <= level <= achievedLevel:
        raise SoftException('wrong progression level: {} for component: {} at vehicle: {}'.format(level, component.id, vehTypeCD))
    return


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


def _validateProjectionDecal(component, item, vehDescr, usedStyle=None):
    options = component.options
    if options & Options.PROJECTION_DECALS_ALLOWED_OPTIONS_VALUE != options:
        raise SoftException('projection decal {} wrong options {}'.format(component.id, options))
    if component.scaleFactorId not in PROJECTION_DECALS_SCALE_ID_VALUES:
        raise SoftException('projection decal {} wrong scaleFactorId {}'.format(component.id, component.scaleFactorId))
    slotId = component.slotId
    slotParams = getVehicleProjectionDecalSlotParams(vehDescr, slotId)
    if slotParams is None:
        raise SoftException('projection decal {} wrong slotId = {}. VehType = {}'.format(component.id, slotId, vehDescr.type))
    if options & Options.MIRRORED_HORIZONTALLY and not (item.canBeMirroredHorizontally or item.canBeMirroredOnlyVertically):
        raise SoftException('projection decal {} wrong horizontally mirrored option'.format(component.id))
    if options & Options.MIRRORED_VERTICALLY and not (item.canBeMirroredVertically and slotParams.canBeMirroredVertically):
        raise SoftException('projection decal {} wrong vertically mirrored option for slotId = {}'.format(component.id, slotId))
    if item.canBeMirroredOnlyVertically and options ^ Options.COMBO_MIRRORED and options ^ Options.NONE:
        raise SoftException('projection decal {} must have equal mirroring options for both directions'.format(component.id))
    if HIDDEN_FOR_USER_TAG in slotParams.tags:
        raise SoftException('Hidden for user slot (slotId = {}) can not be in outfit'.format(slotId))
    usedModel = SLOT_DEFAULT_ALLOWED_MODEL if usedStyle is None or not usedStyle.modelsSet else usedStyle.modelsSet
    if usedModel not in slotParams.compatibleModels:
        raise SoftException('user slot (slotId = {}, compatibleModels={}) is not compatible with used modelset {}'.format(slotId, slotParams.compatibleModels, usedModel))
    slotFormFactors = set([ tag for tag in slotParams.tags if tag.startswith(ProjectionDecalFormTags.PREFIX) ])
    if slotFormFactors:
        formfactor = next((tag for tag in item.tags if tag.startswith(ProjectionDecalFormTags.PREFIX)), '')
        if not formfactor:
            raise SoftException('projection decal {} wrong XML. formfactor is missing'.format(component.id, formfactor))
        if formfactor not in slotFormFactors:
            raise SoftException('projection decal {} wrong formfactor {}'.format(component.id, formfactor))
    return


def _validatePersonalNumber(component, item):
    number = component.number
    if not number or len(number) != item.digitsCount:
        raise SoftException('personal number {} has wrong number {}'.format(component.id, number))
    if not isPersonalNumberAllowed(number):
        raise SoftException('number {} of personal number {} is prohibited'.format(number, component.id))


def _validateEditableStyle(componentId, typeName, itemType, component, item, baseStyle, outfit, vehDescr, baseComponents, season=SeasonType.ALL):
    if componentId == EMPTY_ITEM_ID:
        if isinstance(component, int):
            raise SoftException('slot type {} is simple and not clearable in editable style'.format(typeName, outfit.styleId))
        if itemType == CustomizationType.DECAL:
            slotTypes = []
            if component.appliedTo & ApplyArea.INSCRIPTION_REGIONS_VALUE > 0:
                slotTypes.append(SLOT_TYPE_NAMES.INSCRIPTION)
            if component.appliedTo & ApplyArea.EMBLEM_REGIONS_VALUE > 0:
                slotTypes.append(SLOT_TYPE_NAMES.EMBLEM)
        else:
            slotTypes = [getSlotType(itemType)]
        for slotType in slotTypes:
            if slotType not in baseStyle.clearableSlotTypes:
                raise SoftException('slot type {} is not clearable in editable style {}'.format(slotType, outfit.styleId))

    else:
        if itemType in CustomizationType.APPLIED_TO_TYPES:
            appliedTo = component.appliedTo
            baseAppliedTo = (comp.appliedTo for comp in baseComponents if comp.id == item.id)
            baseAppliedTo = reduce(int.__or__, baseAppliedTo, 0)
            isBase = not (baseAppliedTo | appliedTo) ^ baseAppliedTo
        elif isinstance(component, int):
            isBase = False
        else:
            baseSlots = set((comp.slotId for comp in baseComponents if comp.id == item.id))
            isBase = component.slotId in baseSlots
        if not isBase and not baseStyle.isItemInstallable(item):
            raise SoftException('{} {} is not installable in editable style {}'.format(typeName, item.id, outfit.styleId))
        if item.itemType in (CustomizationType.PAINT, CustomizationType.CAMOUFLAGE):
            vehAllAppliedTo = vehDescr.chassis.customizableVehicleAreas.get(typeName)[0]
            vehAllAppliedTo |= vehDescr.hull.customizableVehicleAreas.get(typeName)[0]
            vehAllAppliedTo |= vehDescr.turret.customizableVehicleAreas.get(typeName)[0]
            vehAllAppliedTo |= vehDescr.gun.customizableVehicleAreas.get(typeName)[0]
            if vehAllAppliedTo != component.appliedTo:
                raise SoftException('{} {} shall be applied to full tank in editable style. Expected appliedTo {}, got {}'.format(typeName, item.id, vehAllAppliedTo, component.appliedTo))


def _validateDependencies(outfit, usedStyle, vehDescr, season):
    outfitToCheckDependencies = {}
    dependenciesSeason = season if season != SeasonType.ALL else SeasonType.SUMMER
    baseSeasonOutfit = usedStyle.outfits.get(dependenciesSeason)
    camouflages = getattr(outfit, 'camouflages')
    if baseSeasonOutfit:
        camouflageID = camouflages[0].id if len(camouflages) != 0 else baseSeasonOutfit.camouflages[0].id
        availableEmblemRegions = set()
        availableInscriptionRegions = set()
        for partName in CUSTOMIZATION_SLOTS_VEHICLE_PARTS:
            availableEmblemRegions |= getAvailableRegions(vehDescr, partName, 'emblem')
            availableInscriptionRegions |= getAvailableRegions(vehDescr, partName, 'inscription')

        availableEmblemRegions = reduce(int.__or__, availableEmblemRegions, 0)
        availableInscriptionRegions = reduce(int.__or__, availableInscriptionRegions, 0)
        if vehDescr.turret.showEmblemsOnGun:
            TURRET_EMBLEM_REGIONS_VALUE = reduce(int.__or__, ApplyArea.TURRET_EMBLEM_REGIONS)
            TURRET_INSCRIPTION_REGIONS_VALUE = reduce(int.__or__, ApplyArea.TURRET_INSCRIPTION_REGIONS)
            availableTurretEmblemRegions = availableEmblemRegions & TURRET_EMBLEM_REGIONS_VALUE
            availableTurretInscriptionRegions = availableInscriptionRegions & TURRET_INSCRIPTION_REGIONS_VALUE
            if availableTurretEmblemRegions:
                availableEmblemRegions &= ~availableTurretEmblemRegions
                availableEmblemRegions |= availableTurretEmblemRegions << 4
            if availableTurretInscriptionRegions:
                availableInscriptionRegions &= ~availableTurretInscriptionRegions
                availableInscriptionRegions |= availableTurretInscriptionRegions << 4
        modifiedOutfit = baseSeasonOutfit.applyDiff(outfit)
        outfitToCheckDependencies[CustomizationType.MODIFICATION] = modifiedOutfit.modifications
        for paint in modifiedOutfit.paints:
            if paint.appliedTo & ApplyArea.PAINT_REGIONS_VALUE:
                outfitToCheckDependencies.setdefault(CustomizationType.PAINT, set()).add(paint.id)

        for decal in modifiedOutfit.decals:
            if decal.appliedTo & availableEmblemRegions or decal.appliedTo & availableInscriptionRegions:
                outfitToCheckDependencies.setdefault(CustomizationType.DECAL, set()).add(decal.id)

        for number in modifiedOutfit.personal_numbers:
            if number.appliedTo & availableInscriptionRegions:
                outfitToCheckDependencies.setdefault(CustomizationType.PERSONAL_NUMBER, set()).add(number.id)

        for projectionDecal in modifiedOutfit.projection_decals:
            outfitToCheckDependencies.setdefault(CustomizationType.PROJECTION_DECAL, set()).add(projectionDecal.id)

        for itemType, itemIDs in outfitToCheckDependencies.iteritems():
            camouflageItemTypeDependencies = usedStyle.dependencies.get(camouflageID, {}).get(itemType, {})
            for itemID in itemIDs:
                if itemID in usedStyle.alternateItems.get(itemType, ()):
                    ancestors = usedStyle.dependenciesAncestors.get(itemType, {}).get(itemID, ())
                    if camouflageItemTypeDependencies and ancestors and itemID not in camouflageItemTypeDependencies:
                        raise SoftException('Incorrect dependent item {} for camouflage {}'.format(itemID, camouflageID))


def getAvailableRegions(vehDescr, partName, slotType):
    part = getattr(vehDescr, partName)
    availableRegions = set()
    regions = iter(getattr(ApplyArea, '{}_{}_REGIONS'.format(partName.upper(), slotType.upper()), ()))
    availableRegions |= set((next(regions) for slot in part.emblemSlots if slot.type == getattr(SLOT_TYPE_NAMES, slotType.upper())))
    return availableRegions


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
    for wantedPartName in partNames:
        partApplyArea = getattr(ApplyArea, '{}_REGIONS_VALUE'.format(upper(wantedPartName)))
        for partName in CUSTOMIZATION_SLOTS_VEHICLE_PARTS:
            for vehicleSlot in getattr(vehicleDescr, partName).slotsAnchors:
                if vehicleSlot.type == slotTypeName and vehicleSlot.slotId == vehicleSlotId:
                    if partName in partNames or partApplyArea & vehicleSlot.showOn:
                        return vehicleSlot

    return None


def isPersonalNumberAllowed(personalNumber):
    return personalNumber not in PersonalNumberItem.getProhibitedNumbers()


def isSlotFitsVehicle(slotDescriptor, vehicleDescriptor):
    if slotDescriptor.attachedParts is None:
        return True
    else:
        for partType, attachedParts in slotDescriptor.attachedParts.iteritems():
            part = getattr(vehicleDescriptor, partType, None)
            if part is None:
                raise SoftException('projection decal {} wrong attached part type: {}'.format(slotDescriptor.slotId, partType))
            if part.name not in attachedParts:
                return False

        return True


def getAvailableSlotsCount(item, vehicleDescriptor):
    slotType = getItemSlotType(item)
    count = 0
    for partName in CUSTOMIZATION_SLOTS_VEHICLE_PARTS:
        part = getattr(vehicleDescriptor, partName)
        slots = part.emblemSlots if item.itemType == CustomizationType.DECAL else part.slotsAnchors
        count += sum((1 for slot in slots if slot.type == slotType))

    if item.itemType == CustomizationType.PROJECTION_DECAL:
        count = min(count, MAX_USERS_PROJECTION_DECALS)
    return count


@lru_cache(maxsize=10)
def isVehicleHasSlots(vehicleDescriptor, slotType):
    isDecal = slotType in SLOT_TYPE_NAMES.DECALS
    for partName in CUSTOMIZATION_SLOTS_VEHICLE_PARTS:
        part = getattr(vehicleDescriptor, partName)
        slots = part.emblemSlots if isDecal else part.slotsAnchors
        if any((slot.type == slotType for slot in slots)):
            return True

    return False


def getItemSlotType(item):
    decalType = item.type if item.itemType == CustomizationType.DECAL else None
    slotType = getSlotType(item.itemType, decalType)
    return slotType


def getSlotType(itemType, decalType=None):
    slotType = ''
    if itemType == CustomizationType.PAINT:
        slotType = SLOT_TYPE_NAMES.PAINT
    elif itemType == CustomizationType.CAMOUFLAGE:
        slotType = SLOT_TYPE_NAMES.CAMOUFLAGE
    elif itemType == CustomizationType.DECAL:
        slotType = SLOT_TYPE_NAMES.INSCRIPTION if decalType == DecalType.INSCRIPTION else SLOT_TYPE_NAMES.EMBLEM
    elif itemType == CustomizationType.STYLE:
        slotType = SLOT_TYPE_NAMES.STYLE
    elif itemType == CustomizationType.MODIFICATION:
        slotType = SLOT_TYPE_NAMES.EFFECT
    elif itemType == CustomizationType.PROJECTION_DECAL:
        slotType = SLOT_TYPE_NAMES.PROJECTION_DECAL
    elif itemType == CustomizationType.INSIGNIA:
        slotType = SLOT_TYPE_NAMES.INSIGNIA
    elif itemType == CustomizationType.PERSONAL_NUMBER:
        slotType = SLOT_TYPE_NAMES.INSCRIPTION
    return slotType