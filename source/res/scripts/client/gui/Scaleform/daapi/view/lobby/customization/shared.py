# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/shared.py
from collections import namedtuple, Counter
import Math
import nations
from CurrentVehicle import g_currentVehicle
from gui.Scaleform import getNationsFilterAssetPath
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.customization.shared import HighlightingMode, SEASONS_ORDER, AdditionalPurchaseGroups, PurchaseItem
from gui.hangar_cameras.hangar_camera_common import CameraMovementStates
from gui.shared.formatters import icons, text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER, VEHICLE_TAGS
from helpers import dependency, int2roman
from helpers.i18n import makeString as _ms
from items.components.c11n_constants import SeasonType, ProjectionDecalFormTags
from items.vehicles import VEHICLE_CLASS_TAGS
from shared_utils import CONST_CONTAINER, first
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
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
REGIONS_SLOTS = tuple((TABS_SLOT_TYPE_MAPPING[regionTab] for regionTab in C11nTabs.REGIONS))
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
SCALE_SIZE = (VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_SCALE_SMALL, VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_SCALE_NORMAL, VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_SCALE_LARGE)
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
    if buyMore and modified is not None:
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


def fromWorldCoordsToHangarVehicle(worldCoords):
    compoundModel = g_currentVehicle.hangarSpace.space.getVehicleEntity().appearance.compoundModel
    modelMat = Math.Matrix(compoundModel.matrix)
    modelMat.invert()
    return modelMat.applyPoint(worldCoords)


def fromHangarVehicleToWorldCoords(hangarVehicleCoords):
    compoundModel = g_currentVehicle.hangarSpace.space.getVehicleEntity().appearance.compoundModel
    modelMatrix = Math.Matrix(compoundModel.matrix)
    return modelMatrix.applyPoint(hangarVehicleCoords)


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
            conditions.append(text_styles.main(makeVehiclesShortNamesString(set(node.vehicles), currentVehicle, flat=True)))
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


def getProjectionSlotFormfactor(anchorId):
    if anchorId.slotType != GUI_ITEM_TYPE.PROJECTION_DECAL:
        return None
    else:
        anchorSlot = g_currentVehicle.item.getAnchorBySlotId(anchorId.slotType, anchorId.areaId, anchorId.regionIdx)
        return ProjectionDecalFormTags.ALL.index(first(anchorSlot.formfactors))
