# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/shared.py
import logging
from collections import namedtuple, Counter
import struct
from itertools import ifilter
import typing
import BigWorld
import Math
import nations
from AccountCommands import isCodeValid
from CurrentVehicle import g_currentVehicle
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from constants import REQUEST_COOLDOWN
from gui import GUI_NATIONS_ORDER_INDICES
from gui.Scaleform import getNationsFilterAssetPath
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.customization.constants import CustomizationModes
from gui.customization.shared import QUANTITY_LIMITED_CUSTOMIZATION_TYPES, appliedToFromSlotsIds, C11nId, PurchaseItem, AdditionalPurchaseGroups, isVehicleCanBeCustomized, getAvailableRegions, EDITABLE_STYLE_APPLY_TO_ALL_AREAS_TYPES, EDITABLE_STYLE_IRREMOVABLE_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.hangar_cameras.hangar_camera_common import CameraMovementStates
from gui.shared.formatters import icons, text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER, VEHICLE_TAGS
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.money import Money
from gui.shared.utils import code2str
from helpers import dependency, int2roman
from helpers.func_utils import CallParams, cooldownCallerDecorator
from helpers.i18n import makeString as _ms
from items import parseIntCompactDescr
from items.components.c11n_components import getItemSlotType
from items.components.c11n_constants import SeasonType, ProjectionDecalFormTags, ProjectionDecalDirectionTags
from items.vehicles import VEHICLE_CLASS_TAGS
from shared_utils import first
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from vehicle_outfit.containers import SlotData
from vehicle_outfit.outfit import Area, Outfit
from vehicle_outfit.packers import ProjectionDecalPacker
_logger = logging.getLogger(__name__)
EMPTY_PERSONAL_NUMBER = ''

class CustomizationTabs(object):
    DEFAULT = -1
    PAINTS = 1
    CAMOUFLAGES = 2
    PROJECTION_DECALS = 3
    EMBLEMS = 4
    INSCRIPTIONS = 5
    MODIFICATIONS = 6
    STYLES = 7
    ALL = (PAINTS,
     CAMOUFLAGES,
     PROJECTION_DECALS,
     EMBLEMS,
     INSCRIPTIONS,
     MODIFICATIONS,
     STYLES)
    REGIONS = (PAINTS,
     CAMOUFLAGES,
     MODIFICATIONS,
     STYLES)
    MODES = {CustomizationModes.CUSTOM: (PAINTS,
                                 CAMOUFLAGES,
                                 PROJECTION_DECALS,
                                 EMBLEMS,
                                 INSCRIPTIONS,
                                 MODIFICATIONS),
     CustomizationModes.STYLED: (STYLES,),
     CustomizationModes.EDITABLE_STYLE: (PAINTS,
                                         CAMOUFLAGES,
                                         PROJECTION_DECALS,
                                         EMBLEMS,
                                         INSCRIPTIONS,
                                         MODIFICATIONS)}
    SLOT_TYPES = {PAINTS: GUI_ITEM_TYPE.PAINT,
     CAMOUFLAGES: GUI_ITEM_TYPE.CAMOUFLAGE,
     PROJECTION_DECALS: GUI_ITEM_TYPE.PROJECTION_DECAL,
     EMBLEMS: GUI_ITEM_TYPE.EMBLEM,
     INSCRIPTIONS: GUI_ITEM_TYPE.INSCRIPTION,
     MODIFICATIONS: GUI_ITEM_TYPE.MODIFICATION,
     STYLES: GUI_ITEM_TYPE.STYLE}
    ITEM_TYPES = {PAINTS: (GUI_ITEM_TYPE.PAINT,),
     CAMOUFLAGES: (GUI_ITEM_TYPE.CAMOUFLAGE,),
     PROJECTION_DECALS: (GUI_ITEM_TYPE.PROJECTION_DECAL,),
     EMBLEMS: (GUI_ITEM_TYPE.EMBLEM,),
     INSCRIPTIONS: (GUI_ITEM_TYPE.INSCRIPTION, GUI_ITEM_TYPE.PERSONAL_NUMBER),
     MODIFICATIONS: (GUI_ITEM_TYPE.MODIFICATION,),
     STYLES: (GUI_ITEM_TYPE.STYLE,)}


