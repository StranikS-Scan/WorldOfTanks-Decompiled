# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/items_parameters/params.py
import collections
import copy
import inspect
import math
import operator
from collections import namedtuple, defaultdict
from itertools import izip_longest
from math import ceil, floor
import BigWorld
import typing
from constants import SHELL_TYPES, BonusTypes, IS_DEVELOPMENT
from debug_utils import LOG_DEBUG
from gui import GUI_SETTINGS
from gui.shared.formatters import text_styles
from gui.shared.gui_items import KPI
from gui.shared.gui_items.Tankman import isSkillLearnt, crewMemberRealSkillLevel
from gui.shared.items_parameters import calcGunParams, calcShellParams, getShotsPerMinute, getGunDescriptors, isAutoReloadGun, isDualGun, isDualAccuracy, isTwinGun
from gui.shared.items_parameters import functions, getShellDescriptors, getOptionalDeviceWeight, NO_DATA
from gui.shared.items_parameters.comparator import rateParameterState, PARAM_STATE
from gui.shared.items_parameters.functions import getBasicShell, getRocketAccelerationKpiFactors
from gui.shared.items_parameters.params_cache import g_paramsCache
from gui.shared.utils import DAMAGE_PROP_NAME, PIERCING_POWER_PROP_NAME, AIMING_TIME_PROP_NAME, STUN_DURATION_PROP_NAME, GUARANTEED_STUN_DURATION_PROP_NAME, AUTO_RELOAD_PROP_NAME, GUN_AUTO_RELOAD, GUN_CAN_BE_AUTO_RELOAD, GUN_AUTO_SHOOT, GUN_CAN_BE_AUTO_SHOOT, MAX_STEERING_LOCK_ANGLE, WHEELED_SWITCH_OFF_TIME, WHEELED_SWITCH_ON_TIME, WHEELED_SWITCH_TIME, WHEELED_SPEED_MODE_SPEED, GUN_DUAL_GUN, GUN_CAN_BE_DUAL_GUN, RELOAD_TIME_SECS_PROP_NAME, DUAL_GUN_CHARGE_TIME, DUAL_GUN_RATE_TIME, TURBOSHAFT_ENGINE_POWER, TURBOSHAFT_SPEED_MODE_SPEED, TURBOSHAFT_INVISIBILITY_MOVING_FACTOR, TURBOSHAFT_INVISIBILITY_STILL_FACTOR, TURBOSHAFT_SWITCH_TIME, TURBOSHAFT_SWITCH_ON_TIME, TURBOSHAFT_SWITCH_OFF_TIME, CHASSIS_REPAIR_TIME, ROCKET_ACCELERATION_ENGINE_POWER, ROCKET_ACCELERATION_SPEED_LIMITS, ROCKET_ACCELERATION_REUSE_AND_DURATION, DUAL_ACCURACY_COOLING_DELAY, DUAL_ACCURACY_AFTER_SHOT_DISPERSION_ANGLE, BURST_FIRE_RATE, MAX_MUTABLE_DAMAGE_PROP_NAME, MIN_MUTABLE_DAMAGE_PROP_NAME, AUTO_SHOOT_CLIP_FIRE_RATE, TWIN_GUN_SWITCH_FIRE_MODE_TIME, TWIN_GUN_TOP_SPEED, GUN_CAN_BE_TWIN_GUN, GUN_TWIN_GUN
from gui.shared.utils import DISPERSION_RADIUS_PROP_NAME, SHELLS_PROP_NAME, SHELLS_COUNT_PROP_NAME
from gui.shared.utils import RELOAD_TIME_PROP_NAME, RELOAD_MAGAZINE_TIME_PROP_NAME, SHELL_RELOADING_TIME_PROP_NAME
from helpers import time_utils, dependency
from items import getTypeOfCompactDescr, getTypeInfoByIndex, ITEM_TYPES, vehicles, tankmen
from items import utils as items_utils
from items.components import component_constants
from post_progression_common import ACTION_TYPES
from shared_utils import findFirst, first
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
from helpers_common import computePiercingPowerAtDist, computeDamageAtDist
if typing.TYPE_CHECKING:
    from items.vehicles import VehicleDescriptor, CompositeVehicleDescriptor, VehicleDescr
    from gui.shared.gui_items.Vehicle import Vehicle
_DO_TTC_LOG = False and IS_DEVELOPMENT
MAX_VISION_RADIUS = 500
MIN_VISION_RADIUS = 150
PIERCING_DISTANCES = (50, 500)
ONE_HUNDRED_PERCENTS = 100
MIN_RELATIVE_VALUE = 1
EXTRAS_CAMOUFLAGE = 'camouflageExtras'
MAX_DAMAGED_MODULES_DETECTION_PERK_VAL = -4
MAX_ART_NOTIFICATION_DELAY_PERK_VAL = -2
_Weight = namedtuple('_Weight', 'current, max')
_Invisibility = namedtuple('_Invisibility', 'current, atShot')
_PenaltyInfo = namedtuple('_PenaltyInfo', 'roleName, value, vehicleIsNotNative')
MODULES = {ITEM_TYPES.vehicleRadio: lambda vehicleDescr: vehicleDescr.radio,
 ITEM_TYPES.vehicleEngine: lambda vehicleDescr: vehicleDescr.engine,
 ITEM_TYPES.vehicleChassis: lambda vehicleDescr: vehicleDescr.chassis,
 ITEM_TYPES.vehicleTurret: lambda vehicleDescr: vehicleDescr.turret,
 ITEM_TYPES.vehicleGun: lambda vehicleDescr: vehicleDescr.gun}
HIDDEN_PARAM_DEFAULTS = {KPI.Name.ART_NOTIFICATION_DELAY_FACTOR: 2.1,
 KPI.Name.DAMAGED_MODULES_DETECTION_TIME: 4.5}
METERS_PER_SECOND_TO_KILOMETERS_PER_HOUR = 3.6
_FACTOR_TO_SKILL_PENALTY_MAP = {'turret/rotationSpeed': ('turretRotationSpeed', 'relativePower'),
 'circularVisionRadius': ('circularVisionRadius', 'relativeVisibility'),
 'radio/distance': ('radioDistance', 'relativeVisibility'),
 'gun/reloadTime': ('reloadTime',
                    'avgDamagePerMinute',
                    'relativePower',
                    'reloadTimeSecs',
                    'clipFireRate',
                    AUTO_SHOOT_CLIP_FIRE_RATE,
                    'autoReloadTime'),
 'gun/aimingTime': ('aimingTime',),
 'vehicle/rotationSpeed': ('chassisRotationSpeed', 'relativeMobility'),
 'chassis/terrainResistance': ('chassisRotationSpeed', 'relativeMobility'),
 'shotDispersion': ('shotDispersionAngle',),
 'dualAccuracyCoolingDelay': (DUAL_ACCURACY_COOLING_DELAY,)}
_SHELL_KINDS = (SHELL_TYPES.HOLLOW_CHARGE,
 SHELL_TYPES.HIGH_EXPLOSIVE,
 SHELL_TYPES.ARMOR_PIERCING,
 SHELL_TYPES.ARMOR_PIERCING_HE,
 SHELL_TYPES.ARMOR_PIERCING_CR)
_AUTOCANNON_SHOT_DISTANCE = 400

def _processExtraBonuses(vehicle):
    result = []
    withRareCamouflage = vehicle.intCD in g_paramsCache.getVehiclesWithoutCamouflage()
    if withRareCamouflage or vehicle.hasBonusCamo():
        result.append((EXTRAS_CAMOUFLAGE, 'extra'))
    return result


def _universalSum(a, b):
    return map(operator.add, a, b) if isinstance(a, collections.Sequence) else a + b


def _getInstalledModuleVehicle(vehicleDescr, itemDescr):
    curVehicle = None
    if vehicleDescr:
        compDescrType = getTypeOfCompactDescr(itemDescr.compactDescr)
        module = MODULES[compDescrType](vehicleDescr)
        if module.id[1] == itemDescr.id[1]:
            curVehicle = vehicleDescr.type.userString
    return curVehicle


def _average(listOfNumbers):
    return sum(listOfNumbers) / len(listOfNumbers)


def _isStunParamVisible(shellDict):
    lobbyContext = dependency.instance(ILobbyContext)
    return shellDict.hasStun and lobbyContext.getServerSettings().spgRedesignFeatures.isStunEnabled()


def _timesToSecs(timesPerMinutes):
    return time_utils.ONE_MINUTE / timesPerMinutes


def _getMaxSteeringLockAngle(axleSteeringLockAngles):
    return max(map(abs, axleSteeringLockAngles)) if axleSteeringLockAngles else None


def _turboshaftEnginePower(vehicleDescr, engineName):
    return vehicleDescr.siegeVehicleDescr.physics['enginePower'] if vehicleDescr.hasTurboshaftEngine else None


def _rocketAccelerationEnginePower(vehicleDescr, value):
    return value * getRocketAccelerationKpiFactors(vehicleDescr).getCoeff(KPI.Name.VEHICLE_ENGINE_POWER) if vehicleDescr.hasRocketAcceleration else None


class _ParameterBase(object):

    def __init__(self, itemDescr, vehicleDescr=None):
        self._itemDescr = itemDescr
        self._vehicleDescr = vehicleDescr
        self.__preCachedInfo = None
        self.__rawParams = None
        return

    def getParamsDict(self):
        return _ParamsDictProxy(self)

    def getAllDataDict(self):
        params = self.getParamsDict() if GUI_SETTINGS.technicalInfo else {}
        return {'parameters': params,
         'compatible': self._getCompatible()}

    def _getPrecachedInfo(self):
        if self.__preCachedInfo is None:
            self.__preCachedInfo = g_paramsCache.getPrecachedParameters(self._itemDescr.compactDescr)
        return self.__preCachedInfo

    def _getRawParams(self):
        if self.__rawParams is None:
            self.__rawParams = self._extractRawParams()
        return self.__rawParams

    def _extractRawParams(self):
        return self._getPrecachedInfo().params

    def _getCompatible(self):
        return tuple()


