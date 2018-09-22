# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/shared.py
from collections import namedtuple, Counter
import Math
from CurrentVehicle import g_currentVehicle
from gui.customization.shared import HighlightingMode
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_EMPTY
from gui.Scaleform.genConsts.SEASONS_CONSTANTS import SEASONS_CONSTANTS
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from helpers import dependency
from items.components.c11n_constants import SeasonType
from shared_utils import CONST_CONTAINER
from skeletons.gui.shared import IItemsCache
from gui.shared.money import Money

class C11nMode(CONST_CONTAINER):
    STYLE, CUSTOM = range(2)


class C11nTabs(CONST_CONTAINER):
    STYLE, PAINT, CAMOUFLAGE, EMBLEM, INSCRIPTION, PROJECTION_DECAL, EFFECT = range(7)
    AVAILABLE_REGIONS = (PAINT,
     CAMOUFLAGE,
     EMBLEM,
     INSCRIPTION,
     PROJECTION_DECAL)
    ALL = (STYLE,
     PAINT,
     CAMOUFLAGE,
     EMBLEM,
     INSCRIPTION,
     PROJECTION_DECAL,
     EFFECT)
    VISIBLE = (PAINT,
     CAMOUFLAGE,
     EMBLEM,
     INSCRIPTION,
     PROJECTION_DECAL,
     EFFECT)
    REGIONS = {STYLE: HighlightingMode.WHOLE_VEHICLE,
     PAINT: HighlightingMode.REPAINT_REGIONS_MERGED,
     CAMOUFLAGE: HighlightingMode.CAMO_REGIONS,
     EFFECT: HighlightingMode.WHOLE_VEHICLE}


TABS_ITEM_MAPPING = {C11nTabs.STYLE: GUI_ITEM_TYPE.STYLE,
 C11nTabs.PAINT: GUI_ITEM_TYPE.PAINT,
 C11nTabs.CAMOUFLAGE: GUI_ITEM_TYPE.CAMOUFLAGE,
 C11nTabs.EMBLEM: GUI_ITEM_TYPE.EMBLEM,
 C11nTabs.INSCRIPTION: GUI_ITEM_TYPE.INSCRIPTION,
 C11nTabs.PROJECTION_DECAL: GUI_ITEM_TYPE.PROJECTION_DECAL,
 C11nTabs.EFFECT: GUI_ITEM_TYPE.MODIFICATION}
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
SCALE_SIZE = (VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_SCALE_SMALL, VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_SCALE_NORMAL, VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_SCALE_LARGE)
SEASONS_ORDER = (SeasonType.SUMMER, SeasonType.WINTER, SeasonType.DESERT)
TYPES_ORDER = (GUI_ITEM_TYPE.PAINT,
 GUI_ITEM_TYPE.CAMOUFLAGE,
 GUI_ITEM_TYPE.PROJECTION_DECAL,
 GUI_ITEM_TYPE.EMBLEM,
 GUI_ITEM_TYPE.INSCRIPTION,
 GUI_ITEM_TYPE.MODIFICATION,
 GUI_ITEM_TYPE.STYLE)
DRAG_AND_DROP_INACTIVE_TABS = (C11nTabs.STYLE, C11nTabs.EFFECT)

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


CartInfo = namedtuple('CartInfo', 'totalPrice numSelected numApplying numTotal minPriceItem isAtLeastOneItemFromInventory isAtLeastOneItemDismantled')

class AdditionalPurchaseGroups(object):
    STYLES_GROUP_ID = -1
    UNASSIGNED_GROUP_ID = -2


OutfitInfo = namedtuple('OutfitInfo', ('original', 'modified'))

def getCustomPurchaseItems(outfitsInfo):
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


def getOutfitWithoutItems(outfitsInfo, intCD, count):
    for season, outfitCompare in outfitsInfo.iteritems():
        backward = outfitCompare.modified.diff(outfitCompare.original)
        for container in backward.containers():
            for slot in container.slots():
                for idx in range(slot.capacity()):
                    item = slot.getItem(idx)
                    if item and item.intCD == intCD and count:
                        outfit = outfitCompare.original
                        season = season
                        container = outfit.getContainer(container.getAreaID())
                        slot = container.slotFor(item.itemTypeID)
                        slot.remove(idx)
                        count -= 1

        yield (season, outfitCompare.original)