ITEM_TYPE_TO_TAB = {value:key for key, values in CustomizationTabs.ITEM_TYPES.iteritems() for value in values}
ITEM_TYPE_TO_SLOT_TYPE = {itemType:CustomizationTabs.SLOT_TYPES[tabId] for itemType, tabId in ITEM_TYPE_TO_TAB.iteritems()}
REGIONS_SLOTS = tuple((CustomizationTabs.SLOT_TYPES[tabId] for tabId in CustomizationTabs.REGIONS))
APPLIED_TO_TYPES = (GUI_ITEM_TYPE.EMBLEM,
 GUI_ITEM_TYPE.INSCRIPTION,
 GUI_ITEM_TYPE.PERSONAL_NUMBER,
 GUI_ITEM_TYPE.PAINT,
 GUI_ITEM_TYPE.CAMOUFLAGE)
SCALE_SIZE = (VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_SCALE_SMALL, VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_SCALE_NORMAL, VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_SCALE_LARGE)
TYPES_ORDER = (GUI_ITEM_TYPE.PAINT,
 GUI_ITEM_TYPE.CAMOUFLAGE,
 GUI_ITEM_TYPE.PROJECTION_DECAL,
 GUI_ITEM_TYPE.EMBLEM,
 GUI_ITEM_TYPE.PERSONAL_NUMBER,
 GUI_ITEM_TYPE.INSCRIPTION,
 GUI_ITEM_TYPE.MODIFICATION,
 GUI_ITEM_TYPE.STYLE)
SEASON_TYPE_TO_INFOTYPE_MAP = {SeasonType.SUMMER: VEHICLE_CUSTOMIZATION.CUSTOMIZATION_INFOTYPE_MAPTYPE_SUMMER,
 SeasonType.DESERT: VEHICLE_CUSTOMIZATION.CUSTOMIZATION_INFOTYPE_MAPTYPE_DESERT,
 SeasonType.WINTER: VEHICLE_CUSTOMIZATION.CUSTOMIZATION_INFOTYPE_MAPTYPE_WINTER}
OutfitInfo = namedtuple('OutfitInfo', ('original', 'modified'))
CustomizationSlotUpdateVO = namedtuple('CustomizationSlotUpdateVO', ('slotId', 'itemIntCD', 'uid'))

@dependency.replace_none_kwargs(c11nService=ICustomizationService)
def getCustomPurchaseItems(season, modifiedOutfits, c11nService=None):
    purchaseItems = []
    seasonOrder = [season] + [ s for s in SeasonType.COMMON_SEASONS if s != season ]
    vehicleCD = g_currentVehicle.item.descriptor.makeCompactDescr()
    inventoryCounts = __getInventoryCounts(modifiedOutfits, vehicleCD)
    for s in seasonOrder:
        for intCD, component, idx, container, _ in modifiedOutfits[s].itemsFull():
            item = c11nService.getItemByCD(intCD)
            isFromInventory = inventoryCounts[intCD] > 0
            slotType = ITEM_TYPE_TO_SLOT_TYPE.get(item.itemTypeID)
            if slotType is None:
                _logger.error('Failed to get slotType for purchaseItem: [%s]', item)
                continue
            purchaseItems.append(PurchaseItem(item, price=item.getBuyPrice(), areaID=container.getAreaID(), slotType=slotType, regionIdx=idx, selected=True, group=s, isFromInventory=isFromInventory, component=component))
            inventoryCounts[intCD] -= 1

    return purchaseItems