class CompatibleParams(_ParameterBase):

    @property
    def compatibles(self):
        return g_paramsCache.getComponentVehiclesNames(self._itemDescr.compactDescr)

    def _getCompatible(self):
        curVehicle = _getInstalledModuleVehicle(self._vehicleDescr, self._itemDescr)
        return (('vehicles', _formatCompatibles(curVehicle, self.compatibles)),)


class WeightedParam(CompatibleParams):

    @property
    def weight(self):
        return self._itemDescr.weight


class RadioParams(WeightedParam):

    @property
    def radioDistance(self):
        return int(self._itemDescr.distance)


class EngineParams(WeightedParam):

    @property
    def enginePower(self):
        return int(round(self._itemDescr.power / component_constants.HP_TO_WATTS, 0))

    @property
    def turboshaftEnginePower(self):
        power = _turboshaftEnginePower(self._vehicleDescr, self._itemDescr.name)
        return power and int(round(power / component_constants.HP_TO_WATTS))

    @property
    def rocketAccelerationEnginePower(self):
        return _rocketAccelerationEnginePower(self._vehicleDescr, self.enginePower)

    @property
    def fireStartingChance(self):
        return int(round(self._itemDescr.fireStartingChance * ONE_HUNDRED_PERCENTS))

    @property
    def forwardMaxSpeed(self):
        return self._vehicleDescr.type.xphysics['engines'][self._itemDescr.name]['smplFwMaxSpeed']


class ChassisParams(WeightedParam):
    itemsCache = dependency.descriptor(IItemsCache)

    @property
    def maxLoad(self):
        return self._itemDescr.maxLoad / 1000

    @property
    def rotationSpeed(self):
        return int(round(math.degrees(self._itemDescr.rotationSpeed))) if not self.isWheeled or self.isWheeledOnSpotRotation else None

    @property
    def maxSteeringLockAngle(self):
        return _getMaxSteeringLockAngle(g_paramsCache.getWheeledChassisAxleLockAngles(self._itemDescr.compactDescr)) if self.isWheeled else None

    @property
    def chassisRepairTime(self):
        chassis = self._itemDescr
        repairTimes = []
        if chassis.trackPairs:
            for track in chassis.trackPairs:
                repairTimes.append(track.healthParams.repairTime)

            repairTimes.reverse()
        else:
            repairTimes.append(chassis.repairTime)
        return [ repairTime / 0.57 for repairTime in repairTimes ]

    @property
    def isHydraulic(self):
        return self._getPrecachedInfo().isHydraulic

    @property
    def isWheeled(self):
        return self._getPrecachedInfo().isWheeled

    @property
    def isTrackWithinTrack(self):
        return self._getPrecachedInfo().isTrackWithinTrack

    @property
    def hasAutoSiege(self):
        return self._getPrecachedInfo().hasAutoSiege

    @property
    def isWheeledOnSpotRotation(self):
        return self._getPrecachedInfo().isWheeledOnSpotRotation


class TurretParams(WeightedParam):

    @property
    def armor(self):
        return tuple((round(armor) for armor in self._itemDescr.primaryArmor))

    @property
    def rotationSpeed(self):
        return int(round(math.degrees(self._itemDescr.rotationSpeed)))

    @property
    def circularVisionRadius(self):
        return self._itemDescr.circularVisionRadius

    @property
    def gunCompatibles(self):
        return [ gun.i18n.userString for gun in self._itemDescr.guns ]

    def _getCompatible(self):
        if self._vehicleDescr is not None:
            curGun = self._vehicleDescr.gun.i18n.userString
        else:
            curGun = None
        compatibleVehicles = list(super(TurretParams, self)._getCompatible())
        compatibleVehicles.append(('guns', _formatCompatibles(curGun, self.gunCompatibles)))
        return tuple(compatibleVehicles)


