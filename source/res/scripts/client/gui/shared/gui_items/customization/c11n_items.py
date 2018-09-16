# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/customization/c11n_items.py
import Math
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.shared.gui_items import GUI_ITEM_TYPE_NAMES, GUI_ITEM_TYPE
from gui.shared.gui_items.fitting_item import FittingItem, RentalInfoProvider
from gui.shared.gui_items.Vehicle import Vehicle
from helpers import i18n, dependency
from items.components.c11n_constants import SeasonType, ModificationType
from shared_utils import first
from skeletons.gui.server_events import IEventsCache
_UNBOUND_VEH = 0
_CAMO_ICON_TEMPLATE = 'img://camouflage,{width},{height},"{texture}","{background}",{colors},{weights}'
_CAMO_SWATCH_WIDTH = 128
_CAMO_SWATCH_HEIGHT = 128
_CAMO_SWATCH_BACKGROUND = 'gui/maps/vehicles/camouflages/camo_back.dds'

def camoIconTemplate(texture, width, height, colors, background=_CAMO_SWATCH_BACKGROUND):
    """ Fill the _CAMO_ICON_TEMPLATE (in order to dynamically generate camo image)
    """
    weights = Math.Vector4(*[ (color >> 24) / 255.0 for color in colors ])
    return _CAMO_ICON_TEMPLATE.format(width=width, height=height, texture=texture, background=background, colors=','.join((str(color) for color in colors)), weights=','.join((str(weight) for weight in weights)))


class ConcealmentBonus(object):
    """ Concealment bonus that camouflage gives to a vehicle.
    
    We don't have generic bonus system at the moment (stage 1), this class
    only supports the existing camouflage concealment bonus.
    """
    __slots__ = ('_camouflageId', '_season')

    def __init__(self, camouflageId, season):
        self._camouflageId = camouflageId
        self._season = season

    def getValue(self, vehicle):
        """ Get concealment value that the camouflage gives to the given vehicle.
        """
        _, still = vehicle.descriptor.computeBaseInvisibility(crewFactor=0, camouflageId=self._camouflageId)
        return still

    def getFormattedValue(self, vehicle):
        """ Get concealment percent that the camouflage gives to the given vehicle.
        """
        return '{:.0%}'.format(self.getValue(vehicle))

    @property
    def icon(self):
        """ Returns bonuses's icon path.
        """
        return RES_ICONS.getItemBonus42x42('camouflage')

    @property
    def iconSmall(self):
        """ Returns bonuses's small icon path.
        """
        return RES_ICONS.getItemBonus16x16('camouflage')

    @property
    def description(self):
        return i18n.makeString(VEHICLE_CUSTOMIZATION.BONUS_CONDITION_SEASON)

    @property
    def userName(self):
        """ Returns bonus's name represented as user-readable string.
        """
        return i18n.makeString(VEHICLE_CUSTOMIZATION.getBonusName('camouflage'))

    @property
    def shortUserName(self):
        """ Returns bonus's short name represented as user-readable string.
        """
        return i18n.makeString(VEHICLE_CUSTOMIZATION.getShortBonusName('camouflage'))