@dependency.replace_none_kwargs(c11nService=ICustomizationService)
def getStylePurchaseItems(style, modifiedOutfits, c11nService=None, prolongRent=False, progressionLevel=-1):
    purchaseItems = []
    vehicle = g_currentVehicle.item
    vehicleCD = vehicle.descriptor.makeCompactDescr()
    isStyleInstalled = c11nService.getCurrentOutfit(SeasonType.SUMMER).id == style.id
    inventoryCounts = __getInventoryCounts(modifiedOutfits, vehicleCD)
    styleCount = style.fullInventoryCount(vehicle.intCD)
    isFromInventory = not prolongRent and (styleCount > 0 or isStyleInstalled)
    if style.isProgressive:
        totalPrice = ItemPrice(Money(), Money())
        currentProgressionLvl = style.getLatestOpenedProgressionLevel(vehicle)
        progressivePrice = style.getUpgradePrice(currentProgressionLvl, progressionLevel)
        if style.isProgressionPurchasable(progressionLevel):
            totalPrice = progressivePrice
        if not style.isHidden and not isFromInventory:
            totalPrice += style.getBuyPrice()
        isFromInventory = False if progressionLevel > currentProgressionLvl else isFromInventory
        purchaseItem = PurchaseItem(style, totalPrice, areaID=None, slotType=None, regionIdx=None, selected=True, group=AdditionalPurchaseGroups.STYLES_GROUP_ID, isFromInventory=isFromInventory, locked=True, progressionLevel=progressionLevel)
        purchaseItems.append(purchaseItem)
    else:
        purchaseItem = PurchaseItem(style, style.getBuyPrice(), areaID=None, slotType=None, regionIdx=None, selected=True, group=AdditionalPurchaseGroups.STYLES_GROUP_ID, isFromInventory=isFromInventory, locked=True)
        purchaseItems.append(purchaseItem)
    for season in SeasonType.COMMON_SEASONS:
        modifiedOutfit = modifiedOutfits[season]
        if style.isProgressive:
            modifiedOutfit = c11nService.removeAdditionalProgressionData(outfit=modifiedOutfit, style=style, vehCD=vehicleCD, season=season)
        baseOutfit = style.getOutfit(season, vehicleCD)
        for intCD, component, regionIdx, container, _ in modifiedOutfit.itemsFull():
            item = c11nService.getItemByCD(intCD)
            itemTypeID = item.itemTypeID
            slotType = ITEM_TYPE_TO_SLOT_TYPE.get(itemTypeID)
            if slotType is None:
                continue
            slotId = C11nId(container.getAreaID(), slotType, regionIdx)
            modifiedSlotData = SlotData(intCD, component)
            baseSlotData = getSlotDataFromSlot(baseOutfit, slotId)
            isEdited = baseSlotData.intCD != modifiedSlotData.intCD
            if isEdited:
                if slotId != correctSlot(slotId):
                    continue
                price = item.getBuyPrice()
                isFromInventory = inventoryCounts[intCD] > 0 or item.isStyleOnly
                locked = bool(style.getDependenciesIntCDs()) and itemTypeID in EDITABLE_STYLE_IRREMOVABLE_TYPES and itemTypeID != GUI_ITEM_TYPE.CAMOUFLAGE
            else:
                price = ItemPrice(Money(credits=0), Money())
                isFromInventory = True
                locked = isPurchaseItemLocked(item, style)
            purchaseItem = PurchaseItem(item, price=price, areaID=slotId.areaId, slotType=slotId.slotType, regionIdx=slotId.regionIdx, selected=True, group=season, isFromInventory=isFromInventory, component=component, locked=locked, isEdited=isEdited)
            purchaseItems.append(purchaseItem)
            inventoryCounts[intCD] -= 1

    return purchaseItems


def correctSlot(slotId):
    if slotId.slotType in EDITABLE_STYLE_APPLY_TO_ALL_AREAS_TYPES:
        slotId = EDITABLE_STYLE_APPLY_TO_ALL_AREAS_TYPES[slotId.slotType]
    return slotId


def fitOutfit(outfit, availableRegionsMap):
    for container in outfit.containers():
        areaRegions = availableRegionsMap.get(container.getAreaID(), {})
        for slot in container.slots():
            availableRegions = set()
            isProjectionDecal = False
            slotItemTypes = slot.getTypes()
            if {GUI_ITEM_TYPE.SEQUENCE, GUI_ITEM_TYPE.ATTACHMENT, GUI_ITEM_TYPE.INSIGNIA} & set(slotItemTypes):
                continue
            for itemType in slotItemTypes:
                availableRegions.update(areaRegions.get(itemType, ()))
                isProjectionDecal |= itemType == GUI_ITEM_TYPE.PROJECTION_DECAL

            for regionIdx in range(slot.capacity()):
                component = slot.getComponent(regionIdx)
                if component is None:
                    continue
                if isProjectionDecal and (component.slotId == ProjectionDecalPacker.STYLED_SLOT_ID or component.matchingTag):
                    continue
                if regionIdx not in availableRegions:
                    slot.remove(regionIdx)

    outfit.invalidateItemsCounter()
    return