class VehicleParams(_ParameterBase):

    def __init__(self, vehicle, situationalBonuses=None):
        super(VehicleParams, self).__init__(self._getVehicleDescriptor(vehicle))
        self.__factors = functions.getVehicleFactors(vehicle, situationalBonuses)
        self.__kpi = functions.getKpiFactors(vehicle)
        self.__coefficients = g_paramsCache.getSimplifiedCoefficients()
        self.__vehicle = vehicle

    def __getattr__(self, item):
        if KPI.Name.hasValue(item):
            return self.__kpi.getFactor(item)
        suffix = 'Situational'
        if item.endswith(suffix):
            return getattr(self, item[:-len(suffix)])
        raise AttributeError('Cant get factor {0}'.format(item))

    @property
    def maxHealth(self):
        return self._itemDescr.maxHealth

    @property
    def vehicleWeight(self):
        return _Weight(self._itemDescr.physics['weight'] / 1000, self._itemDescr.miscAttrs['maxWeight'] / 1000)

    @property
    def enginePower(self):
        skillName = 'driver_motorExpert'
        argName = 'enginePower'
        enginePowerFactor = self.__getFactorValueFromSkill(skillName, argName)
        enginePower = self.__getEnginePower(self._itemDescr.physics['enginePower'])
        if _DO_TTC_LOG:
            LOG_DEBUG('TTC of enginePower: enginePower:%f * driver_motorExpertFactor:%f' % (enginePower, enginePowerFactor))
        return enginePower * enginePowerFactor

    @property
    def turboshaftEnginePower(self):
        power = _turboshaftEnginePower(self._itemDescr, self._itemDescr.engine.name)
        if power:
            skillName = 'driver_motorExpert'
            argName = 'enginePower'
            enginePowerFactor = self.__getFactorValueFromSkill(skillName, argName)
            power = power * enginePowerFactor
            if _DO_TTC_LOG:
                LOG_DEBUG('TTC of turboshaftEnginePower: power:%f * driver_motorExpertFactor:%f' % (power, enginePowerFactor))
        return power and self.__getEnginePower(power)

    @property
    def enginePowerPerTon(self):
        powerPerTon = round(self.enginePower / self.vehicleWeight.current, 2)
        if self._itemDescr.hasTurboshaftEngine:
            return (powerPerTon, round(self.turboshaftEnginePower / self.vehicleWeight.current, 2))
        return (powerPerTon, round(self.rocketAccelerationEnginePower / self.vehicleWeight.current, 2)) if self._itemDescr.hasRocketAcceleration else (powerPerTon,)

    @property
    def speedLimits(self):
        return self.__speedLimits(self._itemDescr.physics['speedLimits'], ('forwardMaxSpeedKMHTerm', 'backwardMaxSpeedKMHTerm'))

    @property
    def wheeledSpeedModeSpeed(self):
        return self.__speedLimits(self._itemDescr.siegeVehicleDescr.physics['speedLimits'], ('forwardMaxSpeedKMHTerm', 'backwardMaxSpeedKMHTerm')) if self.__hasWheeledSwitchMode() else None

    @property
    def turboshaftSpeedModeSpeed(self):
        return self.__speedLimits(self._itemDescr.siegeVehicleDescr.physics['speedLimits'], ('forwardMaxSpeedKMHTerm', 'backwardMaxSpeedKMHTerm')) if self.__hasTurboshaftSwitchMode() else None

    @property
    def rocketAccelerationEnginePower(self):
        return _rocketAccelerationEnginePower(self._itemDescr, self.enginePower)

    @property
    def rocketAccelerationSpeedLimits(self):
        if self._itemDescr.hasRocketAcceleration:
            rocketFactors = getRocketAccelerationKpiFactors(self._itemDescr)

            def rounder(v, needRound):
                return float(round(v, 2)) if needRound else float(v)

            return [ rounder(value * coeff, needRound) for value, coeff, needRound in zip(self.speedLimits, (rocketFactors.getCoeff(KPI.Name.VEHICLE_FORWARD_MAX_SPEED), rocketFactors.getCoeff(KPI.Name.VEHICLE_BACKWARD_MAX_SPEED)), (True, False)) ]
        else:
            return None

    @property
    def rocketAccelerationReuseAndDuration(self):
        if self._itemDescr.hasRocketAcceleration:
            rocketParams = self._itemDescr.type.rocketAccelerationParams
            return (rocketParams.reuseCount, rocketParams.duration)
        else:
            return None

    @property
    def dualAccuracyAfterShotDispersionAngle(self):
        return float(math.tan(self._itemDescr.gun.dualAccuracy.afterShotDispersionAngle) * 100) if self._itemDescr.hasDualAccuracy else None

    @property
    def dualAccuracyCoolingDelay(self):
        return items_utils.getClientCoolingDelay(self._itemDescr, self.__factors) if self._itemDescr.hasDualAccuracy else None

    @property
    def chassisRotationSpeed(self):
        skillName = 'driver_virtuoso'
        argName = 'vehicleAllGroundRotationSpeed'
        if self._itemDescr.isWheeledVehicle and not self._itemDescr.isWheeledOnSpotRotation:
            return None
        else:
            allTrfs = self.__getTerrainResistanceFactors()
            avgTrf = sum(allTrfs) / len(allTrfs)
            chassisRotationSpeed = items_utils.getChassisRotationSpeed(self._itemDescr, self.__factors)
            baseRotationSpeed = math.degrees(chassisRotationSpeed) / avgTrf
            rotationSpeedFactor = self.__getFactorValueFromSkill(skillName, argName)
            if _DO_TTC_LOG:
                LOG_DEBUG('TTC of chassisRotationSpeed: baseRotationSpeed:%f * driver_virtuosoFactor:%f' % (baseRotationSpeed, rotationSpeedFactor))
            return baseRotationSpeed * rotationSpeedFactor

    @property
    def maxSteeringLockAngle(self):
        return _getMaxSteeringLockAngle(self.__getChassisPhysics().get('axleSteeringLockAngles')) if self._itemDescr.isWheeledVehicle else None

    @property
    def wheelRiseSpeed(self):
        return self.__getChassisPhysics().get('wheelRiseSpeed') if self._itemDescr.isWheeledVehicle else None

    @property
    def hullArmor(self):
        return tuple((round(armor) for armor in self._itemDescr.hull.primaryArmor))

    @property
    def damage(self):
        shell = self._itemDescr.shot.shell
        return self.__calculateDamageOrPiercingRandom(shell.armorDamage[0], shell.damageRandomization)

    @property
    def maxMutableDamage(self):
        shell = self._itemDescr.shot.shell
        if shell.isDamageMutable:
            damage = computeDamageAtDist(shell.armorDamage, PIERCING_DISTANCES[0])
            return self.__calculateDamageOrPiercingRandom(damage, shell.damageRandomization)
        else:
            return None

    @property
    def minMutableDamage(self):
        shell = self._itemDescr.shot.shell
        if shell.isDamageMutable:
            dist = min(self._itemDescr.shot.maxDistance, PIERCING_DISTANCES[1])
            damage = computeDamageAtDist(shell.armorDamage, dist)
            return self.__calculateDamageOrPiercingRandom(damage, shell.damageRandomization)
        else:
            return None

    @property
    def avgDamage(self):
        return int(round(sum(self.damage) / 2.0))

    @property
    def avgDamagePerSecond(self):
        return round(float(self.avgDamage) / self._itemDescr.gun.clip[1]) if self._itemDescr.isAutoShootGunVehicle else None

    @property
    def chargeTime(self):
        return (float(self._itemDescr.gun.dualGun.chargeTime), self._itemDescr.gun.dualGun.reloadLockTime) if self.__hasDualGun() else None

    @property
    def avgDamagePerMinute(self):
        if _DO_TTC_LOG:
            LOG_DEBUG('TTC of avgDamagePerMinute:')
        return round(max(self.__calcReloadTime()) * self.avgDamage)

    @property
    def avgDamagePerMinuteSituational(self):
        if _DO_TTC_LOG:
            LOG_DEBUG('TTC of avgDamagePerMinuteSituational:')
        return round(max(self.__calcReloadTime(isSituational=True)) * self.avgDamage)

    @property
    def avgPiercingPower(self):
        return int(round(sum(self.piercingPower) / 2.0))

    @property
    def piercingPower(self):
        piercingPower = self._itemDescr.shot.piercingPower[0]
        piercingPowerRandomization = self._itemDescr.shot.shell.piercingPowerRandomization
        return self.__calculateDamageOrPiercingRandom(piercingPower, piercingPowerRandomization)

    @property
    def maxPiercingPower(self):
        shell = self._itemDescr.shot.shell
        if shell.isPiercingDistanceDependent:
            piercingPower = computePiercingPowerAtDist(self._itemDescr.shot.piercingPower, PIERCING_DISTANCES[0])
            piercingPowerRandomization = self._itemDescr.shot.shell.piercingPowerRandomization
            return self.__calculateDamageOrPiercingRandom(piercingPower, piercingPowerRandomization)
        else:
            return None

    @property
    def minPiercingPower(self):
        shell = self._itemDescr.shot.shell
        if shell.isPiercingDistanceDependent:
            dist = min(self._itemDescr.shot.maxDistance, PIERCING_DISTANCES[1])
            piercingPower = computePiercingPowerAtDist(self._itemDescr.shot.piercingPower, dist)
            piercingPowerRandomization = self._itemDescr.shot.shell.piercingPowerRandomization
            return self.__calculateDamageOrPiercingRandom(piercingPower, piercingPowerRandomization)
        else:
            return None

    @property
    def reloadTime(self):
        if _DO_TTC_LOG:
            LOG_DEBUG('TTC of reloadTime:')
        return None if self.__hasAutoReload() or self.__hasDualGun() or self.__hasTwinGun() else min(self.__calcReloadTime())

    @property
    def reloadTimeSituational(self):
        if _DO_TTC_LOG:
            LOG_DEBUG('TTC of reloadTimeSituational:')
        return None if self.__hasAutoReload() or self.__hasDualGun() or self.__hasTwinGun() else min(self.__calcReloadTime(isSituational=True))

    @property
    def continuousShotsPerMinute(self):
        return round(60.0 / self._itemDescr.gun.clip[1]) if self._itemDescr.isAutoShootGunVehicle else None

    @property
    def turretRotationSpeed(self):
        rotSpeedVal = round(math.degrees(items_utils.getTurretRotationSpeed(self._itemDescr, self.__factors)), 2)
        skillName = 'gunner_quickAiming'
        argName = 'turretRotationSpeed'
        factor = self.__getFactorValueFromSkill(skillName, argName)
        rotSpeedVal *= factor
        if self.__hasUnsupportedSwitchMode() or self.__hasTwinGun():
            rotSpeedSiegeVal = items_utils.getTurretRotationSpeed(self._itemDescr.siegeVehicleDescr, self.__factors)
            rotSpeedSiegeVal *= factor
            return (rotSpeedVal, round(math.degrees(rotSpeedSiegeVal), 2))
        return (rotSpeedVal,)

    @property
    def circularVisionRadius(self):
        baseCircularVisionRadius = items_utils.getCircularVisionRadius(self._itemDescr, self.__factors)
        skillName = 'radioman_finder'
        argName = 'vehicleCircularVisionRadius'
        factor = self.__getFactorValueFromSkill(skillName, argName)
        baseCircularVisionRadius *= factor
        if _DO_TTC_LOG:
            LOG_DEBUG('TTC of circularVisionRadius: round(baseCircularVisionRadius:%f * radioman_finderFactor:%f)' % (baseCircularVisionRadius, factor))
        result = round(baseCircularVisionRadius)
        if self.__hasUnsupportedSwitchMode():
            visRadiusSiegeVal = items_utils.getCircularVisionRadius(self._itemDescr.siegeVehicleDescr, self.__factors)
            return (result, round(visRadiusSiegeVal * factor))
        return (result,)

    @property
    def radioDistance(self):
        baseDistance = items_utils.getRadioDistance(self._itemDescr, self.__factors)
        return int(baseDistance)

    @property
    def turretArmor(self):
        return tuple((round(armor) for armor in self._itemDescr.turret.primaryArmor)) if self.__hasTurret() else None

    @property
    def explosionRadius(self):
        shotShell = self._itemDescr.shot.shell
        return round(shotShell.type.explosionRadius, 2) if shotShell.kind == SHELL_TYPES.HIGH_EXPLOSIVE else 0

    @property
    def aimingTime(self):
        aimingTimeVal = items_utils.getGunAimingTime(self._itemDescr, self.__factors)
        skillName = 'gunner_quickAiming'
        argName = 'aimingTime'
        gunnerQuickAimingFactor = self.__getFactorValueFromSkill(skillName, argName)
        if _DO_TTC_LOG:
            LOG_DEBUG('TTC of aimingTime: aimingTimeVal:%f * gunner_quickAimingFactor:%f' % (aimingTimeVal, gunnerQuickAimingFactor))
        aimingTimeVal *= gunnerQuickAimingFactor
        if self._itemDescr.hasTurboshaftEngine or self.__hasTwinGun():
            siegeAimingTimeVal = items_utils.getGunAimingTime(self._itemDescr.siegeVehicleDescr, self.__factors)
            siegeAimingTimeVal *= gunnerQuickAimingFactor
            if aimingTimeVal != siegeAimingTimeVal:
                return (aimingTimeVal, siegeAimingTimeVal)
        return (aimingTimeVal,)

    @property
    def aimingTimeSituational(self):
        aimingTimeVal = items_utils.getGunAimingTime(self._itemDescr, self.__factors)
        skillName = 'gunner_quickAiming'
        argName = 'aimingTime'
        gunnerQuickAimingFactor = self.__getFactorValueFromSkill(skillName, argName)
        skillName = 'commander_coordination'
        commanderCoordinationReloadFactor = self.__getFactorValueFromSkill(skillName, argName)
        if _DO_TTC_LOG:
            LOG_DEBUG('TTC of aimingTimeSituational: aimingTimeVal:%f * gunner_quickAimingFactor:%f * commander_coordinationFactor:%f' % (aimingTimeVal, gunnerQuickAimingFactor, commanderCoordinationReloadFactor))
        aimingTimeVal *= gunnerQuickAimingFactor
        aimingTimeVal *= commanderCoordinationReloadFactor
        if self._itemDescr.hasTurboshaftEngine:
            siegeAimingTimeVal = items_utils.getGunAimingTime(self._itemDescr.siegeVehicleDescr, self.__factors)
            siegeAimingTimeVal *= gunnerQuickAimingFactor
            siegeAimingTimeVal *= commanderCoordinationReloadFactor
            return (aimingTimeVal, siegeAimingTimeVal)
        return (aimingTimeVal,)

    def __shotDispersionAngle(self, isSituational=False):
        shotDispersions = items_utils.getClientShotDispersion(self._itemDescr, self.__factors['shotDispersion'][0])
        baseShotDispersions = (round(shotDispersion * 100, 4) for shotDispersion in shotDispersions)
        focusFactorValue = 1
        skillName = 'gunner_armorer'
        argName = 'shotDispersionAngle'
        armorerFactorValue = self.__getFactorValueFromSkill(skillName, argName)
        if isSituational:
            skillName = 'gunner_focus'
            focusFactorValue = self.__getFactorValueFromSkill(skillName, argName)
        resShotDispersion = [ baseShotDispersion * armorerFactorValue * focusFactorValue for baseShotDispersion in baseShotDispersions ]
        if _DO_TTC_LOG:
            for shotDispersion in resShotDispersion:
                LOG_DEBUG('TTC of shotDispersionAngle: baseShotDispersion:%f * gunner_armorerFactor:%f * gunner_focusFactor:%f' % (shotDispersion, armorerFactorValue, focusFactorValue))

        return resShotDispersion

    @property
    def shotDispersionAngle(self):
        return self.__shotDispersionAngle()

    @property
    def shotDispersionAngleSituational(self):
        return self.__shotDispersionAngle(isSituational=True)

    @property
    def reloadTimeSecs(self):
        if _DO_TTC_LOG:
            LOG_DEBUG('TTC of reloadTimeSecs:')
        if self.__hasClipGun() or self.__hasAutoReload():
            return None
        elif self.__hasDualGun():
            return tuple((_timesToSecs(reloadTime) for reloadTime in self.__calcReloadTime()))
        else:
            return tuple((_timesToSecs(reloadTime) for reloadTime in reversed(self.__calcReloadTime()))) if self.__hasTwinGun() else (_timesToSecs(first(self.__calcReloadTime())),)

    @property
    def reloadTimeSecsSituational(self):
        if _DO_TTC_LOG:
            LOG_DEBUG('TTC of reloadTimeSecsSituational:')
        if self.__hasClipGun() or self.__hasAutoReload():
            return None
        elif self.__hasDualGun():
            return tuple((_timesToSecs(reloadTime) for reloadTime in self.__calcReloadTime(isSituational=True)))
        elif self.__hasTwinGun():
            isSituational = True
            return tuple((_timesToSecs(reloadTime) for reloadTime in reversed(self.__calcReloadTime(isSituational))))
        else:
            _val = self.__calcReloadTime(isSituational=True)
            return (_timesToSecs(first(_val)),)

    @property
    def autoReloadTime(self):
        return tuple(reversed(items_utils.getClipReloadTime(self._itemDescr, self.__factors))) if self.__hasAutoReload() else None

    @property
    def autoReloadTimeSituational(self):
        if self.__hasAutoReload():
            skillName = 'loader_melee'
            argName = 'gunReloadSpeed'
            loaderMeleeReloadFactor = self.__getFactorValueFromSkill(skillName, argName)
            skillName = 'loader_desperado'
            argName = 'gunReloadSpeed'
            loaderDesperadoReloadFactor = self.__getFactorValueFromSkill(skillName, argName)
            reloadTimes = tuple(reversed(items_utils.getClipReloadTime(self._itemDescr, self.__factors)))
            return tuple((reloadTime * loaderMeleeReloadFactor * loaderDesperadoReloadFactor for reloadTime in reloadTimes))
        else:
            return None

    @property
    def relativePower(self):
        coeffs = self.__coefficients['power']
        penetration = self._itemDescr.shot.piercingPower[0]
        rotationSpeed = self.turretRotationSpeed[0]
        turretCoefficient = 1 if self.__hasTurret() else coeffs['turretCoefficient']
        heCorrection = 1.0
        if 'SPG' in self._itemDescr.type.tags:
            spgCorrection = 6
        else:
            spgCorrection = 1
            if self.__currentShot().shell.kind == SHELL_TYPES.HIGH_EXPLOSIVE:
                heCorrection = coeffs['alphaDamage']
        gunCorrection = self.__adjustmentCoefficient('guns').get(self._itemDescr.gun.name, {})
        gunCorrection = gunCorrection.get('caliberCorrection', 1)
        value = round(self.avgDamagePerMinute * penetration / self.shotDispersionAngle[-1] * (coeffs['rotationIntercept'] + coeffs['rotationSlope'] * rotationSpeed) * turretCoefficient * coeffs['normalization'] * self.__adjustmentCoefficient('power') * spgCorrection * gunCorrection * heCorrection)
        return max(value, MIN_RELATIVE_VALUE)

    @property
    def relativeArmor(self):
        coeffs = self.__coefficients['armour']
        hullArmor = self._itemDescr.hull.primaryArmor
        turretArmor = self._itemDescr.turret.primaryArmor if self.__hasTurret() else hullArmor
        value = round((hullArmor[0] * coeffs['hullFront'] + hullArmor[1] * coeffs['hullSide'] + hullArmor[2] * coeffs['hullBack'] + turretArmor[0] * coeffs['turretFront'] + turretArmor[1] * coeffs['turretSide'] + turretArmor[2] * coeffs['turretBack']) * self.maxHealth * coeffs['normalization'] * self.__adjustmentCoefficient('armour'))
        return max(value, MIN_RELATIVE_VALUE)

    @property
    def relativeMobility(self):
        coeffs = self.__coefficients['mobility']
        if self._itemDescr.isWheeledVehicle and not self._itemDescr.isWheeledOnSpotRotation:
            suspensionInfluence = self.maxSteeringLockAngle * coeffs['maxSteeringLockAngle']
        else:
            suspensionInfluence = self.chassisRotationSpeed * coeffs['chassisRotation']
        value = round((suspensionInfluence + self.speedLimits[0] * coeffs['speedLimit'] + self.__getRealSpeedLimit() * coeffs['realSpeedLimit']) * coeffs['normalization'] * self.__adjustmentCoefficient('mobility'))
        return max(value, MIN_RELATIVE_VALUE)

    @property
    def relativeVisibility(self):
        coeffs = self.__coefficients['visibility']
        value = round((self.circularVisionRadius[0] - MIN_VISION_RADIUS) / (MAX_VISION_RADIUS - MIN_VISION_RADIUS) * coeffs['normalization'] * self.__adjustmentCoefficient('visibility'))
        return max(value, MIN_RELATIVE_VALUE)

    @property
    def relativeCamouflage(self):
        coeffs = self.__coefficients['camouflage']
        invisibilityMovingFactor, invisibilityStillFactor = self.__getInvisibilityValues(self._itemDescr)
        value = round((invisibilityMovingFactor.current + invisibilityStillFactor.current + invisibilityStillFactor.atShot) / 3.0 * coeffs['normalization'] * self.__adjustmentCoefficient('camouflage'))
        return max(value, MIN_RELATIVE_VALUE)

    @property
    def damagedModulesDetectionTimeSituational(self):
        return max(MAX_DAMAGED_MODULES_DETECTION_PERK_VAL, self.__kpi.getFactor(KPI.Name.DAMAGED_MODULES_DETECTION_TIME))

    @property
    def damagedModulesDetectionTime(self):
        realDetectTime = max(MAX_DAMAGED_MODULES_DETECTION_PERK_VAL, self.__kpi.getFactor(KPI.Name.DAMAGED_MODULES_DETECTION_TIME))
        return HIDDEN_PARAM_DEFAULTS[KPI.Name.DAMAGED_MODULES_DETECTION_TIME] + realDetectTime

    @property
    def vehicleGunShotDispersionTurretRotation(self):
        return 0 if self.__vehicle.descriptor.currentDescr.gun.staticTurretYaw is not None else self.__kpi.getFactor(KPI.Name.VEHICLE_GUN_SHOT_DISPERSION_TURRET_ROTATION)

    @property
    def turretYawLimits(self):
        return None if not self.__hasTurret() else self.__getGunYawLimits()

    @property
    def gunYawLimits(self):
        if self._itemDescr.isYawHullAimingAvailable:
            return (0, 0)
        else:
            return None if self.__hasTurret() else self.__getGunYawLimits()

    @property
    def pitchLimits(self):
        limits = []
        for limit in self.__getPitchLimitsValues():
            limits.append(math.degrees(limit) * -1)

        return sorted(limits)

    @property
    def invisibilityStillFactor(self):
        _, still = self.__getInvisibilityValues(self._itemDescr)
        return still

    @property
    def invisibilityMovingFactor(self):
        moving, _ = self.__getInvisibilityValues(self._itemDescr)
        return moving

    @property
    def turboshaftInvisibilityStillFactor(self):
        if not self.__hasTurboshaftSwitchMode():
            return None
        else:
            _, still = self.__getInvisibilityValues(self._itemDescr.siegeVehicleDescr)
            return still

    @property
    def turboshaftInvisibilityMovingFactor(self):
        if not self.__hasTurboshaftSwitchMode():
            return None
        else:
            moving, _ = self.__getInvisibilityValues(self._itemDescr.siegeVehicleDescr)
            return moving

    @property
    def invisibilityFactorAtShot(self):
        return self._itemDescr.miscAttrs['invisibilityFactorAtShot']

    @property
    def clipFireRate(self):
        return self.__calcClipFireRate() if not self._itemDescr.isAutoShootGunVehicle else None

    @property
    def clipFireRateSituational(self):
        return self.__calcClipFireRateSituational() if not self._itemDescr.isAutoShootGunVehicle else None

    @property
    def autoShootClipFireRate(self):
        if self._itemDescr.isAutoShootGunVehicle:
            clipFireRate = self.__calcClipFireRate()
            return (clipFireRate[0], clipFireRate[2])
        else:
            return None

    @property
    def autoShootClipFireRateSituational(self):
        if self._itemDescr.isAutoShootGunVehicle:
            clipFireRateSituational = self.__calcClipFireRateSituational()
            return (clipFireRateSituational[0], clipFireRateSituational[2])
        else:
            return None

    @property
    def burstFireRate(self):
        if self.__hasBurst():
            gun = self._itemDescr.gun
            burstCountLeft, burstInterval = gun.burst
            return (burstInterval, gun.clip[0] / burstCountLeft, burstCountLeft)
        else:
            return None

    @property
    def turboshaftBurstFireRate(self):
        if self.__hasUnsupportedSwitchMode():
            gun = self._itemDescr.siegeVehicleDescr.gun
            burstCountLeft, burstInterval = gun.burst
            return (burstInterval, gun.clip[0] / burstCountLeft, burstCountLeft)
        else:
            return None

    @property
    def switchOnTime(self):
        return self.__getSwitchOnTime() if self.__hasHydraulicSiegeMode() else None

    @property
    def switchOffTime(self):
        return self.__getSwitchOffTime() if self.__hasHydraulicSiegeMode() else None

    @property
    def switchTime(self):
        return (self.switchOnTime, self.switchOffTime) if self.__hasHydraulicSiegeMode() else None

    @property
    def wheeledSwitchOnTime(self):
        return self.__getSwitchOnTime() if self.__hasWheeledSwitchMode() else None

    @property
    def wheeledSwitchOffTime(self):
        return self.__getSwitchOffTime() if self.__hasWheeledSwitchMode() else None

    @property
    def wheeledSwitchTime(self):
        onTime, offTime = self.wheeledSwitchOnTime, self.wheeledSwitchOffTime
        return (onTime, offTime) if onTime or offTime else None

    @property
    def turboshaftSwitchOnTime(self):
        return self.__getSwitchOnTime() if self.__hasTurboshaftSwitchMode() else None

    @property
    def turboshaftSwitchOffTime(self):
        return self.__getSwitchOffTime() if self.__hasTurboshaftSwitchMode() else None

    @property
    def turboshaftSwitchTime(self):
        onTime, offTime = self.turboshaftSwitchOnTime, self.turboshaftSwitchOffTime
        return (onTime, offTime) if onTime or offTime else None

    @property
    def stunMaxDuration(self):
        shell = self._itemDescr.shot.shell
        return shell.stun.stunDuration if shell.hasStun else None

    @property
    def stunMinDuration(self):
        item = self._itemDescr.shot.shell
        return item.stun.guaranteedStunDuration * item.stun.stunDuration if item.hasStun else None

    @property
    def vehicleEnemySpottingTime(self):
        kpiFactor = self.__kpi.getFactor(KPI.Name.VEHICLE_ENEMY_SPOTTING_TIME)
        skillName = 'gunner_rancorous'
        skillDuration = 0.0
        skillBattleBoosters = None
        for battleBoosters in self.__vehicle.battleBoosters.installed:
            if battleBoosters is not None and battleBoosters.getAffectedSkillName() == skillName:
                skillBattleBoosters = battleBoosters

        skillLearnt = isSkillLearnt(skillName, self.__vehicle)
        if skillLearnt and skillBattleBoosters is not None:
            skillDuration = skillBattleBoosters.descriptor.duration
        elif skillLearnt or skillBattleBoosters is not None:
            skillDuration = tankmen.getSkillsConfig().getSkill(skillName).duration
        return kpiFactor + skillDuration

    @property
    def chassisRepairTime(self):
        repairTime = []
        chassis = self._itemDescr.chassis
        if chassis.trackPairs:
            for track in chassis.trackPairs:
                if track.healthParams.repairTime is None:
                    repairTime = []
                    break
                repairTime.append(self.__calcRealChassisRepairTime(track.healthParams.repairTime))

            repairTime.reverse()
        elif chassis.repairTime is not None:
            repairTime.append(self.__calcRealChassisRepairTime(chassis.repairTime))
        return repairTime

    @property
    def wheelsRotationSpeed(self):
        return None if not self._itemDescr.isWheeledVehicle and not self._itemDescr.isWheeledOnSpotRotation else self.__kpi.getFactor(KPI.Name.WHEELS_ROTATION_SPEED)

    @property
    def softGroundFactor(self):
        skillName = 'driver_badRoadsKing'
        realSkillLevel = crewMemberRealSkillLevel(self.__vehicle, skillName)
        if realSkillLevel == tankmen.NO_SKILL:
            return 0
        allTrfs = self.__getTerrainResistanceFactors()
        avgTrf = sum(allTrfs) / len(allTrfs)
        argName = 'mediumGroundFactor'
        badRoadsKingMediumGroundFactor = self.__getFactorValueFromSkill(skillName, argName)
        mediumGroundFactor = self._itemDescr.chassis.terrainResistance[1] / badRoadsKingMediumGroundFactor * avgTrf
        softGroundFactor = self._itemDescr.chassis.terrainResistance[2] * avgTrf
        baseTerrainResDiff = softGroundFactor - mediumGroundFactor
        argName = 'softGroundFactor'
        badRoadsKingSoftGroundFactor = min(self.__getFactorValueFromSkill(skillName, argName) - 1, 1)
        realSoftGroundFactor = softGroundFactor - baseTerrainResDiff * badRoadsKingSoftGroundFactor
        resValInPercent = (1 - realSoftGroundFactor / softGroundFactor) * 100
        if _DO_TTC_LOG:
            LOG_DEBUG('TTC of softGroundFactor: realSoftGroundFactor:%f = softGroundFactor:%f - (baseTerrainResDiff:%f * badRoadsKingSoftGroundFactor:%f);resValInPercent:%f = ((1 - (realSoftGroundFactor:%f / softGroundFactor:%f)) * 100)' % (realSoftGroundFactor,
             softGroundFactor,
             baseTerrainResDiff,
             badRoadsKingSoftGroundFactor,
             resValInPercent,
             realSoftGroundFactor,
             softGroundFactor))
        return round(resValInPercent, 2)

    @property
    def artNotificationDelayFactorSituational(self):
        return max(MAX_ART_NOTIFICATION_DELAY_PERK_VAL, self.__kpi.getFactor(KPI.Name.ART_NOTIFICATION_DELAY_FACTOR))

    @property
    def artNotificationDelayFactor(self):
        artNotificationDelayFactor = self.__kpi.getFactor(KPI.Name.ART_NOTIFICATION_DELAY_FACTOR)
        realNotificationDelayTime = max(MAX_ART_NOTIFICATION_DELAY_PERK_VAL, artNotificationDelayFactor)
        return HIDDEN_PARAM_DEFAULTS[KPI.Name.ART_NOTIFICATION_DELAY_FACTOR] + realNotificationDelayTime

    @property
    def fireExtinguishingRate(self):
        skillName = 'fireFighting'
        return self.__getKpiValueFromSkillConfig(skillName, KPI.Name.FIRE_EXTINGUISHING_RATE, kpiType=KPI.Type.ADD)

    @property
    def twinGunSwitchFireModeTime(self):
        if self.__hasTwinGun():
            onTime, offTime = self.__getSwitchOnTime(), self.__getSwitchOffTime()
            if onTime != offTime:
                return (onTime, offTime)
            return onTime
        else:
            return None

    @property
    def twinGunTopSpeed(self):
        return self.__speedLimits(self._itemDescr.siegeVehicleDescr.physics['speedLimits'], ('forwardMaxSpeedKMHTerm', 'backwardMaxSpeedKMHTerm')) if self.__hasTwinGun() else None

    def getParamsDict(self, preload=False):
        conditionalParams = ('aimingTime',
         'clipFireRate',
         BURST_FIRE_RATE,
         'turretYawLimits',
         'gunYawLimits',
         'turretRotationSpeed',
         'turretArmor',
         'reloadTimeSecs',
         'switchOnTime',
         'switchOffTime',
         'switchTime',
         DUAL_GUN_CHARGE_TIME,
         AUTO_RELOAD_PROP_NAME,
         RELOAD_TIME_PROP_NAME,
         MAX_STEERING_LOCK_ANGLE,
         WHEELED_SWITCH_ON_TIME,
         WHEELED_SWITCH_OFF_TIME,
         WHEELED_SWITCH_TIME,
         WHEELED_SPEED_MODE_SPEED,
         'wheelRiseSpeed',
         TURBOSHAFT_ENGINE_POWER,
         TURBOSHAFT_SPEED_MODE_SPEED,
         TURBOSHAFT_INVISIBILITY_MOVING_FACTOR,
         TURBOSHAFT_INVISIBILITY_STILL_FACTOR,
         TURBOSHAFT_SWITCH_TIME,
         TURBOSHAFT_SWITCH_ON_TIME,
         TURBOSHAFT_SWITCH_OFF_TIME,
         CHASSIS_REPAIR_TIME,
         ROCKET_ACCELERATION_ENGINE_POWER,
         ROCKET_ACCELERATION_SPEED_LIMITS,
         ROCKET_ACCELERATION_REUSE_AND_DURATION,
         'chassisRotationSpeed',
         'turboshaftBurstFireRate',
         DUAL_ACCURACY_COOLING_DELAY,
         AUTO_SHOOT_CLIP_FIRE_RATE,
         TWIN_GUN_TOP_SPEED,
         TWIN_GUN_SWITCH_FIRE_MODE_TIME)
        stunConditionParams = ('stunMaxDuration', 'stunMinDuration')
        result = _ParamsDictProxy(self, preload, conditions=((conditionalParams, lambda v: v is not None), (stunConditionParams, lambda s: _isStunParamVisible(self._itemDescr.shot.shell))))
        return result

    def getAllDataDict(self):

        def getItemFullName(itemTypeIdx, itemDescr):
            return getTypeInfoByIndex(itemTypeIdx)['userString'] + ' ' + itemDescr.userString

        result = super(VehicleParams, self).getAllDataDict()
        base = [getItemFullName(ITEM_TYPES.vehicleGun, self._itemDescr.gun),
         getItemFullName(ITEM_TYPES.vehicleEngine, self._itemDescr.engine),
         getItemFullName(ITEM_TYPES.vehicleChassis, self._itemDescr.chassis),
         getItemFullName(ITEM_TYPES.vehicleRadio, self._itemDescr.radio)]
        if self.__hasTurret():
            base.insert(1, getItemFullName(ITEM_TYPES.vehicleTurret, self._itemDescr.turret))
        result['base'] = base
        return result

    @staticmethod
    def getBonuses(vehicle, ignoreDisabledPostProgression=True):
        installedItems = [ item for item in vehicle.consumables.installed.getItems() ]
        result = [ (eq.name, eq.itemTypeName) for eq in installedItems ]
        optDevs = vehicle.optDevices.installed.getItems()
        optDevs = [ (device.name, device.itemTypeName) for device in optDevs ]
        result.extend(optDevs)
        for battleBooster in vehicle.battleBoosters.installed.getItems():
            if battleBooster.isAffectsOnVehicle(vehicle):
                result.append((battleBooster.name, 'battleBooster'))

        if not (ignoreDisabledPostProgression and vehicle.postProgression.isDisabled(vehicle)):
            for step in vehicle.postProgression.iterUnorderedSteps():
                if step.isReceived():
                    action = step.action
                    if action.actionType == ACTION_TYPES.MODIFICATION:
                        result.append((action.getTechName(), BonusTypes.BASE_MODIFICATION))
                    elif action.actionType == ACTION_TYPES.PAIR_MODIFICATION:
                        subAction = action.getPurchasedModification()
                        if subAction is not None:
                            result.append((subAction.getTechName(), BonusTypes.PAIR_MODIFICATION))

        for _, tankman in vehicle.crew:
            if tankman is None:
                continue
            for skill in tankman.skills:
                if skill.isSkillActive:
                    result.append((skill.name, 'skill'))

            for bonusSkills in tankman.bonusSkills.itervalues():
                for bonusSkill in bonusSkills:
                    if bonusSkill and bonusSkill.isSkillActive:
                        result.append((bonusSkill.name, 'skill'))

        perksSet = set()
        for perksScope in BigWorld.player().inventory.abilities.abilitiesManager.getPerksByVehicle(vehicle.invID):
            for perkID, _ in perksScope:
                perksSet.add((str(perkID), 'perk'))

        result.extend(list(perksSet))
        result.extend(_processExtraBonuses(vehicle))
        return set(result)

    def getPenalties(self, vehicle):
        crew, emptySlots, otherVehicleSlots = functions.extractCrewDescrs(vehicle, replaceNone=False)
        crewFactors = items_utils.getCrewAffectedFactors(vehicle.descriptor, crew)
        result = {}
        currParams = self.getParamsDict(True)
        for slotId, factors in crewFactors.iteritems():
            for factor, factorValue in factors.iteritems():
                if factor in _FACTOR_TO_SKILL_PENALTY_MAP:
                    oldFactor = copy.copy(self.__factors[factor])
                    self.__factors[factor] = _universalSum(oldFactor, factorValue)
                    params = _FACTOR_TO_SKILL_PENALTY_MAP[factor]
                    for paramName in params:
                        paramPenalties = result.setdefault(paramName, {})
                        if slotId not in emptySlots:
                            newValue = getattr(self, paramName)
                            if newValue is None:
                                continue
                            state = rateParameterState(paramName, currParams[paramName], newValue)
                            if isinstance(currParams[paramName], collections.Iterable):
                                states, deltas = zip(*state)
                                if findFirst(lambda v: v == PARAM_STATE.WORSE, states):
                                    paramPenalties[slotId] = deltas
                            elif state[0] == PARAM_STATE.WORSE:
                                paramPenalties[slotId] = state[1]
                        paramPenalties[slotId] = 0

                    self.__factors[factor] = oldFactor

        roles = vehicle.descriptor.type.crewRoles
        for paramName, penalties in result.items():
            result[paramName] = [ _PenaltyInfo(roles[slotId][0], value, slotId in otherVehicleSlots) for slotId, value in penalties.iteritems() ]

        return {k:v for k, v in result.iteritems() if v}

    def _getVehicleDescriptor(self, vehicle):
        return vehicle.descriptor

    def __calculateDamageOrPiercingRandom(self, avgParam, randomization):
        lowerRandomizationFactor = self.damageAndPiercingDistributionLowerBound / 100.0
        upperRandomizationFactor = self.damageAndPiercingDistributionUpperBound / 100.0
        lowerBoundRandomization = randomization - lowerRandomizationFactor
        upperBoundRandomization = randomization + upperRandomizationFactor
        if _DO_TTC_LOG:
            LOG_DEBUG('TTC of calculateDamageOrPiercingRandom: floor(avgParam:%f - avgParam:%f * lowerBoundRandomization:%f);ceil(avgParam:%f + avgParam:%f * upperBoundRandomization:%f)' % (avgParam,
             avgParam,
             lowerBoundRandomization,
             avgParam,
             avgParam,
             upperBoundRandomization))
        return (int(floor(avgParam - avgParam * lowerBoundRandomization)), int(ceil(avgParam + avgParam * upperBoundRandomization)))

    def __calcRealChassisRepairTime(self, chassisRepairTime):
        skillName = 'repair'
        argName = 'vehicleRepairSpeed'
        realSkillLevel = crewMemberRealSkillLevel(self.__vehicle, skillName)
        kpiSkillFactor = 1
        if realSkillLevel > 0:
            kpiSkillFactor = self.__getKpiValueFromSkillConfig(skillName, argName)
        repairFactor = self.__factors.get('repairSpeed', 1.0)
        vehicleRepairSpeed = self.__kpi.getCoeff('vehicleRepairSpeed')
        repairKpi = 1 + (vehicleRepairSpeed - kpiSkillFactor)
        repairChassisKpi = self.__kpi.getCoeff('vehicleChassisRepairSpeed')
        if _DO_TTC_LOG:
            LOG_DEBUG('TTC of ChassisRepairTime: repairKpi:%f = 1 + (vehicleRepairSpeed:%f - kpiSkillFactor:%f)time = chassisRepairTime:%f / repairFactor:%f / repairKpi:%f / repairChassisKpi:%f' % (repairKpi,
             vehicleRepairSpeed,
             kpiSkillFactor,
             chassisRepairTime,
             repairFactor,
             repairKpi,
             repairChassisKpi))
        return chassisRepairTime / repairFactor / repairKpi / repairChassisKpi

    def __speedLimits(self, limits, miscAttrs=None):
        correction = []
        if miscAttrs:
            if len(miscAttrs) > len(limits):
                raise SoftException('correction can not be less than speed limits')
            correction = map(self._itemDescr.miscAttrs.get, miscAttrs)
        skillName = 'driver_motorExpert'
        realSkillLevel = crewMemberRealSkillLevel(self.__vehicle, skillName)
        if realSkillLevel != tankmen.NO_SKILL:
            forwardMaxSpeed = self.__getKpiValueFromSkillConfig(skillName, KPI.Name.VEHICLE_FORWARD_MAX_SPEED)
            backwardMaxSpeed = self.__getKpiValueFromSkillConfig(skillName, KPI.Name.VEHICLE_BACKWARD_MAX_SPEED)
            motorExpertSpeed = [forwardMaxSpeed, backwardMaxSpeed]
        else:
            motorExpertSpeed = [0, 0]
        speedLimit = [ round(speed * METERS_PER_SECOND_TO_KILOMETERS_PER_HOUR + correct, 2) for speed, correct in izip_longest(limits, correction, fillvalue=0) ]
        resultSpeedLimit = map(sum, zip(speedLimit, motorExpertSpeed))
        return resultSpeedLimit

    def __adjustmentCoefficient(self, paramName):
        return self._itemDescr.type.clientAdjustmentFactors[paramName]

    def __getGunYawLimits(self):
        limits = self._itemDescr.gun.turretYawLimits
        if limits is not None:
            limits = [ abs(math.degrees(limit)) for limit in limits[:] ]
        return limits

    def __hasTurret(self):
        vDescr = self._itemDescr
        return len(vDescr.hull.fakeTurrets['lobby']) != len(vDescr.turrets)

    def __hasHydraulicSiegeMode(self):
        return self._itemDescr.hasHydraulicChassis and self._itemDescr.hasSiegeMode

    def __hasWheeledSwitchMode(self):
        return self._itemDescr.isWheeledVehicle and self._itemDescr.hasSiegeMode

    def __hasTurboshaftSwitchMode(self):
        return self._itemDescr.hasTurboshaftEngine and self._itemDescr.hasSiegeMode

    def __hasUnsupportedSwitchMode(self):
        return self._itemDescr.type.compactDescr == 32321

    def __hasBurst(self):
        return self._itemDescr.hasBurst

    def __getRealSpeedLimit(self):
        enginePower = self._itemDescr.miscAttrs['enginePowerFactor'] * self.__getEnginePhysics()['smplEnginePower']
        rollingFriction = self.__getChassisPhysics()['grounds']['medium']['rollingFriction']
        return enginePower / self.vehicleWeight.current * METERS_PER_SECOND_TO_KILOMETERS_PER_HOUR * self.__factors['engine/power'] / 12.25 / rollingFriction

    def __getInvisibilityValues(self, itemDescription):
        camouflageFactor = self.__factors.get('camouflage', 1)
        moving, still = items_utils.getClientInvisibility(itemDescription, self.__vehicle, camouflageFactor, self.__factors)
        moving *= ONE_HUNDRED_PERCENTS
        still *= ONE_HUNDRED_PERCENTS
        movingAtShot = moving * self.invisibilityFactorAtShot
        stillAtShot = still * self.invisibilityFactorAtShot
        return (_Invisibility(moving, movingAtShot), _Invisibility(still, stillAtShot))

    def __getPitchLimitsValues(self):
        if self._itemDescr.isPitchHullAimingAvailable:
            hullAimingParams = self._itemDescr.type.hullAimingParams
            wheelsCorrectionAngles = hullAimingParams['pitch']['wheelsCorrectionAngles']
            hullAimingPitchMin = wheelsCorrectionAngles['pitchMin']
            hullAimingPitchMax = wheelsCorrectionAngles['pitchMax']
            if self._itemDescr.gun.staticPitch is not None:
                return (hullAimingPitchMin, hullAimingPitchMax)
            pitchLimits = self._itemDescr.gun.pitchLimits
            minPitch = pitchLimits['minPitch']
            maxPitch = pitchLimits['maxPitch']
            hullAimingPitchMin = wheelsCorrectionAngles['pitchMin']
            hullAimingPitchMax = wheelsCorrectionAngles['pitchMax']
            return (min([ key for _, key in minPitch ]) + hullAimingPitchMin, max([ key for _, key in maxPitch ]) + hullAimingPitchMax)
        else:
            return self._itemDescr.gun.pitchLimits['absolute']

    def __getEnginePower(self, power):
        return round(power * self.__factors['engine/power'] * self._itemDescr.miscAttrs['enginePowerFactor'] / component_constants.HP_TO_WATTS)

    def __getSwitchOffTime(self):
        siegeMode = self._itemDescr.type.siegeModeParams
        return siegeMode['switchOffTime'] if siegeMode else None

    def __getSwitchOnTime(self):
        siegeMode = self._itemDescr.type.siegeModeParams
        return siegeMode['switchOnTime'] if siegeMode else None

    def __hasClipGun(self):
        return self._itemDescr.gun.clip[0] != 1

    def __hasAutoReload(self):
        return isAutoReloadGun(self._itemDescr.gun)

    def __hasDualGun(self):
        return isDualGun(self._itemDescr.gun)

    def __hasTwinGun(self):
        return isTwinGun(self._itemDescr.gun)

    def __calcReloadTime(self, isSituational=False):
        loaderMeleeReloadFactor = 1
        loaderDesperadoReloadFactor = 1
        if isSituational:
            skillName = 'loader_melee'
            argName = 'gunReloadSpeed'
            loaderMeleeReloadFactor = self.__getFactorValueFromSkill(skillName, argName)
            skillName = 'loader_desperado'
            argName = 'gunReloadSpeed'
            loaderDesperadoReloadFactor = self.__getFactorValueFromSkill(skillName, argName)

        def getParams(f):
            reloadTimes = f(self._itemDescr, self.__factors)
            reloadTimesMax = max(reloadTimes) * loaderMeleeReloadFactor * loaderDesperadoReloadFactor
            reloadTimesMin = min(reloadTimes) * loaderMeleeReloadFactor * loaderDesperadoReloadFactor
            return (getShotsPerMinute(self._itemDescr.gun, reloadTimesMax, hasAutoReload), getShotsPerMinute(self._itemDescr.gun, reloadTimesMin, hasAutoReload))

        hasAutoReload = self.__hasAutoReload()
        if hasAutoReload:
            return getParams(items_utils.getClipReloadTime)
        if self.__hasDualGun():
            return getParams(items_utils.getDualGunReloadTime)
        if self.__hasTwinGun():
            return getParams(items_utils.geTwinGunReloadTime)
        reloadTime = items_utils.getReloadTime(self._itemDescr, self.__factors)
        if _DO_TTC_LOG:
            LOG_DEBUG('reloadTime:%f * loader_meleeFactor:%f * loader_desperadoFactor:%f' % (reloadTime, loaderMeleeReloadFactor, loaderDesperadoReloadFactor))
        return (getShotsPerMinute(self._itemDescr.gun, reloadTime * loaderMeleeReloadFactor * loaderDesperadoReloadFactor, hasAutoReload),)

    def __calcClipFireRate(self):
        if self.__hasClipGun():
            clipData = self._itemDescr.gun.clip
            if self.__hasAutoReload():
                reloadTime = sum(items_utils.getClipReloadTime(self._itemDescr, self.__factors))
            else:
                reloadTime = items_utils.getReloadTime(self._itemDescr, self.__factors)
            return (reloadTime, clipData[1], clipData[0])
        elif self.__hasDualGun():
            reloadTimes = items_utils.getDualGunReloadTime(self._itemDescr, self.__factors)
            return (sum(reloadTimes), self._itemDescr.gun.dualGun.rateTime, len(reloadTimes))
        else:
            return None

    def __calcClipFireRateSituational(self):
        clipFireRate = self.__calcClipFireRate()
        if clipFireRate is None:
            return
        else:
            skillName = 'loader_melee'
            argName = 'gunReloadSpeed'
            loaderMeleeReloadFactor = self.__getFactorValueFromSkill(skillName, argName)
            skillName = 'loader_desperado'
            argName = 'gunReloadSpeed'
            loaderDesperadoReloadFactor = self.__getFactorValueFromSkill(skillName, argName)
            reloadTime = clipFireRate[0] * loaderMeleeReloadFactor * loaderDesperadoReloadFactor
            return (reloadTime, clipFireRate[1], clipFireRate[2])

    def __getChassisPhysics(self):
        chassisName = self._itemDescr.chassis.name
        return self._itemDescr.type.xphysics['chassis'][chassisName]

    def __getEnginePhysics(self):
        engineName = self._itemDescr.engine.name
        return self._itemDescr.type.xphysics['engines'][engineName]

    @staticmethod
    def __mapGrounds(itemsDict):
        return (itemsDict['firm'], itemsDict['medium'], itemsDict['soft'])

    def __currentShot(self):
        return self._itemDescr.gun.shots[self._itemDescr.activeGunShotIndex]

    def __getTerrainResistanceFactors(self):
        terrainResistancePhysicsFactors = map(operator.truediv, self._itemDescr.physics['terrainResistance'], self._itemDescr.chassis.terrainResistance)
        return map(operator.mul, self.__factors['chassis/terrainResistance'], terrainResistancePhysicsFactors)

    def __getFactorValueFromSkill(self, skillName, argName):
        skill = tankmen.getSkillsConfig().getSkill(skillName)
        param = skill.params.get(argName)
        factorPerLevel = param.value if param else 0.0
        realSkillLevel = crewMemberRealSkillLevel(self.__vehicle, skillName)
        realFactorValue = 1
        if realSkillLevel != tankmen.NO_SKILL:
            realFactorValue += factorPerLevel * realSkillLevel
        return realFactorValue

    def __getKpiValueFromSkillConfig(self, skillName, argName, kpiType=KPI.Type.MUL):
        skillKpi = tankmen.getSkillsConfig().getSkill(skillName).kpi
        result = 1.0 if kpiType == KPI.Type.MUL else 0.0
        realSkillLevel = crewMemberRealSkillLevel(self.__vehicle, skillName)
        if realSkillLevel != tankmen.NO_SKILL:
            for _kpi in skillKpi:
                if _kpi.name == argName:
                    baseValue = 1.0 if _kpi.type == KPI.Type.MUL else 0.0
                    result = baseValue - (baseValue - _kpi.value) * realSkillLevel / tankmen.MAX_SKILL_LEVEL

        return result


