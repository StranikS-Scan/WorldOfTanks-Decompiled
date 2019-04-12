# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/shared.py
from collections import namedtuple, Counter
import Math
import nations
from CurrentVehicle import g_currentVehicle
from gui.Scaleform import getNationsFilterAssetPath
from gui.customization.shared import HighlightingMode
from gui.hangar_cameras.hangar_camera_common import CameraMovementStates
from gui.shared.formatters import icons, text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER, VEHICLE_TAGS
from gui.shared.gui_items.customization.outfit import Area
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_EMPTY
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import isIngameShopEnabled
from gui.Scaleform.genConsts.SEASONS_CONSTANTS import SEASONS_CONSTANTS
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from helpers import dependency, int2roman
from helpers.i18n import makeString as _ms
from items.components.c11n_constants import SeasonType, PERSONAL_NUMBER_DIGITS_COUNT
from items.vehicles import VEHICLE_CLASS_TAGS
from shared_utils import CONST_CONTAINER
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from gui.shared.money import Currency, Money
from skeletons.gui.shared.utils import IHangarSpace

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


TABS_SLOT_TYPE_MAPPING = {C11nTabs.STYLE: GUI_ITEM_TYPE.STYLE,
 C11nTabs.PAINT: GUI_ITEM_TYPE.PAINT,
 C11nTabs.CAMOUFLAGE: GUI_ITEM_TYPE.CAMOUFLAGE,
 C11nTabs.EMBLEM: GUI_ITEM_TYPE.EMBLEM,
 C11nTabs.INSCRIPTION: GUI_ITEM_TYPE.INSCRIPTION,
 C11nTabs.PROJECTION_DECAL: GUI_ITEM_TYPE.PROJECTION_DECAL,
 C11nTabs.EFFECT: GUI_ITEM_TYPE.MODIFICATION}
TABS_ITEM_TYPE_MAPPING = {C11nTabs.STYLE: (GUI_ITEM_TYPE.STYLE,),
 C11nTabs.PAINT: (GUI_ITEM_TYPE.PAINT,),
 C11nTabs.CAMOUFLAGE: (GUI_ITEM_TYPE.CAMOUFLAGE,),
 C11nTabs.EMBLEM: (GUI_ITEM_TYPE.EMBLEM,),
 C11nTabs.INSCRIPTION: (GUI_ITEM_TYPE.INSCRIPTION, GUI_ITEM_TYPE.PERSONAL_NUMBER),
 C11nTabs.PROJECTION_DECAL: (GUI_ITEM_TYPE.PROJECTION_DECAL,),
 C11nTabs.EFFECT: (GUI_ITEM_TYPE.MODIFICATION,)}
TYPE_TO_TAB_IDX = {GUI_ITEM_TYPE.STYLE: C11nTabs.STYLE,
 GUI_ITEM_TYPE.PAINT: C11nTabs.PAINT,
 GUI_ITEM_TYPE.CAMOUFLAGE: C11nTabs.CAMOUFLAGE,
 GUI_ITEM_TYPE.EMBLEM: C11nTabs.EMBLEM,
 GUI_ITEM_TYPE.INSCRIPTION: C11nTabs.INSCRIPTION,
 GUI_ITEM_TYPE.PERSONAL_NUMBER: C11nTabs.INSCRIPTION,
 GUI_ITEM_TYPE.PROJECTION_DECAL: C11nTabs.PROJECTION_DECAL,
 GUI_ITEM_TYPE.MODIFICATION: C11nTabs.EFFECT}
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
 GUI_ITEM_TYPE.PERSONAL_NUMBER,
 GUI_ITEM_TYPE.INSCRIPTION,
 GUI_ITEM_TYPE.MODIFICATION,
 GUI_ITEM_TYPE.STYLE)
DRAG_AND_DROP_INACTIVE_TABS = (C11nTabs.STYLE, C11nTabs.EFFECT)
SEASON_TYPE_TO_INFOTYPE_MAP = {SeasonType.SUMMER: VEHICLE_CUSTOMIZATION.CUSTOMIZATION_INFOTYPE_MAPTYPE_SUMMER,
 SeasonType.DESERT: VEHICLE_CUSTOMIZATION.CUSTOMIZATION_INFOTYPE_MAPTYPE_DESERT,
 SeasonType.WINTER: VEHICLE_CUSTOMIZATION.CUSTOMIZATION_INFOTYPE_MAPTYPE_WINTER}

