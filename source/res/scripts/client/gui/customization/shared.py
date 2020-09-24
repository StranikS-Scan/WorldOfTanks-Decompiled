# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/customization/shared.py
from collections import namedtuple, Counter
import logging
import Math
from gui.Scaleform.daapi.view.dialogs.ExchangeDialogMeta import InfoItemBase
from gui.Scaleform.genConsts.SEASONS_CONSTANTS import SEASONS_CONSTANTS
from gui.customization.constants import CustomizationModes
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_EMPTY
from gui.shared.money import Currency, ZERO_MONEY
from items.components.c11n_constants import CustomizationType, C11N_MASK_REGION, MAX_USERS_PROJECTION_DECALS, ProjectionDecalFormTags, SeasonType, ApplyArea, C11N_GUN_APPLY_REGIONS, UNBOUND_VEH_KEY, EMPTY_ITEM_ID
from shared_utils import CONST_CONTAINER, isEmpty
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.customization import ICustomizationService
from vehicle_systems.tankStructure import TankPartIndexes, TankPartNames
from CurrentVehicle import g_currentVehicle
from gui.shared.utils.requesters import REQ_CRITERIA
from vehicle_outfit.outfit import Area, SLOT_TYPE_TO_ANCHOR_TYPE_MAP, scaffold, Outfit
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from items.vehicles import g_cache
_logger = logging.getLogger(__name__)
C11nId = namedtuple('C11nId', ('areaId', 'slotType', 'regionIdx'))
C11nId.__new__.__defaults__ = (-1, -1, -1)
C11N_ITEM_TYPE_MAP = {GUI_ITEM_TYPE.PAINT: CustomizationType.PAINT,
 GUI_ITEM_TYPE.CAMOUFLAGE: CustomizationType.CAMOUFLAGE,
 GUI_ITEM_TYPE.MODIFICATION: CustomizationType.MODIFICATION,
 GUI_ITEM_TYPE.DECAL: CustomizationType.DECAL,
 GUI_ITEM_TYPE.EMBLEM: CustomizationType.DECAL,
 GUI_ITEM_TYPE.INSCRIPTION: CustomizationType.DECAL,
 GUI_ITEM_TYPE.PERSONAL_NUMBER: CustomizationType.PERSONAL_NUMBER,
 GUI_ITEM_TYPE.STYLE: CustomizationType.STYLE,
 GUI_ITEM_TYPE.PROJECTION_DECAL: CustomizationType.PROJECTION_DECAL,
 GUI_ITEM_TYPE.ATTACHMENT: CustomizationType.ATTACHMENT,
 GUI_ITEM_TYPE.SEQUENCE: CustomizationType.SEQUENCE}
PURCHASE_ITEMS_ORDER = (GUI_ITEM_TYPE.STYLE,
 GUI_ITEM_TYPE.ATTACHMENT,
 GUI_ITEM_TYPE.SEQUENCE,
 GUI_ITEM_TYPE.PROJECTION_DECAL,
 GUI_ITEM_TYPE.PERSONAL_NUMBER,
 GUI_ITEM_TYPE.INSCRIPTION,
 GUI_ITEM_TYPE.MODIFICATION,
 GUI_ITEM_TYPE.PAINT,
 GUI_ITEM_TYPE.CAMOUFLAGE,
 GUI_ITEM_TYPE.EMBLEM)
_EDITED_ITEM_ORDER_SHIFT = 8
PURCHASE_ITEMS_ORDER += tuple((key << _EDITED_ITEM_ORDER_SHIFT for key in PURCHASE_ITEMS_ORDER))
EDITABLE_STYLE_IRREMOVABLE_TYPES = (GUI_ITEM_TYPE.PAINT, GUI_ITEM_TYPE.CAMOUFLAGE, GUI_ITEM_TYPE.MODIFICATION)
EDITABLE_STYLE_APPLY_TO_ALL_AREAS_TYPES = {GUI_ITEM_TYPE.PAINT: C11nId(Area.HULL, GUI_ITEM_TYPE.PAINT, 0),
 GUI_ITEM_TYPE.CAMOUFLAGE: C11nId(Area.HULL, GUI_ITEM_TYPE.CAMOUFLAGE, 0)}