def getOutfitWithoutItems(outfitsInfo, intCD, count):
    customizationService = dependency.instance(ICustomizationService)
    for season, outfitCompare in outfitsInfo.iteritems():
        backward = outfitCompare.modified.diff(outfitCompare.original)
        for container in backward.containers():
            for slot in container.slots():
                for idx in range(slot.capacity()):
                    regionIntCD = slot.getItemCD(idx)
                    if regionIntCD == intCD and count:
                        item = customizationService.getItemByCD(regionIntCD)
                        outfit = outfitCompare.original
                        container = outfit.getContainer(container.getAreaID())
                        slot = container.slotFor(item.itemTypeID)
                        slot.remove(idx)
                        count -= 1

        yield (season, outfitCompare.original)


def getOutfitWithoutItemsNoDiff(outfits, intCD, count):
    for season, outfit in outfits.iteritems():
        for container in outfit.containers():
            for slot in container.slots():
                for idx in range(slot.capacity()):
                    regionIntCD = slot.getItemCD(idx)
                    if regionIntCD == intCD and count:
                        container = outfit.getContainer(container.getAreaID())
                        slot.remove(idx)
                        count -= 1

        yield (season, outfit)


def fromWorldCoordsToHangarVehicle(worldCoords):
    compoundModel = g_currentVehicle.hangarSpace.space.getVehicleEntity().appearance.compoundModel
    modelMat = Math.Matrix(compoundModel.matrix)
    modelMat.invert()
    return modelMat.applyPoint(worldCoords)


def fromHangarVehicleToWorldCoords(hangarVehicleCoords):
    compoundModel = g_currentVehicle.hangarSpace.space.getVehicleEntity().appearance.compoundModel
    modelMatrix = Math.Matrix(compoundModel.matrix)
    return modelMatrix.applyPoint(hangarVehicleCoords)


def getSuitableText(item, currentVehicle=None, formatVehicle=True):
    conditions = []
    for node in item.descriptor.filter.include:
        separator = ' '.join(['&nbsp;&nbsp;', icons.makeImageTag(RES_ICONS.MAPS_ICONS_CUSTOMIZATION_TOOLTIP_SEPARATOR, 3, 21, -6), '  '])
        if node.nations:
            sortedNations = sorted(node.nations, key=GUI_NATIONS_ORDER_INDICES.get)
            for nation in sortedNations:
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
            vehicleName = makeVehiclesShortNamesString(set(node.vehicles), currentVehicle, flat=True)
            conditions.append(text_styles.main(vehicleName) if formatVehicle else vehicleName)
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


def formatPersonalNumber(number, digitsCount):
    return number.rjust(digitsCount, '0')


def fitPersonalNumber(number, digitsCount):
    return number[max(0, len(number) - digitsCount):]


def getProjectionSlotFormfactor(slotId):
    if slotId.slotType != GUI_ITEM_TYPE.PROJECTION_DECAL:
        return None
    else:
        anchorSlot = g_currentVehicle.item.getAnchorBySlotId(slotId.slotType, slotId.areaId, slotId.regionIdx)
        return ProjectionDecalFormTags.ALL.index(first(anchorSlot.formfactors))


def getMultiSlot(outfit, slotId):
    container = outfit.getContainer(slotId.areaId)
    return None if container is None else container.slotFor(slotId.slotType)


def getSlotDataFromSlot(outfit, slotId):
    multiSlot = getMultiSlot(outfit, slotId)
    return None if multiSlot is None else multiSlot.getSlotData(slotId.regionIdx)


@dependency.replace_none_kwargs(service=ICustomizationService)
def getItemFromSlot(outfit, slotId, service=None):
    if slotId.slotType == GUI_ITEM_TYPE.STYLE:
        if outfit.id:
            return service.getItemByID(GUI_ITEM_TYPE.STYLE, outfit.id)
        return
    else:
        slotData = getSlotDataFromSlot(outfit, slotId)
        if slotData is None:
            return
        return None if not slotData.intCD else service.getItemByCD(slotData.intCD)


