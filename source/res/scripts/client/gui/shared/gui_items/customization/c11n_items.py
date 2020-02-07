# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/customization/c11n_items.py
import os
import urllib
from collections import defaultdict
import Math
import ResMgr
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items import GUI_ITEM_TYPE_NAMES, GUI_ITEM_TYPE
from gui.shared.gui_items.fitting_item import FittingItem, RentalInfoProvider
from gui.shared.image_helper import getTextureLinkByID
from helpers import dependency
from items.components.c11n_constants import SeasonType, ItemTags, ProjectionDecalDirectionTags, ProjectionDecalFormTags, UNBOUND_VEH_KEY, NUM_ALL_ITEMS_KEY
from shared_utils import first
from skeletons.gui.server_events import IEventsCache
_CAMO_ICON_TEMPLATE = 'img://camouflage,{width},{height},"{texture}","{background}",{colors},{weights}'
_CAMO_ICON_URL = 'camo://{texture}?{params}'
_CAMO_SWATCH_WIDTH = 128
_CAMO_SWATCH_HEIGHT = 128
_CAMO_SWATCH_BACKGROUND = 'gui/maps/vehicles/camouflages/camo_back.dds'
_PERSONAL_NUM_ICON_TEMPLATE = 'img://personal_num,{width},{height},"{texture}","{fontPath}","{number}","{textureMask}","{background}"'
_PERSONAL_NUM_ICON_URL = 'pnum://{texture}?{params}'
_PN_SWATCH_WIDTH = 228
_PN_SWATCH_HEIGHT = 104
_PREVIEW_ICON_TEMPLATE = 'img://preview_icon,{width},{height},{innerWidth},{innerHeight},"{texture}"'
_PREVIEW_ICON_OUTSIDE_SIZE_WIDTH = 226
_PREVIEW_ICON_OUTSIDE_SIZE_HEIGHT = 102
_PREVIEW_ICON_INNER_SIZE_BY_DEFAULT = (74, 74)
_PREVIEW_ICON_INNER_SIZE_BY_FORMFACTOR = {'formfactor_square': (74, 74),
 'formfactor_rect1x2': (174, 87),
 'formfactor_rect1x3': (186, 62),
 'formfactor_rect1x4': (220, 55),
 'formfactor_rect1x6': (220, 37)}
_STYLE_GROUP_ID_TO_GROUP_NAME_MAP = {}
_STYLE_GROUP_ID_TO_FULL_GROUP_NAME_MAP = {}

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


def camoIconTemplate(texture, width, height, colors, background=_CAMO_SWATCH_BACKGROUND):
    weights = Math.Vector4(*[ (color >> 24) / 255.0 for color in colors ])
    return _CAMO_ICON_TEMPLATE.format(width=width, height=height, texture=texture, background=background, colors=','.join((str(color) for color in colors)), weights=','.join((str(weight) for weight in weights)))


def camoIconUrl(texture, width, height, colors, background=_CAMO_SWATCH_BACKGROUND):
    weights = Math.Vector4(*[ (color >> 24) / 255.0 for color in colors ])
    params = {'back': background,
     'w': width,
     'h': height,
     'r': colors[0],
     'g': colors[1],
     'b': colors[2],
     'a': colors[3],
     'rw': weights[0],
     'gw': weights[1],
     'bw': weights[2],
     'aw': weights[3]}
    return _CAMO_ICON_URL.format(texture=texture, params=urllib.urlencode(params))


def personalNumIconTemplate(number, width, height, texture, fontPath, textureMask='', background=''):
    return _PERSONAL_NUM_ICON_TEMPLATE.format(width=width, height=height, number=number, texture=texture, textureMask=textureMask, fontPath=fontPath, background=background)


def previewTemplate(texture, width, height, innerWidth, innerHeight):
    return _PREVIEW_ICON_TEMPLATE.format(width=width, height=height, texture=texture, innerWidth=innerWidth, innerHeight=innerHeight)