class PurchaseItem(object):
    __slots__ = ('item', 'price', 'areaID', 'slotType', 'regionIdx', 'selected', 'group', 'isFromInventory', 'isDismantling', 'component', 'locked', 'isEdited')

    def __init__(self, item, price, areaID, slotType, regionIdx, selected, group, isFromInventory=False, isDismantling=False, component=None, locked=False, isEdited=False):
        self.item = item
        self.price = price
        self.areaID = areaID
        self.slotType = slotType
        self.regionIdx = regionIdx
        self.selected = selected
        self.group = group
        self.isFromInventory = isFromInventory
        self.isDismantling = isDismantling
        self.component = component
        self.locked = locked
        self.isEdited = isEdited

    def getOrderKey(self):
        return self.item.itemTypeID if not self.isEdited else self.item.itemTypeID << _EDITED_ITEM_ORDER_SHIFT


class HighlightingMode(CONST_CONTAINER):
    PAINT_REGIONS = 0
    CAMO_REGIONS = 1
    WHOLE_VEHICLE = 2
    REPAINT_REGIONS_MERGED = 3
    CAMO_REGIONS_SKIP_TURRET = 4


MODE_TO_C11N_TYPE = {HighlightingMode.PAINT_REGIONS: GUI_ITEM_TYPE.PAINT,
 HighlightingMode.REPAINT_REGIONS_MERGED: GUI_ITEM_TYPE.PAINT,
 HighlightingMode.CAMO_REGIONS: GUI_ITEM_TYPE.CAMOUFLAGE,
 HighlightingMode.WHOLE_VEHICLE: GUI_ITEM_TYPE.STYLE,
 HighlightingMode.CAMO_REGIONS_SKIP_TURRET: GUI_ITEM_TYPE.CAMOUFLAGE}
REGIONS_BY_AREA_ID = {Area.CHASSIS: ApplyArea.CHASSIS_REGIONS,
 Area.HULL: ApplyArea.HULL_REGIONS,
 Area.TURRET: ApplyArea.TURRET_REGIONS,
 Area.GUN: ApplyArea.GUN_REGIONS}
AREA_ID_BY_REGION = {region:areaId for areaId, regions in REGIONS_BY_AREA_ID.iteritems() for region in regions}
QUANTITY_LIMITED_CUSTOMIZATION_TYPES = {GUI_ITEM_TYPE.PROJECTION_DECAL: MAX_USERS_PROJECTION_DECALS}
PROJECTION_DECAL_IMAGE_FORM_TAG = {ProjectionDecalFormTags.SQUARE: backport.image(R.images.gui.maps.icons.customization.icon_form_1()),
 ProjectionDecalFormTags.RECT1X2: backport.image(R.images.gui.maps.icons.customization.icon_form_2()),
 ProjectionDecalFormTags.RECT1X3: backport.image(R.images.gui.maps.icons.customization.icon_form_3()),
 ProjectionDecalFormTags.RECT1X4: backport.image(R.images.gui.maps.icons.customization.icon_form_4()),
 ProjectionDecalFormTags.RECT1X6: backport.image(R.images.gui.maps.icons.customization.icon_form_6())}
PROJECTION_DECAL_TEXT_FORM_TAG = {ProjectionDecalFormTags.SQUARE: backport.text(R.strings.vehicle_customization.form.formfactor_square()),
 ProjectionDecalFormTags.RECT1X2: backport.text(R.strings.vehicle_customization.form.formfactor_rect1x2()),
 ProjectionDecalFormTags.RECT1X3: backport.text(R.strings.vehicle_customization.form.formfactor_rect1x3()),
 ProjectionDecalFormTags.RECT1X4: backport.text(R.strings.vehicle_customization.form.formfactor_rect1x4()),
 ProjectionDecalFormTags.RECT1X6: backport.text(R.strings.vehicle_customization.form.formfactor_rect1x6())}
PROJECTION_DECAL_FORM_TO_UI_ID = {ProjectionDecalFormTags.SQUARE: 1,
 ProjectionDecalFormTags.RECT1X2: 2,
 ProjectionDecalFormTags.RECT1X3: 3,
 ProjectionDecalFormTags.RECT1X4: 4,
 ProjectionDecalFormTags.RECT1X6: 6}
SEASON_IDX_TO_TYPE = {SEASONS_CONSTANTS.SUMMER_INDEX: SeasonType.SUMMER,
 SEASONS_CONSTANTS.WINTER_INDEX: SeasonType.WINTER,
 SEASONS_CONSTANTS.DESERT_INDEX: SeasonType.DESERT}
SEASON_TYPE_TO_NAME = {SeasonType.SUMMER: SEASONS_CONSTANTS.SUMMER,
 SeasonType.WINTER: SEASONS_CONSTANTS.WINTER,
 SeasonType.DESERT: SEASONS_CONSTANTS.DESERT}
