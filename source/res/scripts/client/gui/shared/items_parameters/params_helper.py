# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/items_parameters/params_helper.py
from collections import namedtuple
import copy
import time
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_ERROR
from gui import GUI_SETTINGS
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_parameters import params, RELATIVE_PARAMS, MAX_RELATIVE_VALUE
from gui.shared.items_parameters.comparator import VehiclesComparator, ItemsComparator
from gui.shared.items_parameters.functions import getBasicShell
from gui.shared.items_parameters.params_cache import g_paramsCache
from helpers import dependency
from items import vehicles, ITEM_TYPES
from shared_utils import findFirst, first
from skeletons.gui.shared.gui_items import IGuiItemsFactory
_ITEM_TYPE_HANDLERS = {ITEM_TYPES.vehicleRadio: params.RadioParams,
 ITEM_TYPES.vehicleEngine: params.EngineParams,
 ITEM_TYPES.vehicleChassis: params.ChassisParams,
 ITEM_TYPES.vehicleTurret: params.TurretParams,
 ITEM_TYPES.vehicleGun: params.GunParams,
 ITEM_TYPES.shell: params.ShellParams,
 ITEM_TYPES.equipment: params.EquipmentParams,
 ITEM_TYPES.optionalDevice: params.OptionalDeviceParams,
 ITEM_TYPES.vehicle: params.VehicleParams}
RELATIVE_POWER_PARAMS = ('avgDamage', 'avgPiercingPower', 'stunMinDuration', 'stunMaxDuration', 'reloadTime', 'reloadTimeSecs', 'gunRotationSpeed', 'turretRotationSpeed', 'turretYawLimits', 'pitchLimits', 'gunYawLimits', 'clipFireRate', 'aimingTime', 'shotDispersionAngle', 'avgDamagePerMinute')
RELATIVE_ARMOR_PARAMS = ('maxHealth', 'hullArmor', 'turretArmor')
RELATIVE_MOBILITY_PARAMS = ('vehicleWeight', 'enginePower', 'enginePowerPerTon', 'speedLimits', 'chassisRotationSpeed', 'switchOnTime', 'switchOffTime')
RELATIVE_CAMOUFLAGE_PARAMS = ('invisibilityStillFactor', 'invisibilityMovingFactor')
RELATIVE_VISIBILITY_PARAMS = ('circularVisionRadius', 'radioDistance')
PARAMS_GROUPS = {'relativePower': RELATIVE_POWER_PARAMS,
 'relativeArmor': RELATIVE_ARMOR_PARAMS,
 'relativeMobility': RELATIVE_MOBILITY_PARAMS,
 'relativeCamouflage': RELATIVE_CAMOUFLAGE_PARAMS,
 'relativeVisibility': RELATIVE_VISIBILITY_PARAMS}

def _getParamsProvider(item, vehicleDescr=None):
    if vehicles.isVehicleDescr(item.descriptor):
        return _ITEM_TYPE_HANDLERS[ITEM_TYPES.vehicle](item)
    itemTypeIdx, _, _ = vehicles.parseIntCompactDescr(item.descriptor.compactDescr)
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
    bonuses = vehicleParamsObject.getBonuses(vehicle)
    penalties = vehicleParamsObject.getPenalties(vehicle)
    compatibleArtefacts = g_paramsCache.getCompatibleArtefacts(vehicle.descriptor)
    idealCrewVehicle = copy.copy(vehicle)
    idealCrewVehicle.crew = vehicle.getPerfectCrew()
    perfectVehicleParams = params.VehicleParams(idealCrewVehicle).getParamsDict()
    return VehiclesComparator(vehicleParams, perfectVehicleParams, compatibleArtefacts, bonuses, penalties)


def itemOnVehicleComparator(vehicle, item):
    vehicleParams = params.VehicleParams(vehicle).getParamsDict()
    withItemParams = vehicleParams
    mayInstall, reason = vehicle.descriptor.mayInstallComponent(item.intCD)
    if item.itemTypeID == ITEM_TYPES.vehicleTurret:
        mayInstall, reason = vehicle.descriptor.mayInstallTurret(item.intCD, vehicle.gun.intCD)
        if not mayInstall:
            properGun = findFirst(lambda gun: vehicle.descriptor.mayInstallComponent(gun.compactDescr)[0], item.descriptor.guns)
            if properGun is not None:
                removedModules = vehicle.descriptor.installTurret(item.intCD, properGun.compactDescr)
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