class Customization(FittingItem):
    """ Base customization item.
    """
    __slots__ = ('_boundInventoryCount', '_bonus')
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, intCompactDescr, proxy=None):
        super(Customization, self).__init__(intCompactDescr, proxy)
        self._inventoryCount = 0
        self._boundInventoryCount = {}
        self._bonus = None
        if proxy and proxy.inventory.isSynced():
            invCount = proxy.inventory.getItems(GUI_ITEM_TYPE.CUSTOMIZATION, self.intCD)
            for vehIntCD, count in invCount.iteritems():
                self._boundInventoryCount[vehIntCD] = count

        self._inventoryCount = self.boundInventoryCount.pop(_UNBOUND_VEH, 0)
        self._isUnlocked = True
        return

    def __cmp__(self, other):
        """ Defines a set of rules items should be sorted with.
        """
        return cmp(self.userName, other.userName)

    def __repr__(self):
        return '{}<intCD:{}, id:{}>'.format(self.__class__.__name__, self.intCD, self.id)

    @property
    def id(self):
        """ Unique item id across its type.
        """
        return self.descriptor.id

    @property
    def itemTypeName(self):
        """ Overridden item type (since gui item type differ from common item type)
        """
        return GUI_ITEM_TYPE_NAMES[self.itemTypeID]

    @property
    def groupID(self):
        """ Group id
        """
        return self.descriptor.parentGroup.itemPrototype.userKey

    @property
    def groupUserName(self):
        """ User readable group name
        """
        return self.descriptor.parentGroup.itemPrototype.userString

    @property
    def userType(self):
        """ User readable item type name.
        """
        return i18n.makeString(ITEM_TYPES.customization(self.itemTypeName))

    @property
    def boundInventoryCount(self):
        """ Inventory count bound to vehicles.
        """
        return self._boundInventoryCount

    @property
    def tags(self):
        """ Item's tags (e.g. notInShop, vehicleBound, levelBasedPrice, etc.).
        """
        return self.descriptor.tags

    @property
    def season(self):
        """ Returns an integer that describes seasons the item can be applied on (see SeasonType).
        """
        return self.descriptor.season

    @property
    def seasons(self):
        """ Returns a list of primitive seasons the item can be applied on.
        """
        return [ season for season in SeasonType.SEASONS if season & self.season ]

    @property
    def requiredToken(self):
        """ Returns token required to unlock customization.
        """
        return self.descriptor.requiredToken

    @property
    def priceGroup(self):
        """ Returns price group name of the item.
        """
        return self.descriptor.priceGroup

    @property
    def priceGroupTags(self):
        """ Returns tags associated with item's price group.
        """
        return self.descriptor.priceGroupTags

    @property
    def bonus(self):
        """ Returns bonus that customization item gives when applied.
        """
        return self._bonus

    @property
    def icon(self):
        """ Returns an icon for the item.
        """
        return self.descriptor.texture.replace('gui/', '../', 1)

    def isHistorical(self):
        """ Flag that determines whether item is historically accurate or not.
        """
        return self.descriptor.historical

    def isSummer(self):
        """ Returns true if item is applicable for summer maps, false otherwise.
        """
        return self.season & SeasonType.SUMMER

    def isWinter(self):
        """ Returns true if item is applicable for winter maps, false otherwise.
        """
        return self.season & SeasonType.WINTER

    def isDesert(self):
        """ Returns true if item is applicable for desert maps, false otherwise.
        """
        return self.season & SeasonType.DESERT

    def isAllSeason(self):
        """ Returns true if item is applicable for all seasons, false otherwise.
        """
        return self.season == SeasonType.ALL

    def isEvent(self):
        """ Returns true if item is applicable for event.
        """
        return self.season & SeasonType.EVENT

    def mayInstall(self, vehicle, _=None):
        """ Checks whether item is applicable for the given vehicle or not.
        
        :param vehicle: instance of Vehicle
        """
        return True if not self.descriptor.filter else self.descriptor.filter.matchVehicleType(vehicle.descriptor.type)

    def isWide(self):
        """ Checks whether the item icon should be displayed with a wide swatch
        """
        return False

    def isUnlocked(self):
        """ Check if item is unlocked.
        """
        return bool(self.eventsCache.questsProgress.getTokenCount(self.requiredToken)) if self.requiredToken else True

    def isRare(self):
        """ Check if item is rare (i.e. is from personal mission).
        """
        return self.descriptor.isRare()

    def fullInventoryCount(self, vehicle):
        """ Check if item is in inventory.
        """
        return self.inventoryCount + self.boundInventoryCount.get(vehicle.intCD, 0)


class Paint(Customization):
    """ Paint is an item that covers some part of a vehicle.
    """

    def __init__(self, *args, **kwargs):
        super(Paint, self).__init__(*args, **kwargs)
        self.itemTypeID = GUI_ITEM_TYPE.PAINT

    @property
    def color(self):
        """ Returns a color of the paint (integer).
        """
        return self.descriptor.color

    @property
    def gloss(self):
        """ Returns 'gloss' of the paint.
        """
        return self.descriptor.gloss

    @property
    def metallic(self):
        """ Returns 'metallic' of the paint.
        """
        return self.descriptor.metallic