SEASON_TYPE_TO_IDX = {SeasonType.SUMMER: SEASONS_CONSTANTS.SUMMER_INDEX,
 SeasonType.WINTER: SEASONS_CONSTANTS.WINTER_INDEX,
 SeasonType.DESERT: SEASONS_CONSTANTS.DESERT_INDEX}
SEASONS_ORDER = (SeasonType.SUMMER, SeasonType.WINTER, SeasonType.DESERT)
CartInfo = namedtuple('CartInfo', 'totalPrice numSelected numApplying numBought numTotal isAtLeastOneItemFromInventory isAtLeastOneItemDismantled')

class MoneyForPurchase(object):
    NOT_ENOUGH = 0
    ENOUGH_WITH_EXCHANGE = 1
    ENOUGH = 2


class AdditionalPurchaseGroups(object):
    STYLES_GROUP_ID = -1
    UNASSIGNED_GROUP_ID = -2


class CartExchangeCreditsInfoItem(InfoItemBase):

    @property
    def itemTypeName(self):
        pass

    @property
    def userName(self):
        pass

    @property
    def itemTypeID(self):
        return GUI_ITEM_TYPE.CUSTOMIZATION

    def getExtraIconInfo(self):
        return None

    def getGUIEmblemID(self):
        pass


class CustomizationTankPartNames(TankPartNames):
    MASK = 'mask'
    ALL = TankPartNames.ALL + (MASK,)


def chooseMode(itemTypeID, modeId, vehicle):
    if modeId == CustomizationModes.EDITABLE_STYLE:
        return HighlightingMode.WHOLE_VEHICLE
    if itemTypeID == GUI_ITEM_TYPE.CAMOUFLAGE:
        if not __isTurretCustomizable(vehicle.descriptor):
            return HighlightingMode.CAMO_REGIONS_SKIP_TURRET
        return HighlightingMode.CAMO_REGIONS
    return HighlightingMode.REPAINT_REGIONS_MERGED if itemTypeID == GUI_ITEM_TYPE.PAINT else HighlightingMode.WHOLE_VEHICLE


def getAvailableRegions(areaId, slotType, vehicleDescr=None):
    if vehicleDescr is None:
        if not g_currentVehicle.isPresent():
            return ()
        vehicleDescr = g_currentVehicle.item.descriptor
    outfit = Outfit(vehicleCD=vehicleDescr.makeCompactDescr())
    container = outfit.getContainer(areaId)
    if container is None:
        return ()
    else:
        slot = container.slotFor(slotType)
        if slot is None:
            return ()
        if slotType in (GUI_ITEM_TYPE.MODIFICATION,):
            if areaId == Area.MISC:
                return (0,)
            return ()
        if slotType in (GUI_ITEM_TYPE.PROJECTION_DECAL, GUI_ITEM_TYPE.ATTACHMENT, GUI_ITEM_TYPE.SEQUENCE):
            return tuple(range(len(slot.getRegions())))
        if slotType in (GUI_ITEM_TYPE.INSCRIPTION, GUI_ITEM_TYPE.EMBLEM):
            return __getAvailableDecalRegions(areaId, slotType, vehicleDescr)
        if slotType in (GUI_ITEM_TYPE.PAINT, GUI_ITEM_TYPE.CAMOUFLAGE):
            return __getAppliedToRegions(areaId, slotType, vehicleDescr)
        _logger.error('Wrong customization slotType: %s', slotType)
        return ()


def getCustomizationTankPartName(areaId, regionIdx):
    return CustomizationTankPartNames.MASK if areaId == TankPartIndexes.GUN and regionIdx == C11N_MASK_REGION else TankPartIndexes.getName(areaId)


def createCustomizationBaseRequestCriteria(vehicle, progress, appliedItems, season=None, itemTypeID=None):
    season = season or SeasonType.ALL
    criteria = REQ_CRITERIA.CUSTOM(lambda item: (not itemTypeID or item.itemTypeID == itemTypeID) and item.season & season and (not item.requiredToken or progress.getTokenCount(item.requiredToken) > 0) and (item.buyCount > 0 or item.fullInventoryCount(vehicle.intCD) > 0 or appliedItems and item.intCD in appliedItems or item.installedCount() > 0 and not item.isVehicleBound) and item.mayInstall(vehicle) and (not item.isProgressive or item.getLatestOpenedProgressionLevel(vehicle) > 0))
    return criteria


