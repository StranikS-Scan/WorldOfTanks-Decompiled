# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/customization/c11n_items.py
import os
import urllib
import typing
import logging
from copy import deepcopy
import Math
import ResMgr
from CurrentVehicle import g_currentVehicle
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items import GUI_ITEM_TYPE_NAMES, GUI_ITEM_TYPE
from gui.shared.gui_items.fitting_item import FittingItem, RentalInfoProvider
from gui.shared.image_helper import getTextureLinkByID
from gui.shared.utils.functions import getImageResourceFromPath
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from helpers import dependency
from items import makeIntCompactDescrByID
from items.components.c11n_constants import SeasonType, ItemTags, ProjectionDecalDirectionTags, ProjectionDecalFormTags, UNBOUND_VEH_KEY, ImageOptions
from items.customizations import parseCompDescr, isEditedStyle, createNationalEmblemComponents
from items.vehicles import VehicleDescr
from shared_utils import first
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from items.components import c11n_components as cc
if typing.TYPE_CHECKING:
    from items.components.c11n_components import ProgressForCustomization
    from gui.shared.gui_items.Vehicle import Vehicle
_logger = logging.getLogger(__name__)
_CAMO_ICON_TEMPLATE = 'img://camouflage,{width},{height},{options},"{texture}","{background}",{colors},{weights}'
_CAMO_ICON_URL = 'camo://{texture}?{params}'
_CAMO_SWATCH_WIDTH = 128
_CAMO_SWATCH_HEIGHT = 128
_CAMO_SWATCH_BACKGROUND = 'gui/maps/vehicles/camouflages/camo_back.dds'
_PERSONAL_NUM_ICON_TEMPLATE = 'img://personal_num,{width},{height},"{texture}","{fontPath}","{number}","{textureMask}","{background}"'
_PERSONAL_NUM_ICON_URL = 'pnum://{texture}?{params}'
_PN_SWATCH_WIDTH = 228
_PN_SWATCH_HEIGHT = 104
_PREVIEW_ICON_TEMPLATE = 'img://preview_icon,{width},{height},{innerWidth},{innerHeight},"{texture}"'
_PREVIEW_ICON_URL = 'preview://{texture}?{params}'
_PREVIEW_ICON_SIZE = (226, 102)
_PREVIEW_ICON_INNER_SIZE_DEFAULT = (74, 74)
_PREVIEW_ICON_INNER_SIZE = {ProjectionDecalFormTags.SQUARE: (74, 74),
 ProjectionDecalFormTags.RECT1X2: (174, 87),
 ProjectionDecalFormTags.RECT1X3: (186, 62),
 ProjectionDecalFormTags.RECT1X4: (220, 55),
 ProjectionDecalFormTags.RECT1X6: (220, 37)}
_STYLE_GROUP_ID_TO_GROUP_NAME_MAP = {}
_STYLE_GROUP_ID_TO_FULL_GROUP_NAME_MAP = {}
_PROGRESSION_LEVEL_CONDITION_INDEX = 1
STYLE_GROUP_ID_TO_GROUP_NAME_MAP = {VEHICLE_CUSTOMIZATION.STYLES_SPECIAL_STYLES: VEHICLE_CUSTOMIZATION.CUSTOMIZATION_INFOTYPE_TYPE_STYLE_SPECIAL,
 VEHICLE_CUSTOMIZATION.STYLES_MAIN_STYLES: VEHICLE_CUSTOMIZATION.CUSTOMIZATION_INFOTYPE_TYPE_STYLE_MAIN,
 VEHICLE_CUSTOMIZATION.STYLES_RENTED_STYLES: VEHICLE_CUSTOMIZATION.CUSTOMIZATION_INFOTYPE_TYPE_STYLE_RENTAL,
 VEHICLE_CUSTOMIZATION.STYLES_UNIQUE_STYLES: VEHICLE_CUSTOMIZATION.CUSTOMIZATION_INFOTYPE_TYPE_STYLE_UNIQUE,
 VEHICLE_CUSTOMIZATION.STYLES_HISTORICAL_STYLES: VEHICLE_CUSTOMIZATION.CUSTOMIZATION_INFOTYPE_TYPE_STYLE_HISTORICAL}

