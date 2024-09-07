# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/items_parameters/params.py
import collections
import copy
import inspect
import logging
import math
import operator
import typing
from collections import namedtuple, defaultdict
from math import ceil, floor
from itertools import izip_longest
import BigWorld
from constants import SHELL_TYPES, PIERCING_POWER, BonusTypes, HAS_EXPLOSION, PenaltyTypes
from gui import GUI_SETTINGS
from gui.shared.formatters import text_styles
from gui.shared.gui_items import KPI
from gui.shared.gui_items.Tankman import Tankman, isSkillLearnt, crewMemberRealSkillLevel
from gui.shared.items_parameters import calcGunParams, calcShellParams, getShotsPerMinute, getGunDescriptors, isAutoReloadGun, isDualGun, isDualAccuracy
from gui.shared.items_parameters import functions, getShellDescriptors, NO_DATA
from gui.shared.items_parameters.comparator import rateParameterState, PARAM_STATE
from gui.shared.items_parameters.functions import getBasicShell, getRocketAccelerationKpiFactors
from gui.shared.items_parameters.params_cache import g_paramsCache
from gui.shared.utils import DAMAGE_PROP_NAME, PIERCING_POWER_PROP_NAME, AIMING_TIME_PROP_NAME, STUN_DURATION_PROP_NAME, AUTO_RELOAD_PROP_NAME, GUN_AUTO_RELOAD, GUN_CAN_BE_AUTO_RELOAD, MAX_STEERING_LOCK_ANGLE, WHEELED_SWITCH_OFF_TIME, WHEELED_SWITCH_ON_TIME, WHEELED_SWITCH_TIME, WHEELED_SPEED_MODE_SPEED, GUN_DUAL_GUN, GUN_CAN_BE_DUAL_GUN, RELOAD_TIME_SECS_PROP_NAME, DUAL_GUN_CHARGE_TIME, DUAL_GUN_RATE_TIME, TURBOSHAFT_ENGINE_POWER, TURBOSHAFT_SPEED_MODE_SPEED, TURBOSHAFT_INVISIBILITY_MOVING_FACTOR, TURBOSHAFT_INVISIBILITY_STILL_FACTOR, TURBOSHAFT_SWITCH_TIME, TURBOSHAFT_SWITCH_ON_TIME, TURBOSHAFT_SWITCH_OFF_TIME, CHASSIS_REPAIR_TIME, ROCKET_ACCELERATION_ENGINE_POWER, ROCKET_ACCELERATION_SPEED_LIMITS, ROCKET_ACCELERATION_REUSE_AND_DURATION, SHELLS_BURST_COUNT_PROP_NAME, SHELLS_FLAME_BURST_COUNT_PROP_NAME, DUAL_ACCURACY_COOLING_DELAY, DUAL_ACCURACY_AFTER_SHOT_DISPERSION_ANGLE, BURST_FIRE_RATE
from gui.shared.utils import DISPERSION_RADIUS_PROP_NAME, SHELLS_PROP_NAME, GUN_NORMAL, SHELLS_COUNT_PROP_NAME
from gui.shared.utils import GUN_CAN_BE_CLIP, RELOAD_TIME_PROP_NAME
from gui.shared.utils import RELOAD_MAGAZINE_TIME_PROP_NAME, SHELL_RELOADING_TIME_PROP_NAME, GUN_CLIP
from helpers import time_utils, dependency
from items import getTypeOfCompactDescr, getTypeInfoByIndex, ITEM_TYPES, vehicles, tankmen
from items import utils as items_utils
from items.components import component_constants
from post_progression_common import ACTION_TYPES
from shared_utils import findFirst, first
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from items.vehicles import VehicleDescriptor, CompositeVehicleDescriptor
_logger = logging.getLogger(__name__)
MAX_VISION_RADIUS = 500
MIN_VISION_RADIUS = 150
PIERCING_DISTANCES = (50, 500)
ONE_HUNDRED_PERCENTS = 100
MIN_RELATIVE_VALUE = 1
EXTRAS_CAMOUFLAGE = 'camouflageExtras'
MAX_DAMAGED_MODULES_DETECTION_PERK_VAL = -4
MAX_ART_NOTIFICATION_DELAY_PERK_VAL = -2
_Invisibility = namedtuple('_Invisibility', 'current, atShot')
_PenaltyInfo = namedtuple('_PenaltyInfo', 'roleName, value, vehicleIsNotNative, penaltyType')
MODULES = {ITEM_TYPES.vehicleRadio: lambda vehicleDescr: vehicleDescr.radio,
 ITEM_TYPES.vehicleEngine: lambda vehicleDescr: vehicleDescr.engine,
 ITEM_TYPES.vehicleChassis: lambda vehicleDescr: vehicleDescr.chassis,
 ITEM_TYPES.vehicleTurret: lambda vehicleDescr: vehicleDescr.turret,
 ITEM_TYPES.vehicleGun: lambda vehicleDescr: vehicleDescr.gun}
