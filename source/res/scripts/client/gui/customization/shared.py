# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/customization/shared.py
from collections import namedtuple
import logging
import Math
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from items.components.c11n_constants import CustomizationType, C11N_MASK_REGION, SeasonType, ApplyArea, MAX_USERS_PROJECTION_DECALS, C11N_GUN_APPLY_REGIONS
from shared_utils import CONST_CONTAINER, isEmpty
from vehicle_systems.tankStructure import TankPartIndexes, TankPartNames
from CurrentVehicle import g_currentVehicle
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.gui_items.customization.outfit import Area, scaffold
_logger = logging.getLogger(__name__)
C11nId = namedtuple('C11nId', ('areaId', 'slotType', 'regionIdx'))
C11nId.__new__.__defaults__ = (-1, -1, -1)
C11N_ITEM_TYPE_MAP = {GUI_ITEM_TYPE.PAINT: CustomizationType.PAINT,
 GUI_ITEM_TYPE.CAMOUFLAGE: CustomizationType.CAMOUFLAGE,
 GUI_ITEM_TYPE.MODIFICATION: CustomizationType.MODIFICATION,
 GUI_ITEM_TYPE.DECAL: CustomizationType.DECAL,
 GUI_ITEM_TYPE.EMBLEM: CustomizationType.DECAL,
 GUI_ITEM_TYPE.INSCRIPTION: CustomizationType.DECAL,
 GUI_ITEM_TYPE.STYLE: CustomizationType.STYLE,
 GUI_ITEM_TYPE.PROJECTION_DECAL: CustomizationType.PROJECTION_DECAL}

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
ANCHOR_TYPE_TO_SLOT_TYPE_MAP = {'inscription': GUI_ITEM_TYPE.INSCRIPTION,
 'player': GUI_ITEM_TYPE.EMBLEM,
 'paint': GUI_ITEM_TYPE.PAINT,
 'camouflage': GUI_ITEM_TYPE.CAMOUFLAGE,
 'projectionDecal': GUI_ITEM_TYPE.PROJECTION_DECAL,
 'style': GUI_ITEM_TYPE.STYLE,
 'effect': GUI_ITEM_TYPE.MODIFICATION}
SLOT_TYPE_TO_ANCHOR_TYPE_MAP = {v:k for k, v in ANCHOR_TYPE_TO_SLOT_TYPE_MAP.iteritems()}

class CustomizationTankPartNames(TankPartNames):
    MASK = 'mask'
    ALL = TankPartNames.ALL + (MASK,)


def chooseMode(itemTypeID, vehicle):
    if itemTypeID == GUI_ITEM_TYPE.CAMOUFLAGE:
        if not __isTurretCustomizable(vehicle.descriptor):
            return HighlightingMode.CAMO_REGIONS_SKIP_TURRET
        return HighlightingMode.CAMO_REGIONS
    return HighlightingMode.REPAINT_REGIONS_MERGED if itemTypeID == GUI_ITEM_TYPE.PAINT else HighlightingMode.WHOLE_VEHICLE