def getComponentFromSlot(outfit, slotId):
    slotData = getSlotDataFromSlot(outfit, slotId)
    return None if slotData is None else slotData.component


def isNeedToMirrorProjectionDecal(item, slot):
    if not item.canBeMirroredHorizontally:
        return False
    return False if item.direction == ProjectionDecalDirectionTags.ANY or slot.direction == ProjectionDecalDirectionTags.ANY else item.direction != slot.direction


def isSlotFilled(outfit, slotId):
    if slotId.slotType == GUI_ITEM_TYPE.STYLE:
        return bool(outfit.id)
    else:
        component = getComponentFromSlot(outfit, slotId)
        return component is not None and component.isFilled()


def isItemLimitReached(item, outfits=None, customizationMode=None):
    if not item.isLimited and not item.isHidden:
        return False
    if customizationMode:
        inventoryCount = customizationMode.getItemInventoryCount(item)
    else:
        inventoryCount = getItemInventoryCount(item, outfits)
    if inventoryCount > 0:
        return False
    if item.buyCount == 0:
        return True
    purchaseLimit = getPurchaseLimit(item, outfits)
    return purchaseLimit == 0


def getPurchaseLimit(item, outfits=None):
    appliedCount = getItemAppliedCount(item, outfits)
    inventoryCount = item.fullInventoryCount(g_currentVehicle.intCD)
    purchaseLimit = item.buyCount - max(appliedCount - inventoryCount, 0)
    return max(purchaseLimit, 0)


@dependency.replace_none_kwargs(service=ICustomizationService)
def isItemsQuantityLimitReached(outfit, itemType, service=None):
    if itemType not in QUANTITY_LIMITED_CUSTOMIZATION_TYPES:
        return False
    qty = 0
    for intCD, component, _, _, _ in outfit.itemsFull():
        item = service.getItemByCD(intCD)
        if item.itemTypeID == itemType and component.isFilled():
            qty += 1

    return qty >= QUANTITY_LIMITED_CUSTOMIZATION_TYPES[itemType]


def getEmptyRegions(outfit, slotType):
    emptyRegions = []
    for areaId in Area.ALL:
        regionsIndexes = getAvailableRegions(areaId, slotType)
        for regionIdx in regionsIndexes:
            intCD = outfit.getContainer(areaId).slotFor(slotType).getItemCD(regionIdx)
            if not intCD:
                emptyRegions.append((areaId, slotType, regionIdx))

    mask = appliedToFromSlotsIds(emptyRegions)
    return mask


def getCurrentVehicleAvailableRegionsMap():
    availableRegionsMap = {}
    for areaId in Area.ALL:
        availableRegionsMap[areaId] = {}
        for slotType in CustomizationTabs.SLOT_TYPES.itervalues():
            regions = getAvailableRegions(areaId, slotType)
            availableRegionsMap[areaId][slotType] = regions

    return availableRegionsMap


def checkSlotsFilling(outfit, slotType):
    availableCount = 0
    filledCount = 0
    for areaId in Area.ALL:
        regionsIndexes = getAvailableRegions(areaId, slotType)
        availableCount += len(regionsIndexes)
        for regionIdx in regionsIndexes:
            intCD = outfit.getContainer(areaId).slotFor(slotType).getItemCD(regionIdx)
            if intCD:
                filledCount += 1

    if slotType in QUANTITY_LIMITED_CUSTOMIZATION_TYPES:
        availableCount = min(availableCount, QUANTITY_LIMITED_CUSTOMIZATION_TYPES[slotType])
    return (availableCount, filledCount)


def isSlotLocked(outfit, slotId):
    if slotId.slotType not in QUANTITY_LIMITED_CUSTOMIZATION_TYPES:
        return False
    limit = QUANTITY_LIMITED_CUSTOMIZATION_TYPES[slotId.slotType]
    slot = outfit.getContainer(slotId.areaId).slotFor(slotId.slotType)
    regions = slot.getRegions()
    filledRegions = [ regions.index(region) for region, _, __ in slot.items() ]
    isLocked = len(filledRegions) >= limit and slotId.regionIdx not in filledRegions
    return isLocked