def getStyleGroupNameResourceID(groupID):
    if not _STYLE_GROUP_ID_TO_GROUP_NAME_MAP:
        _groupIDs = R.strings.vehicle_customization.styles
        _groupNames = R.strings.vehicle_customization.customization.infotype.type.style
        _STYLE_GROUP_ID_TO_GROUP_NAME_MAP.update({backport.msgid(_groupIDs.special_styles()): _groupNames.special(),
         backport.msgid(_groupIDs.main_styles()): _groupNames.main(),
         backport.msgid(_groupIDs.rented_styles()): _groupNames.rental(),
         backport.msgid(_groupIDs.unique_styles()): _groupNames.unique(),
         backport.msgid(_groupIDs.historical_styles()): _groupNames.historical()})
    return _STYLE_GROUP_ID_TO_GROUP_NAME_MAP[groupID] if groupID in _STYLE_GROUP_ID_TO_GROUP_NAME_MAP else R.invalid()


def getGroupFullNameResourceID(groupID):
    if not _STYLE_GROUP_ID_TO_FULL_GROUP_NAME_MAP:
        _groupIDs = R.strings.vehicle_customization.styles
        _groupNames = R.strings.vehicle_customization.carousel.swatch.style
        _STYLE_GROUP_ID_TO_FULL_GROUP_NAME_MAP.update({backport.msgid(_groupIDs.special_styles()): _groupNames.special(),
         backport.msgid(_groupIDs.main_styles()): _groupNames.main(),
         backport.msgid(_groupIDs.rented_styles()): _groupNames.rented(),
         backport.msgid(_groupIDs.unique_styles()): _groupNames.unique(),
         backport.msgid(_groupIDs.historical_styles()): _groupNames.historical()})
    return _STYLE_GROUP_ID_TO_FULL_GROUP_NAME_MAP[groupID] if groupID in _STYLE_GROUP_ID_TO_FULL_GROUP_NAME_MAP else R.invalid()


class SpecialEvents(object):
    NY18 = 'NY2018_style'
    NY19 = 'NY2019_style'
    FOOTBALL18 = 'football2018'
    WINTER_HUNT = 'winter_hunt'
    KURSK_BATTLE = 'Kursk_battle'
    HALLOWEEN = 'Halloween'
    ALL = (NY18,
     NY19,
     FOOTBALL18,
     WINTER_HUNT,
     KURSK_BATTLE,
     HALLOWEEN)
    ICONS = {NY18: backport.image(R.images.gui.maps.icons.customization.style_info.newYear()),
     NY19: backport.image(R.images.gui.maps.icons.customization.style_info.newYear()),
     FOOTBALL18: backport.image(R.images.gui.maps.icons.customization.style_info.football()),
     WINTER_HUNT: backport.image(R.images.gui.maps.icons.customization.style_info.marathon()),
     KURSK_BATTLE: backport.image(R.images.gui.maps.icons.customization.style_info.marathon()),
     HALLOWEEN: backport.image(R.images.gui.maps.icons.customization.style_info.halloween())}
    NAMES = {NY18: backport.text(R.strings.vehicle_customization.styleInfo.event.ny18()),
     NY19: backport.text(R.strings.vehicle_customization.styleInfo.event.ny19()),
     FOOTBALL18: backport.text(R.strings.vehicle_customization.styleInfo.event.football18()),
     WINTER_HUNT: backport.text(R.strings.vehicle_customization.styleInfo.event.winter_hunt()),
     KURSK_BATTLE: backport.text(R.strings.vehicle_customization.styleInfo.event.kursk_battle()),
     HALLOWEEN: backport.text(R.strings.vehicle_customization.styleInfo.event.halloween())}


def camoIconTemplate(texture, width, height, colors, background=_CAMO_SWATCH_BACKGROUND, options=ImageOptions.NONE):
    weights = Math.Vector4(*[ (color >> 24) / 255.0 for color in colors ])
    return _CAMO_ICON_TEMPLATE.format(width=width, height=height, options=options, texture=texture, background=background, colors=','.join((str(color) for color in colors)), weights=','.join((str(weight) for weight in weights)))


def camoIconUrl(texture, width, height, colors, background=_CAMO_SWATCH_BACKGROUND, options=ImageOptions.NONE):
    weights = Math.Vector4(*[ (color >> 24) / 255.0 for color in colors ])
    params = {'back': background,
     'w': width,
     'h': height,
     'r': colors[0],
     'g': colors[1],
     'b': colors[2],
     'a': colors[3],
     'o': options,
     'rw': weights[0],
     'gw': weights[1],
     'bw': weights[2],
     'aw': weights[3]}
    return _CAMO_ICON_URL.format(texture=texture, params=urllib.urlencode(params))


