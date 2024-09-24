# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/items_parameters/params_helper.py
import copy
from itertools import chain
import typing
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_ERROR, LOG_WARNING
from gui import GUI_SETTINGS
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.shared.gui_items import GUI_ITEM_TYPE, KPI
from gui.shared.items_parameters import params, RELATIVE_PARAMS, MAX_RELATIVE_VALUE
from gui.shared.items_parameters.bonus_helper import CREW_MASTERY_BONUSES, isSituationalBonus
from gui.shared.items_parameters.comparator import CONDITIONAL_BONUSES
from gui.shared.items_parameters.comparator import VehiclesComparator, ItemsComparator, PARAM_STATE
from gui.shared.items_parameters.functions import getBasicShell
from gui.shared.items_parameters.params import HIDDEN_PARAM_DEFAULTS
from gui.shared.items_parameters.params_cache import g_paramsCache
from gui.shared.utils import AUTO_RELOAD_PROP_NAME, MAX_STEERING_LOCK_ANGLE, TURBOSHAFT_SPEED_MODE_SPEED, WHEELED_SPEED_MODE_SPEED, DUAL_GUN_CHARGE_TIME, TURBOSHAFT_ENGINE_POWER, TURBOSHAFT_INVISIBILITY_STILL_FACTOR, SHOT_DISPERSION_ANGLE, TURBOSHAFT_INVISIBILITY_MOVING_FACTOR, TURBOSHAFT_SWITCH_TIME, CHASSIS_REPAIR_TIME, CONTINUOUS_SHOTS_PER_MINUTE, ROCKET_ACCELERATION_ENGINE_POWER, ROCKET_ACCELERATION_SPEED_LIMITS, ROCKET_ACCELERATION_REUSE_AND_DURATION, DUAL_ACCURACY_COOLING_DELAY, BURST_FIRE_RATE, AUTO_SHOOT_CLIP_FIRE_RATE, AVG_DAMAGE_PER_SECOND, TWIN_GUN_SWITCH_FIRE_MODE_TIME, TWIN_GUN_TOP_SPEED
from helpers import dependency
from items import vehicles, ITEM_TYPES
from shared_utils import findFirst, first
from skeletons.gui.shared.gui_items import IGuiItemsFactory
RELATIVE_POWER_PARAMS = ('avgDamage',
 AVG_DAMAGE_PER_SECOND,
 'avgPiercingPower',
 'stunMinDuration',
 'stunMaxDuration',
 'reloadTime',
 CONTINUOUS_SHOTS_PER_MINUTE,
 AUTO_RELOAD_PROP_NAME,
 'reloadTimeSecs',
 TWIN_GUN_SWITCH_FIRE_MODE_TIME,
 'clipFireRate',
 AUTO_SHOOT_CLIP_FIRE_RATE,
 BURST_FIRE_RATE,
 'turboshaftBurstFireRate',
 DUAL_GUN_CHARGE_TIME,
 'turretRotationSpeed',
 'turretYawLimits',
 'pitchLimits',
 'gunYawLimits',
 'aimingTime',
 SHOT_DISPERSION_ANGLE,
 DUAL_ACCURACY_COOLING_DELAY,
 'avgDamagePerMinute')
RELATIVE_ARMOR_PARAMS = ('maxHealth',
 'hullArmor',
 'turretArmor',
 CHASSIS_REPAIR_TIME)