def isPurchaseItemLocked(item, style):
    sType = getItemSlotType(item.descriptor)
    locked = item.itemTypeID in EDITABLE_STYLE_IRREMOVABLE_TYPES or sType not in style.changeableSlotTypes
    return locked


@dependency.replace_none_kwargs(service=ICustomizationService)
def isItemUsedUp(item, service=None):
    ctx = service.getCtx()
    if ctx is None:
        _logger.warning('Customization helper function "isItemUsedUp" is used out of customization context')
        return False
    if item.itemTypeID == GUI_ITEM_TYPE.STYLE:
        isApplied = ctx.modeId == CustomizationModes.STYLED and ctx.mode.modifiedStyle == item
    else:
        isApplied = any((ctx.mode.getModifiedOutfit(s).has(item) for s in SeasonType.COMMON_SEASONS))
    if isApplied:
        return False
    elif ctx.mode.getItemInventoryCount(item) > 0:
        return False
    else:
        return False if ctx.mode.getPurchaseLimit(item) > 0 else True


def getItemInventoryCount(item, outfits=None):
    if item.itemTypeID == GUI_ITEM_TYPE.STYLE:
        inventoryCount = __getStyleInventoryCount(item, outfits)
    else:
        inventoryCount = __getItemInventoryCount(item, outfits)
    return max(0, inventoryCount)


def getItemAppliedCount(item, outfits):
    if item.itemTypeID == GUI_ITEM_TYPE.STYLE:
        appliedCount = __getStyleAppliedCount(item, outfits)
    else:
        appliedCount = __getItemAppliedCount(item, outfits)
    return appliedCount


def getItemInstalledCount(item):
    if item.itemTypeID == GUI_ITEM_TYPE.STYLE:
        installedCount = int(__isStyleInstalled(item))
    else:
        installedCount = item.installedCount(g_currentVehicle.intCD)
    return installedCount


def getProgressionItemStatusText(level):
    return backport.text(R.strings.vehicle_customization.progression.item.doneFirst()) if level == 1 else backport.text(R.strings.vehicle_customization.customization.infotype.progression.achievedState(), level=int2roman(level))


def vehicleHasSlot(slotType, vehicle=None):
    vehicle = vehicle or g_currentVehicle.item
    for areaId in Area.ALL:
        if any(vehicle.getAnchors(slotType, areaId)):
            return True

    return False


def getItemTypesAvailableForVehicle(vehicle=None):
    availableItemTypes = set()
    for itemType in GUI_ITEM_TYPE.CUSTOMIZATIONS:
        slotType = ITEM_TYPE_TO_SLOT_TYPE.get(itemType)
        if slotType is not None and vehicleHasSlot(slotType, vehicle):
            availableItemTypes.add(itemType)

    return availableItemTypes


def customizationSlotIdToUid(slotId):
    s = struct.pack('bbh', slotId.areaId, slotId.slotType, slotId.regionIdx)
    uid = struct.unpack('I', s)[0]
    return uid


@dependency.replace_none_kwargs(settingsCore=ISettingsCore)
def getEditableStylesExtraNotificationCounter(styles=None, settingsCore=None):
    vehicle = g_currentVehicle.item
    serverSettings = settingsCore.serverSettings
    if not serverSettings.getOnceOnlyHintsSetting(OnceOnlyHints.C11N_EDITABLE_STYLES_HINT):
        itemsFilter = lambda item: item.isEditable
    elif not serverSettings.getOnceOnlyHintsSetting(OnceOnlyHints.C11N_PROGRESSION_REQUIRED_STYLES_HINT):
        itemsFilter = lambda item: item.isProgressionRequiredCanBeEdited(vehicle.intCD)
    else:
        return 0
    if styles is not None:
        if any(ifilter(itemsFilter, styles)):
            return 1
        return 0
    else:
        return 1 if isVehicleCanBeCustomized(vehicle, GUI_ITEM_TYPE.STYLE, itemsFilter=itemsFilter) else 0


def getEditableStyleOutfitDiffComponent(outfit, baseOutfit):
    component = outfit.pack()
    baseComponent = baseOutfit.pack()
    diffComponent = component.getDiff(baseComponent)
    return diffComponent


