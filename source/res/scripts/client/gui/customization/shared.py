# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/customization/shared.py
from gui.shared.gui_items import GUI_ITEM_TYPE
from items.components.c11n_constants import CustomizationType, C11N_MASK_REGION, SeasonType
from shared_utils import CONST_CONTAINER
from vehicle_systems.tankStructure import TankPartIndexes, TankPartNames
from CurrentVehicle import g_currentVehicle
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.battle_control.vehicle_getter import hasTurretRotator
C11N_ITEM_TYPE_MAP = {GUI_ITEM_TYPE.PAINT: CustomizationType.PAINT,
 GUI_ITEM_TYPE.CAMOUFLAGE: CustomizationType.CAMOUFLAGE,
 GUI_ITEM_TYPE.MODIFICATION: CustomizationType.MODIFICATION,
 GUI_ITEM_TYPE.DECAL: CustomizationType.DECAL,
 GUI_ITEM_TYPE.EMBLEM: CustomizationType.DECAL,
 GUI_ITEM_TYPE.INSCRIPTION: CustomizationType.DECAL,
 GUI_ITEM_TYPE.STYLE: CustomizationType.STYLE}

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

class CustomizationTankPartNames(TankPartNames):
    MASK = 'mask'
    ALL = TankPartNames.ALL + (MASK,)


def chooseMode(itemTypeID, vehicle):
    if itemTypeID == GUI_ITEM_TYPE.CAMOUFLAGE:
        if vehicle.turret.isGunCarriage:
            return HighlightingMode.CAMO_REGIONS_SKIP_TURRET
        return HighlightingMode.CAMO_REGIONS
    return HighlightingMode.REPAINT_REGIONS_MERGED if itemTypeID == GUI_ITEM_TYPE.PAINT else HighlightingMode.WHOLE_VEHICLE


def getAppliedRegionsForCurrentHangarVehicle(areaId, slotId):
    if areaId == TankPartIndexes.TURRET and not hasTurretRotator(g_currentVehicle.item.descriptor):
        return ()
    outfit = g_currentVehicle.item.getCustomOutfit(SeasonType.SUMMER)
    area = outfit.getContainer(areaId)
    if area:
        slot = area.slotFor(slotId)
        if slot:
            if slotId != GUI_ITEM_TYPE.PAINT:
                if slotId in (GUI_ITEM_TYPE.INSCRIPTION, GUI_ITEM_TYPE.EMBLEM):
                    descriptor = g_currentVehicle.hangarSpace.getVehicleEntity().typeDescriptor
                    allDecalesSlots = ()
                    if areaId == TankPartIndexes.HULL:
                        allDecalesSlots = descriptor.hull.emblemSlots
                    elif areaId == TankPartIndexes.TURRET and not descriptor.turret.showEmblemsOnGun or areaId == TankPartIndexes.GUN and descriptor.turret.showEmblemsOnGun:
                        allDecalesSlots = descriptor.turret.emblemSlots
                    if slotId == GUI_ITEM_TYPE.INSCRIPTION:
                        slotType = 'inscription'
                    else:
                        slotType = 'player'
                    decalesSlots = tuple((slt for slt in allDecalesSlots if slt.type == slotType))
                    return tuple(range(min(len(decalesSlots), len(slot.getRegions()))))
                return tuple(range(len(slot.getRegions())))
            if areaId != TankPartIndexes.GUN:
                if slot.getRegions():
                    return (0,)
                return ()
            if 'GUN_2' in g_currentVehicle.item.descriptor.type.customizableVehicleAreas:
                return (0, C11N_MASK_REGION)
            return (0,)


def getCustomizationTankPartName(areaId, regionIdx):
    return CustomizationTankPartNames.MASK if areaId == TankPartIndexes.GUN and regionIdx == C11N_MASK_REGION else TankPartIndexes.getName(areaId)


def createCustomizationBaseRequestCriteria(vehicle, progress, appliedItems, season=None, itemTypeID=None):
    season = season or SeasonType.ALL
    criteria = REQ_CRITERIA.CUSTOM(lambda item: item.mayInstall(vehicle) and item.season & season and (not item.isHidden or item.fullInventoryCount(vehicle) > 0 or appliedItems and item.intCD in appliedItems) and (not item.requiredToken or progress.getTokenCount(item.requiredToken) > 0) and (not itemTypeID or item.itemTypeID == itemTypeID))
    return criteria