RELATIVE_MOBILITY_PARAMS = ('vehicleWeight',
 'enginePower',
 TURBOSHAFT_ENGINE_POWER,
 ROCKET_ACCELERATION_ENGINE_POWER,
 'enginePowerPerTon',
 'speedLimits',
 TWIN_GUN_TOP_SPEED,
 WHEELED_SPEED_MODE_SPEED,
 TURBOSHAFT_SPEED_MODE_SPEED,
 ROCKET_ACCELERATION_SPEED_LIMITS,
 'chassisRotationSpeed',
 ROCKET_ACCELERATION_REUSE_AND_DURATION,
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
EXTRA_POWER_PARAMS = (KPI.Name.VEHICLE_GUN_SHOT_DISPERSION,
 KPI.Name.VEHICLE_GUN_SHOT_DISPERSION_CHASSIS_MOVEMENT,
 KPI.Name.VEHICLE_GUN_SHOT_DISPERSION_CHASSIS_ROTATION,
 KPI.Name.VEHICLE_GUN_SHOT_DISPERSION_TURRET_ROTATION,
 KPI.Name.VEHICLE_GUN_SHOT_DISPERSION_WHILE_GUN_DAMAGED,
 KPI.Name.VEHICLE_GUN_SHOT_DISPERSION_AFTER_SHOT,
 KPI.Name.VEHICLE_RELOAD_TIME_AFTER_SHELL_CHANGE,
 KPI.Name.DAMAGE_AND_PIERCING_DISTRIBUTION_LOWER_BOUND,
 KPI.Name.DAMAGE_AND_PIERCING_DISTRIBUTION_UPPER_BOUND,
 KPI.Name.ENEMY_MODULES_CREW_CRIT_CHANCE,
 KPI.Name.VEHICLE_DAMAGE_ENEMIES_BY_RAMMING,
 KPI.Name.SHELL_VELOCITY)
EXTRA_ARMOR_PARAMS = (KPI.Name.CREW_HIT_CHANCE,
 KPI.Name.CREW_REPEATED_STUN_DURATION,
 KPI.Name.CREW_STUN_DURATION,
 KPI.Name.EQUIPMENT_PREPARATION_TIME,
 KPI.Name.VEHICLE_AMMO_BAY_ENGINE_FUEL_STRENGTH,
 KPI.Name.VEHICLE_AMMO_BAY_STRENGTH,
 KPI.Name.VEHICLE_CHASSIS_FALL_DAMAGE,
 KPI.Name.VEHICLE_CHASSIS_STRENGTH,
 KPI.Name.VEHICLE_FIRE_CHANCE,
 KPI.Name.VEHICLE_RAM_DAMAGE_RESISTANCE,
 KPI.Name.VEHICLE_REPAIR_SPEED,
 KPI.Name.STUN_RESISTANCE_EFFECT_FACTOR,
 KPI.Name.VEHICLE_FUEL_TANK_LESION_CHANCE,
 KPI.Name.VEHICLE_RAM_CHASSIS_DAMAGE_RESISTANCE,
 KPI.Name.FIRE_EXTINGUISHING_RATE,
 KPI.Name.WOUNDED_CREW_EFFICIENCY,
 KPI.Name.VEHICLE_HE_SHELL_DAMAGE_RESISTANCE,
 KPI.Name.VEHICLE_FALLING_DAMAGE_RESISTANCE,
 KPI.Name.VEHICLE_PENALTY_FOR_DAMAGED_ENGINE,
 KPI.Name.VEHICLE_PENALTY_FOR_DAMAGED_AMMORACK)
EXTRA_MOBILITY_PARAMS = (KPI.Name.VEHICLE_SPEED_GAIN,
 KPI.Name.MEDIUM_GROUND_FACTOR,
 KPI.Name.SOFT_GROUND_FACTOR,
 KPI.Name.WHEELS_ROTATION_SPEED)
EXTRA_CAMOUFLAGE_PARAMS = (KPI.Name.VEHICLE_OWN_SPOTTING_TIME, KPI.Name.FOLIAGE_MASKING_FACTOR, KPI.Name.COMMANDER_LAMP_DELAY)
EXTRA_VISIBILITY_PARAMS = (KPI.Name.VEHICLE_ENEMY_SPOTTING_TIME,
 KPI.Name.DEMASK_FOLIAGE_FACTOR,
 KPI.Name.DEMASK_MOVING_FACTOR,
 KPI.Name.PENALTY_TO_DAMAGED_SURVEYING_DEVICE,
 KPI.Name.ART_NOTIFICATION_DELAY_FACTOR,
 KPI.Name.DAMAGED_MODULES_DETECTION_TIME)
EXTRA_PARAMS_GROUP = {'relativePower': EXTRA_POWER_PARAMS,
 'relativeArmor': EXTRA_ARMOR_PARAMS,
 'relativeMobility': EXTRA_MOBILITY_PARAMS,
 'relativeCamouflage': EXTRA_CAMOUFLAGE_PARAMS,
 'relativeVisibility': EXTRA_VISIBILITY_PARAMS}
_ITEM_TYPE_HANDLERS = {ITEM_TYPES.vehicleRadio: params.RadioParams,
 ITEM_TYPES.vehicleEngine: params.EngineParams,
 ITEM_TYPES.vehicleChassis: params.ChassisParams,
 ITEM_TYPES.vehicleTurret: params.TurretParams,
 ITEM_TYPES.vehicleGun: params.GunParams,
 ITEM_TYPES.shell: params.ShellParams,
 ITEM_TYPES.equipment: params.EquipmentParams,
 ITEM_TYPES.optionalDevice: params.OptionalDeviceParams,
 ITEM_TYPES.vehicle: params.VehicleParams}
_STATE_TO_HIGHLIGHT = {PARAM_STATE.WORSE: HANGAR_ALIASES.VEH_PARAM_RENDERER_HIGHLIGHT_NEGATIVE,
 PARAM_STATE.BETTER: HANGAR_ALIASES.VEH_PARAM_RENDERER_HIGHLIGHT_POSITIVE,
 PARAM_STATE.NOT_APPLICABLE: HANGAR_ALIASES.VEH_PARAM_RENDERER_HIGHLIGHT_NONE,
 PARAM_STATE.NORMAL: HANGAR_ALIASES.VEH_PARAM_RENDERER_HIGHLIGHT_NONE}
_PARAMS_WITH_AVAILABLE_ZERO_VALUES = {DUAL_ACCURACY_COOLING_DELAY: lambda v: v is not None}

def isValidEmptyValue(paramName, paramValue):
    func = _PARAMS_WITH_AVAILABLE_ZERO_VALUES.get(paramName)
    return func(paramValue) if func is not None else False


def _getParamsProvider(item, vehicleDescr=None):
    if vehicles.isVehicleDescr(item.descriptor):
        return _ITEM_TYPE_HANDLERS[ITEM_TYPES.vehicle](item)
    itemTypeIdx, _, _ = vehicles.parseIntCompactDescr(item.descriptor.compactDescr)
    return _ITEM_TYPE_HANDLERS[itemTypeIdx](item.descriptor, vehicleDescr)


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


def get(item, vehicleDescr=None):
    try:
        return _getParamsProvider(item, vehicleDescr).getAllDataDict()
    except Exception:
        LOG_CURRENT_EXCEPTION()
        return dict()


def getParameters(item, vehicleDescr=None):
    return get(item, vehicleDescr).get('parameters', dict())


def getCompatibles(item, vehicleDescr=None):
    return get(item, vehicleDescr).get('compatible')


def similarCrewComparator(vehicle):
    vehicleParamsObject = params.VehicleParams(vehicle)
    vehicleParams = vehicleParamsObject.getParamsDict()
    bonuses = vehicleParamsObject.getBonuses(vehicle)
    compatibleArtefacts = g_paramsCache.getCompatibleArtefacts(vehicle)
    similarCrewVehicle = copy.copy(vehicle)
    similarCrewVehicle.crew = vehicle.getSimilarCrew()
    perfectVehicleParams = params.VehicleParams(similarCrewVehicle).getParamsDict()
    return VehiclesComparator(vehicleParams, perfectVehicleParams, compatibleArtefacts, bonuses)


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


def skillOnSimilarCrewComparator(vehicle, skillNames=None, highlightedSkills=None):
    vehicleWithIdealCrew = copy.copy(vehicle)
    vehicleWithIdealCrew.crew = vehicle.getSimilarCrew()
    situationalBonuses = []
    highlightedSkills = highlightedSkills or []
    skillNames = skillNames or []
    for skillName in skillNames:
        if skillName in CREW_MASTERY_BONUSES:
            situationalBonuses.append(skillName)

    if highlightedSkills:
        for highlightedSkill in highlightedSkills:
            if isSituationalBonus(highlightedSkill):
                vehicleWithIdealCrew.crew = vehicleWithIdealCrew.getCrewWithoutSkill(highlightedSkill)

    vehicleParamsObject = params.VehicleParams(vehicleWithIdealCrew, situationalBonuses)
    vehicleParams = vehicleParamsObject.getParamsDict()
    bonuses = vehicleParamsObject.getBonuses(vehicleWithIdealCrew)
    penalties = vehicleParamsObject.getPenalties(vehicleWithIdealCrew)
    compatibleArtefacts = g_paramsCache.getCompatibleArtefacts(vehicleWithIdealCrew)
    newVehicle = copy.copy(vehicle)
    newVehicle.crew = newVehicle.getCrewWithSkill(skillNames)
    updateCrewBonus(newVehicle)
    newVehicleParams = params.VehicleParams(newVehicle, situationalBonuses).getParamsDict()
    situationalParams, situationalKPI = getSituationalParams(skillNames)
    return VehiclesComparator(newVehicleParams, vehicleParams, suitableArtefacts=compatibleArtefacts, bonuses=bonuses, penalties=penalties, paramsThatCountAsSituational=situationalParams, situationalKPI=situationalKPI, highlightedBonuses=highlightedSkills)


def updateCrewBonus(vehicle):
    crewDescriptors = []
    for _, tman in vehicle.crew:
        crewDescriptors.append(tman.descriptor.makeCompactDescr() if tman else None)

    vehicle.calcCrewBonuses(crewDescriptors, vehicle.itemsCache.items, fromBattle=True)
    for _, tankman in vehicle.crew:
        if tankman is not None:
            tankman.updateBonusesFromVehicle(vehicle)

    return


def getSituationalParams(skillNames):
    from items import tankmen
    situationalParams = []
    situationalKPI = []
    for skillName in skillNames:
        if skillName in CREW_MASTERY_BONUSES:
            situationalParams.append('situationalCrewLevelIncrease')
        skill = tankmen.getSkillsConfig().getSkill(skillName)
        for param in skill.params.values():
            if param.situational:
                situationalParams.append(param.name)

        for kpi in skill.kpi:
            if kpi.situational:
                situationalKPI.append(kpi.name)

    return (situationalParams, situationalKPI)


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
    return VehiclesComparator(params.VehicleParams(comparableVehicle).getParamsDict(), params.VehicleParams(vehicle).getParamsDict(), suitableArtefacts=g_paramsCache.getCompatibleArtefacts(vehicle))


def previewVehiclesComparator(comparableVehicle, vehicle, withSituational=False):
    if vehicle is None:
        return
    else:
        skillNames = getSkillsDiff(comparableVehicle, vehicle) if withSituational else []
        situationalBonuses = []
        for skillName in skillNames:
            if skillName in CREW_MASTERY_BONUSES:
                situationalBonuses.append(skillName)

        situationalParams, situationalKPI = getSituationalParams(skillNames)
        updateCrewBonus(comparableVehicle)
        return VehiclesComparator(params.VehicleParams(comparableVehicle, situationalBonuses).getParamsDict(), params.VehicleParams(vehicle, situationalBonuses).getParamsDict(), suitableArtefacts=g_paramsCache.getCompatibleArtefacts(comparableVehicle), bonuses=params.VehicleParams(comparableVehicle, situationalBonuses).getBonuses(comparableVehicle, False), paramsThatCountAsSituational=situationalParams, situationalKPI=situationalKPI)


def previewNoSkillsVehiclesComparator(comparableVehicle, vehicle):
    if vehicle is None:
        return
    else:
        vehicleCopy = copy.copy(vehicle)
        vehicleCopy.crew = vehicle.getCrewWithoutSkills()
        comparableVehicleCopy = copy.copy(comparableVehicle)
        comparableVehicleCopy.crew = comparableVehicle.getCrewWithoutSkills()
        return VehiclesComparator(params.VehicleParams(comparableVehicleCopy).getParamsDict(), params.VehicleParams(vehicleCopy).getParamsDict(), suitableArtefacts=g_paramsCache.getCompatibleArtefacts(comparableVehicleCopy), bonuses=params.VehicleParams(comparableVehicleCopy).getBonuses(comparableVehicleCopy, False))


def getSkillsDiff(comparableVehicle, vehicle):
    skillsDiff = []
    for _, comparableTman in comparableVehicle.crew:
        if comparableTman:
            for skill in comparableTman.skillsMap:
                if not any((skill in tman.skillsMap for _, tman in vehicle.crew if tman)):
                    skillsDiff.append(skill)

    return skillsDiff


def _getIdealCrewVehicle(vehicle):
    perfectCrew = vehicle.getPerfectCrew()
    changedCrew = []
    for idx, tmanData in enumerate(vehicle.crew):
        _, tman = tmanData
        changedCrew.append(tmanData if tman and tman.isMaxRoleEfficiency else perfectCrew[idx])

    idealCrewVehicle = copy.copy(vehicle)
    idealCrewVehicle.crew = changedCrew
    return idealCrewVehicle


def tankSetupVehiclesComparator(comparableVehicle, vehicle):
    vehicleParamsObject = params.VehicleParams(comparableVehicle)
    return VehiclesComparator(vehicleParamsObject.getParamsDict(), params.VehicleParams(_getIdealCrewVehicle(vehicle)).getParamsDict(), suitableArtefacts=g_paramsCache.getCompatibleArtefacts(vehicle), bonuses=vehicleParamsObject.getBonuses(vehicle), penalties=vehicleParamsObject.getPenalties(vehicle))


def postProgressionVehiclesComparator(comparableVehicle, vehicle):
    vehicleParamsObject = params.VehicleParams(comparableVehicle)
    return VehiclesComparator(vehicleParamsObject.getParamsDict(), params.VehicleParams(_getIdealCrewVehicle(vehicle)).getParamsDict(), suitableArtefacts=g_paramsCache.getCompatibleArtefacts(comparableVehicle), bonuses=vehicleParamsObject.getBonuses(comparableVehicle, False), penalties=vehicleParamsObject.getPenalties(comparableVehicle) if vehicle.isInInventory else None)


def itemsComparator(currentItem, otherItem, vehicleDescr=None):
    return ItemsComparator(getParameters(currentItem, vehicleDescr), getParameters(otherItem, vehicleDescr))


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
        if comparator.getPenalties(paramName):
            return True

    return False


def __hasEffect(groupName, comparator, targetState):
    for paramName in chain(PARAMS_GROUPS[groupName], EXTRA_PARAMS_GROUP[groupName]):
        state = comparator.getExtendedData(paramName).state
        if type(state[0]) is not tuple:
            state = (state,)
        if any([ status == targetState for status, _ in state ]):
            return True

    return False


def hasNegativeEffect(groupName, comparator):
    return __hasEffect(groupName, comparator, PARAM_STATE.WORSE)


def hasPositiveEffect(groupName, comparator):
    return __hasEffect(groupName, comparator, PARAM_STATE.BETTER)


def hasSituationalEffect(groupName, comparator):
    return __hasEffect(groupName, comparator, PARAM_STATE.SITUATIONAL)


def getCommonParam(state, name, parentID='', highlight=HANGAR_ALIASES.VEH_PARAM_RENDERER_HIGHLIGHT_NONE):
    return {'state': state,
     'paramID': name,
     'parentID': parentID,
     'highlight': highlight}


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

    def getFormattedParams(self, comparator, expandedGroups=None, vehIntCD=None, diffParams=None, hasNormalization=False):
        result = []
        if not GUI_SETTINGS.technicalInfo:
            return result
        else:
            diffParams = diffParams if diffParams is not None else {}
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
                        param = comparator.getExtendedData(paramName, hasNormalization)
                        highlight = diffParams.get(paramName, HANGAR_ALIASES.VEH_PARAM_RENDERER_HIGHLIGHT_NONE)
                        formattedParam = self._makeAdvancedParamVO(param, groupName, highlight)
                        if formattedParam:
                            result.append(formattedParam)
                            hasParams = True

                    diffParams.update({'vehIntCD': vehIntCD})
                    result.extend(self._getExtraParams(comparator, groupName, diffParams))
                if hasParams and groupIdx < len(RELATIVE_PARAMS) - 1:
                    separator = self._makeSeparator(groupName)
                    if separator:
                        result.append(separator)

            return result

    def processDiffParams(self, comparator=None, expandedGroups=None):
        result = {}
        if comparator is None:
            return result
        else:
            for groupName in RELATIVE_PARAMS:
                needOpenGroup = False
                extraParams = EXTRA_PARAMS_GROUP[groupName] if self._isExtraParamEnabled() else []
                for paramName in PARAMS_GROUPS[groupName] + extraParams:
                    result[paramName] = highlight = self._getHighlightType(comparator, paramName)
                    needOpenGroup = needOpenGroup or highlight != HANGAR_ALIASES.VEH_PARAM_RENDERER_HIGHLIGHT_NONE

                if needOpenGroup and expandedGroups is not None:
                    expandedGroups[groupName] = True

            return result

    def _isExtraParamEnabled(self):
        return False

    def _isHiddenBooster(self, vehicle, extraParamName, paramValue, installedBoosters):
        if extraParamName in HIDDEN_PARAM_DEFAULTS and paramValue == HIDDEN_PARAM_DEFAULTS[extraParamName]:
            return True
        conditionalBonus = CONDITIONAL_BONUSES.get(extraParamName)
        if conditionalBonus:
            boosterName = next(((key[0] if key else None) for key in conditionalBonus.keys()))
            for item in installedBoosters:
                if vehicle and item and item.name == boosterName:
                    return not item.isAffectsOnVehicle(vehicle)

        return False

    def _getExtraParams(self, comparator, groupName, diffParams):
        from gui.Scaleform.daapi.view.lobby.tank_setup.ammunition_setup_vehicle import g_tankSetupVehicle
        result = []
        if self._isExtraParamEnabled():
            hasExtraParams = False
            vehicle = g_tankSetupVehicle.item
            if vehicle is None:
                return result
            installedBoosters = []
            if vehicle and vehicle.compactDescr == diffParams.get('vehIntCD'):
                installedBoosters = vehicle.battleBoosters.installed
            for extraParamName in EXTRA_PARAMS_GROUP[groupName]:
                param = comparator.getExtendedData(extraParamName)
                if self._isHiddenBooster(vehicle, extraParamName, param.value, installedBoosters):
                    continue
                highlight = diffParams.get(extraParamName, HANGAR_ALIASES.VEH_PARAM_RENDERER_HIGHLIGHT_NONE)
                formattedParam, nSlashCount = self._makeExtraParamVO(param, groupName, highlight)
                if formattedParam:
                    if not hasExtraParams:
                        lineSeparator = self._makeLineSeparator(groupName)
                        if lineSeparator:
                            result.append(lineSeparator)
                        hasExtraParams = True
                    result.append(formattedParam)
                    for _ in xrange(nSlashCount):
                        block = self._makeExtraAdditionalBlock(extraParamName, groupName, formattedParam['tooltip'])
                        if block is not None:
                            result.append(block)

        return result

    def _getHighlightType(self, comparator, paramName):
        paramState = comparator.getExtendedData(paramName).state
        if not isinstance(paramState[0], (tuple, list)):
            return _STATE_TO_HIGHLIGHT[paramState[0]]
        highlight = HANGAR_ALIASES.VEH_PARAM_RENDERER_HIGHLIGHT_NONE
        for state in paramState:
            stateHighlight = _STATE_TO_HIGHLIGHT[state[0]]
            if highlight == HANGAR_ALIASES.VEH_PARAM_RENDERER_HIGHLIGHT_NONE:
                highlight = stateHighlight
            if stateHighlight != HANGAR_ALIASES.VEH_PARAM_RENDERER_HIGHLIGHT_NONE and highlight != stateHighlight:
                highlight = HANGAR_ALIASES.VEH_PARAM_RENDERER_HIGHLIGHT_MIXED

        return highlight

    def _makeSimpleParamHeaderVO(self, param, isOpen, comparator):
        return getCommonParam(HANGAR_ALIASES.VEH_PARAM_RENDERER_STATE_SIMPLE_TOP, param.name)

    def _makeAdvancedParamVO(self, param, parentID, highlight):
        return getCommonParam(HANGAR_ALIASES.VEH_PARAM_RENDERER_STATE_ADVANCED, param.name, parentID, highlight)

    def _makeExtraParamVO(self, param, parentID, highlight):
        return (getCommonParam(HANGAR_ALIASES.VEH_PARAM_RENDERER_STATE_EXTRA, param.name, parentID, highlight), 0)

    def _makeSimpleParamBottomVO(self, param, vehIntCD=None):
        return None

    def _makeExtraAdditionalBlock(self, paramID, parentID, tooltip):
        return None

    def _makeSeparator(self, parentID):
        return None

    def _makeLineSeparator(self, parentID):
        return None