class PurchaseItem(object):
    __slots__ = ('item', 'price', 'areaID', 'slot', 'regionID', 'selected', 'group', 'isFromInventory', 'isDismantling', 'component')

    def __init__(self, item, price, areaID, slot, regionID, selected, group, isFromInventory=False, isDismantling=False, component=None):
        self.item = item
        self.price = price
        self.areaID = areaID
        self.slot = slot
        self.regionID = regionID
        self.selected = selected
        self.group = group
        self.isFromInventory = isFromInventory
        self.isDismantling = isDismantling
        self.component = component


CartInfo = namedtuple('CartInfo', 'totalPrice numSelected numApplying numTotal minPriceItem isAtLeastOneItemFromInventory isAtLeastOneItemDismantled')

class AdditionalPurchaseGroups(object):
    STYLES_GROUP_ID = -1
    UNASSIGNED_GROUP_ID = -2


class MoneyForPurchase(object):
    NOT_ENOUGH = 0
    ENOUGH_WITH_EXCHANGE = 1
    ENOUGH = 2


OutfitInfo = namedtuple('OutfitInfo', ('original', 'modified'))

def getCustomPurchaseItems(outfitsInfo, seasonOrder=None):
    seasonOrder = seasonOrder or SEASONS_ORDER
    itemsCache = dependency.instance(IItemsCache)
    purchaseItems = []
    inventoryCount = Counter()
    for season, outfitCompare in outfitsInfo.iteritems():
        inventoryCount.update({i.intCD:0 for i in outfitCompare.modified.items()})

    for intCD in inventoryCount.keys():
        item = itemsCache.items.getItemByCD(intCD)
        inventoryCount[intCD] += item.fullInventoryCount(g_currentVehicle.item)

    for season in reversed(seasonOrder):
        if season not in outfitsInfo:
            continue
        outfitCompare = outfitsInfo[season]
        backward = outfitCompare.modified.diff(outfitCompare.original)
        for container in backward.containers():
            for slot in container.slots():
                for idx in range(slot.capacity()):
                    slotData = slot.getSlotData(idx)
                    if slotData and slotData.item:
                        purchaseItems.append(PurchaseItem(slotData.item, price=slotData.item.getBuyPrice(), areaID=container.getAreaID(), slot=slotData.item.itemTypeID, regionID=idx, selected=True, group=season, isFromInventory=False, isDismantling=True, component=slotData.component))
                        inventoryCount[slotData.item.intCD] += 1

    for season in seasonOrder:
        if season not in outfitsInfo:
            continue
        outfitCompare = outfitsInfo[season]
        forward = outfitCompare.original.diff(outfitCompare.modified)
        for container in forward.containers():
            for slot in container.slots():
                for idx in range(slot.capacity()):
                    slotData = slot.getSlotData(idx)
                    if slotData and slotData.item:
                        isFromInventory = inventoryCount[slotData.item.intCD] > 0
                        purchaseItems.append(PurchaseItem(slotData.item, price=slotData.item.getBuyPrice(), areaID=container.getAreaID(), slot=slotData.item.itemTypeID, regionID=idx, selected=True, group=season, isFromInventory=isFromInventory, isDismantling=False, component=slotData.component))
                        inventoryCount[slotData.item.intCD] -= 1

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


def getStylePurchaseItems(styleInfo, buyMore=False):
    purchaseItems = []
    original = styleInfo.original
    modified = styleInfo.modified
    if buyMore:
        purchaseItems.append(PurchaseItem(modified, modified.getBuyPrice(), areaID=None, slot=None, regionID=None, selected=True, group=AdditionalPurchaseGroups.STYLES_GROUP_ID, isFromInventory=False, isDismantling=False))
    elif modified and not original or modified and original.id != modified.id:
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


def containsVehicleBound(purchaseItems):
    fromInventoryCounter = Counter()
    vehCD = g_currentVehicle.item.intCD
    for purchaseItem in purchaseItems:
        if purchaseItem.item and purchaseItem.item.isVehicleBound and not purchaseItem.isDismantling and not purchaseItem.item.isRentable:
            if not purchaseItem.isFromInventory:
                return True
            fromInventoryCounter[purchaseItem.item] += 1

    return any((count > item.boundInventoryCount.get(vehCD, 0) for item, count in fromInventoryCounter.items()))