def getEditableStyleOutfitDiff(outfit, baseOutfit):
    diffComponent = getEditableStyleOutfitDiffComponent(outfit, baseOutfit)
    diff = diffComponent.makeCompDescr()
    return diff


def isStyleEditedForCurrentVehicle(outfits, style):
    vehicleCD = g_currentVehicle.item.descriptor.makeCompactDescr()
    for season, outfit in outfits.iteritems():
        baseOutfit = style.getOutfit(season, vehicleCD)
        fitOutfit(baseOutfit, getCurrentVehicleAvailableRegionsMap())
        if not outfit.isEqual(baseOutfit):
            return True

    return False


@dependency.replace_none_kwargs(service=ICustomizationService)
def getUnsuitableDependentData(outfit, selCamoItemID, styleDependencies, service=None):
    result = []
    styleDependencies = styleDependencies
    outfitItemsList = tuple(((cIntCD, regionIdx, container) for cIntCD, _, regionIdx, container, _ in outfit.itemsFull()))
    getItemByCD = service.getItemByCD
    camoDependencies = styleDependencies.get(selCamoItemID)
    if camoDependencies:
        for cIntCD, regionIdx, container in outfitItemsList:
            possiblyUnsuitable = getItemByCD(cIntCD)
            posUnsuitTypeId = possiblyUnsuitable.itemTypeID
            posUnsuitType = possiblyUnsuitable.descriptor.itemType
            posUnsuitId = possiblyUnsuitable.id
            dependentByType = camoDependencies.get(posUnsuitType)
            if dependentByType and posUnsuitId not in dependentByType:
                for dependent in styleDependencies.itervalues():
                    dItemIds = dependent.get(posUnsuitType)
                    if dItemIds and posUnsuitId in dItemIds:
                        slotType = ITEM_TYPE_TO_SLOT_TYPE[posUnsuitTypeId]
                        slotIdToChange = C11nId(container.getAreaID(), slotType, regionIdx)
                        result.append((possiblyUnsuitable, slotIdToChange))
                        break

    return result


def __resetC11nItemsNoveltyParamsMerger(merged, callParams):
    items = callParams.kwargs.get('items', [])
    items.extend(merged.kwargs.get('items', []))
    return CallParams(kwargs={'items': items})


@cooldownCallerDecorator(cooldown=REQUEST_COOLDOWN.CUSTOMIZATION_NOVELTY + 0.1, paramsMerger=__resetC11nItemsNoveltyParamsMerger)
def resetC11nItemsNovelty(items):

    def _callback(resultID):
        if not isCodeValid(resultID):
            _logger.error('Error occurred while trying to reset c11n items=%s novelty, reason by resultId = %d: %s', items, resultID, code2str(resultID))

    BigWorld.player().shop.resetC11nItemsNovelty(items, _callback)


def removeUnselectedItemsFromEditableStyle(modifiedOutfits, baseOutfits, purchaseItems):
    for pItem in purchaseItems:
        if pItem.selected:
            continue
        season = pItem.group
        slotId = C11nId(pItem.areaID, pItem.slotType, pItem.regionIdx)
        outfit = modifiedOutfits[season]
        baseOutfit = baseOutfits[season]
        removeItemFromEditableStyle(outfit, baseOutfit, slotId)


def removeItemFromEditableStyle(outfit, baseOutfit, slotId):
    slotType = slotId.slotType
    if slotType in EDITABLE_STYLE_APPLY_TO_ALL_AREAS_TYPES:
        __removeItemFromEditableStyleAllAreas(outfit, baseOutfit, slotType)
        if slotType == GUI_ITEM_TYPE.CAMOUFLAGE:
            slotData = getSlotDataFromSlot(outfit, slotId)
            parsedData = parseIntCompactDescr(compactDescr=slotData.intCD)
            for _, uSlotId in getUnsuitableDependentData(outfit, parsedData[2], outfit.style.dependencies):
                __doItemRemoveFromEditableStyleOutfit(outfit, baseOutfit, uSlotId, True)

    else:
        __removeItemFromEditableStyleOutfit(outfit, baseOutfit, slotId)