def personalNumIconUrl(number, width, height, texture, fontPath, textureMask='', background=''):
    params = {'num': number,
     'w': width,
     'h': height,
     'font': fontPath,
     'mask': textureMask,
     'back': background}
    return _PERSONAL_NUM_ICON_URL.format(texture=texture, params=urllib.urlencode(params))


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
    __slots__ = ('_boundInventoryCount', '_bonus', '_installedVehicles', '__noveltyData')
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, intCompactDescr, proxy=None):
        super(Customization, self).__init__(intCompactDescr, proxy)
        self._inventoryCount = 0
        self._boundInventoryCount = {}
        self._bonus = None
        self._installedVehicles = defaultdict(int)
        self.__noveltyData = []
        if proxy is not None and proxy.inventory.isSynced():
            installledVehicles = proxy.inventory.getC11nItemAppliedVehicles(self.intCD)
            invCount = proxy.inventory.getItems(GUI_ITEM_TYPE.CUSTOMIZATION, self.intCD)
            for vehicleCD in installledVehicles:
                self._installedVehicles[vehicleCD] = proxy.inventory.getC11nItemAppliedOnVehicleCount(self.intCD, vehicleCD)

            for vehIntCD, count in invCount.iteritems():
                self._boundInventoryCount[vehIntCD] = count

            self.__noveltyData = proxy.inventory.getC11nItemNoveltyData(intCompactDescr)
        self._inventoryCount = self.boundInventoryCount.pop(UNBOUND_VEH_KEY, 0)
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
    def boundInventoryCount(self):
        return self._boundInventoryCount

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
    def buyCount(self):
        if self.isHidden:
            return 0
        return max(self.descriptor.maxNumber - self.boundInventoryCount.get(NUM_ALL_ITEMS_KEY, 0), 0) if self.isLimited else float('inf')

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

    def getIconApplied(self, component):
        return self.icon

    def getInstalledVehicles(self, vehs=None):
        return [ vehicleCD for vehicleCD, count in self._installedVehicles.items() if count > 0 ]

    def getInstalledOnVehicleCount(self, vehicleIntCD):
        return self._installedVehicles[vehicleIntCD]

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

    def fullInventoryCount(self, vehicle):
        return self.inventoryCount + self.boundInventoryCount.get(vehicle.intCD, 0)

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
    def icon(self):
        return camoIconTemplate(self.texture, _CAMO_SWATCH_WIDTH, _CAMO_SWATCH_HEIGHT, first(self.palettes))

    @property
    def iconUrl(self):
        return camoIconUrl(self.texture, _CAMO_SWATCH_WIDTH, _CAMO_SWATCH_HEIGHT, first(self.palettes))

    def getIconApplied(self, component):
        if component:
            palette = self.palettes[component.palette]
        else:
            palette = first(self.palettes)
        return camoIconTemplate(self.texture, _CAMO_SWATCH_WIDTH, _CAMO_SWATCH_HEIGHT, palette)

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
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(ProjectionDecal, self).__init__(*args, **kwargs)
        self.itemTypeID = GUI_ITEM_TYPE.PROJECTION_DECAL

    @property
    def direction(self):
        directionTags = (tag for tag in self.tags if tag.startswith(ProjectionDecalDirectionTags.PREFIX))
        return first(directionTags, ProjectionDecalDirectionTags.ANY)

    @property
    def formfactor(self):
        formTags = (tag for tag in self.tags if tag.startswith(ProjectionDecalFormTags.PREFIX))
        return first(formTags)

    @property
    def icon(self):
        innerSize = _PREVIEW_ICON_INNER_SIZE_BY_FORMFACTOR.get(self.formfactor, _PREVIEW_ICON_INNER_SIZE_BY_DEFAULT)
        return previewTemplate(self.texture, _PREVIEW_ICON_OUTSIDE_SIZE_WIDTH, _PREVIEW_ICON_OUTSIDE_SIZE_HEIGHT, innerSize[0], innerSize[1])

    @property
    def iconUrl(self):
        path = self.descriptor.texture
        path = self._getPreviewIcon(path)
        return getTextureLinkByID(path)

    def isWide(self):
        return True

    @staticmethod
    def _getPreviewIcon(icon):
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


class Style(Customization):
    __slots__ = ('_outfits',)

    def __init__(self, intCompactDescr, proxy=None):
        super(Style, self).__init__(intCompactDescr, proxy)
        self.itemTypeID = GUI_ITEM_TYPE.STYLE
        self._outfits = {}

    @property
    def isRentable(self):
        return self.descriptor.isRent

    @property
    def isRented(self):
        return False if not self.isRentable else bool(self.boundInventoryCount)

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

    def getDescription(self):
        return self.longDescriptionSpecial or self.fullDescription or self.shortDescriptionSpecial or self.shortDescription

    def getRentInfo(self, vehicle):
        if not self.isRentable:
            return RentalInfoProvider()
        battlesLeft = self.boundInventoryCount.get(vehicle.descriptor.type.compactDescr, 0)
        return RentalInfoProvider(battles=battlesLeft)

    def getOutfit(self, season):
        component = self.descriptor.outfits[season]
        self._outfits[season] = self.itemsFactory.createOutfit(component=component)
        return self._outfits.get(season)

    def isWide(self):
        return True
