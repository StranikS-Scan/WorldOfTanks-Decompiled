# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/shared.py
from collections import namedtuple, Counter
from CurrentVehicle import g_currentVehicle
from gui.customization.shared import HighlightingMode
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_EMPTY
from gui.Scaleform.genConsts.SEASONS_CONSTANTS import SEASONS_CONSTANTS
from gui.Scaleform.genConsts.CUSTOMIZATION_ALIASES import CUSTOMIZATION_ALIASES
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from helpers import dependency
from items.components.c11n_constants import SeasonType
from shared_utils import CONST_CONTAINER
from skeletons.gui.shared import IItemsCache

class C11N_MODE(CONST_CONTAINER):
    """ Customization mode.
    """
    STYLE, CUSTOM = range(2)


class CUSTOMIZATION_TABS(CONST_CONTAINER):
    """
    Enumeration of customization item browser tabs.
    The order of the ALL property corresponds to the order the tab names will appear in.
    """
    STYLE, PAINT, CAMOUFLAGE, EMBLEM, INSCRIPTION, EFFECT = range(6)
    AVAILABLE_REGIONS = (PAINT,
     CAMOUFLAGE,
     EMBLEM,
     INSCRIPTION)
    ALL = (STYLE,
     PAINT,
     CAMOUFLAGE,
     EMBLEM,
     INSCRIPTION,
     EFFECT)
    VISIBLE = (PAINT,
     CAMOUFLAGE,
     EMBLEM,
     INSCRIPTION,
     EFFECT)
    REGIONS = {STYLE: HighlightingMode.WHOLE_VEHICLE,
     PAINT: HighlightingMode.REPAINT_REGIONS_MERGED,
     CAMOUFLAGE: HighlightingMode.CAMO_REGIONS,
     EFFECT: HighlightingMode.WHOLE_VEHICLE}


TABS_ITEM_MAPPING = {CUSTOMIZATION_TABS.STYLE: GUI_ITEM_TYPE.STYLE,
 CUSTOMIZATION_TABS.PAINT: GUI_ITEM_TYPE.PAINT,
 CUSTOMIZATION_TABS.CAMOUFLAGE: GUI_ITEM_TYPE.CAMOUFLAGE,
 CUSTOMIZATION_TABS.EMBLEM: GUI_ITEM_TYPE.EMBLEM,
 CUSTOMIZATION_TABS.INSCRIPTION: GUI_ITEM_TYPE.INSCRIPTION,
 CUSTOMIZATION_TABS.EFFECT: GUI_ITEM_TYPE.MODIFICATION}
TYPE_TO_TAB_IDX = {v:k for k, v in TABS_ITEM_MAPPING.iteritems()}
SEASON_IDX_TO_TYPE = {SEASONS_CONSTANTS.SUMMER_INDEX: SeasonType.SUMMER,
 SEASONS_CONSTANTS.WINTER_INDEX: SeasonType.WINTER,
 SEASONS_CONSTANTS.DESERT_INDEX: SeasonType.DESERT}
SEASON_TYPE_TO_NAME = {SeasonType.SUMMER: SEASONS_CONSTANTS.SUMMER,
 SeasonType.WINTER: SEASONS_CONSTANTS.WINTER,
 SeasonType.DESERT: SEASONS_CONSTANTS.DESERT}
SEASON_TYPE_TO_IDX = {SeasonType.SUMMER: SEASONS_CONSTANTS.SUMMER_INDEX,
 SeasonType.WINTER: SEASONS_CONSTANTS.WINTER_INDEX,
 SeasonType.DESERT: SEASONS_CONSTANTS.DESERT_INDEX}
CAMO_SCALE_SIZE = (VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_CAMO_SCALE_SMALL, VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_CAMO_SCALE_NORMAL, VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_CAMO_SCALE_LARGE)
CUSTOMIZATION_POPOVER_ALIASES = {GUI_ITEM_TYPE.STYLE: CUSTOMIZATION_ALIASES.CUSTOMIZATION_STYLE_POPOVER,
 GUI_ITEM_TYPE.PAINT: CUSTOMIZATION_ALIASES.CUSTOMIZATION_PAINT_POPOVER,
 GUI_ITEM_TYPE.CAMOUFLAGE: CUSTOMIZATION_ALIASES.CUSTOMIZATION_CAMO_POPOVER,
 GUI_ITEM_TYPE.EMBLEM: CUSTOMIZATION_ALIASES.CUSTOMIZATION_DECAL_POPOVER,
 GUI_ITEM_TYPE.INSCRIPTION: CUSTOMIZATION_ALIASES.CUSTOMIZATION_DECAL_POPOVER,
 GUI_ITEM_TYPE.MODIFICATION: CUSTOMIZATION_ALIASES.CUSTOMIZATION_EFFECT_POPOVER}
SEASONS_ORDER = (SeasonType.SUMMER, SeasonType.WINTER, SeasonType.DESERT)

class PurchaseItem(object):
    __slots__ = ('item', 'price', 'areaID', 'slot', 'regionID', 'selected', 'group', 'isFromInventory', 'isDismantling')

    def __init__(self, item, price, areaID, slot, regionID, selected, group, isFromInventory=False, isDismantling=False):
        self.item = item
        self.price = price
        self.areaID = areaID
        self.slot = slot
        self.regionID = regionID
        self.selected = selected
        self.group = group
        self.isFromInventory = isFromInventory
        self.isDismantling = isDismantling


Cart = namedtuple('Cart', 'totalPrice numSelected numApplying numTotal')

class AdditionalPurchaseGroups(object):
    STYLES_GROUP_ID = -1
    UNASSIGNED_GROUP_ID = -2


