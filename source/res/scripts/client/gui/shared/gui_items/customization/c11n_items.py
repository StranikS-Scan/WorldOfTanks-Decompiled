# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/customization/c11n_items.py
import os
from collections import defaultdict
import Math
import ResMgr
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.shared.gui_items import GUI_ITEM_TYPE_NAMES, GUI_ITEM_TYPE
from gui.shared.gui_items.fitting_item import FittingItem, RentalInfoProvider
from helpers import i18n, dependency
from items.components.c11n_constants import SeasonType, ItemTags, ProjectionDecalDirectionTags, ProjectionDecalFormTags, UNBOUND_VEH_KEY, NUM_ALL_ITEMS_KEY
from shared_utils import first
from skeletons.gui.server_events import IEventsCache
_CAMO_ICON_TEMPLATE = 'img://camouflage,{width},{height},"{texture}","{background}",{colors},{weights}'
_CAMO_SWATCH_WIDTH = 128
_CAMO_SWATCH_HEIGHT = 128
_PN_SWATCH_WIDTH = 228
_PN_SWATCH_HEIGHT = 104
_CAMO_SWATCH_BACKGROUND = 'gui/maps/vehicles/camouflages/camo_back.dds'
_PERSONAL_NUM_ICON_TEMPLATE = 'img://personal_num,{width},{height},"{texture}","{alphabet}","{number}","{textureMask}","{background}"'
_PERSONAL_NUM_ICON_TEMPLATE = 'img://personal_num,{width},{height},"{texture}","{fontPath}","{number}","{textureMask}","{background}"'
STYLE_GROUP_ID_TO_GROUP_NAME_MAP = {VEHICLE_CUSTOMIZATION.STYLES_SPECIAL_STYLES: VEHICLE_CUSTOMIZATION.CUSTOMIZATION_INFOTYPE_TYPE_STYLE_SPECIAL,
 VEHICLE_CUSTOMIZATION.STYLES_MAIN_STYLES: VEHICLE_CUSTOMIZATION.CUSTOMIZATION_INFOTYPE_TYPE_STYLE_MAIN,
 VEHICLE_CUSTOMIZATION.STYLES_RENTED_STYLES: VEHICLE_CUSTOMIZATION.CUSTOMIZATION_INFOTYPE_TYPE_STYLE_RENTAL,
 VEHICLE_CUSTOMIZATION.STYLES_UNIQUE_STYLES: VEHICLE_CUSTOMIZATION.CUSTOMIZATION_INFOTYPE_TYPE_STYLE_UNIQUE,
 VEHICLE_CUSTOMIZATION.STYLES_HISTORICAL_STYLES: VEHICLE_CUSTOMIZATION.CUSTOMIZATION_INFOTYPE_TYPE_STYLE_HISTORICAL}
STYLE_GROUP_ID_TO_FULL_GROUP_NAME_MAP = {VEHICLE_CUSTOMIZATION.STYLES_SPECIAL_STYLES: VEHICLE_CUSTOMIZATION.CAROUSEL_SWATCH_STYLE_SPECIAL,
 VEHICLE_CUSTOMIZATION.STYLES_MAIN_STYLES: VEHICLE_CUSTOMIZATION.CAROUSEL_SWATCH_STYLE_MAIN,
 VEHICLE_CUSTOMIZATION.STYLES_RENTED_STYLES: VEHICLE_CUSTOMIZATION.CAROUSEL_SWATCH_STYLE_RENTED,
 VEHICLE_CUSTOMIZATION.STYLES_UNIQUE_STYLES: VEHICLE_CUSTOMIZATION.CAROUSEL_SWATCH_STYLE_UNIQUE,
 VEHICLE_CUSTOMIZATION.STYLES_HISTORICAL_STYLES: VEHICLE_CUSTOMIZATION.CAROUSEL_SWATCH_STYLE_HISTORICAL}

def camoIconTemplate(texture, width, height, colors, background=_CAMO_SWATCH_BACKGROUND):
    weights = Math.Vector4(*[ (color >> 24) / 255.0 for color in colors ])
    return _CAMO_ICON_TEMPLATE.format(width=width, height=height, texture=texture, background=background, colors=','.join((str(color) for color in colors)), weights=','.join((str(weight) for weight in weights)))