def personalNumIconTemplate(number, width, height, texture, fontPath, textureMask='', background=''):
    return _PERSONAL_NUM_ICON_TEMPLATE.format(width=width, height=height, number=number, texture=texture, textureMask=textureMask, fontPath=fontPath, background=background)


def personalNumIconUrl(number, width, height, texture, fontPath, textureMask='', background=''):
    params = {'num': number,
     'w': width,
     'h': height,
     'font': fontPath,
     'mask': textureMask,
     'back': background}
    return _PERSONAL_NUM_ICON_URL.format(texture=texture, params=urllib.urlencode(params))


def previewTemplate(texture, width, height, innerWidth, innerHeight):
    return _PREVIEW_ICON_TEMPLATE.format(width=width, height=height, texture=texture, innerWidth=innerWidth, innerHeight=innerHeight)


def previewUrl(texture, width, height, innerWidth, innerHeight):
    params = {'w': width,
     'h': height,
     'iw': innerWidth,
     'ih': innerHeight}
    return _PREVIEW_ICON_URL.format(texture=texture, params=urllib.urlencode(params))


class ConcealmentBonus(object):
    __slots__ = ('_camouflageId', '_season')

    def __init__(self, camouflageId, season):
        self._camouflageId = camouflageId
        self._season = season

    def getValue(self, vehicle):
        _, still = vehicle.descriptor.computeBaseInvisibility(crewFactor=0, camouflageId=self._camouflageId)
        return still

    def getFormattedValue(self, vehicle):
        return '{:.0%}'.format(self.getValue(vehicle))

    @property
    def icon(self):
        return backport.image(R.images.gui.maps.icons.library.qualifiers.c_42x42.camouflage())

    @property
    def iconSmall(self):
        return backport.image(R.images.gui.maps.icons.library.qualifiers.c_16x16.camouflage())

    @property
    def description(self):
        return backport.text(R.strings.vehicle_customization.bonus.condition.season())

    @property
    def userName(self):
        return backport.text(R.strings.vehicle_customization.bonus.name.extended.camouflage())

    @property
    def shortUserName(self):
        return backport.text(R.strings.vehicle_customization.bonus.name.camouflage())