OutfitInfo = namedtuple('OutfitInfo', ('original', 'modified'))

def getCustomPurchaseItems(outfitsInfo):
    """ Builds and returns a list of PurchaseItems.  This list will only contain items that would be newly purchased.
    This takes into account current inventory and what items are already available.
    :return: list of PurcahseItem entries containing items that would require a new purchase.
    """
    itemsCache = dependency.instance(IItemsCache)
    purchaseItems = []
    inventoryCount = Counter()
    for season, outfitCompare in outfitsInfo.iteritems():
        inventoryCount.update({i.intCD:0 for i in outfitCompare.modified.items()})

    for intCD in inventoryCount.keys():
        item = itemsCache.items.getItemByCD(intCD)
        inventoryCount[intCD] += item.fullInventoryCount(g_currentVehicle.item)

    for season, outfitCompare in outfitsInfo.iteritems():
        backward = outfitCompare.modified.diff(outfitCompare.original)
        for container in backward.containers():
            for slot in container.slots():
                for idx in range(slot.capacity()):
                    item = slot.getItem(idx)
                    if item:
                        purchaseItems.append(PurchaseItem(item, price=item.getBuyPrice(), areaID=container.getAreaID(), slot=slot.getType(), regionID=idx, selected=True, group=season, isFromInventory=False, isDismantling=True))
                        inventoryCount[item.intCD] += 1

    for season, outfitCompare in outfitsInfo.iteritems():
        forward = outfitCompare.original.diff(outfitCompare.modified)
        for container in forward.containers():
            for slot in container.slots():
                for idx in range(slot.capacity()):
                    item = slot.getItem(idx)
                    if item:
                        isFromInventory = inventoryCount[item.intCD] > 0
                        purchaseItems.append(PurchaseItem(item, price=item.getBuyPrice(), areaID=container.getAreaID(), slot=slot.getType(), regionID=idx, selected=True, group=season, isFromInventory=isFromInventory, isDismantling=False))
                        inventoryCount[item.intCD] -= 1

    return purchaseItems


def getOutfitWithoutItem(outfitsInfo, intCD):
    """ Get original outfit with one item put off.
    """
    for season, outfitCompare in outfitsInfo.iteritems():
        backward = outfitCompare.modified.diff(outfitCompare.original)
        for container in backward.containers():
            for slot in container.slots():
                for idx in range(slot.capacity()):
                    item = slot.getItem(idx)
                    if item and item.intCD == intCD:
                        outfit = outfitCompare.original
                        season = season
                        container = outfit.getContainer(container.getAreaID())
                        slot = container.slotFor(item.itemTypeID)
                        slot.remove(idx)
                        return (season, outfit)

    return (None, None)


def getStylePurchaseItems(styleInfo):
    """ Get purchase items for the styles mode.
    """
    purchaseItems = []
    original = styleInfo.original
    modified = styleInfo.modified
    if modified and not original or modified and original.id != modified.id:
        inventoryCount = styleInfo.modified.fullInventoryCount(g_currentVehicle.item)
        isFromInventory = inventoryCount > 0
        purchaseItems.append(PurchaseItem(modified, modified.getBuyPrice(), areaID=None, slot=None, regionID=None, selected=True, group=AdditionalPurchaseGroups.STYLES_GROUP_ID, isFromInventory=isFromInventory, isDismantling=False))
    elif original and not modified:
        purchaseItems.append(PurchaseItem(original, original.getBuyPrice(), areaID=None, slot=None, regionID=None, selected=True, group=AdditionalPurchaseGroups.STYLES_GROUP_ID, isFromInventory=False, isDismantling=True))
    return purchaseItems


def getItemInventoryCount(item, outfitsInfo=None):
    """ Gets the actual available inventory count of an item.
    (including the items that had been put off but haven't been committed yet)
    """
    inventoryCount = item.fullInventoryCount(g_currentVehicle.item)
    if not outfitsInfo:
        return inventoryCount
    intCD = item.intCD
    for season, outfitCompare in outfitsInfo.iteritems():
        old = Counter((i.intCD for i in outfitCompare.original.items()))
        new = Counter((i.intCD for i in outfitCompare.modified.items()))
        inventoryCount += old[intCD] - new[intCD]

    return max(0, inventoryCount)


def getStyleInventoryCount(item, styleInfo=None):
    """ Gets the actual available inventory count of a style.
    """
    inventoryCount = item.fullInventoryCount(g_currentVehicle.item)
    if not styleInfo:
        return inventoryCount
    original = styleInfo.original
    modified = styleInfo.modified
    if not item.isRentable:
        if modified and modified.intCD == item.intCD:
            inventoryCount -= 1
        if original and original.intCD == item.intCD:
            inventoryCount += 1
    elif original and original.intCD == item.intCD:
        if g_currentVehicle.item.getStyledOutfit(SeasonType.SUMMER).isEnabled():
            inventoryCount += 1
    return max(0, inventoryCount)


def getTotalPurchaseInfo(purchaseItems):
    """ Get purchase info (total price that needs to be paid,
    number of actually selected items and total number of items.
    """
    totalPrice = ITEM_PRICE_EMPTY
    numSelectedItems = 0
    numApplyingItems = 0
    for purchaseItem in purchaseItems:
        if not purchaseItem.isDismantling:
            numApplyingItems += 1
        if purchaseItem.selected and not purchaseItem.isDismantling:
            numSelectedItems += 1
            if not purchaseItem.isFromInventory:
                totalPrice += purchaseItem.price

    return Cart(totalPrice, numSelectedItems, numApplyingItems, len(purchaseItems))