def getStylePurchaseItems(styleInfo):
    purchaseItems = []
    original = styleInfo.original
    modified = styleInfo.modified
    if modified and not original or modified and original.id != modified.id:
        inventoryCount = styleInfo.modified.fullInventoryCount(g_currentVehicle.item)
        isFromInventory = inventoryCount > 0
        purchaseItems.append(PurchaseItem(modified, modified.getBuyPrice(), areaID=None, slot=None, regionID=None, selected=True, group=AdditionalPurchaseGroups.STYLES_GROUP_ID, isFromInventory=isFromInventory, isDismantling=False))
    elif original and not modified:
        purchaseItems.append(PurchaseItem(original, original.getBuyPrice(), areaID=None, slot=None, regionID=None, selected=True, group=AdditionalPurchaseGroups.STYLES_GROUP_ID, isFromInventory=False, isDismantling=True))
    elif not original and not modified:
        purchaseItems.append(PurchaseItem(original, None, areaID=None, slot=None, regionID=None, selected=True, group=AdditionalPurchaseGroups.STYLES_GROUP_ID, isFromInventory=False, isDismantling=True))
    return purchaseItems


def getItemInventoryCount(item, outfitsInfo=None):
    inventoryCount = item.fullInventoryCount(g_currentVehicle.item)
    if outfitsInfo is not None:
        intCD = item.intCD
        for outfitCompare in outfitsInfo.itervalues():
            old = outfitCompare.original.itemsCounter
            new = outfitCompare.modified.itemsCounter
            inventoryCount += old[intCD] - new[intCD]

    return max(0, inventoryCount)


def getItemAppliedCount(item, outfitsInfo=None):
    appliedCount = 0
    if outfitsInfo is not None:
        intCD = item.intCD
        for outfitCompare in outfitsInfo.itervalues():
            old = outfitCompare.original.itemsCounter
            new = outfitCompare.modified.itemsCounter
            appliedCount += new[intCD] - old[intCD]

    return appliedCount


def getStyleInventoryCount(item, styleInfo=None):
    inventoryCount = item.fullInventoryCount(g_currentVehicle.item)
    if not styleInfo:
        return inventoryCount
    else:
        original = styleInfo.original
        modified = styleInfo.modified
        if not item.isRentable:
            if modified and modified.intCD == item.intCD:
                inventoryCount -= 1
            if original and original.intCD == item.intCD:
                inventoryCount += 1
        elif original and original.intCD == item.intCD:
            styledOutfit = g_currentVehicle.item.getStyledOutfit(SeasonType.SUMMER)
            if styledOutfit is not None and styledOutfit.isEnabled():
                inventoryCount += 1
        return max(0, inventoryCount)


def getTotalPurchaseInfo(purchaseItems):
    totalPrice = ITEM_PRICE_EMPTY
    numSelectedItems = 0
    numApplyingItems = 0
    isAtLeastOneItemFromInventory = False
    isAtLeastOneItemDismantled = False
    minPriceItem = Money()
    for purchaseItem in purchaseItems:
        if not purchaseItem.isDismantling:
            numApplyingItems += 1
        else:
            isAtLeastOneItemDismantled = True
        if purchaseItem.selected and not purchaseItem.isDismantling:
            numSelectedItems += 1
            if not purchaseItem.isFromInventory:
                totalPrice += purchaseItem.price
                if not minPriceItem.isDefined() or purchaseItem.price.price < minPriceItem:
                    minPriceItem = purchaseItem.price.price
            else:
                isAtLeastOneItemFromInventory = True

    return CartInfo(totalPrice, numSelectedItems, numApplyingItems, len(purchaseItems), minPriceItem, isAtLeastOneItemFromInventory, isAtLeastOneItemDismantled)


def fromWorldCoordsToHangarVehicle(worldCoords):
    compoundModel = g_currentVehicle.hangarSpace.space.getVehicleEntity().appearance.compoundModel
    modelMat = Math.Matrix(compoundModel.matrix)
    modelMat.invert()
    return modelMat.applyPoint(worldCoords)


def fromHangarVehicleToWorldCoords(hangarVehicleCoords):
    compoundModel = g_currentVehicle.hangarSpace.space.getVehicleEntity().appearance.compoundModel
    modelMatrix = Math.Matrix(compoundModel.matrix)
    return modelMatrix.applyPoint(hangarVehicleCoords)
