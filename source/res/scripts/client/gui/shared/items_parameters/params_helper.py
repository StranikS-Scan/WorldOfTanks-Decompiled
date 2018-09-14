# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/items_parameters/params_helper.py
from collections import namedtuple
import copy
from datetime import time
import time
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_ERROR
from gui.shared.items_parameters import params
from gui.shared.items_parameters.comparator import VehiclesComparator, ItemsComparator
from gui.shared.items_parameters.params_cache import g_paramsCache
from items import vehicles, ITEM_TYPES
from shared_utils import findFirst
_ITEM_TYPE_HANDLERS = {ITEM_TYPES.vehicleRadio: params.RadioParams,
 ITEM_TYPES.vehicleEngine: params.EngineParams,
 ITEM_TYPES.vehicleChassis: params.ChassisParams,
 ITEM_TYPES.vehicleTurret: params.TurretParams,
 ITEM_TYPES.vehicleGun: params.GunParams,
 ITEM_TYPES.shell: params.ShellParams,
 ITEM_TYPES.equipment: params.EquipmentParams,
 ITEM_TYPES.optionalDevice: params.OptionalDeviceParams,
 ITEM_TYPES.vehicle: params.VehicleParams}

def _getParamsProvider(item, vehicleDescr=None):
    if isinstance(item.descriptor, vehicles.VehicleDescr):
        return _ITEM_TYPE_HANDLERS[ITEM_TYPES.vehicle](item)
    else:
        itemTypeIdx, _, _ = vehicles.parseIntCompactDescr(item.descriptor['compactDescr'])
        return _ITEM_TYPE_HANDLERS[itemTypeIdx](item.descriptor, vehicleDescr)


def get(item, vehicleDescr=None):
    try:
        return _getParamsProvider(item, vehicleDescr).getAllDataDict()
    except Exception:
        LOG_CURRENT_EXCEPTION()
        return dict()


_DescriptorWrapper = namedtuple('DescriptorWrapper', 'descriptor')

def getParameters(item, vehicleDescr=None):
    return get(item, vehicleDescr).get('parameters', dict())


def getCompatibles(item, vehicleDescr=None):
    return get(item, vehicleDescr).get('compatible')


def idealCrewComparator(vehicle):
    vehicleParamsObject = params.VehicleParams(vehicle)
    vehicleParams = vehicleParamsObject.getParamsDict()
    bonuses = vehicleParamsObject.getBonuses()
    penalties = vehicleParamsObject.getPenalties()
    possibleBonuses = g_paramsCache.getCompatibleBonuses(vehicle.descriptor)
    idealCrewVehicle = copy.copy(vehicle)
    idealCrewVehicle.crew = vehicle.getPerfectCrew()
    perfectVehicleParams = params.VehicleParams(idealCrewVehicle).getParamsDict()
    return VehiclesComparator(vehicleParams, perfectVehicleParams, possibleBonuses, bonuses, penalties)


def itemOnVehicleComparator(vehicle, item):
    vehicleParams = params.VehicleParams(vehicle).getParamsDict()
    withItemParams = vehicleParams
    mayInstall, reason = vehicle.descriptor.mayInstallComponent(item.intCD)
    if item.itemTypeID == ITEM_TYPES.vehicleTurret:
        mayInstall, reason = vehicle.descriptor.mayInstallTurret(item.intCD, vehicle.gun.intCD)
        if not mayInstall:
            properGun = findFirst(lambda gun: vehicle.descriptor.mayInstallComponent(gun['compactDescr'])[0], item.descriptor['guns'])
            if properGun is not None:
                removedModules = vehicle.descriptor.installTurret(item.intCD, properGun['compactDescr'])
                withItemParams = params.VehicleParams(vehicle).getParamsDict()
                vehicle.descriptor.installTurret(*removedModules)
            else:
                LOG_ERROR('not possible to install turret', item, reason)
        else:
            removedModules = vehicle.descriptor.installTurret(item.intCD, vehicle.gun.intCD)
            withItemParams = params.VehicleParams(vehicle).getParamsDict()
            vehicle.descriptor.installTurret(*removedModules)
    elif not mayInstall and reason == 'not for current vehicle' and item.itemTypeID == ITEM_TYPES.vehicleGun:
        turret = g_paramsCache.getPrecachedParameters(item.intCD).getTurretsForVehicle(vehicle.intCD)[0]
        removedModules = vehicle.descriptor.installTurret(turret, vehicle.gun.intCD)
        vehicleParams = params.VehicleParams(vehicle).getParamsDict()
        vehicle.descriptor.installTurret(turret, item.intCD)
        withItemParams = params.VehicleParams(vehicle).getParamsDict()
        vehicle.descriptor.installTurret(*removedModules)
    else:
        removedModule = vehicle.descriptor.installComponent(item.intCD)
        withItemParams = params.VehicleParams(vehicle).getParamsDict()
        vehicle.descriptor.installComponent(removedModule[0])
    return VehiclesComparator(withItemParams, vehicleParams)


def artifactComparator(vehicle, item, slotIdx):
    vehicleParams = params.VehicleParams(vehicle).getParamsDict()
    if item.itemTypeID == ITEM_TYPES.optionalDevice:
        removable, notRemovable = vehicle.descriptor.installOptionalDevice(item.intCD, slotIdx)
        withItemParams = params.VehicleParams(vehicle).getParamsDict()
        removed = removable or notRemovable
        if removed:
            vehicle.descriptor.installOptionalDevice(removed[0], slotIdx)
        else:
            vehicle.descriptor.removeOptionalDevice(slotIdx)
    else:
        oldEq = vehicle.eqs[slotIdx]
        vehicle.eqs[slotIdx] = item
        withItemParams = params.VehicleParams(vehicle).getParamsDict()
        vehicle.eqs[slotIdx] = oldEq
    return VehiclesComparator(withItemParams, vehicleParams)


def vehiclesComparator(comparableVehicle, vehicle):
    return VehiclesComparator(params.VehicleParams(comparableVehicle).getParamsDict(), params.VehicleParams(vehicle).getParamsDict())


def itemsComparator(currentItem, otherItem, vehicleDescr=None):
    return ItemsComparator(getParameters(currentItem, vehicleDescr), getParameters(otherItem, vehicleDescr))


def camouflageComparator(vehicle, camouflage):
    """
    :param vehicle: instance of  gui.shared.gui_items.Vehicle.Vehicle
    :param camouflage: instance of  gui.customization.elements.Camouflage
    :return: instance of VehiclesComparator
    """
    vDescr = vehicle.descriptor
    currParams = params.VehicleParams(vehicle).getParamsDict()
    camouflageID = camouflage.getID()
    camouflageInfo = vehicles.g_cache.customization(vDescr.type.customizationNationID)['camouflages'].get(camouflageID)
    if camouflageInfo is not None:
        pos = camouflageInfo['kind']
        oldCamouflageData = vDescr.camouflages[pos]
        vDescr.setCamouflage(pos, camouflageID, int(time.time()), 0)
        newParams = params.VehicleParams(vehicle).getParamsDict()
        vDescr.setCamouflage(pos, *oldCamouflageData)
    else:
        newParams = currParams.copy()
    return VehiclesComparator(newParams, currParams)