def isOutfitVisuallyEmpty(oufit):
    customizationService = dependency.instance(ICustomizationService)
    return isEmpty((intCD for intCD in oufit.items() if not customizationService.getItemByCD(intCD).isHiddenInUI()))


def fromWorldCoordsToHangarVehicle(worldCoords):
    compoundModel = g_currentVehicle.hangarSpace.space.getVehicleEntity().appearance.compoundModel
    modelMat = Math.Matrix(compoundModel.matrix)
    modelMat.invert()
    return modelMat.applyPoint(worldCoords)


def fromHangarVehicleToWorldCoords(hangarVehicleCoords):
    compoundModel = g_currentVehicle.hangarSpace.space.getVehicleEntity().appearance.compoundModel
    modelMatrix = Math.Matrix(compoundModel.matrix)
    return modelMatrix.applyPoint(hangarVehicleCoords)


def slotsIdsFromAppliedTo(appliedTo, slotType):
    st = scaffold()
    result = list()
    for region in ApplyArea.RANGE:
        if appliedTo & region:
            areaId = AREA_ID_BY_REGION[region]
            slot = st[areaId].slotFor(slotType)
            if slot is not None:
                regions = slot.getRegions()
                regionIdx = next((i for i, rg in enumerate(regions) if rg == region), -1)
                result.append((areaId, slotType, regionIdx))

    return result


def appliedToFromSlotsIds(slotsIds):
    st = scaffold()
    appliedTo = 0
    for slotId in slotsIds:
        areaId, slotType, regionIdx = slotId
        slot = st[areaId].slotFor(slotType)
        if slot is not None:
            regions = slot.getRegions()
            region = regions[regionIdx] if len(regions) > regionIdx else ApplyArea.NONE
            appliedTo |= region

    return appliedTo


def getVehiclePartByIdx(vehicleDescriptor, partIdx):
    vehiclePart = None
    if partIdx == TankPartIndexes.CHASSIS:
        vehiclePart = vehicleDescriptor.chassis
    if partIdx == TankPartIndexes.TURRET:
        vehiclePart = vehicleDescriptor.turret
    if partIdx == TankPartIndexes.HULL:
        vehiclePart = vehicleDescriptor.hull
    if partIdx == TankPartIndexes.GUN:
        vehiclePart = vehicleDescriptor.gun
    return vehiclePart


def getTotalPurchaseInfo(purchaseItems):
    numSelectedItems = 0
    numApplyingItems = 0
    isAtLeastOneItemFromInventory = False
    isAtLeastOneItemDismantled = False
    itemCartInfo = {}
    for purchaseItem in purchaseItems:
        if purchaseItem.item is not None:
            itemCD = purchaseItem.item.intCD
            if itemCD not in itemCartInfo.keys():
                itemCartInfo.update({itemCD: {'totalPrice': ITEM_PRICE_EMPTY,
                          'quantity': 0}})
            if not purchaseItem.isDismantling:
                numApplyingItems += 1
                if purchaseItem.selected:
                    numSelectedItems += 1
                    itemCartInfo[itemCD]['totalPrice'] += purchaseItem.price
                    itemCartInfo[itemCD]['quantity'] += 1
                    if purchaseItem.isFromInventory:
                        isAtLeastOneItemFromInventory = True
                if purchaseItem.isFromInventory:
                    itemCartInfo[itemCD]['totalPrice'] -= purchaseItem.price
                    itemCartInfo[itemCD]['quantity'] -= 1
            else:
                isAtLeastOneItemDismantled = True

    totalPrice = sum([ item['totalPrice'] for item in itemCartInfo.itervalues() if item['totalPrice'].price > ZERO_MONEY ], ITEM_PRICE_EMPTY)
    numBoughtItems = sum((item['quantity'] for item in itemCartInfo.itervalues() if item['quantity'] > 0))
    return CartInfo(totalPrice, numSelectedItems, numApplyingItems, numBoughtItems, len(purchaseItems), isAtLeastOneItemFromInventory, isAtLeastOneItemDismantled)