class Customization(FittingItem):
    __slots__ = ('_boundVehicles', '_bonus', '_installedVehicles', '__noveltyData', '__progressingData', '__installedCount', '__boundInventoryCount', '__fullInventoryCount', '__fullCount')
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, intCompactDescr, proxy=None):
        super(Customization, self).__init__(intCompactDescr, proxy)
        self._inventoryCount = 0
        self._bonus = None
        self._boundVehicles = {}
        self._installedVehicles = {}
        self.__noveltyData = []
        self.__progressingData = {}
        self.__installedCount = None
        self.__boundInventoryCount = None
        self.__fullInventoryCount = None
        self.__fullCount = None
        if proxy is not None and proxy.inventory.isSynced():
            installedVehicles = proxy.inventory.getC11nItemAppliedVehicles(self.intCD)
            invCount = proxy.inventory.getItems(GUI_ITEM_TYPE.CUSTOMIZATION, self.intCD)
            for vehicleCD in installedVehicles:
                self._installedVehicles[vehicleCD] = proxy.inventory.getC11nItemAppliedOnVehicleCount(self.intCD, vehicleCD)

            for vehIntCD, count in invCount.iteritems():
                self._boundVehicles[vehIntCD] = count

            self._inventoryCount = self._boundVehicles.pop(UNBOUND_VEH_KEY, 0)
            self.__noveltyData = proxy.inventory.getC11nItemNoveltyData(intCompactDescr)
            self.__progressingData = proxy.inventory.getC11nProgressionDataForItem(intCompactDescr)
        self._isUnlocked = True
        return

    def __cmp__(self, other):
        return cmp(self.userName, other.userName)

    def __repr__(self):
        return '{}<intCD:{}, id:{}>'.format(self.__class__.__name__, self.intCD, self.id)

    @property
    def id(self):
        return self.descriptor.id

    @property
    def itemTypeName(self):
        return GUI_ITEM_TYPE_NAMES[self.itemTypeID]

    @property
    def itemFullTypeName(self):
        return self.itemTypeName

    @property
    def groupID(self):
        return self.descriptor.parentGroup.itemPrototype.userKey

    @property
    def groupUserName(self):
        return self.descriptor.parentGroup.itemPrototype.userString

    @property
    def userTypeID(self):
        return R.strings.item_types.customization.dyn(self.itemFullTypeName)()

    @property
    def userType(self):
        return backport.text(self.userTypeID)

    @property
    def tags(self):
        return self.descriptor.tags

    @property
    def season(self):
        return self.descriptor.season

    @property
    def seasons(self):
        return [ season for season in SeasonType.SEASONS if season & self.season ]

    @property
    def requiredToken(self):
        return self.descriptor.requiredToken

    @property
    def priceGroup(self):
        return self.descriptor.priceGroup

    @property
    def priceGroupTags(self):
        return self.descriptor.priceGroupTags

    @property
    def bonus(self):
        return self._bonus

    @property
    def texture(self):
        return self.descriptor.texture

    @property
    def icon(self):
        return self.descriptor.texture.replace('gui/', '../', 1)

    @property
    def iconUrl(self):
        return getTextureLinkByID(self.texture)

    @property
    def isVehicleBound(self):
        return ItemTags.VEHICLE_BOUND in self.tags

    @property
    def isLimited(self):
        return self.descriptor.maxNumber > 0

    @property
    def isStyleOnly(self):
        return self.descriptor.isStyleOnly

    @property
    def inventoryCount(self):
        return self._inventoryCount

    def boundInventoryCount(self, vehicleIntCD=None):
        if vehicleIntCD is not None:
            if vehicleIntCD in self._boundVehicles:
                return self._boundVehicles[vehicleIntCD]
            return 0
        else:
            if self.__boundInventoryCount is None:
                self.__boundInventoryCount = sum(self._boundVehicles.itervalues())
            return self.__boundInventoryCount

    def fullInventoryCount(self, vehicleIntCD=None):
        if vehicleIntCD is not None:
            return self.inventoryCount + self.boundInventoryCount(vehicleIntCD)
        else:
            if self.__fullInventoryCount is None:
                self.__fullInventoryCount = self.inventoryCount + self.boundInventoryCount()
            return self.__fullInventoryCount

    def installedCount(self, vehicleIntCD=None):
        if vehicleIntCD is not None:
            if vehicleIntCD in self._installedVehicles:
                return self._installedVehicles[vehicleIntCD]
            return 0
        else:
            if self.__installedCount is None:
                self.__installedCount = sum(self._installedVehicles.itervalues())
            return self.__installedCount

    def fullCount(self, vehicleIntCD=None):
        if vehicleIntCD is not None:
            return self.fullInventoryCount(vehicleIntCD) + self.installedCount(vehicleIntCD)
        else:
            if self.__fullCount is None:
                self.__fullCount = self.fullInventoryCount() + self.installedCount()
            return self.__fullCount

    @property
    def buyCount(self):
        if self.isHidden:
            return 0
        return max(self.descriptor.maxNumber - self.fullCount(), 0) if self.isLimited else float('inf')

    @property
    def mayApply(self):
        return self.inventoryCount > 0 or self.buyCount > 0

    @property
    def specialEventTag(self):
        eventTags = (tag for tag in self.tags if tag in SpecialEvents.ALL)
        return first(eventTags)

    @property
    def specialEventIcon(self):
        return SpecialEvents.ICONS.get(self.specialEventTag, '')

    @property
    def specialEventName(self):
        return SpecialEvents.NAMES.get(self.specialEventTag, '')

    @property
    def isProgressive(self):
        return self.descriptor.progression is not None

    @property
    def isProgressionAutoBound(self):
        return self.descriptor.progression.autobound if self.isProgressive else False

    @property
    def progressionConditions(self):
        return self.descriptor.progression.levels if self.isProgressive else None

    def getIconApplied(self, component):
        return self.icon

    def getInstalledVehicles(self, vehicles=None):
        return set(self._installedVehicles)

    def getBoundVehicles(self):
        return set(self._boundVehicles)

    def isHistorical(self):
        return self.descriptor.historical

    def isDim(self):
        return ItemTags.DIM in self.tags

    def isSummer(self):
        return self.season & SeasonType.SUMMER

    def isWinter(self):
        return self.season & SeasonType.WINTER

    def isDesert(self):
        return self.season & SeasonType.DESERT

    def isAllSeason(self):
        return self.season == SeasonType.ALL

    def isEvent(self):
        return self.season & SeasonType.EVENT

    def mayInstall(self, vehicle, _=None):
        itemFilter = self._descriptor.filter
        return itemFilter is None or itemFilter.matchVehicleType(vehicle.descriptor.type)

    def isWide(self):
        return False

    def isUnlocked(self):
        return bool(self.eventsCache.questsProgress.getTokenCount(self.requiredToken)) if self.requiredToken else True

    def isRare(self):
        return self.descriptor.isRare()

    def isHiddenInUI(self):
        return self.descriptor.isHiddenInUI()

    def getGUIEmblemID(self):
        pass

    def isNew(self):
        return bool(self.__noveltyData)

    def getNoveltyCounter(self, vehicle):
        if not self.mayInstall(vehicle):
            return 0
        return sum([ self.__noveltyData.get(key, 0) for key in (UNBOUND_VEH_KEY, vehicle.intCD) ])

    @staticmethod
    def getSpecialArgs(component):
        return None

    def getMaxProgressionLevel(self):
        return len(self.descriptor.progression.levels) if self.isProgressive else -1

    def getLatestOpenedProgressionLevel(self, vehicle):
        vehProgressData = self.__getCurrentProgressionDataForVehicle(vehicle)
        return vehProgressData.currentLevel if vehProgressData is not None else -1

    def getCurrentProgressOnCurrentLevel(self, vehicle, conditionPath=None):
        if self.isProgressive:
            vehProgressData = self.__getCurrentProgressionDataForVehicle(vehicle)
            if vehProgressData is not None:
                if conditionPath is not None:
                    return vehProgressData.currentProgressOnLevel.get(conditionPath, 0)
                if vehProgressData.currentProgressOnLevel.values():
                    return vehProgressData.currentProgressOnLevel.values()[0]
            return 0
        else:
            return -1

    def getMaxProgressOnCurrentLevel(self, vehicle, conditionPath=None):
        vehProgressData = self.__getCurrentProgressionDataForVehicle(vehicle)
        if vehProgressData is not None:
            if conditionPath is not None:
                return vehProgressData.maxProgressOnLevel.get(conditionPath, -1)
            if vehProgressData.maxProgressOnLevel.values():
                return vehProgressData.maxProgressOnLevel.values()[0]
        return -1

    @staticmethod
    def getTextureByProgressionLevel(baseTexture, progressionLevel):
        path, name = os.path.split(baseTexture)
        name, ext = os.path.splitext(name)
        basePart, delimiter, _ = name.rpartition('_')
        if not basePart:
            _logger.error('Wrong name of texture for progression customization item (texture name is "%s" )', baseTexture)
            return ''
        name = basePart + delimiter + str(progressionLevel)
        texture = path + '/' + name + ext
        if not ResMgr.isFile(texture):
            _logger.error('Failed to get texture by progression level. Base texture %s; level: %s', baseTexture, progressionLevel)
            return ''
        return texture

    def getUsedProgressionLevel(self, component, vehicle=None):
        if self.isProgressive and component:
            progressionLevel = component.progressionLevel
            if progressionLevel == 0:
                progressionLevel = self.getLatestOpenedProgressionLevel(g_currentVehicle.item if vehicle is None else vehicle)
            return progressionLevel
        else:
            return -1

    def iconByProgressionLevel(self, progressionLevel):
        return self.getTextureByProgressionLevel(self.texture, progressionLevel).replace('gui/', '../', 1) if self.isProgressive else None

    def iconUrlByProgressionLevel(self, progressionLevel):
        return getTextureLinkByID(self.getTextureByProgressionLevel(self.texture, progressionLevel)) if self.isProgressive else None

    def iconResourceByProgressionLevel(self, progressionLevel):
        return getImageResourceFromPath(self.getTextureByProgressionLevel(self.texture, progressionLevel)) if self.isProgressive else None

    def availableForPurchaseProgressive(self, vehicle):
        if self.isHidden:
            return 0
        elif self.isProgressionAutoBound and vehicle is not None:
            availableSlotsCount = cc.getAvailableSlotsCount(self.descriptor, vehicle.descriptor) * len(SeasonType.COMMON_SEASONS)
            installed = self.installedCount(vehicle.intCD)
            bounded = self.boundInventoryCount(vehicle.intCD)
            availableToBuy = availableSlotsCount - installed - bounded
            return max(0, availableToBuy)
        else:
            return float('inf')

    def __getCurrentProgressionDataForVehicle(self, vehicle):
        if self.isProgressive and self.__progressingData is not None:
            if vehicle.intCD in self.__progressingData:
                return self.__progressingData[vehicle.intCD]
            if UNBOUND_VEH_KEY in self.__progressingData and self.mayInstall(vehicle):
                return self.__progressingData[UNBOUND_VEH_KEY]
        return