HIDDEN_PARAM_DEFAULTS = {KPI.Name.ART_NOTIFICATION_DELAY_FACTOR: 2.1,
 KPI.Name.DAMAGED_MODULES_DETECTION_TIME: 4.5}
METERS_PER_SECOND_TO_KILOMETERS_PER_HOUR = 3.6
_GUN_EXCLUDED_PARAMS = {GUN_NORMAL: (SHELLS_COUNT_PROP_NAME,
              RELOAD_MAGAZINE_TIME_PROP_NAME,
              SHELL_RELOADING_TIME_PROP_NAME,
              AUTO_RELOAD_PROP_NAME,
              RELOAD_TIME_SECS_PROP_NAME,
              DUAL_GUN_CHARGE_TIME,
              DUAL_GUN_RATE_TIME),
 GUN_CLIP: (RELOAD_TIME_PROP_NAME,
            AUTO_RELOAD_PROP_NAME,
            RELOAD_TIME_SECS_PROP_NAME,
            DUAL_GUN_CHARGE_TIME,
            DUAL_GUN_RATE_TIME),
 GUN_CAN_BE_CLIP: (SHELLS_COUNT_PROP_NAME,
                   RELOAD_MAGAZINE_TIME_PROP_NAME,
                   SHELL_RELOADING_TIME_PROP_NAME,
                   AUTO_RELOAD_PROP_NAME,
                   RELOAD_TIME_SECS_PROP_NAME,
                   DUAL_GUN_CHARGE_TIME,
                   DUAL_GUN_RATE_TIME),
 GUN_AUTO_RELOAD: (RELOAD_TIME_PROP_NAME,
                   RELOAD_MAGAZINE_TIME_PROP_NAME,
                   RELOAD_TIME_SECS_PROP_NAME,
                   DUAL_GUN_CHARGE_TIME,
                   DUAL_GUN_RATE_TIME),
 GUN_CAN_BE_AUTO_RELOAD: (SHELLS_COUNT_PROP_NAME,
                          RELOAD_MAGAZINE_TIME_PROP_NAME,
                          SHELL_RELOADING_TIME_PROP_NAME,
                          RELOAD_TIME_SECS_PROP_NAME,
                          DUAL_GUN_CHARGE_TIME,
                          DUAL_GUN_RATE_TIME),
 GUN_DUAL_GUN: (SHELLS_COUNT_PROP_NAME,
                RELOAD_MAGAZINE_TIME_PROP_NAME,
                RELOAD_TIME_PROP_NAME,
                SHELL_RELOADING_TIME_PROP_NAME),
 GUN_CAN_BE_DUAL_GUN: (SHELLS_COUNT_PROP_NAME,
                       RELOAD_MAGAZINE_TIME_PROP_NAME,
                       RELOAD_TIME_PROP_NAME,
                       SHELL_RELOADING_TIME_PROP_NAME)}
