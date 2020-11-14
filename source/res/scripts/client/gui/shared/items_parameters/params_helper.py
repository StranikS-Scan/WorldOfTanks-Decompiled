# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/items_parameters/params_helper.py
import copy
from collections import namedtuple
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_ERROR, LOG_WARNING
from gui import GUI_SETTINGS
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_parameters import params, RELATIVE_PARAMS, MAX_RELATIVE_VALUE
from gui.shared.items_parameters.comparator import VehiclesComparator, ItemsComparator
from gui.shared.items_parameters.functions import getBasicShell
from gui.shared.items_parameters.params_cache import g_paramsCache
from gui.shared.utils import AUTO_RELOAD_PROP_NAME, MAX_STEERING_LOCK_ANGLE, TURBOSHAFT_SPEED_MODE_SPEED, WHEELED_SPEED_MODE_SPEED, DUAL_GUN_CHARGE_TIME, TURBOSHAFT_ENGINE_POWER, TURBOSHAFT_INVISIBILITY_STILL_FACTOR, TURBOSHAFT_INVISIBILITY_MOVING_FACTOR, TURBOSHAFT_SWITCH_TIME
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
RELATIVE_POWER_PARAMS = ('avgDamage',
 'avgPiercingPower',
 'stunMinDuration',
 'stunMaxDuration',
 'reloadTime',
 AUTO_RELOAD_PROP_NAME,
 'reloadTimeSecs',
 'clipFireRate',
 DUAL_GUN_CHARGE_TIME,
 'turretRotationSpeed',
 'turretYawLimits',
 'pitchLimits',
 'gunYawLimits',
 'aimingTime',
 'shotDispersionAngle',
 'avgDamagePerMinute')
RELATIVE_ARMOR_PARAMS = ('maxHealth', 'hullArmor', 'turretArmor')
RELATIVE_MOBILITY_PARAMS = ('vehicleWeight',
 'enginePower',
 TURBOSHAFT_ENGINE_POWER,
 'enginePowerPerTon',
 'speedLimits',
 WHEELED_SPEED_MODE_SPEED,
 TURBOSHAFT_SPEED_MODE_SPEED,
 'chassisRotationSpeed',
 MAX_STEERING_LOCK_ANGLE,
 'switchOnTime',
 'switchOffTime',
 TURBOSHAFT_SWITCH_TIME)
RELATIVE_CAMOUFLAGE_PARAMS = ('invisibilityStillFactor',
 'invisibilityMovingFactor',
 TURBOSHAFT_INVISIBILITY_STILL_FACTOR,
 TURBOSHAFT_INVISIBILITY_MOVING_FACTOR)
RELATIVE_VISIBILITY_PARAMS = ('circularVisionRadius', 'radioDistance')
PARAMS_GROUPS = {'relativePower': RELATIVE_POWER_PARAMS,
 'relativeArmor': RELATIVE_ARMOR_PARAMS,
 'relativeMobility': RELATIVE_MOBILITY_PARAMS,
 'relativeCamouflage': RELATIVE_CAMOUFLAGE_PARAMS,
 'relativeVisibility': RELATIVE_VISIBILITY_PARAMS}
EXTRA_POWER_PARAMS = ('vehicleGunShotDispersion', 'vehicleReloadTimeAfterShellChange')
EXTRA_ARMOR_PARAMS = ('vehicleRepairSpeed', 'vehicleRamOrExplosionDamageResistance', 'crewHitChance', 'crewRepeatedStunDuration', 'crewStunDuration', 'vehicleChassisStrength', 'vehicleChassisFallDamage', 'vehicleChassisRepairSpeed', 'vehicleAmmoBayEngineFuelStrength', 'vehPenaltyForDamageEngineAndCombat', 'vehicleFireChance')
EXTRA_MOBILITY_PARAMS = ('vehicleSpeedGain',)
EXTRA_CAMOUFLAGE_PARAMS = ('vehicleOwnSpottingTime',)
EXTRA_VISIBILITY_PARAMS = ('vehicleEnemySpottingTime', 'demaskFoliageFactor', 'demaskMovingFactor')
EXTRA_PARAMS_GROUP = {'relativePower': EXTRA_POWER_PARAMS,
 'relativeArmor': EXTRA_ARMOR_PARAMS,
 'relativeMobility': EXTRA_MOBILITY_PARAMS,
 'relativeCamouflage': EXTRA_CAMOUFLAGE_PARAMS,
 'relativeVisibility': EXTRA_VISIBILITY_PARAMS}

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
    elif not mayInstall:
        if reason == 'not for current vehicle' and item.itemTypeID == ITEM_TYPES.vehicleGun:
            turret = g_paramsCache.getPrecachedParameters(item.intCD).getTurretsForVehicle(vehicle.intCD)[0]
            removedModules = vehicle.descriptor.installTurret(turret, vehicle.gun.intCD)
            vehicleParams = params.VehicleParams(vehicle).getParamsDict()
            vehicle.descriptor.installTurret(turret, item.intCD)
            withItemParams = params.VehicleParams(vehicle).getParamsDict()
            vehicle.descriptor.installTurret(*removedModules)
        else:
            LOG_WARNING('Module {} cannot be installed on vehicle {}'.format(item, vehicle))
            return VehiclesComparator(withItemParams, vehicleParams)
    else:
        removedModule = vehicle.descriptor.installComponent(item.intCD)
        withItemParams = params.VehicleParams(vehicle).getParamsDict()
        vehicle.descriptor.installComponent(removedModule[0])
    return VehiclesComparator(withItemParams, vehicleParams)