class Paint(Customization):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(Paint, self).__init__(*args, **kwargs)
        self.itemTypeID = GUI_ITEM_TYPE.PAINT

    @property
    def color(self):
        return self.descriptor.color

    @property
    def gloss(self):
        return self.descriptor.gloss

    @property
    def metallic(self):
        return self.descriptor.metallic


class Camouflage(Customization):
    __slots__ = ('_bonus',)

    def __init__(self, *args, **kwargs):
        super(Camouflage, self).__init__(*args, **kwargs)
        self.itemTypeID = GUI_ITEM_TYPE.CAMOUFLAGE
        self._bonus = ConcealmentBonus(camouflageId=self.id, season=self.season)

    @property
    def imageOptions(self):
        options = ImageOptions.NONE
        options |= self.isFullRGB and ImageOptions.FULL_RGB
        return options

    @property
    def icon(self):
        return camoIconTemplate(texture=self.texture, width=_CAMO_SWATCH_WIDTH, height=_CAMO_SWATCH_HEIGHT, colors=first(self.palettes), options=self.imageOptions)

    @property
    def iconUrl(self):
        return camoIconUrl(texture=self.texture, width=_CAMO_SWATCH_WIDTH, height=_CAMO_SWATCH_HEIGHT, colors=first(self.palettes), options=self.imageOptions)

    def getIconApplied(self, component):
        if component:
            palette = self.palettes[component.palette]
        else:
            palette = first(self.palettes)
        return camoIconTemplate(texture=self.texture, width=_CAMO_SWATCH_WIDTH, height=_CAMO_SWATCH_HEIGHT, colors=palette, options=self.imageOptions)

    @property
    def tiling(self):
        return self.descriptor.tiling

    @property
    def tilingSettings(self):
        return self.descriptor.tilingSettings

    @property
    def rotation(self):
        return self.descriptor.rotation

    @property
    def scales(self):
        return self.descriptor.scales

    @property
    def palettes(self):
        return self.descriptor.palettes

    @property
    def isFullRGB(self):
        return ItemTags.FULL_RGB in self.tags

    @staticmethod
    def getSpecialArgs(component):
        return [component.id,
         component.patternSize,
         component.appliedTo,
         component.palette]