def artifactComparator(vehicle, item, slotIdx, compareWithEmptySlot=False):
    vehicleParams = params.VehicleParams(vehicle).getParamsDict()
    if item.itemTypeID == ITEM_TYPES.optionalDevice:
        removable, notRemovable = vehicle.descriptor.installOptionalDevice(item.intCD, slotIdx)
        withItemParams = params.VehicleParams(vehicle).getParamsDict()
        removed = removable or notRemovable
        if removed:
            if compareWithEmptySlot:
                vehicle.descriptor.removeOptionalDevice(slotIdx)
                vehicleParams = params.VehicleParams(vehicle).getParamsDict()
            vehicle.descriptor.installOptionalDevice(removed[0], slotIdx)
        else:
            vehicle.descriptor.removeOptionalDevice(slotIdx)
    else:
        consumables = vehicle.equipment.regularConsumables if item.itemTypeID == ITEM_TYPES.equipment else vehicle.equipment.battleBoosterConsumables
        oldEq = consumables[slotIdx]
        if compareWithEmptySlot:
            consumables[slotIdx] = None
            vehicleParams = params.VehicleParams(vehicle).getParamsDict()
        consumables[slotIdx] = item
        withItemParams = params.VehicleParams(vehicle).getParamsDict()
        consumables[slotIdx] = oldEq
    return VehiclesComparator(withItemParams, vehicleParams)


def artifactRemovedComparator(vehicle, item, slotIdx):
    vehicleParams = params.VehicleParams(vehicle).getParamsDict()
    if item.itemTypeID == ITEM_TYPES.optionalDevice:
        oldOptDevice = vehicle.optDevices[slotIdx]
        vehicle.descriptor.removeOptionalDevice(slotIdx)
        withItemParams = params.VehicleParams(vehicle).getParamsDict()
        vehicle.descriptor.installOptionalDevice(oldOptDevice.intCD, slotIdx)
    else:
        consumables = vehicle.equipment.regularConsumables if item.itemTypeID == ITEM_TYPES.equipment else vehicle.equipment.battleBoosterConsumables
        oldEq = consumables[slotIdx]
        consumables[slotIdx] = None
        withItemParams = params.VehicleParams(vehicle).getParamsDict()
        consumables[slotIdx] = oldEq
    return VehiclesComparator(withItemParams, vehicleParams)


def vehiclesComparator(comparableVehicle, vehicle):
    return VehiclesComparator(params.VehicleParams(comparableVehicle).getParamsDict(), params.VehicleParams(vehicle).getParamsDict(), suitableArtefacts=g_paramsCache.getCompatibleArtefacts(vehicle.descriptor))


def itemsComparator(currentItem, otherItem, vehicleDescr=None):
    return ItemsComparator(getParameters(currentItem, vehicleDescr), getParameters(otherItem, vehicleDescr))


@dependency.replace_none_kwargs(factory=IGuiItemsFactory)
def camouflageComparator(vehicle, camo, factory=None):
    """
    :param vehicle: instance of  gui.shared.gui_items.Vehicle.Vehicle
    :param camo: instance of gui.shared.gui_items.customization.c11n_items.Camouflage
    :return: instance of VehiclesComparator
    """
    currParams = params.VehicleParams(vehicle).getParamsDict()
    if camo:
        season = first(camo.seasons)
        outfit = vehicle.getOutfit(season)
        if not outfit:
            outfit = factory.createOutfit(isEnabled=True)
            vehicle.setCustomOutfit(season, outfit)
        slot = outfit.hull.slotFor(GUI_ITEM_TYPE.CAMOUFLAGE)
        oldCamo = slot.getItem()
        slot.set(camo)
        newParams = params.VehicleParams(vehicle).getParamsDict(preload=True)
        if oldCamo:
            slot.set(oldCamo)
        else:
            slot.clear()
    else:
        newParams = currParams.copy()
    return VehiclesComparator(newParams, currParams)