class GunParams(WeightedParam):

    @property
    def caliber(self):
        return self._itemDescr.shots[0].shell.caliber

    @property
    def shellsCount(self):
        return self._getRawParams()[SHELLS_COUNT_PROP_NAME]

    @property
    def shellReloadingTime(self):
        return self._getRawParams()[SHELL_RELOADING_TIME_PROP_NAME]

    @property
    def reloadMagazineTime(self):
        return self._getRawParams()[RELOAD_MAGAZINE_TIME_PROP_NAME]

    @property
    def reloadTime(self):
        return None if self.getReloadingType() in (GUN_CAN_BE_AUTO_RELOAD,
         GUN_AUTO_RELOAD,
         GUN_CAN_BE_DUAL_GUN,
         GUN_DUAL_GUN,
         GUN_CAN_BE_TWIN_GUN,
         GUN_TWIN_GUN) else self._getRawParams()[RELOAD_TIME_PROP_NAME]

    @property
    def reloadTimeSecs(self):
        return self._getRawParams()[RELOAD_TIME_SECS_PROP_NAME]

    @property
    def reloadTimeSingleGun(self):
        gun = self.__getVehicleGun()
        return gun.reloadTime if isTwinGun(gun) else None

    @property
    def reloadTimeTwinGun(self):
        gun = self.__getVehicleGun()
        return self._vehicleDescr.gun.twinGun.twinGunReloadTime if isTwinGun(gun) else None

    @property
    def chargeTime(self):
        return self._getRawParams()[DUAL_GUN_CHARGE_TIME]

    @property
    def rateTime(self):
        return self._getRawParams()[DUAL_GUN_RATE_TIME]

    @property
    def avgPiercingPower(self):
        return self._getRawParams()[PIERCING_POWER_PROP_NAME]

    @property
    def avgDamageList(self):
        return self._getRawParams()[DAMAGE_PROP_NAME]

    @property
    def maxAvgMutableDamageList(self):
        return self._getRawParams()[MAX_MUTABLE_DAMAGE_PROP_NAME]

    @property
    def minAvgMutableDamageList(self):
        return self._getRawParams()[MIN_MUTABLE_DAMAGE_PROP_NAME]

    @property
    def dispertionRadius(self):
        disp = self._getRawParams()[DISPERSION_RADIUS_PROP_NAME][0]
        gun = self.__getVehicleGun()
        if isDualAccuracy(gun):
            return (math.tan(gun.dualAccuracy.afterShotDispersionAngle) * 100, disp)
        else:
            return (disp, math.tan(self._vehicleDescr.siegeVehicleDescr.gun.shotDispersionAngle) * 100) if isTwinGun(gun) else (None, disp)

    @property
    def aimingTime(self):
        gun = self.__getVehicleGun()
        return (self._getRawParams()[AIMING_TIME_PROP_NAME][1], self._vehicleDescr.siegeVehicleDescr.gun.aimingTime) if isTwinGun(gun) else self._getRawParams()[AIMING_TIME_PROP_NAME]

    @property
    def compatibles(self):
        allVehiclesNames = set(g_paramsCache.getComponentVehiclesNames(self._itemDescr.compactDescr))
        clipVehiclesNames = set(self._getPrecachedInfo().clipVehiclesNames)
        return allVehiclesNames.difference(clipVehiclesNames)

    @property
    def clipVehiclesCompatibles(self):
        return set(self._getPrecachedInfo().clipVehiclesNames)

    @property
    def shellsCompatibles(self):
        return self._getRawParams().get(SHELLS_PROP_NAME, tuple())

    @property
    def maxShotDistance(self):
        return self._itemDescr.shots[0].maxDistance

    @property
    def clipVehiclesCD(self):
        return self._getPrecachedInfo().clipVehicles

    @property
    def continuousShotsPerMinute(self):
        return tuple((round(60.0 / t) for t in self.shellReloadingTime)) if self.getReloadingType() in (GUN_AUTO_SHOOT, GUN_CAN_BE_AUTO_SHOOT) else None

    @property
    def continuousDamagePerSecond(self):
        return tuple((round(self.avgDamageList[0] / t) for t in self.shellReloadingTime)) if self.getReloadingType() in (GUN_AUTO_SHOOT, GUN_CAN_BE_AUTO_SHOOT) else None

    @property
    def avgDamagePerMinute(self):
        return round(self.reloadTime[0] * self.avgDamageList[0])

    @property
    def stunMaxDurationList(self):
        res = self._getRawParams().get(STUN_DURATION_PROP_NAME)
        return res if res else None

    @property
    def burstTimeInterval(self):
        burstData = self._getRawParams()[BURST_FIRE_RATE]
        return burstData[0] if burstData else None

    @property
    def burstCount(self):
        burstSize = self.burstSize
        return self.shellsCount[0] / burstSize if burstSize else None

    @property
    def burstSize(self):
        burstData = self._getRawParams()[BURST_FIRE_RATE]
        return burstData[1] if burstData else None

    @property
    def stunMinDurationList(self):
        res = self._getRawParams().get(GUARANTEED_STUN_DURATION_PROP_NAME)
        return res if res else None

    @property
    def autoReloadTime(self):
        return tuple(reversed(self._getRawParams().get(AUTO_RELOAD_PROP_NAME)))

    @property
    def dualAccuracyAfterShotDispersionAngle(self):
        res = self._getRawParams().get(DUAL_ACCURACY_AFTER_SHOT_DISPERSION_ANGLE)
        return res if res else None

    @property
    def dualAccuracyCoolingDelay(self):
        gun = self.__getVehicleGun()
        return gun.dualAccuracy.coolingDelay if isDualAccuracy(gun) else None

    def getParamsDict(self):
        stunConditionParams = (STUN_DURATION_PROP_NAME, GUARANTEED_STUN_DURATION_PROP_NAME)
        stunItem = self._itemDescr.shots[0].shell
        result = _ParamsDictProxy(self, conditions=((['maxShotDistance'], lambda v: v == _AUTOCANNON_SHOT_DISTANCE), (stunConditionParams, lambda s: _isStunParamVisible(stunItem))))
        return result

    def getReloadingType(self, vehicleCD=None):
        if vehicleCD is None and self._vehicleDescr is not None:
            vehicleCD = self._vehicleDescr.type.compactDescr
        return self._getPrecachedInfo().getReloadingType(vehicleCD)

    def _extractRawParams(self):
        if self._vehicleDescr is not None:
            descriptors = getGunDescriptors(self._itemDescr, self._vehicleDescr)
            params = calcGunParams(self._itemDescr, descriptors)
        else:
            params = self._getPrecachedInfo().params
        return params

    def _getCompatible(self):
        vehiclesNamesList = self.compatibles
        clipVehicleNamesList = self.clipVehiclesCompatibles
        curVehicle = _getInstalledModuleVehicle(self._vehicleDescr, self._itemDescr)
        result = []
        if clipVehicleNamesList:
            if vehiclesNamesList:
                result.append(('uniChargedVehicles', _formatCompatibles(curVehicle, vehiclesNamesList)))
            result.append(('clipVehicles', _formatCompatibles(curVehicle, clipVehicleNamesList)))
        else:
            result.append(('vehicles', _formatCompatibles(curVehicle, vehiclesNamesList)))
        result.append(('shells', ', '.join(self.shellsCompatibles)))
        return tuple(result)

    def __getVehicleGun(self):
        if self._vehicleDescr is not None:
            guns = getGunDescriptors(self._itemDescr, self._vehicleDescr)
            return next((obj for obj in guns if obj.compactDescr == self._itemDescr.compactDescr), None)
        else:
            return