def containsVehicleBound(purchaseItems):
    fromInventoryCounter = Counter()
    vehCD = g_currentVehicle.item.intCD
    for purchaseItem in purchaseItems:
        if purchaseItem.item and purchaseItem.item.isVehicleBound and not purchaseItem.item.isProgressionAutoBound and not purchaseItem.isDismantling and not purchaseItem.item.isRentable:
            if not purchaseItem.isFromInventory:
                return True
            fromInventoryCounter[purchaseItem.item] += 1

    for item in fromInventoryCounter:
        fromInventoryCounter[item] -= item.installedCount(vehCD)

    return any((count > item.boundInventoryCount(vehCD) for item, count in fromInventoryCounter.items()))


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
    return moneyState != MoneyForPurchase.NOT_ENOUGH or Currency.GOLD in shortage.getCurrency()


def isVehicleCanBeCustomized(vehicle, itemTypeID, itemsFilter=None):
    if itemTypeID not in C11N_ITEM_TYPE_MAP:
        _logger.error('Failed to get customization item from cache. Wrong itemTypeID: %s', itemTypeID)
        return False
    else:
        cType = C11N_ITEM_TYPE_MAP[itemTypeID]
        customizationCache = g_cache.customization20().itemTypes
        if cType not in customizationCache:
            _logger.error('Failed to get customization item from cache. Wrong cType: %s', cType)
            return False
        for areaId in Area.ALL:
            if any(vehicle.getAnchors(itemTypeID, areaId)):
                break
        else:
            return False

        customizationService = dependency.instance(ICustomizationService)
        eventsCache = dependency.instance(IEventsCache)
        requirement = createCustomizationBaseRequestCriteria(vehicle, eventsCache.questsProgress, set(), itemTypeID=itemTypeID)
        if itemsFilter is not None:
            requirement |= REQ_CRITERIA.CUSTOM(itemsFilter)
        for itemID in customizationCache[cType]:
            if itemID == EMPTY_ITEM_ID:
                continue
            item = customizationService.getItemByID(itemTypeID, itemID)
            if requirement(item):
                return True

        return False


def getBaseStyleItems():
    items = set()
    c11nService = dependency.instance(ICustomizationService)
    ctx = c11nService.getCtx()
    if ctx is None:
        return items
    else:
        styleDescr = ctx.mode.currentOutfit.style
        if styleDescr is not None:
            style = c11nService.getItemByID(GUI_ITEM_TYPE.STYLE, styleDescr.id)
            for season in SeasonType.COMMON_SEASONS:
                outfit = style.getOutfit(season, vehicleCD=g_currentVehicle.item.descriptor.makeCompactDescr())
                items.update(outfit.items())

        return items


def checkIsFirstProgressionDecalOnVehicle(vehicleCD, newItemsCDs):
    itemsCache = dependency.instance(IItemsCache)
    progressionData = itemsCache.items.inventory.getC11nProgressionDataForVehicle(vehicleCD)
    if vehicleCD == UNBOUND_VEH_KEY:
        return False
    for itemCD, c11nProgressData in progressionData.iteritems():
        if c11nProgressData.currentLevel > 1:
            return False
        if c11nProgressData.currentLevel == 1 and itemCD not in newItemsCDs:
            return False

    return True


def __isTurretCustomizable(vhicleDescriptor):
    applyAreaMask, _ = vhicleDescriptor.turret.customizableVehicleAreas['camouflage']
    return bool(ApplyArea.TURRET & applyAreaMask)


def __getAvailableDecalRegions(areaId, slotType, vehicleDescr):
    showTurretEmblemsOnGun = vehicleDescr.turret.showEmblemsOnGun
    if areaId == TankPartIndexes.HULL:
        anchors = vehicleDescr.hull.emblemSlots
    elif areaId == TankPartIndexes.GUN and showTurretEmblemsOnGun:
        anchors = vehicleDescr.turret.emblemSlots
    elif areaId == TankPartIndexes.TURRET and not showTurretEmblemsOnGun:
        anchors = vehicleDescr.turret.emblemSlots
    else:
        return ()
    anchorType = SLOT_TYPE_TO_ANCHOR_TYPE_MAP[slotType]
    anchors = tuple((anchor for anchor in anchors if anchor.type == anchorType))
    return tuple(range(len(anchors)))


def __getAppliedToRegions(areaId, slotType, vehicleDescr):
    if areaId not in Area.TANK_PARTS:
        return ()
    itemTypeName = GUI_ITEM_TYPE_NAMES[slotType]
    vehiclePart = getVehiclePartByIdx(vehicleDescr, areaId)
    _, regionNames = vehiclePart.customizableVehicleAreas[itemTypeName]
    return tuple((C11N_GUN_APPLY_REGIONS[regionName] for regionName in regionNames)) if areaId == TankPartIndexes.GUN else tuple(range(len(regionNames)))