class Modification(Customization):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(Modification, self).__init__(*args, **kwargs)
        self.itemTypeID = GUI_ITEM_TYPE.MODIFICATION

    def modValue(self, modType, default=0.0):
        return self.descriptor.getEffectValue(modType, default=default)

    @property
    def effects(self):
        return self.descriptor.effects

    def isWide(self):
        return True


class Decal(Customization):
    __slots__ = ()

    @property
    def canBeMirrored(self):
        return self.descriptor.canBeMirrored


class Emblem(Decal):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(Emblem, self).__init__(*args, **kwargs)
        self.itemTypeID = GUI_ITEM_TYPE.EMBLEM


class Inscription(Decal):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(Inscription, self).__init__(*args, **kwargs)
        self.itemTypeID = GUI_ITEM_TYPE.INSCRIPTION

    def isWide(self):
        return True


class Insignia(Customization):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(Insignia, self).__init__(*args, **kwargs)
        self.itemTypeID = GUI_ITEM_TYPE.INSIGNIA

    @property
    def atlas(self):
        return self.descriptor.atlas

    @property
    def alphabet(self):
        return self.descriptor.alphabet

    @property
    def canBeMirrored(self):
        return self.descriptor.canBeMirrored


class ProjectionDecal(Decal):
    __slots__ = ('__previewIcon',)

    def __init__(self, *args, **kwargs):
        super(ProjectionDecal, self).__init__(*args, **kwargs)
        self.itemTypeID = GUI_ITEM_TYPE.PROJECTION_DECAL
        self.__previewIcon = ''

    @property
    def direction(self):
        directionTags = (tag for tag in self.tags if tag.startswith(ProjectionDecalDirectionTags.PREFIX))
        return first(directionTags, ProjectionDecalDirectionTags.ANY)

    @property
    def formfactor(self):
        formTags = (tag for tag in self.tags if tag.startswith(ProjectionDecalFormTags.PREFIX))
        return first(formTags)

    @property
    def canBeMirroredHorizontally(self):
        return self.descriptor.canBeMirroredHorizontally

    @property
    def previewIcon(self):
        if not self.__previewIcon:
            self.__previewIcon = self.__getPreviewIcon(self.texture)
        return self.__previewIcon

    @property
    def previewIconUrl(self):
        return getTextureLinkByID(self.previewIcon)

    @property
    def previewIconRes(self):
        return getImageResourceFromPath(self.previewIcon)

    @property
    def icon(self):
        texture, size, innerSize = self.__getPreviewParams()
        return previewTemplate(texture, size[0], size[1], innerSize[0], innerSize[1])

    @property
    def iconUrl(self):
        texture, size, innerSize = self.__getPreviewParams()
        return previewUrl(texture, size[0], size[1], innerSize[0], innerSize[1])

    def previewIconByProgressionLevel(self, level):
        if not self.isProgressive:
            return self.previewIcon
        icon = self.getTextureByProgressionLevel(self.texture, level)
        return self.__getPreviewIcon(icon)

    def previewIconUrlByProgressionLevel(self, level):
        if not self.isProgressive:
            return self.previewIconUrl
        previewIcon = self.previewIconByProgressionLevel(level)
        return getTextureLinkByID(previewIcon)

    def previewIconResByProgressionLevel(self, level):
        if not self.isProgressive:
            return self.previewIconRes
        previewIcon = self.previewIconByProgressionLevel(level)
        return getImageResourceFromPath(previewIcon)

    def iconByProgressionLevel(self, level, size=None, innerSize=None):
        if not self.isProgressive:
            return self.icon
        texture, size, innerSize = self.__getPreviewParams(level, size, innerSize)
        return previewTemplate(texture, size[0], size[1], innerSize[0], innerSize[1])

    def iconUrlByProgressionLevel(self, level, size=None, innerSize=None):
        if not self.isProgressive:
            return self.iconUrl
        texture, size, innerSize = self.__getPreviewParams(level, size, innerSize)
        return previewUrl(texture, size[0], size[1], innerSize[0], innerSize[1])

    def isWide(self):
        return True

    def __getPreviewParams(self, level=None, size=None, innerSize=None):
        texture = self.getTextureByProgressionLevel(self.texture, level) if level is not None else self.texture
        size = size or _PREVIEW_ICON_SIZE
        innerSize = innerSize or _PREVIEW_ICON_INNER_SIZE.get(self.formfactor, _PREVIEW_ICON_INNER_SIZE_DEFAULT)
        return (texture, size, innerSize)

    @staticmethod
    def __getPreviewIcon(icon):
        f, _ = os.path.splitext(icon)
        iconPath = '{}_preview.png'.format(f)
        return iconPath if ResMgr.isFile(iconPath) else icon