def personalNumIconTemplate(number, width, height, texture, fontPath, textureMask='', background=''):
    return _PERSONAL_NUM_ICON_TEMPLATE.format(width=width, height=height, number=number, texture=texture, textureMask=textureMask, fontPath=fontPath, background=background)


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
        return RES_ICONS.getItemBonus42x42('camouflage')

    @property
    def iconSmall(self):
        return RES_ICONS.getItemBonus16x16('camouflage')

    @property
    def description(self):
        return i18n.makeString(VEHICLE_CUSTOMIZATION.BONUS_CONDITION_SEASON)

    @property
    def userName(self):
        return i18n.makeString(VEHICLE_CUSTOMIZATION.getBonusName('camouflage'))

    @property
    def shortUserName(self):
        return i18n.makeString(VEHICLE_CUSTOMIZATION.getShortBonusName('camouflage'))


class Customization(FittingItem):
    __slots__ = ('_boundInventoryCount', '_bonus', '_installedVehicles')
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
    def groupID(self):
        return self.descriptor.parentGroup.itemPrototype.userKey

    @property
    def groupUserName(self):
        return self.descriptor.parentGroup.itemPrototype.userString

    @property
    def userType(self):
        return i18n.makeString(ITEM_TYPES.customization(self.itemTypeName))

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
    def icon(self):
        return self.descriptor.texture.replace('gui/', '../', 1)

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

    def getIconApplied(self, component):
        return self.icon

    def getInstalledVehicles(self, vehs=None):
        return [ vehicleCD for vehicleCD, count in self._installedVehicles.items() if count > 0 ]

    def getInstalledOnVehicleCount(self, vehicleIntCD):
        return self._installedVehicles[vehicleIntCD]

    def isHistorical(self):
        return self.descriptor.historical

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

    def __init__(self, *args, **kwargs):
        super(Camouflage, self).__init__(*args, **kwargs)
        self.itemTypeID = GUI_ITEM_TYPE.CAMOUFLAGE
        self._bonus = ConcealmentBonus(camouflageId=self.id, season=self.season)

    @property
    def texture(self):
        return self.descriptor.texture

    @property
    def icon(self):
        return camoIconTemplate(self.texture, _CAMO_SWATCH_WIDTH, _CAMO_SWATCH_HEIGHT, first(self.palettes))

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

    @property
    def texture(self):
        return self.descriptor.texture

    @property
    def canBeMirrored(self):
        return self.descriptor.canBeMirrored


class Emblem(Decal):

    def __init__(self, *args, **kwargs):
        super(Emblem, self).__init__(*args, **kwargs)
        self.itemTypeID = GUI_ITEM_TYPE.EMBLEM


class Inscription(Decal):

    def __init__(self, *args, **kwargs):
        super(Inscription, self).__init__(*args, **kwargs)
        self.itemTypeID = GUI_ITEM_TYPE.INSCRIPTION

    def isWide(self):
        return True


class Insignia(Customization):

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
    def texture(self):
        return self.descriptor.texture

    @property
    def canBeMirrored(self):
        return self.descriptor.canBeMirrored


class ProjectionDecal(Decal):

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
        return first(formTags, ProjectionDecalFormTags.ANY)

    @property
    def icon(self):
        path = self.descriptor.texture
        f, _ = os.path.splitext(path)
        iconPath = '{}_preview.{}'.format(f, 'png')
        return iconPath.replace('gui/', '../', 1) if ResMgr.isFile(iconPath) else path.replace('gui/', '../', 1)

    def isWide(self):
        return True


class PersonalNumber(Customization):

    def __init__(self, *args, **kwargs):
        super(PersonalNumber, self).__init__(*args, **kwargs)
        self.itemTypeID = GUI_ITEM_TYPE.PERSONAL_NUMBER

    @property
    def texture(self):
        return self.descriptor.texture

    @property
    def previewTexture(self):
        return self.descriptor.previewTexture

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
        return super(PersonalNumber, self).icon if number == '' else personalNumIconTemplate(number, _PN_SWATCH_WIDTH, _PN_SWATCH_HEIGHT, self.fontInfo.texture, self.fontInfo.alphabet, self.fontInfo.mask)


class Sequence(Customization):

    def __init__(self, *args, **kwargs):
        super(Sequence, self).__init__(*args, **kwargs)
        self.itemTypeID = GUI_ITEM_TYPE.SEQUENCE

    @property
    def sequenceName(self):
        return self.descriptor.sequenceName


class Attachment(Customization):

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
    def userType(self):
        return i18n.makeString(STYLE_GROUP_ID_TO_GROUP_NAME_MAP[self.groupID])

    @property
    def textInfo(self):
        return self.descriptor.textInfo

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