def getSuitableText(item, currentVehicle=None):
    conditions = []
    for node in item.descriptor.filter.include:
        separator = ' '.join(['&nbsp;&nbsp;', icons.makeImageTag(RES_ICONS.MAPS_ICONS_CUSTOMIZATION_TOOLTIP_SEPARATOR, 3, 21, -6), '  '])
        if node.nations:
            for nation in node.nations:
                name = nations.NAMES[nation]
                conditions.append(icons.makeImageTag(getNationsFilterAssetPath(name), 26, 16, -4))
                conditions.append('  ')

            conditions = conditions[:-1]
            conditions.append(' ')
        if node.tags:
            for vehType in VEHICLE_TYPES_ORDER:
                if vehType in node.tags:
                    conditions.append(icons.makeImageTag(RES_ICONS.getFilterVehicleType(vehType), 27, 17, -4))

            if VEHICLE_CLASS_TAGS & node.tags:
                conditions.append(separator)
            if VEHICLE_TAGS.PREMIUM in node.tags:
                conditions.append(icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_PREM_SMALL_ICON, 20, 17, -4))
            if VEHICLE_TAGS.PREMIUM_IGR in node.tags:
                conditions.append(icons.premiumIgrSmall())
                conditions.append(separator)
        if node.levels:
            for level in node.levels:
                conditions.append(text_styles.stats(int2roman(level)))
                conditions.append(text_styles.stats(',&nbsp;'))

            conditions = conditions[:-1]
            conditions.append(separator)
        if node.vehicles:
            conditions.append(text_styles.standard(makeVehiclesShortNamesString(set(node.vehicles), currentVehicle, flat=True)))
            conditions.append(separator)

    return text_styles.concatStylesToSingleLine(*conditions[:-1])


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def makeVehiclesShortNamesString(vehiclesCDs, currentVehicle, flat=False, itemsCache=None):

    def getVehicleShortName(vehicleCD):
        return itemsCache.items.getItemByCD(vehicleCD).shortUserName

    vehiclesShortNames = []
    if currentVehicle is not None and currentVehicle.intCD in vehiclesCDs and not flat:
        vehiclesCDs.remove(currentVehicle.intCD)
        vehiclesShortNames.append(currentVehicle.shortUserName + _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_LIMITED_CURRENT_VEHICLE))
    vehiclesShortNames.extend(map(getVehicleShortName, vehiclesCDs))
    return ', '.join(vehiclesShortNames)


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext, hangarSpace=IHangarSpace)
def isC11nEnabled(lobbyContext=None, hangarSpace=None):
    state = g_currentVehicle.getViewState()
    vehicleEntity = hangarSpace.getVehicleEntity()
    if vehicleEntity is None:
        isVehicleCameraReadyForC11n = False
    else:
        isVehicleCameraReadyForC11n = vehicleEntity.state == CameraMovementStates.ON_OBJECT
    return lobbyContext.getServerSettings().isCustomizationEnabled() and state.isCustomizationEnabled() and not state.isOnlyForEventBattles() and hangarSpace.spaceInited and hangarSpace.isModelLoaded and isVehicleCameraReadyForC11n


def getPurchaseMoneyState(price):
    itemsCache = dependency.instance(IItemsCache)
    money = itemsCache.items.stats.money
    exchangeRate = itemsCache.items.shop.exchangeRate
    shortage = money.getShortage(price)
    if not shortage:
        moneyState = MoneyForPurchase.ENOUGH
    else:
        money = money - price + shortage
        price = shortage
        money = money.exchange(Currency.GOLD, Currency.CREDITS, exchangeRate, default=0)
        shortage = money.getShortage(price)
        if not shortage:
            moneyState = MoneyForPurchase.ENOUGH_WITH_EXCHANGE
        else:
            moneyState = MoneyForPurchase.NOT_ENOUGH
    return moneyState


def isTransactionValid(moneyState, price):
    itemsCache = dependency.instance(IItemsCache)
    money = itemsCache.items.stats.money
    shortage = money.getShortage(price)
    inGameShopOn = Currency.GOLD in shortage.getCurrency() and isIngameShopEnabled()
    validTransaction = moneyState != MoneyForPurchase.NOT_ENOUGH or inGameShopOn
    return validTransaction


def formatPersonalNumber(number):
    return number.rjust(PERSONAL_NUMBER_DIGITS_COUNT, '0')


def getAllParentProjectionSlots(vehicle):
    return [ anchor for anchor in vehicle.item.getAnchors(GUI_ITEM_TYPE.PROJECTION_DECAL, Area.MISC) if anchor.isParent ]