@dependency.replace_none_kwargs(service=ICustomizationService)
def removeItemsFromOutfit(outfit, filterMethod, service=None):
    for slot in outfit.slots():
        for idx in range(slot.capacity()):
            intCD = slot.getItemCD(idx)
            if not intCD:
                continue
            item = service.getItemByCD(intCD)
            if item.isHiddenInUI():
                continue
            if filterMethod(item):
                slot.remove(idx)


def __removeItemFromEditableStyleAllAreas(outfit, baseOutfit, slotType):
    for areaId in Area.TANK_PARTS:
        regionsIndexes = getAvailableRegions(areaId, slotType)
        for regionIdx in regionsIndexes:
            slotId = C11nId(areaId=areaId, slotType=slotType, regionIdx=regionIdx)
            __removeItemFromEditableStyleOutfit(outfit, baseOutfit, slotId)


def __removeItemFromEditableStyleOutfit(outfit, baseOutfit, slotId):
    __doItemRemoveFromEditableStyleOutfit(outfit, baseOutfit, slotId, slotId.slotType in EDITABLE_STYLE_IRREMOVABLE_TYPES)


def __doItemRemoveFromEditableStyleOutfit(outfit, baseOutfit, slotId, isSetToDefault):
    multiSlot = outfit.getContainer(slotId.areaId).slotFor(slotId.slotType)
    multiSlot.remove(slotId.regionIdx)
    if isSetToDefault:
        slotData = getSlotDataFromSlot(baseOutfit, slotId)
        if slotData is not None and not slotData.isEmpty():
            multiSlot.set(slotData.intCD, slotId.regionIdx, slotData.component)
    return


def __getItemInventoryCount(item, outfits=None):
    inventoryCount = item.fullInventoryCount(g_currentVehicle.intCD)
    if outfits is not None:
        appliedCount = getItemAppliedCount(item, outfits)
        inventoryCount -= appliedCount
    return inventoryCount


def __getStyleInventoryCount(item, outfits=None):
    if g_currentVehicle is None:
        return 0
    else:
        inventoryCount = item.fullInventoryCount(g_currentVehicle.intCD)
        appliedCount = 0
        if outfits is not None:
            appliedCount = getItemAppliedCount(item, outfits)
            inventoryCount -= appliedCount
        if item.isRentable:
            if getItemInstalledCount(item) + appliedCount:
                inventoryCount += 1
        return inventoryCount


def __getItemAppliedCount(item, outfits):
    appliedCount = sum((outfit.itemsCounter[item.intCD] for outfit in outfits.itervalues()))
    appliedCount -= getItemInstalledCount(item)
    return appliedCount


def __getStyleAppliedCount(item, outfits):
    appliedCount = int(outfits[SeasonType.SUMMER].id == item.id)
    appliedCount -= getItemInstalledCount(item)
    return appliedCount


def __isStyleInstalled(style):
    vehicleItem = g_currentVehicle.item
    if vehicleItem is None:
        return False
    else:
        currentOutfit = vehicleItem.getOutfit(SeasonType.SUMMER)
        return False if currentOutfit is None else currentOutfit.id == style.id


@dependency.replace_none_kwargs(itemsCache=IItemsCache, c11nService=ICustomizationService)
def __getInventoryCounts(modifiedOutfits, vehicleCD, itemsCache=None, c11nService=None):
    inventoryCounts = Counter()
    removedCounts = Counter()
    for modifiedOutfit in modifiedOutfits.itervalues():
        for intCD in modifiedOutfit.items():
            if intCD in inventoryCounts:
                continue
            item = itemsCache.items.getItemByCD(intCD)
            inventoryCounts[intCD] = item.fullInventoryCount(g_currentVehicle.intCD)

    outfit = c11nService.getCurrentOutfit(SeasonType.SUMMER)
    style = c11nService.getItemByID(GUI_ITEM_TYPE.STYLE, outfit.id) if outfit.id else None
    for season in SeasonType.COMMON_SEASONS:
        removed = c11nService.getCurrentOutfit(season)
        if style is not None:
            baseOutfit = style.getOutfit(season, vehicleCD)
            removed = baseOutfit.diff(removed)
        removedCounts += removed.itemsCounter

    for intCD in removedCounts:
        item = itemsCache.items.getItemByCD(intCD)
        if item.isStyleOnly:
            removedCounts[intCD] = 0

    return inventoryCounts + removedCounts