def shellOnVehicleComparator(shell, vehicle):
    vDescriptor = vehicle.descriptor
    oldIdx = vDescriptor.activeGunShotIndex
    vehicleParams = params.VehicleParams(vehicle).getParamsDict()
    idx, _ = findFirst(lambda (i, s): s.shell.compactDescr == shell.intCD, enumerate(vDescriptor.gun.shots), (0, None))
    vDescriptor.activeGunShotIndex = idx
    newParams = params.VehicleParams(vehicle).getParamsDict(preload=True)
    vDescriptor.activeGunShotIndex = oldIdx
    return VehiclesComparator(newParams, vehicleParams)


def shellComparator(shell, vehicle):
    if vehicle is not None:
        vDescriptor = vehicle.descriptor
        basicShellDescr = getBasicShell(vDescriptor)
        return ItemsComparator(params.ShellParams(shell.descriptor, vDescriptor).getParamsDict(), params.ShellParams(basicShellDescr, vDescriptor).getParamsDict())
    else:
        return


def getGroupBonuses(groupName, comparator):
    """
    Gets set of bonuses for selected group
    """
    bonuses = set()
    for paramName in PARAMS_GROUPS[groupName]:
        bonuses.update(comparator.getExtendedData(paramName).bonuses)

    return bonuses


def hasGroupPenalties(groupName, comparator):
    for paramName in PARAMS_GROUPS[groupName]:
        if comparator.getExtendedData(paramName).penalties:
            return True

    return False


def getCommonParam(state, name):
    return {'state': state,
     'paramID': name}


class SimplifiedBarVO(dict):
    """
        This class contains values for status bar and is used to send data to FE
    """

    def __init__(self, **kwargs):
        super(SimplifiedBarVO, self).__init__(**kwargs)
        if 'value' not in kwargs or 'markerValue' not in kwargs:
            LOG_ERROR('value and markerValue should be specified for simplified parameter status bar')
        self.setdefault('delta', 0)
        self.setdefault('minValue', 0)
        self.setdefault('useAnim', False)
        self['maxValue'] = max(MAX_RELATIVE_VALUE, self['value'] + self['delta'])
        self.setdefault('isOptional', False)


class VehParamsBaseGenerator(object):

    def getFormattedParams(self, comparator, expandedGroups=None, vehIntCD=None):
        """
        Provides list of parameters in predefined order for particular vehicle in proper format
        :param comparator: instance gui.shared.items_parameters.comparator.ItemsComparator
        :param expandedGroups: the list of groups which parameters have to be added into the result list
        :param vehIntCD: intCD of target Vehicle
        :return: list of formatted parameters
        """
        result = []
        if GUI_SETTINGS.technicalInfo:
            for groupIdx, groupName in enumerate(RELATIVE_PARAMS):
                hasParams = False
                relativeParam = comparator.getExtendedData(groupName)
                isOpened = expandedGroups is None or expandedGroups.get(groupName, False)
                result.append(self._makeSimpleParamHeaderVO(relativeParam, isOpened, comparator))
                bottomVo = self._makeSimpleParamBottomVO(relativeParam, vehIntCD)
                if bottomVo:
                    result.append(bottomVo)
                if isOpened:
                    for paramName in PARAMS_GROUPS[groupName]:
                        param = comparator.getExtendedData(paramName)
                        formattedParam = self._makeAdvancedParamVO(param)
                        if formattedParam:
                            result.append(formattedParam)
                            hasParams = True

                if hasParams and groupIdx < len(RELATIVE_PARAMS) - 1:
                    separator = self._makeSeparator()
                    if separator:
                        result.append(separator)

        return result

    def _makeSimpleParamHeaderVO(self, param, isOpen, comparator):
        return getCommonParam(HANGAR_ALIASES.VEH_PARAM_RENDERER_STATE_SIMPLE_TOP, param.name)

    def _makeAdvancedParamVO(self, param):
        return getCommonParam(HANGAR_ALIASES.VEH_PARAM_RENDERER_STATE_ADVANCED, param.name)

    def _makeSimpleParamBottomVO(self, param, vehIntCD=None):
        return None

    def _makeSeparator(self):
        return None
