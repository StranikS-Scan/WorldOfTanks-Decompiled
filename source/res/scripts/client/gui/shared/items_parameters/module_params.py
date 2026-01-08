# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/items_parameters/module_params.py
import math
from gui.shared.items_parameters import calcGunParams, getGunDescriptors, isDualAccuracy, isTwinGun, isUnlimitedClipGun, isOverheatedUnlimitedGun, isTemperatureGun
from gui.shared.items_parameters.base_params import ParamsDictProxy, WeightedParam
from gui.shared.items_parameters.params_constants import ONE_HUNDRED_PERCENTS, AUTOCANNON_SHOT_DISTANCE
from gui.shared.items_parameters.functions import isStunParamVisible, getTurboshaftEnginePower, getRocketAccelerationEnginePower, getMaxSteeringLockAngle, getInstalledModuleVehicle, formatCompatibles
from gui.shared.items_parameters.params_cache import g_paramsCache
from gui.shared.utils import DAMAGE_PROP_NAME, PIERCING_POWER_PROP_NAME, AIMING_TIME_PROP_NAME, STUN_DURATION_PROP_NAME, GUARANTEED_STUN_DURATION_PROP_NAME, AUTO_RELOAD_PROP_NAME, GUN_AUTO_RELOAD, GUN_CAN_BE_AUTO_RELOAD, GUN_AUTO_SHOOT, GUN_CAN_BE_AUTO_SHOOT, GUN_DUAL_GUN, GUN_CAN_BE_DUAL_GUN, RELOAD_TIME_SECS_PROP_NAME, DUAL_GUN_CHARGE_TIME, DUAL_GUN_RATE_TIME, DUAL_ACCURACY_AFTER_SHOT_DISPERSION_ANGLE, BURST_FIRE_RATE, MAX_MUTABLE_DAMAGE_PROP_NAME, MIN_MUTABLE_DAMAGE_PROP_NAME, GUN_CAN_BE_TWIN_GUN, GUN_TWIN_GUN, DISPERSION_RADIUS_PROP_NAME, SHELLS_PROP_NAME, SHELLS_COUNT_PROP_NAME, RELOAD_TIME_PROP_NAME, RELOAD_MAGAZINE_TIME_PROP_NAME, SHELL_RELOADING_TIME_PROP_NAME, SHELL_LOADING_TIME_PROP_NAME
from helpers import dependency
from items.components import component_constants
from items.params_utils import getTemperatureRateOfFire, getHeatedAimingTime, getHeatedShotDispersion
from skeletons.gui.shared import IItemsCache

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
        power = getTurboshaftEnginePower(self._vehicleDescr, self._itemDescr.name)
        return power and int(round(power / component_constants.HP_TO_WATTS))

    @property
    def rocketAccelerationEnginePower(self):
        return getRocketAccelerationEnginePower(self._vehicleDescr, self.enginePower)

    @property
    def fireStartingChance(self):
        return int(round(self._itemDescr.fireStartingChance * ONE_HUNDRED_PERCENTS))

    @property
    def forwardMaxSpeed(self):
        return self._vehicleDescr.type.xphysics['engines'][self._itemDescr.name]['smplFwMaxSpeed']


class ChassisParams(WeightedParam):
    itemsCache = dependency.descriptor(IItemsCache)

    @property
    def rotationSpeed(self):
        return int(round(math.degrees(self._itemDescr.rotationSpeed))) if not self.isWheeled or self.isWheeledOnSpotRotation else None

    @property
    def maxSteeringLockAngle(self):
        return getMaxSteeringLockAngle(g_paramsCache.getWheeledChassisAxleLockAngles(self._itemDescr.compactDescr)) if self.isWheeled else None

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
        compatibleVehicles.append(('guns', formatCompatibles(curGun, self.gunCompatibles)))
        return tuple(compatibleVehicles)


class GunParams(WeightedParam):
    _GUNS_WITH_HIDDEN_RELOAD_TIME = (GUN_CAN_BE_AUTO_RELOAD,
     GUN_AUTO_RELOAD,
     GUN_CAN_BE_DUAL_GUN,
     GUN_DUAL_GUN,
     GUN_CAN_BE_TWIN_GUN,
     GUN_TWIN_GUN)

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
        if self.getReloadingType() in self._GUNS_WITH_HIDDEN_RELOAD_TIME:
            return None
        else:
            gun = self.__getVehicleGun()
            return (getTemperatureRateOfFire(gun, isVehicle=False),) if isOverheatedUnlimitedGun(gun) else self._getRawParams()[RELOAD_TIME_PROP_NAME]

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
        return gun.twinGun.twinGunReloadTime if isTwinGun(gun) else None

    @property
    def shellLoadingTime(self):
        gun = self.__getVehicleGun()
        return self._getRawParams()[SHELL_LOADING_TIME_PROP_NAME] if isUnlimitedClipGun(gun) else None

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
        elif isTwinGun(gun):
            return (disp, math.tan(self._vehicleDescr.siegeVehicleDescr.gun.shotDispersionAngle) * 100)
        else:
            return (round(getHeatedShotDispersion(gun.shotDispersionAngle, gun) * 100, 2), disp) if isTemperatureGun(gun) else (None, disp)

    @property
    def aimingTime(self):
        gun = self.__getVehicleGun()
        aimingTime = self._getRawParams()[AIMING_TIME_PROP_NAME]
        if isTwinGun(gun):
            return (aimingTime[1], self._vehicleDescr.siegeVehicleDescr.gun.aimingTime)
        if isTemperatureGun(gun):
            baseAimingTime = aimingTime[1]
            return (getHeatedAimingTime(baseAimingTime, gun), baseAimingTime)
        return aimingTime

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
        gun = self.__getVehicleGun()
        return round(self.continuousShotsPerMinute[0] * self.avgDamageList[0]) if isUnlimitedClipGun(gun) and not isTemperatureGun(gun) else round(self.reloadTime[0] * self.avgDamageList[0])

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
        unlimitedClipHiddenParams = (SHELLS_COUNT_PROP_NAME, RELOAD_MAGAZINE_TIME_PROP_NAME, RELOAD_TIME_PROP_NAME)
        stunItem = self._itemDescr.shots[0].shell
        gun = self.__getVehicleGun()
        result = ParamsDictProxy(self, conditions=((['maxShotDistance'], lambda v: v == AUTOCANNON_SHOT_DISTANCE), (stunConditionParams, lambda s: isStunParamVisible(stunItem)), (unlimitedClipHiddenParams, lambda v: not isUnlimitedClipGun(gun))))
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
        curVehicle = getInstalledModuleVehicle(self._vehicleDescr, self._itemDescr)
        result = []
        if clipVehicleNamesList:
            if vehiclesNamesList:
                result.append(('uniChargedVehicles', formatCompatibles(curVehicle, vehiclesNamesList)))
            result.append(('clipVehicles', formatCompatibles(curVehicle, clipVehicleNamesList)))
        else:
            result.append(('vehicles', formatCompatibles(curVehicle, vehiclesNamesList)))
        result.append(('shells', ', '.join(self.shellsCompatibles)))
        return tuple(result)

    def __getVehicleGun(self):
        if self._vehicleDescr is not None:
            guns = getGunDescriptors(self._itemDescr, self._vehicleDescr)
            return next((obj for obj in guns if obj.compactDescr == self._itemDescr.compactDescr), None)
        else:
            return self._itemDescr