class Camouflage(Customization):
    """ Camouflage is an item that covers some part of a vehicle.
    
    Camouflage is applied on top of paint.
    """

    def __init__(self, *args, **kwargs):
        super(Camouflage, self).__init__(*args, **kwargs)
        self.itemTypeID = GUI_ITEM_TYPE.CAMOUFLAGE
        self._bonus = ConcealmentBonus(camouflageId=self.id, season=self.season)

    @property
    def texture(self):
        """ Returns path to camo's texture (*.dds)
        """
        return self.descriptor.texture

    @property
    def icon(self):
        """ Returns gui path to camo's texture.
        """
        return camoIconTemplate(self.texture, _CAMO_SWATCH_WIDTH, _CAMO_SWATCH_HEIGHT, first(self.palettes))

    @property
    def tiling(self):
        """ Returns camouflage's tiling.
        """
        return self.descriptor.tiling

    @property
    def scales(self):
        """ Returns camouflage's scale settings.
        """
        return self.descriptor.scales

    @property
    def palettes(self):
        """ Returns palettes the camouflage can be painted with.
        """
        return self.descriptor.palettes


class Modification(Customization):
    """ Modification is an item that modifies vehicle look in general.
    """

    def __init__(self, *args, **kwargs):
        super(Modification, self).__init__(*args, **kwargs)
        self.itemTypeID = GUI_ITEM_TYPE.MODIFICATION

    def modValue(self, type, default=0.0):
        """ Returns value of modification.
        """
        return self.descriptor.getEffectValue(type, default=default)

    @property
    def effects(self):
        """ Returns dictionary of all effects listed in item.
        """
        return self.descriptor.effects

    def isWide(self):
        return True


class Decal(Customization):
    """ Sticker or inscription that can be installed in a slot.
    
    This item shouldn't be created in valid flow, Inscription and Emblem should be
    used instead.
    """

    @property
    def texture(self):
        """ Returns path to decal's texture (*.dds)
        """
        return self.descriptor.texture

    @property
    def isMirrored(self):
        """ Returns a flag indicating whether decal should be mirrored on the
        opposite side or not.
        """
        return self.descriptor.isMirrored


class Emblem(Decal):
    """ Emblem that can be installed in a slot.
    """

    def __init__(self, *args, **kwargs):
        super(Decal, self).__init__(*args, **kwargs)
        self.itemTypeID = GUI_ITEM_TYPE.EMBLEM


class Inscription(Decal):
    """ Inscription that can be installed in a slot.
    """

    def __init__(self, *args, **kwargs):
        super(Decal, self).__init__(*args, **kwargs)
        self.itemTypeID = GUI_ITEM_TYPE.INSCRIPTION

    def isWide(self):
        return True


class Style(Customization):
    """ Style is a predefined outfit.
    """
    __slots__ = ('_outfits',)

    def __init__(self, intCompactDescr, proxy=None):
        super(Style, self).__init__(intCompactDescr, proxy)
        self.itemTypeID = GUI_ITEM_TYPE.STYLE
        self._outfits = {}
        for season, component in self.descriptor.outfits.iteritems():
            outfitDescr = component.makeCompDescr()
            self._outfits[season] = self.itemsFactory.createOutfit(outfitDescr, proxy=proxy)

    @property
    def isRentable(self):
        """ Returns True if style can be rented and can't be bought.
        
        Note: inverse case is also valid: if item can be bought it can't be rented.
        """
        return self.descriptor.isRent

    @property
    def isRented(self):
        """ Returns True if style is actually rented on any vehicle.
        """
        return False if not self.isRentable else bool(self.boundInventoryCount)

    @property
    def rentCount(self):
        """ Returns number of battles this style provides (if it's rentable)
        """
        return self.descriptor.rentCount if self.isRentable else 0

    @property
    def userType(self):
        """ User readable item type name.
        """
        return i18n.makeString(VEHICLE_CUSTOMIZATION.CAROUSEL_SWATCH_STYLE_RENT) if self.isRentable else i18n.makeString(VEHICLE_CUSTOMIZATION.CAROUSEL_SWATCH_STYLE_PERMANENT)

    def getRentInfo(self, vehicle):
        """ Get rental info for the given vehicle.
        """
        if not self.isRentable:
            return RentalInfoProvider()
        battlesLeft = self.boundInventoryCount.get(vehicle.descriptor.type.compactDescr, 0)
        return RentalInfoProvider(battles=battlesLeft)

    def getOutfit(self, season):
        """ Get an outfit defined in the style for a given season.
        """
        return self._outfits.get(season)

    def isWide(self):
        return True