def getAppliedRegionsForCurrentHangarVehicle(areaId, slotId):
    outfit = g_currentVehicle.item.getCustomOutfit(SeasonType.SUMMER)
    area = outfit.getContainer(areaId)
    if area:
        slot = area.slotFor(slotId)
        if slot:
            if slotId in (GUI_ITEM_TYPE.INSCRIPTION, GUI_ITEM_TYPE.EMBLEM):
                descriptor = g_currentVehicle.item.descriptor
                allDecalesSlots = ()
                if areaId == TankPartIndexes.HULL:
                    allDecalesSlots = descriptor.hull.emblemSlots + descriptor.hull.slotsAnchors
                elif areaId == TankPartIndexes.TURRET and not descriptor.turret.showEmblemsOnGun or areaId == TankPartIndexes.GUN and descriptor.turret.showEmblemsOnGun:
                    allDecalesSlots = descriptor.turret.emblemSlots + descriptor.turret.slotsAnchors
                slotType = SLOT_TYPE_TO_ANCHOR_TYPE_MAP.get(slotId, None)
                if slotType is not None:
                    decalesSlots = tuple((slt for slt in allDecalesSlots if slt.type == slotType))
                    return tuple(range(min(len(decalesSlots), len(slot.getRegions()))))
                _logger.warning('slotId=%d does not have matched value', slotId)
                return ()
            if slotId in (GUI_ITEM_TYPE.PROJECTION_DECAL,):
                descriptor = g_currentVehicle.item.descriptor
                vehSlotsCounter = 0
                slotTypeName = GUI_ITEM_TYPE_NAMES[slotId]
                for vehiclePartSlots in (descriptor.hull.slotsAnchors,
                 descriptor.chassis.slotsAnchors,
                 descriptor.turret.slotsAnchors,
                 descriptor.gun.slotsAnchors):
                    for vehicleSlot in vehiclePartSlots:
                        if vehicleSlot.type == slotTypeName:
                            vehSlotsCounter += 1

                return tuple(range(vehSlotsCounter))
            if slotId in (GUI_ITEM_TYPE.PAINT, GUI_ITEM_TYPE.CAMOUFLAGE):
                customizableAreas = []
                vehiclePart = getVehiclePartByIdx(g_currentVehicle.item, areaId)
                if vehiclePart is not None:
                    if areaId == TankPartIndexes.GUN:
                        return tuple((C11N_GUN_APPLY_REGIONS[area] for area in vehiclePart.customizableVehicleAreas[GUI_ITEM_TYPE_NAMES[slotId]]))
                    customizableAreas = vehiclePart.customizableVehicleAreas[GUI_ITEM_TYPE_NAMES[slotId]]
                return tuple(range(len(customizableAreas)))
            if slotId in (GUI_ITEM_TYPE.MODIFICATION,):
                return (0,)
    return ()


def __isTurretCustomizable(vhicleDescriptor):
    return 'TURRET' in vhicleDescriptor.turret.customizableVehicleAreas['camouflage']


def getCustomizationTankPartName(areaId, regionIdx):
    return CustomizationTankPartNames.MASK if areaId == TankPartIndexes.GUN and regionIdx == C11N_MASK_REGION else TankPartIndexes.getName(areaId)


def createCustomizationBaseRequestCriteria(vehicle, progress, appliedItems, season=None, itemTypeID=None):
    season = season or SeasonType.ALL
    criteria = REQ_CRITERIA.CUSTOM(lambda item: (not itemTypeID or item.itemTypeID == itemTypeID) and item.season & season and (not item.requiredToken or progress.getTokenCount(item.requiredToken) > 0) and (item.buyCount > 0 or item.fullInventoryCount(vehicle) > 0 or appliedItems and item.intCD in appliedItems or item.getInstalledVehicles() and not item.isVehicleBound) and item.mayInstall(vehicle))
    return criteria


def isOutfitVisuallyEmpty(oufit):
    return isEmpty((item for item in oufit.items() if not item.isHiddenInUI()))


ProjectionDecalSlotParams = namedtuple('ProjectionDecalSlotParams', ('position', 'rotation', 'scale', 'showOn'))

def getVehicleProjectionDecalSlotParams(vehicleDescr, vehicleSlotId):
    slotTypeName = GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.PROJECTION_DECAL]
    for vehiclePartSlots in (vehicleDescr.hull.slotsAnchors,
     vehicleDescr.chassis.slotsAnchors,
     vehicleDescr.turret.slotsAnchors,
     vehicleDescr.gun.slotsAnchors):
        for vehicleSlot in vehiclePartSlots:
            if vehicleSlot.type != slotTypeName or vehicleSlot.slotId != vehicleSlotId:
                continue
            return ProjectionDecalSlotParams(vehicleSlot.position, vehicleSlot.rotation, vehicleSlot.scale, vehicleSlot.showOn)

    return None


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


def getVehiclePartByIdx(vehicle, partIdx):
    vehiclePart = None
    if partIdx == TankPartIndexes.CHASSIS:
        vehiclePart = vehicle.descriptor.chassis
    if partIdx == TankPartIndexes.TURRET:
        vehiclePart = vehicle.descriptor.turret
    if partIdx == TankPartIndexes.HULL:
        vehiclePart = vehicle.descriptor.hull
    if partIdx == TankPartIndexes.GUN:
        vehiclePart = vehicle.descriptor.gun
    return vehiclePart