class PersonalNumber(Customization):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(PersonalNumber, self).__init__(*args, **kwargs)
        self.itemTypeID = GUI_ITEM_TYPE.PERSONAL_NUMBER

    @property
    def previewTexture(self):
        return self.descriptor.previewTexture

    @property
    def digitsCount(self):
        return self.descriptor.digitsCount

    @property
    def fontInfo(self):
        return self.descriptor.fontInfo

    @property
    def isMirrored(self):
        return self.descriptor.isMirrored

    def getIconApplied(self, component):
        return self.descriptor.previewTexture.replace('gui/', '../', 1)

    def isWide(self):
        return True

    def numberIcon(self, number=''):
        return super(PersonalNumber, self).icon if not number else personalNumIconTemplate(number, _PN_SWATCH_WIDTH, _PN_SWATCH_HEIGHT, self.fontInfo.texture, self.fontInfo.alphabet, self.fontInfo.mask)

    @property
    def itemFullTypeName(self):
        return self.itemTypeName + '_' + str(self.digitsCount)

    def numberIconUrl(self, number=''):
        return self.iconUrl if not number else personalNumIconUrl(number, _PN_SWATCH_WIDTH, _PN_SWATCH_HEIGHT, self.fontInfo.texture, self.fontInfo.alphabet, self.fontInfo.mask)


class Sequence(Customization):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(Sequence, self).__init__(*args, **kwargs)
        self.itemTypeID = GUI_ITEM_TYPE.SEQUENCE

    @property
    def sequenceName(self):
        return self.descriptor.sequenceName


class Attachment(Customization):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(Attachment, self).__init__(*args, **kwargs)
        self.itemTypeID = GUI_ITEM_TYPE.ATTACHMENT

    @property
    def modelName(self):
        return self.descriptor.modelName

    @property
    def sequenceId(self):
        return self.descriptor.sequenceId

    @property
    def attachmentLogic(self):
        return self.descriptor.attachmentLogic

    @property
    def initialVisibility(self):
        return self.descriptor.initialVisibility