class ShellParams(CompatibleParams):

    @property
    def caliber(self):
        return self._itemDescr.caliber

    @property
    def piercingPower(self):
        return self._getRawParams()[PIERCING_POWER_PROP_NAME]

    @property
    def damage(self):
        return self._getRawParams()[DAMAGE_PROP_NAME]

    @property
    def avgDamage(self):
        return self._itemDescr.armorDamage[0]

    @property
    def avgMutableDamage(self):
        return self._itemDescr.armorDamage if self._itemDescr.isDamageMutable else None

    @property
    def avgDamagePerSecond(self):
        return self.avgDamage / self._vehicleDescr.gun.clip[1] if self._vehicleDescr and self._vehicleDescr.isAutoShootGunVehicle else None

    @property
    def avgPiercingPower(self):
        return _average(self.piercingPower)

    @property
    def explosionRadius(self):
        return self._itemDescr.type.explosionRadius if self._itemDescr.kind == SHELL_TYPES.HIGH_EXPLOSIVE else 0

    @property
    def piercingPowerTable(self):
        if self._itemDescr.kind in (SHELL_TYPES.ARMOR_PIERCING, SHELL_TYPES.ARMOR_PIERCING_CR):
            if self._vehicleDescr is None:
                return NO_DATA
            result = []
            shellDescriptor = self.__getShellDescriptor()
            if not shellDescriptor:
                return
            maxDistance = self.maxShotDistance
            for distance in PIERCING_DISTANCES:
                if distance > maxDistance:
                    distance = int(maxDistance)
                currPiercing = computePiercingPowerAtDist(shellDescriptor.piercingPower, distance)
                result.append((distance, currPiercing))

            return result
        else:
            return

    @property
    def maxShotDistance(self):
        if self._itemDescr.kind in _SHELL_KINDS:
            if self._vehicleDescr is not None:
                result = self.__getShellDescriptor()
                if result:
                    return result.maxDistance
        return

    @property
    def isBasic(self):
        return self._vehicleDescr is not None and getBasicShell(self._vehicleDescr).compactDescr == self._itemDescr.compactDescr

    @property
    def compatibles(self):
        getter = vehicles.getItemByCompactDescr
        overallList = [ getter(gunCD).userString for gunCD in self._getPrecachedInfo().guns ]
        uniques = []
        for weapon in overallList:
            if weapon not in uniques:
                uniques.append(weapon)

        return uniques

    @property
    def stunMaxDuration(self):
        return self._itemDescr.stun.stunDuration if self._itemDescr.hasStun else None

    @property
    def stunMinDuration(self):
        return self._itemDescr.stun.guaranteedStunDuration * self._itemDescr.stun.stunDuration if self._itemDescr.hasStun else None

    @property
    def stunDurationList(self):
        return (self.stunMinDuration, self.stunMaxDuration) if self._itemDescr.hasStun else None

    @property
    def shotSpeed(self):
        if self._itemDescr.kind in _SHELL_KINDS and self._vehicleDescr is not None:
            result = self.__getShellDescriptor()
            if result:
                projSpeedFactor = vehicles.g_cache.commonConfig['miscParams']['projectileSpeedFactor']
                return result.speed / projSpeedFactor
        return

    def getParamsDict(self):
        stunConditionParams = ('stunMaxDuration', 'stunMinDuration')
        result = _ParamsDictProxy(self, conditions=((['maxShotDistance'], lambda v: v == _AUTOCANNON_SHOT_DISTANCE), (stunConditionParams, lambda s: _isStunParamVisible(self._itemDescr))))
        return result

    def _extractRawParams(self):
        if self._vehicleDescr is not None:
            descriptors = getShellDescriptors(self._itemDescr, self._vehicleDescr)
            params = calcShellParams(descriptors)
        else:
            params = self._getPrecachedInfo().params
        return params

    def _getCompatible(self):
        return (('shellGuns', ', '.join(self.compatibles)),)

    def __getShellDescriptor(self):
        shellDescriptors = getShellDescriptors(self._itemDescr, self._vehicleDescr)
        return shellDescriptors[0] if shellDescriptors else None