_FACTOR_TO_SKILL_PENALTY_MAP = {'turret/rotationSpeed': ('turretRotationSpeed', 'relativePower'),
 'circularVisionRadius': ('circularVisionRadius', 'relativeVisibility'),
 'radio/distance': ('radioDistance', 'relativeVisibility'),
 'gun/reloadTime': ('reloadTime',
                    'avgDamagePerMinute',
                    'relativePower',
                    'reloadTimeSecs',
                    'clipFireRate',
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
 SHELL_TYPES.ARMOR_PIERCING_CR,
 SHELL_TYPES.ARMOR_PIERCING_FSDS,
 SHELL_TYPES.FLAME)
_POWER_PIERCING_SHELLS = (SHELL_TYPES.ARMOR_PIERCING, SHELL_TYPES.ARMOR_PIERCING_CR, SHELL_TYPES.ARMOR_PIERCING_FSDS)
_AUTOCANNON_SHOT_DISTANCE = 400

def _processExtraBonuses(vehicle):
    result = []
    withRareCamouflage = vehicle.intCD in g_paramsCache.getVehiclesWithoutCamouflage()
    hasCamo = bool(vehicle.getBonusCamo())
    if withRareCamouflage or hasCamo:
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


def _rawTurboshaftEnginePower(vehicleDescr, engineName):
    result = None
    try:
        engines = vehicleDescr.siegeVehicleDescr.type.xphysics['engines']
        result = engines[engineName]['smplEnginePower']
    except KeyError:
        pass

    return result


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
        return _rawTurboshaftEnginePower(self._vehicleDescr, self._itemDescr.name)

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
    def vehicleGunShotStabilizationChassisMovement(self):
        movementDispersion = int(round(self._itemDescr.shotDispersionFactors[0] * component_constants.KMH_TO_MS * 100))
        return 100 - movementDispersion

    @property
    def vehicleGunShotStabilizationChassisRotation(self):
        rotationDispersion = int(round(math.radians(self._itemDescr.shotDispersionFactors[1]) * 100))
        return 100 - rotationDispersion

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
            if chassis.isMultiTrack and repairTimes:
                repairTimes = [min(repairTimes), max(repairTimes)]
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

    def __init__(self, vehicle):
        super(VehicleParams, self).__init__(self._getVehicleDescriptor(vehicle))
        self.__factors = functions.getVehicleFactors(vehicle)
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
        return self._itemDescr.physics['weight'] / 1000

    @property
    def enginePower(self):
        enginePower = self.__getEnginePower(self._itemDescr.physics['enginePower'])
        return enginePower

    @property
    def turboshaftEnginePower(self):
        power = _turboshaftEnginePower(self._itemDescr, self._itemDescr.engine.name)
        return power and self.__getEnginePower(power)

    @property
    def enginePowerPerTon(self):
        powerPerTon = round(self.enginePower / self.vehicleWeight, 2)
        if self._itemDescr.hasTurboshaftEngine:
            return (powerPerTon, round(self.turboshaftEnginePower / self.vehicleWeight, 2))
        return (powerPerTon, round(self.rocketAccelerationEnginePower / self.vehicleWeight, 2)) if self._itemDescr.hasRocketAcceleration else (powerPerTon,)

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
            rotationSpeedFactor = self.__getFactorValueFromSkill(skillName, argName, Tankman.ROLES.DRIVER)
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
        damageRandomization = self._itemDescr.shot.shell.damageRandomization
        lowerRandomizationFactor = self.damageAndPiercingDistributionLowerBound / 100.0
        upperRandomizationFactor = self.damageAndPiercingDistributionUpperBound / 100.0
        lowerBoundRandomization = damageRandomization - lowerRandomizationFactor
        upperBoundRandomization = damageRandomization + upperRandomizationFactor
        minDamage, maxDamage = self._itemDescr.shot.shell.dmgLimits
        return (int(floor(minDamage - minDamage * lowerBoundRandomization)), int(ceil(maxDamage + maxDamage * upperBoundRandomization)))

    @property
    def avgDamage(self):
        return self._itemDescr.shot.shell.distanceDmg.avgDamage if self._itemDescr.shot.shell.distanceDmg is not None else int(round(sum(self.damage) / 2.0))

    @property
    def chargeTime(self):
        return (float(self._itemDescr.gun.dualGun.chargeTime), self._itemDescr.gun.dualGun.reloadLockTime) if self.__hasDualGun() else None

    @property
    def avgDamagePerMinute(self):
        return round(max(self.__calcReloadTime()) * self.avgDamage)

    @property
    def avgDamagePerMinuteSituational(self):
        return round(max(self.__calcReloadTime(isSituational=True)) * self.avgDamage)

    @property
    def avgPiercingPower(self):
        return int(round(sum(self.piercingPower) / 2.0))

    @property
    def piercingPower(self):
        piercingPower = self._itemDescr.shot.piercingPower[0]
        piercingPowerRandomization = self._itemDescr.shot.shell.piercingPowerRandomization
        lowerRandomizationFactor = self.damageAndPiercingDistributionLowerBound / 100.0
        upperRandomizationFactor = self.damageAndPiercingDistributionUpperBound / 100.0
        lowerBoundRandomization = piercingPowerRandomization - lowerRandomizationFactor
        upperBoundRandomization = piercingPowerRandomization + upperRandomizationFactor
        return (int(floor(piercingPower - piercingPower * lowerBoundRandomization)), int(ceil(piercingPower + piercingPower * upperBoundRandomization)))

    @property
    def reloadTime(self):
        return None if self.__hasAutoReload() or self.__hasDualGun() else min(self.__calcReloadTime())

    @property
    def reloadTimeSituational(self):
        return None if self.__hasAutoReload() or self.__hasDualGun() else min(self.__calcReloadTime(isSituational=True))

    @property
    def turretRotationSpeed(self):
        rotSpeedVal = round(math.degrees(items_utils.getTurretRotationSpeed(self._itemDescr, self.__factors)), 2)
        if self.__hasUnsupportedSwitchMode():
            rotSpeedSiegeVal = items_utils.getTurretRotationSpeed(self._itemDescr.siegeVehicleDescr, self.__factors)
            return (rotSpeedVal, round(math.degrees(rotSpeedSiegeVal), 2))
        return (rotSpeedVal,)

    @property
    def circularVisionRadius(self):
        baseCircularVisionRadius = items_utils.getCircularVisionRadius(self._itemDescr, self.__factors)
        result = round(baseCircularVisionRadius)
        if self.__hasUnsupportedSwitchMode():
            visRadiusSiegeVal = items_utils.getCircularVisionRadius(self._itemDescr.siegeVehicleDescr, self.__factors)
            return (result, round(visRadiusSiegeVal))
        return (result,)

    @property
    def radioDistance(self):
        baseDistance = items_utils.getRadioDistance(self._itemDescr, self.__factors)
        skillName = 'radioman_inventor'
        argName = 'radioDistance'
        factor = self.__getFactorValueFromSkill(skillName, argName, Tankman.ROLES.RADIOMAN)
        return int(baseDistance * factor)

    @property
    def turretArmor(self):
        return tuple((round(armor) for armor in self._itemDescr.turret.primaryArmor)) if self.__hasTurret() else None

    @property
    def explosionRadius(self):
        shotShell = self._itemDescr.shot.shell
        return round(shotShell.type.explosionRadius, 2) if shotShell.kind in HAS_EXPLOSION else 0

    @property
    def aimingTime(self):
        aimingTimeVal = items_utils.getGunAimingTime(self._itemDescr, self.__factors)
        if self._itemDescr.hasTurboshaftEngine:
            siegeAimingTimeVal = items_utils.getGunAimingTime(self._itemDescr.siegeVehicleDescr, self.__factors)
            return (aimingTimeVal, siegeAimingTimeVal)
        return (aimingTimeVal,)

    def __shotDispersionAngle(self, isSituational=False):
        skillName = 'gunner_focus'
        argName = 'shotDispersionAngle'
        shotDispersions = items_utils.getClientShotDispersion(self._itemDescr, self.__factors['shotDispersion'][0])
        baseShotDispersions = (round(shotDispersion * 100, 4) for shotDispersion in shotDispersions)
        skillFactorValue = 1
        if isSituational:
            skillFactorValue = self.__getFactorValueFromSkill(skillName, argName, Tankman.ROLES.GUNNER, isSituational)
        return [ baseShotDispersion * skillFactorValue for baseShotDispersion in baseShotDispersions ]

    @property
    def shotDispersionAngle(self):
        return self.__shotDispersionAngle()

    @property
    def shotDispersionAngleSituational(self):
        return self.__shotDispersionAngle(isSituational=True)

    @property
    def reloadTimeSecs(self):
        if self.__hasClipGun() or self.__hasAutoReload():
            return None
        else:
            return tuple((_timesToSecs(reloadTime) for reloadTime in self.__calcReloadTime())) if self.__hasDualGun() else (_timesToSecs(first(self.__calcReloadTime())),)

    @property
    def reloadTimeSecsSituational(self):
        if self.__hasClipGun() or self.__hasAutoReload():
            return None
        elif self.__hasDualGun():
            return tuple((_timesToSecs(reloadTime) for reloadTime in self.__calcReloadTime(isSituational=True)))
        else:
            _val = self.__calcReloadTime(isSituational=True)
            return (_timesToSecs(first(_val)),)

    @property
    def autoReloadTime(self):
        return tuple(reversed(items_utils.getClipReloadTime(self._itemDescr, self.__factors))) if self.__hasAutoReload() else None

    @property
    def autoReloadTimeSituational(self):
        if self.__hasAutoReload():
            skillName = 'loader_desperado'
            argName = 'gunReloadSpeed'
            loaderDesperadoReloadFactor = self.__getFactorValueFromSkill(skillName, argName, Tankman.ROLES.LOADER, True)
            reloadTimes = tuple(reversed(items_utils.getClipReloadTime(self._itemDescr, self.__factors)))
            return tuple((reloadTime * loaderDesperadoReloadFactor for reloadTime in reloadTimes))
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
        value = round(self.avgDamagePerMinute * penetration / min(self.shotDispersionAngle) * (coeffs['rotationIntercept'] + coeffs['rotationSlope'] * rotationSpeed) * turretCoefficient * coeffs['normalization'] * self.__adjustmentCoefficient('power') * spgCorrection * gunCorrection * heCorrection)
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
        value = round((self.invisibilityMovingFactor.current + self.invisibilityStillFactor.current + self.invisibilityStillFactor.atShot) / 3.0 * coeffs['normalization'] * self.__adjustmentCoefficient('camouflage'))
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
        shotDemaskFactor = self.__getFactorValueFromSkill('loader_ambushMaster', 'shotDemaskFactor', Tankman.ROLES.LOADER)
        return self._itemDescr.miscAttrs['invisibilityFactorAtShot'] * shotDemaskFactor

    @property
    def clipFireRate(self):
        if self.__hasClipGun():
            gunParams = self._itemDescr.gun
            clipData = gunParams.clip
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

    @property
    def clipFireRateSituational(self):
        skillName = 'loader_desperado'
        argName = 'gunReloadSpeed'
        loaderDesperadoReloadFactor = self.__getFactorValueFromSkill(skillName, argName, Tankman.ROLES.LOADER, True)
        if self.__hasClipGun():
            gunParams = self._itemDescr.gun
            clipData = gunParams.clip
            if self.__hasAutoReload():
                reloadTime = sum(items_utils.getClipReloadTime(self._itemDescr, self.__factors))
            else:
                reloadTime = items_utils.getReloadTime(self._itemDescr, self.__factors)
            reloadTime = reloadTime * loaderDesperadoReloadFactor
            rateTime = clipData[1]
            return (reloadTime, rateTime, clipData[0])
        elif self.__hasDualGun():
            reloadTimes = items_utils.getDualGunReloadTime(self._itemDescr, self.__factors)
            reloadTime = sum(reloadTimes) * loaderDesperadoReloadFactor
            rateTime = self._itemDescr.gun.dualGun.rateTime
            return (reloadTime, rateTime, len(reloadTimes))
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
    def flameMaxDistance(self):
        shot = self._itemDescr.shot
        return shot.maxDistance if shot.shell.kind == SHELL_TYPES.FLAME else None

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
            if chassis.isMultiTrack and repairTime:
                repairTime = [min(repairTime), max(repairTime)]
        elif chassis.repairTime is not None:
            repairTime.append(self.__calcRealChassisRepairTime(chassis.repairTime))
        return repairTime

    @property
    def wheelsRotationSpeed(self):
        return None if not self._itemDescr.isWheeledVehicle and not self._itemDescr.isWheeledOnSpotRotation else self.__kpi.getFactor(KPI.Name.WHEELS_ROTATION_SPEED)

    @property
    def artNotificationDelayFactorSituational(self):
        return max(MAX_ART_NOTIFICATION_DELAY_PERK_VAL, self.__kpi.getFactor(KPI.Name.ART_NOTIFICATION_DELAY_FACTOR))

    @property
    def artNotificationDelayFactor(self):
        artNotificationDelayFactor = self.__kpi.getFactor(KPI.Name.ART_NOTIFICATION_DELAY_FACTOR)
        realNotificationDelayTime = max(MAX_ART_NOTIFICATION_DELAY_PERK_VAL, artNotificationDelayFactor)
        return HIDDEN_PARAM_DEFAULTS[KPI.Name.ART_NOTIFICATION_DELAY_FACTOR] + realNotificationDelayTime

    @property
    def radiomanActivityTimeAfterVehicleDestroySituational(self):
        return self.__kpi.getFactor(KPI.Name.RADIOMAN_ACTIVITY_TIME_AFTER_VEHICLE_DESTROY)

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
         'flameMaxDistance')
        stunConditionParams = ('stunMaxDuration',)
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
                if skill.isEnable:
                    result.append((skill.name, 'skill'))

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
            result[paramName] = [ _PenaltyInfo(roles[slotId][0], value, slotId in otherVehicleSlots, PenaltyTypes.CREW) for slotId, value in penalties.iteritems() ]

        return {k:v for k, v in result.iteritems() if v}

    def _getVehicleDescriptor(self, vehicle):
        return vehicle.descriptor

    def __calcRealChassisRepairTime(self, chassisRepairTime):
        skillName = 'repair'
        argName = 'vehicleRepairSpeed'
        realSkillLevel = crewMemberRealSkillLevel(self.__vehicle, skillName, Tankman.ROLES.COMMANDER)
        kpiSkillFactor = 1
        if realSkillLevel > 0:
            kpiSkillFactor = self.__getKpiValueFromSkillConfig(skillName, argName, Tankman.ROLES.COMMANDER)
        repairFactor = self.__factors.get('repairSpeed', 1.0)
        vehicleRepairSpeed = self.__kpi.getCoeff('vehicleRepairSpeed')
        repairKpi = 1 + (vehicleRepairSpeed - kpiSkillFactor)
        repairChassisKpi = self.__kpi.getCoeff('vehicleChassisRepairSpeed')
        return chassisRepairTime / repairFactor / repairKpi / repairChassisKpi

    def __speedLimits(self, limits, miscAttrs=None):
        correction = []
        if miscAttrs:
            if len(miscAttrs) > len(limits):
                raise SoftException('correction can not be less than speed limits')
            correction = map(self._itemDescr.miscAttrs.get, miscAttrs)
        return [ round(speed * METERS_PER_SECOND_TO_KILOMETERS_PER_HOUR + correct, 2) for speed, correct in izip_longest(limits, correction, fillvalue=0) ]

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
        return enginePower / self.vehicleWeight * METERS_PER_SECOND_TO_KILOMETERS_PER_HOUR * self.__factors['engine/power'] / 12.25 / rollingFriction

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

    def __hasDualAccuracy(self):
        return isDualAccuracy(self._itemDescr.gun)

    def __calcReloadTime(self, isSituational=False):
        loaderDesperadoReloadFactor = 1
        if isSituational:
            skillName = 'loader_desperado'
            argName = 'gunReloadSpeed'
            loaderDesperadoReloadFactor = self.__getFactorValueFromSkill(skillName, argName, Tankman.ROLES.LOADER, isSituational)

        def getParams(f):
            reloadTimes = f(self._itemDescr, self.__factors)
            reloadTimesMax = max(reloadTimes) * loaderDesperadoReloadFactor
            reloadTimesMin = min(reloadTimes) * loaderDesperadoReloadFactor
            return (getShotsPerMinute(self._itemDescr.gun, reloadTimesMax, hasAutoReload), getShotsPerMinute(self._itemDescr.gun, reloadTimesMin, hasAutoReload))

        hasAutoReload = self.__hasAutoReload()
        if hasAutoReload:
            return getParams(items_utils.getClipReloadTime)
        if self.__hasDualGun():
            return getParams(items_utils.getDualGunReloadTime)
        reloadTime = items_utils.getReloadTime(self._itemDescr, self.__factors)
        return (getShotsPerMinute(self._itemDescr.gun, reloadTime * loaderDesperadoReloadFactor, hasAutoReload),)

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

    def __getFactorValueFromSkill(self, skillName, argName, role, situational=False):
        skill = tankmen.getSkillsConfig().getSkill(skillName)
        param = skill.params.get(argName)
        factorPerLevel = param.value if param else 0.0
        realSkillLevel = crewMemberRealSkillLevel(self.__vehicle, skillName, role)
        realFactorValue = 1
        if realSkillLevel != tankmen.NO_SKILL:
            realFactorValue += factorPerLevel * realSkillLevel
        return realFactorValue

    def __getKpiValueFromSkillConfig(self, skillName, argName, role, kpiType=KPI.Type.MUL):
        skillKpi = tankmen.getSkillsConfig().getSkill(skillName).kpi
        result = 1.0 if kpiType == KPI.Type.MUL else 0.0
        realSkillLevel = crewMemberRealSkillLevel(self.__vehicle, skillName, role)
        if realSkillLevel != tankmen.NO_SKILL:
            for _kpi in skillKpi:
                if _kpi.name == argName:
                    baseValue = 1.0 if _kpi.type == KPI.Type.MUL else 0.0
                    result = baseValue - (baseValue - _kpi.value) * realSkillLevel / tankmen.MAX_SKILL_LEVEL

        return result