class Style(Customization):
    __slots__ = ('_changableTypes', '_service', '_itemsCache', '__outfits')
    _service = dependency.descriptor(ICustomizationService)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, intCompactDescr, proxy=None):
        super(Style, self).__init__(intCompactDescr, proxy)
        self.itemTypeID = GUI_ITEM_TYPE.STYLE
        self._changableTypes = None
        self.__outfits = {}
        return

    @property
    def isEditable(self):
        return self.descriptor.isEditable

    @property
    def isRentable(self):
        return self.descriptor.isRent

    @property
    def isRented(self):
        return False if not self.isRentable else bool(self.boundInventoryCount())

    @property
    def isProgressionRequired(self):
        return ItemTags.PROGRESSION_REQUIRED in self.tags

    @property
    def rentCount(self):
        return self.descriptor.rentCount if self.isRentable else 0

    @property
    def modelsSet(self):
        return self.descriptor.modelsSet

    @property
    def userTypeID(self):
        return getStyleGroupNameResourceID(self.groupID)

    @property
    def userType(self):
        return backport.text(self.userTypeID)

    @property
    def alternateItems(self):
        items = []
        for itemType, ids in self.descriptor.alternateItems.iteritems():
            for itemId in ids:
                compactDescr = makeIntCompactDescrByID('customizationItem', itemType, itemId)
                items.append(self._service.getItemByCD(compactDescr))

        return items

    @property
    def changeableSlotTypes(self):
        return self.descriptor.changeableSlotTypes

    def getDescription(self):
        return self.longDescriptionSpecial or self.fullDescription or self.shortDescriptionSpecial or self.shortDescription

    def getRentInfo(self, vehicle):
        if not self.isRentable:
            return RentalInfoProvider()
        battlesLeft = self.boundInventoryCount(vehicle.intCD)
        return RentalInfoProvider(battles=battlesLeft)

    def getOutfit(self, season, vehicleCD='', diff=None):
        if diff is not None:
            return self.__createOutfit(season, vehicleCD, diff)
        else:
            if season not in self.__outfits or self.__outfits[season].vehicleCD != vehicleCD:
                self.__outfits[season] = self.__createOutfit(season, vehicleCD)
            return self.__outfits[season].copy()

    def isWide(self):
        return True

    def canBeEditedForVehicle(self, vehicleIntCD):
        if not self.isEditable:
            return False
        if not self.isProgressionRequired:
            return True
        progressionStorage = self._itemsCache.items.inventory.getC11nProgressionDataForVehicle(vehicleIntCD)
        for itemIntCD, progressionData in progressionStorage.iteritems():
            if not progressionData.currentLevel:
                continue
            item = self._service.getItemByCD(itemIntCD)
            if self.descriptor.isItemInstallable(item.descriptor):
                return True

        return False

    def isProgressionRequiredCanBeEdited(self, vehicleIntCD):
        return self.isProgressionRequired and self.canBeEditedForVehicle(vehicleIntCD)

    def isEditedForVehicle(self, vehicleIntCD):
        c11nCtx = self._service.getCtx()
        if c11nCtx is not None and vehicleIntCD == g_currentVehicle.item.intCD:
            diffs = c11nCtx.stylesDiffsCache.getDiffs(self)
            for diff in diffs.itervalues():
                if diff is not None and isEditedStyle(parseCompDescr(diff)):
                    return True

        else:
            outfitsPool = self._itemsCache.items.inventory.getC11nOutfitsFromPool(vehicleIntCD)
            for styleId, _ in outfitsPool:
                if styleId == self.id:
                    return True

        return False

    def __createOutfit(self, season, vehicleCD='', diff=None):
        component = deepcopy(self.descriptor.outfits[season])
        if vehicleCD and ItemTags.ADD_NATIONAL_EMBLEM in self.tags:
            vehDescr = VehicleDescr(vehicleCD)
            emblems = createNationalEmblemComponents(vehDescr)
            component.decals.extend(emblems)
        if diff is not None:
            diffComponent = parseCompDescr(diff)
            if component.styleId != diffComponent.styleId:
                _logger.error('Merging outfits of different styles is not allowed. ID1: %s ID2: %s', component.styleId, diffComponent.styleId)
            else:
                component = component.applyDiff(diffComponent)
        return self.itemsFactory.createOutfit(component=component, vehicleCD=vehicleCD)