class OptionalDeviceParams(WeightedParam):

    @property
    def weight(self):
        return _Weight(*getOptionalDeviceWeight(self._itemDescr, self._vehicleDescr)) if self._vehicleDescr is not None else _Weight(*self._getPrecachedInfo().weight)

    @property
    def nations(self):
        return self._getPrecachedInfo().nations

    def _getCompatible(self):
        return tuple()


class EquipmentParams(_ParameterBase):

    @property
    def equipmentType(self):
        return self._itemDescr.equipmentType

    @property
    def nations(self):
        return self._getPrecachedInfo().nations

    def getParamsDict(self):
        params = {'nations': self.nations}
        params.update(self._getPrecachedInfo().params)
        return params


class _ParamsDictProxy(object):
    __slots__ = ('__paramsCalculator', '__cachedParams', '__allAreLoaded', '__conditions', '__filteredByConditions', '__popped')

    def __init__(self, calculator, preload=False, conditions=None):
        super(_ParamsDictProxy, self).__init__()
        self.__paramsCalculator = calculator
        self.__cachedParams = {}
        self.__allAreLoaded = False
        self.__conditions = defaultdict(list)
        self.__filteredByConditions = set()
        self.__popped = set()
        if conditions is not None:
            for keys, condition in conditions:
                for key in keys:
                    self.__conditions[key].append(condition)

        if preload:
            self.__loadAllValues()
        return

    def pop(self, item, default=None):
        self.__loadAllValues()
        if item in self:
            value = self[item]
            self.__popped.add(item)
            del self.__cachedParams[item]
        else:
            value = default
        return value

    def get(self, k, default=None):
        try:
            return self[k]
        except KeyError:
            return default

    def keys(self):
        return list(self.__iter__())

    def values(self):
        self.__loadAllValues()
        return self.__cachedParams.values()

    def items(self):
        self.__loadAllValues()
        return self.__cachedParams.items()

    def iteritems(self):
        self.__loadAllValues()
        return self.__cachedParams.iteritems()

    def __getitem__(self, item):
        if item not in self.__cachedParams:
            if item not in self.__filteredByConditions and item not in self.__popped and hasattr(self.__paramsCalculator, item):
                value = getattr(self.__paramsCalculator, item)
                if inspect.ismethod(value) or not self.__checkConditions(item, value):
                    self.__filteredByConditions.add(item)
                    raise KeyError(item)
                self.__cachedParams[item] = value
            else:
                raise KeyError(item)
        return self.__cachedParams[item]

    def __iter__(self):
        self.__loadAllValues()
        for k in self.__cachedParams.iterkeys():
            if k not in self.__popped:
                yield k

    def __len__(self):
        self.__loadAllValues()
        return len(self.__cachedParams)

    def __contains__(self, item):
        try:
            _ = self[item]
            return True
        except KeyError:
            return False

    def __loadAllValues(self):
        if not self.__allAreLoaded:
            for k, _ in inspect.getmembers(self.__paramsCalculator.__class__, lambda o: isinstance(o, property)):
                value = getattr(self.__paramsCalculator, k)
                if self.__checkConditions(k, value):
                    self.__cachedParams[k] = value

            self.__allAreLoaded = True

    def __checkConditions(self, key, value):
        if key in self.__conditions:
            for func in self.__conditions[key]:
                if not func(value):
                    self.__filteredByConditions.add(key)
                    return False

        return True


def _formatCompatibles(name, collection):
    return ', '.join([ (text_styles.neutral(c) if c == name else text_styles.main(c)) for c in collection ])