class GunParams(WeightedParam):
    SHELLS_COUNT_PROPS = (SHELLS_COUNT_PROP_NAME, SHELLS_BURST_COUNT_PROP_NAME, SHELLS_FLAME_BURST_COUNT_PROP_NAME)

    @property
    def caliber(self):
        return self._itemDescr.shots[0].shell.caliber

    @property
    def shellsCount(self):
        return self._getRawParams()[SHELLS_COUNT_PROP_NAME]

    @property
    def shellsBurstCount(self):
        return self._getRawParams()[SHELLS_BURST_COUNT_PROP_NAME]

    @property
    def shellsFlameBurstCount(self):
        return self._getRawParams()[SHELLS_BURST_COUNT_PROP_NAME]

    @property
    def shellReloadingTime(self):
        return self._getRawParams()[SHELL_RELOADING_TIME_PROP_NAME]

    @property
    def reloadMagazineTime(self):
        return self._getRawParams()[RELOAD_MAGAZINE_TIME_PROP_NAME]

    @property
    def reloadTime(self):
        if self.getReloadingType() in (GUN_CAN_BE_AUTO_RELOAD, GUN_AUTO_RELOAD):
            return None
        else:
            return None if self.getReloadingType() in (GUN_CAN_BE_DUAL_GUN, GUN_DUAL_GUN) else self._getRawParams()[RELOAD_TIME_PROP_NAME]

    @property
    def reloadTimeSecs(self):
        return self._getRawParams()[RELOAD_TIME_SECS_PROP_NAME]

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
    def dispertionRadius(self):
        disp = self._getRawParams()[DISPERSION_RADIUS_PROP_NAME][0]
        gun = self.__getSelectedVehicleGun()
        return (math.tan(gun.dualAccuracy.afterShotDispersionAngle) * 100, disp) if isDualAccuracy(gun) else (None, disp)

    @property
    def aimingTime(self):
        return self._getRawParams()[AIMING_TIME_PROP_NAME]

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
    def flameMaxDistance(self):
        return self.maxShotDistance if self.__isFlameGun() else None

    @property
    def clipVehiclesCD(self):
        return self._getPrecachedInfo().clipVehicles

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
    def autoReloadTime(self):
        return tuple(reversed(self._getRawParams().get(AUTO_RELOAD_PROP_NAME)))

    @property
    def dualAccuracyAfterShotDispersionAngle(self):
        res = self._getRawParams().get(DUAL_ACCURACY_AFTER_SHOT_DISPERSION_ANGLE)
        return res if res else None

    @property
    def dualAccuracyCoolingDelay(self):
        gun = self.__getSelectedVehicleGun()
        return gun.dualAccuracy.coolingDelay if isDualAccuracy(gun) else None

    def getParamsDict(self):
        stunConditionParams = (STUN_DURATION_PROP_NAME,)
        stunItem = self._itemDescr.shots[0].shell
        shellsCountProp = self.__getShellsCountProp()
        filteredOutShellsCountProps = tuple((p for p in self.SHELLS_COUNT_PROPS if p != shellsCountProp))
        result = _ParamsDictProxy(self, conditions=((['maxShotDistance'], lambda v: v == _AUTOCANNON_SHOT_DISTANCE),
         (['flameMaxDistance'], lambda v: v is not None),
         (filteredOutShellsCountProps, lambda v: False),
         (stunConditionParams, lambda s: _isStunParamVisible(stunItem))))
        return result

    def getReloadingType(self, vehicleCD=None):
        if vehicleCD is None and self._vehicleDescr is not None:
            vehicleCD = self._vehicleDescr.type.compactDescr
        return self._getPrecachedInfo().getReloadingType(vehicleCD)

    def getAllDataDict(self):
        result = super(GunParams, self).getAllDataDict()
        reloadingType = self.getReloadingType()
        result['extras'] = {'gunReloadingType': reloadingType,
         'excludedParams': _GUN_EXCLUDED_PARAMS.get(reloadingType, tuple())}
        return result

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
        compatibleVehiclesType = 'vehicles' if not clipVehicleNamesList or self.__isFlameGun() else 'clipVehicles'
        if clipVehicleNamesList:
            if vehiclesNamesList:
                result.append(('uniChargedVehicles', _formatCompatibles(curVehicle, vehiclesNamesList)))
            result.append((compatibleVehiclesType, _formatCompatibles(curVehicle, clipVehicleNamesList)))
        else:
            result.append((compatibleVehiclesType, _formatCompatibles(curVehicle, vehiclesNamesList)))
        result.append(('ammunition' if self.__isFlameGun() else 'shells', ', '.join(self.shellsCompatibles)))
        return tuple(result)

    def __getSelectedVehicleGun(self):
        if self._vehicleDescr is not None:
            guns = self._vehicleDescr.type.getGuns()
            return next((obj for obj in guns if obj.compactDescr == self._itemDescr.compactDescr), None)
        else:
            return

    def __getShellsCountProp(self):
        if self.__isBurstGun():
            if self.__isFlameGun():
                return SHELLS_FLAME_BURST_COUNT_PROP_NAME
            return SHELLS_BURST_COUNT_PROP_NAME
        return SHELLS_COUNT_PROP_NAME

    def __isFlameGun(self):
        return self._itemDescr.shots[0].shell.kind == SHELL_TYPES.FLAME

    def __isBurstGun(self):
        burstShellsCount = self._getRawParams()[SHELLS_BURST_COUNT_PROP_NAME]
        return burstShellsCount[0] != 1 if burstShellsCount else False


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
        return self._itemDescr.avgDamage

    @property
    def avgPiercingPower(self):
        return _average(self.piercingPower)

    @property
    def explosionRadius(self):
        return self._itemDescr.type.explosionRadius if self._itemDescr.kind in HAS_EXPLOSION else 0

    @property
    def piercingPowerTable(self):
        if self._itemDescr.kind in _POWER_PIERCING_SHELLS:
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
                currPiercing = PIERCING_POWER.computePiercingPowerAtDist(shellDescriptor.piercingPower, distance, maxDistance)
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
    def flameMaxDistance(self):
        return self.maxShotDistance if self._itemDescr.kind == SHELL_TYPES.FLAME else None

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
    def shotSpeed(self):
        if self._itemDescr.kind in _SHELL_KINDS and self._vehicleDescr is not None:
            result = self.__getShellDescriptor()
            if result:
                projSpeedFactor = vehicles.g_cache.commonConfig['miscParams']['projectileSpeedFactor']
                return result.speed / projSpeedFactor
        return

    def getParamsDict(self):
        stunConditionParams = ('stunMaxDuration',)
        result = _ParamsDictProxy(self, conditions=((['maxShotDistance'], lambda v: v == _AUTOCANNON_SHOT_DISTANCE), (['flameMaxDistance'], lambda v: v is not None), (stunConditionParams, lambda s: _isStunParamVisible(self._itemDescr))))
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


class OptionalDeviceParams(CompatibleParams):

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
                    raise KeyError
                self.__cachedParams[item] = value
            else:
                raise KeyError
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
            for k, v in self.__paramsCalculator.__class__.__dict__.iteritems():
                if isinstance(v, property):
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