def artifactComparator(vehicle, item, slotIdx, compareWithEmptySlot=False):
    vehicleParams = params.VehicleParams(vehicle).getParamsDict()
    if item.itemTypeID == ITEM_TYPES.optionalDevice:
        removable, notRemovable = vehicle.descriptor.installOptionalDevice(item.intCD, slotIdx)
        withItemParams = params.VehicleParams(vehicle).getParamsDict(preload=True)
        removed = removable or notRemovable
        if removed:
            if compareWithEmptySlot:
                vehicle.descriptor.removeOptionalDevice(slotIdx)
                vehicleParams = params.VehicleParams(vehicle).getParamsDict(preload=True)
            vehicle.descriptor.installOptionalDevice(removed[0], slotIdx)
        else:
            vehicle.descriptor.removeOptionalDevice(slotIdx)
    else:
        consumables = vehicle.consumables.installed if item.itemTypeID == ITEM_TYPES.equipment else vehicle.battleBoosters.installed
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
        oldOptDevice = vehicle.optDevices.installed[slotIdx]
        vehicle.descriptor.removeOptionalDevice(slotIdx)
        withItemParams = params.VehicleParams(vehicle).getParamsDict()
        vehicle.descriptor.installOptionalDevice(oldOptDevice.intCD, slotIdx)
    else:
        consumables = vehicle.consumables.installed if item.itemTypeID == ITEM_TYPES.equipment else vehicle.battleBoosters.installed
        oldEq = consumables[slotIdx]
        consumables[slotIdx] = None
        withItemParams = params.VehicleParams(vehicle).getParamsDict()
        consumables[slotIdx] = oldEq
    return VehiclesComparator(withItemParams, vehicleParams)


def vehiclesComparator(comparableVehicle, vehicle):
    return VehiclesComparator(params.VehicleParams(comparableVehicle).getParamsDict(), params.VehicleParams(vehicle).getParamsDict(), suitableArtefacts=g_paramsCache.getCompatibleArtefacts(vehicle.descriptor))


def tankSetupVehiclesComparator(comparableVehicle, vehicle):
    idealCrewVehicle = copy.copy(vehicle)
    perfectCrew = vehicle.getPerfectCrew()
    changedCrew = []
    for idx, tmanData in enumerate(vehicle.crew):
        _, tman = tmanData
        changedCrew.append(tmanData if tman and tman.isMaxRoleLevel else perfectCrew[idx])

    idealCrewVehicle.crew = changedCrew
    return VehiclesComparator(params.VehicleParams(comparableVehicle).getParamsDict(), params.VehicleParams(idealCrewVehicle).getParamsDict(), suitableArtefacts=g_paramsCache.getCompatibleArtefacts(vehicle.descriptor))


def itemsComparator(currentItem, otherItem, vehicleDescr=None):
    return ItemsComparator(getParameters(currentItem, vehicleDescr), getParameters(otherItem, vehicleDescr))


@dependency.replace_none_kwargs(factory=IGuiItemsFactory)
def camouflageComparator(vehicle, camo, factory=None):
    currParams = params.VehicleParams(vehicle).getParamsDict()
    if camo:
        season = first(camo.seasons)
        outfit = vehicle.getOutfit(season)
        if not outfit:
            outfit = factory.createOutfit(vehicleCD=vehicle.descriptor.makeCompactDescr())
            vehicle.setCustomOutfit(season, outfit)
        slot = outfit.hull.slotFor(GUI_ITEM_TYPE.CAMOUFLAGE)
        oldCamoCD = slot.getItemCD()
        oldComponent = slot.getComponent()
        slot.set(camo.intCD)
        newParams = params.VehicleParams(vehicle).getParamsDict(preload=True)
        if oldCamoCD:
            slot.set(oldCamoCD, component=oldComponent)
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

                    result.extend(self._getExtraParams(comparator, groupName))
                if hasParams and groupIdx < len(RELATIVE_PARAMS) - 1:
                    separator = self._makeSeparator()
                    if separator:
                        result.append(separator)

        return result

    def _getExtraParams(self, comparator, groupName):
        result = []
        if self._isExtraParamEnabled():
            hasExtraParams = False
            for extraParamName in EXTRA_PARAMS_GROUP[groupName]:
                param = comparator.getExtendedData(extraParamName)
                formattedParam, nSlashCount = self._makeExtraParamVO(param)
                if formattedParam:
                    if not hasExtraParams:
                        lineSeparator = self._makeLineSeparator()
                        if lineSeparator:
                            result.append(lineSeparator)
                        hasExtraParams = True
                    result.append(formattedParam)
                    for _ in xrange(nSlashCount):
                        block = self._makeExtraAdditionalBlock(formattedParam['paramID'], formattedParam['tooltip'])
                        if block is not None:
                            result.append(block)

        return result

    def _isExtraParamEnabled(self):
        return False

    def _makeSimpleParamHeaderVO(self, param, isOpen, comparator):
        return getCommonParam(HANGAR_ALIASES.VEH_PARAM_RENDERER_STATE_SIMPLE_TOP, param.name)

    def _makeAdvancedParamVO(self, param):
        return getCommonParam(HANGAR_ALIASES.VEH_PARAM_RENDERER_STATE_ADVANCED, param.name)

    def _makeExtraParamVO(self, param):
        return (getCommonParam(HANGAR_ALIASES.VEH_PARAM_RENDERER_STATE_EXTRA, param.name), 0)

    def _makeSimpleParamBottomVO(self, param, vehIntCD=None):
        return None

    def _makeExtraAdditionalBlock(self, paramID, tooltip):
        return None

    def _makeSeparator(self):
        return None

    def _makeLineSeparator(self):
        return None
