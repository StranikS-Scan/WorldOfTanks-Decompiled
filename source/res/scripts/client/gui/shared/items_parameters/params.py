# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/items_parameters/params.py
import collections
import copy
import inspect
import math
import operator
from collections import namedtuple, defaultdict
from operator import itemgetter
from math import ceil
from constants import SHELL_TYPES
from debug_utils import LOG_DEBUG
from gui import GUI_SETTINGS
from gui.shared.formatters import text_styles
from gui.shared.items_parameters import calcGunParams, calcShellParams, getShotsPerMinute, getGunDescriptors, getShellDescriptors, getOptionalDeviceWeight, NO_DATA
from gui.shared.items_parameters.comparator import rateParameterState, PARAM_STATE
from gui.shared.items_parameters.functions import getBasicShell
from gui.shared.items_parameters.params_cache import g_paramsCache
from gui.shared.items_parameters import functions
from gui.shared.utils import DAMAGE_PROP_NAME, PIERCING_POWER_PROP_NAME, AIMING_TIME_PROP_NAME, DISPERSION_RADIUS_PROP_NAME, SHELLS_PROP_NAME, GUN_NORMAL, SHELLS_COUNT_PROP_NAME, RELOAD_MAGAZINE_TIME_PROP_NAME, SHELL_RELOADING_TIME_PROP_NAME, GUN_CLIP, RELOAD_TIME_PROP_NAME, GUN_CAN_BE_CLIP
from helpers import time_utils
from items import getTypeOfCompactDescr, vehicles, getTypeInfoByIndex, ITEM_TYPES
from items import utils as items_utils
from shared_utils import findFirst
MAX_VISION_RADIUS = 500
MIN_VISION_RADIUS = 150
PIERCING_DISTANCES = (100, 250, 500)
ONE_HUNDRED_PERCENTS = 100
MIN_RELATIVE_VALUE = 1
_Weight = namedtuple('_Weight', 'current, max')
_Invisibility = namedtuple('_Invisibility', 'current, atShot')
_PenaltyInfo = namedtuple('_PenaltyInfo', 'roleName, value, vehicleIsNotNative')
MODULES = {ITEM_TYPES.vehicleRadio: lambda vehicleDescr: vehicleDescr.radio,
 ITEM_TYPES.vehicleEngine: lambda vehicleDescr: vehicleDescr.engine,
 ITEM_TYPES.vehicleChassis: lambda vehicleDescr: vehicleDescr.chassis,
 ITEM_TYPES.vehicleTurret: lambda vehicleDescr: vehicleDescr.turret,
 ITEM_TYPES.vehicleGun: lambda vehicleDescr: vehicleDescr.gun}
METERS_PER_SECOND_TO_KILOMETERS_PER_HOUR = 3.6
_GUN_EXCLUDED_PARAMS = {GUN_NORMAL: (SHELLS_COUNT_PROP_NAME, RELOAD_MAGAZINE_TIME_PROP_NAME, SHELL_RELOADING_TIME_PROP_NAME),
 GUN_CLIP: (RELOAD_TIME_PROP_NAME,),
 GUN_CAN_BE_CLIP: (SHELLS_COUNT_PROP_NAME, RELOAD_MAGAZINE_TIME_PROP_NAME, SHELL_RELOADING_TIME_PROP_NAME)}
_FACTOR_TO_SKILL_PENALTY_MAP = {'turret/rotationSpeed': ('turretRotationSpeed', 'relativePower'),
 'circularVisionRadius': ('circularVisionRadius', 'relativeVisibility'),
 'radio/distance': ('radioDistance', 'relativeVisibility'),
 'gun/rotationSpeed': ('gunRotationSpeed', 'relativePower'),
 'gun/reloadTime': ('reloadTime',
                    'avgDamagePerMinute',
                    'relativePower',
                    'reloadTimeSecs',
                    'clipFireRate'),
 'gun/aimingTime': ('aimingTime',),
 'vehicle/rotationSpeed': ('chassisRotationSpeed', 'relativeMobility'),
 'chassis/terrainResistance': ('chassisRotationSpeed', 'relativeMobility'),
 'shotDispersion': ('shotDispersionAngle',)}
_SHELL_KINDS = (SHELL_TYPES.HOLLOW_CHARGE,
 SHELL_TYPES.HIGH_EXPLOSIVE,
 SHELL_TYPES.ARMOR_PIERCING,
 SHELL_TYPES.ARMOR_PIERCING_HE,
 SHELL_TYPES.ARMOR_PIERCING_CR)
_AUTOCANNON_SHOT_DISTANCE = 400

def _processExtraBonuses(vehicle):
    result = []
    withRareCamouflage = vehicle.intCD in g_paramsCache.getVehiclesWithoutCamouflage()
    if withRareCamouflage or any(map(itemgetter(0), vehicle.descriptor.camouflages)):
        result.append(('camouflage', 'extra'))
    return result


def _universalSum(a, b):
    if isinstance(a, collections.Sequence):
        return map(operator.add, a, b)
    else:
        return a + b


def _getInstalledModuleVehicle(vehicleDescr, itemDescr):
    curVehicle = None
    if vehicleDescr:
        compDescrType = getTypeOfCompactDescr(itemDescr['compactDescr'])
        module = MODULES[compDescrType](vehicleDescr)
        if module['id'][1] == itemDescr['id'][1]:
            curVehicle = vehicleDescr.type.userString
    return curVehicle


def _average(listOfNumbers):
    return sum(listOfNumbers) / len(listOfNumbers)


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
            self.__preCachedInfo = g_paramsCache.getPrecachedParameters(self._itemDescr['compactDescr'])
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
        return g_paramsCache.getComponentVehiclesNames(self._itemDescr['compactDescr'])

    def _getCompatible(self):
        curVehicle = _getInstalledModuleVehicle(self._vehicleDescr, self._itemDescr)
        return (('vehicles', _formatCompatibles(curVehicle, self.compatibles)),)


class WeightedParam(CompatibleParams):

    @property
    def weight(self):
        return self._itemDescr['weight']


class RadioParams(WeightedParam):

    @property
    def radioDistance(self):
        return int(round(self._itemDescr['distance']))


class EngineParams(WeightedParam):

    @property
    def enginePower(self):
        return int(round(self._itemDescr['power'] / vehicles.HP_TO_WATTS, 0))

    @property
    def fireStartingChance(self):
        return int(round(self._itemDescr['fireStartingChance'] * ONE_HUNDRED_PERCENTS))


class ChassisParams(WeightedParam):

    @property
    def maxLoad(self):
        return self._itemDescr['maxLoad'] / 1000

    @property
    def rotationSpeed(self):
        return int(round(math.degrees(self._itemDescr['rotationSpeed'])))

    @property
    def isHydraulic(self):
        return self._getPrecachedInfo().isHydraulic


class TurretParams(WeightedParam):

    @property
    def armor(self):
        return self._itemDescr['primaryArmor']

    @property
    def rotationSpeed(self):
        return int(round(math.degrees(self._itemDescr['rotationSpeed'])))

    @property
    def circularVisionRadius(self):
        return self._itemDescr['circularVisionRadius']

    @property
    def gunCompatibles(self):
        return [ gun['userString'] for gun in self._itemDescr['guns'] ]

    def _getCompatible(self):
        if self._vehicleDescr is not None:
            curGun = self._vehicleDescr.gun['userString']
        else:
            curGun = None
        compatibleVehicles = list(super(TurretParams, self)._getCompatible())
        compatibleVehicles.append(('guns', _formatCompatibles(curGun, self.gunCompatibles)))
        return tuple(compatibleVehicles)


class VehicleParams(_ParameterBase):

    def __init__(self, vehicle):
        super(VehicleParams, self).__init__(self._getVehicleDescriptor(vehicle))
        self.__factors = functions.getVehicleFactors(vehicle)
        self.__coefficients = g_paramsCache.getSimplifiedCoefficients()

    @property
    def maxHealth(self):
        return self._itemDescr.maxHealth

    @property
    def vehicleWeight(self):
        return _Weight(self._itemDescr.physics['weight'] / 1000, self._itemDescr.miscAttrs['maxWeight'] / 1000)

    @property
    def enginePower(self):
        return round(self._itemDescr.physics['enginePower'] * self.__factors['engine/power'] / vehicles.HP_TO_WATTS)

    @property
    def enginePowerPerTon(self):
        return round(self.enginePower / self.vehicleWeight.current, 2)

    @property
    def speedLimits(self):
        limits = self._itemDescr.physics['speedLimits']
        return map(lambda speed: round(speed * METERS_PER_SECOND_TO_KILOMETERS_PER_HOUR, 2), limits)

    @property
    def chassisRotationSpeed(self):
        allTrfs = self.__getTerrainResistanceFactors()
        avgTrf = sum(allTrfs) / len(allTrfs)
        return math.degrees(items_utils.getChassisRotationSpeed(self._itemDescr, self.__factors)) / avgTrf

    @property
    def hullArmor(self):
        return self._itemDescr.hull['primaryArmor']

    @property
    def damage(self):
        avgDamage = self.avgDamage
        damageRandomization = self._itemDescr.shot['shell']['damageRandomization']
        return (int(avgDamage - avgDamage * damageRandomization), int(ceil(avgDamage + avgDamage * damageRandomization)))

    @property
    def avgDamage(self):
        return self._itemDescr.shot['shell'][DAMAGE_PROP_NAME][0]

    @property
    def avgDamagePerMinute(self):
        return round(self.reloadTime * self.avgDamage)

    @property
    def avgPiercingPower(self):
        return self._itemDescr.shot[PIERCING_POWER_PROP_NAME][0]

    @property
    def piercingPower(self):
        piercingPower = self.avgPiercingPower
        delta = piercingPower * self._itemDescr.shot['shell']['piercingPowerRandomization']
        return (int(piercingPower - delta), int(ceil(piercingPower + delta)))

    @property
    def reloadTime(self):
        reloadTime = items_utils.getReloadTime(self._itemDescr, self.__factors)
        return getShotsPerMinute(self._itemDescr.gun, reloadTime)

    @property
    def turretRotationSpeed(self):
        return round(math.degrees(items_utils.getTurretRotationSpeed(self._itemDescr, self.__factors)), 2) if self.__hasTurret() else None

    @property
    def gunRotationSpeed(self):
        if self._itemDescr.isYawHullAimingAvailable:
            return self.chassisRotationSpeed
        else:
            return round(math.degrees(items_utils.getTurretRotationSpeed(self._itemDescr, self.__factors)), 2) if not self.__hasTurret() else None

    @property
    def circularVisionRadius(self):
        return round(items_utils.getCircularVisionRadius(self._itemDescr, self.__factors))

    @property
    def radioDistance(self):
        return round(items_utils.getRadioDistance(self._itemDescr, self.__factors))

    @property
    def turretArmor(self):
        return self._itemDescr.turret['primaryArmor'] if self.__hasTurret() else None

    @property
    def explosionRadius(self):
        shotShell = self._itemDescr.shot['shell']
        if shotShell['kind'] == SHELL_TYPES.HIGH_EXPLOSIVE:
            return round(shotShell['explosionRadius'], 2)
        else:
            return 0

    @property
    def aimingTime(self):
        return items_utils.getGunAimingTime(self._itemDescr, self.__factors)

    @property
    def shotDispersionAngle(self):
        shotDispersion = items_utils.getClientShotDispersion(self._itemDescr, self.__factors['shotDispersion'][0])
        return round(shotDispersion * 100, 2)

    @property
    def reloadTimeSecs(self):
        if self.__hasClipGun():
            return None
        else:
            return round(time_utils.ONE_MINUTE / self.reloadTime, 3)
            return None

    @property
    def relativePower(self):
        coeffs = self.__coefficients['power']
        penetration = self._itemDescr.shot[PIERCING_POWER_PROP_NAME][0]
        rotationSpeed = self.turretRotationSpeed or self.gunRotationSpeed
        turretCoefficient = 1 if self.__hasTurret() else coeffs['turretCoefficient']
        heCorrection = 1.0
        if 'SPG' in self._itemDescr.type.tags:
            spgCorrection = 6
        else:
            spgCorrection = 1
            if self.__currentShot()['shell']['kind'] == 'HIGH_EXPLOSIVE':
                heCorrection = coeffs['alphaDamage']
        gunCorrection = self.__adjustmentCoefficient('guns').get(self._itemDescr.gun['name'], {})
        gunCorrection = gunCorrection.get('caliberCorrection', 1)
        value = round(self.avgDamagePerMinute * penetration / self.shotDispersionAngle * (coeffs['rotationIntercept'] + coeffs['rotationSlope'] * rotationSpeed) * turretCoefficient * coeffs['normalization'] * self.__adjustmentCoefficient('power') * spgCorrection * gunCorrection * heCorrection)
        return max(value, MIN_RELATIVE_VALUE)

    @property
    def relativeArmor(self):
        coeffs = self.__coefficients['armour']
        hullArmor = self._itemDescr.hull['primaryArmor']
        turretArmor = self._itemDescr.turret['primaryArmor'] if self.__hasTurret() else hullArmor
        value = round((hullArmor[0] * coeffs['hullFront'] + hullArmor[1] * coeffs['hullSide'] + hullArmor[2] * coeffs['hullBack'] + turretArmor[0] * coeffs['turretFront'] + turretArmor[1] * coeffs['turretSide'] + turretArmor[2] * coeffs['turretBack']) * self.maxHealth * coeffs['normalization'] * self.__adjustmentCoefficient('armour'))
        return max(value, MIN_RELATIVE_VALUE)

    @property
    def relativeMobility(self):
        coeffs = self.__coefficients['mobility']
        value = round((self.chassisRotationSpeed * coeffs['chassisRotation'] + self.speedLimits[0] * coeffs['speedLimit'] + self.__getRealSpeedLimit() * coeffs['realSpeedLimit']) * coeffs['normalization'] * self.__adjustmentCoefficient('mobility'))
        return max(value, MIN_RELATIVE_VALUE)

    @property
    def relativeVisibility(self):
        coeffs = self.__coefficients['visibility']
        value = round((self.circularVisionRadius - MIN_VISION_RADIUS) / (MAX_VISION_RADIUS - MIN_VISION_RADIUS) * coeffs['normalization'] * self.__adjustmentCoefficient('visibility'))
        return max(value, MIN_RELATIVE_VALUE)

    @property
    def relativeCamouflage(self):
        coeffs = self.__coefficients['camouflage']
        value = round((self.invisibilityMovingFactor.current + self.invisibilityStillFactor.current + self.invisibilityStillFactor.atShot) / 3.0 * coeffs['normalization'] * self.__adjustmentCoefficient('camouflage'))
        return max(value, MIN_RELATIVE_VALUE)

    @property
    def turretYawLimits(self):
        if not self.__hasTurret():
            return None
        else:
            return self.__getGunYawLimits()
            return None

    @property
    def gunYawLimits(self):
        if self._itemDescr.isYawHullAimingAvailable:
            return (0, 0)
        elif self.__hasTurret():
            return None
        else:
            return self.__getGunYawLimits()
            return None

    @property
    def pitchLimits(self):
        limits = []
        for limit in self.__getPitchLimitsValues():
            limits.append(math.degrees(limit) * -1)

        return sorted(limits)

    @property
    def invisibilityStillFactor(self):
        _, still = self.__getInvisibilityValues()
        return still

    @property
    def invisibilityMovingFactor(self):
        moving, _ = self.__getInvisibilityValues()
        return moving

    @property
    def invisibilityFactorAtShot(self):
        return self._itemDescr.gun['invisibilityFactorAtShot']

    @property
    def clipFireRate(self):
        if self.__hasClipGun():
            gunParams = self._itemDescr.gun
            clipData = gunParams['clip']
            reloadTime = items_utils.getReloadTime(self._itemDescr, self.__factors)
            return (reloadTime, clipData[1], clipData[0])
        else:
            return None
            return None

    @property
    def switchOnTime(self):
        if self._itemDescr.hasSiegeMode:
            return self._itemDescr.type.siegeModeParams['switchOnTime']
        else:
            return None
            return None

    @property
    def switchOffTime(self):
        if self._itemDescr.hasSiegeMode:
            return self._itemDescr.type.siegeModeParams['switchOffTime']
        else:
            return None
            return None

    def getParamsDict(self, preload=False):
        conditionalParams = ('turretYawLimits', 'gunYawLimits', 'clipFireRate', 'gunRotationSpeed', 'turretRotationSpeed', 'turretArmor', 'reloadTimeSecs', 'switchOnTime', 'switchOffTime')
        return _ParamsDictProxy(self, preload, conditions=((conditionalParams, lambda v: v is not None),))

    def getAllDataDict(self):

        def getItemFullName(itemTypeIdx, itemDescr):
            return getTypeInfoByIndex(itemTypeIdx)['userString'] + ' ' + itemDescr['userString']

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
    def getBonuses(vehicle):
        result = map(lambda eq: (eq.name, eq.itemTypeName), [ item for item in vehicle.eqs if item is not None ])
        optDevs = map(lambda device: (device.name, device.itemTypeName), [ item for item in vehicle.optDevices if item is not None ])
        result.extend(optDevs)
        for _, tankman in vehicle.crew:
            if tankman is None:
                continue
            for skill in tankman.skills:
                if skill.isEnable and skill.isActive:
                    result.append((skill.name, 'skill'))

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
        return vehicle.getCustomizedDescriptor()

    def __adjustmentCoefficient(self, paramName):
        return self._itemDescr.type.clientAdjustmentFactors[paramName]

    def __getGunYawLimits(self):
        limits = self._itemDescr.gun['turretYawLimits']
        if limits is not None:
            limits = map(lambda limit: abs(math.degrees(limit)), limits[:])
        return limits

    def __hasTurret(self):
        vDescr = self._itemDescr
        return len(vDescr.hull['fakeTurrets']['lobby']) != len(vDescr.turrets)

    def __getRealSpeedLimit(self):
        enginePower = self.__getEnginePhysics()['smplEnginePower']
        rollingFriction = self.__getChassisPhysics()['grounds']['ground']['rollingFriction']
        return enginePower / self.vehicleWeight.current * METERS_PER_SECOND_TO_KILOMETERS_PER_HOUR * self.__factors['engine/power'] / 12.25 / rollingFriction

    def __getInvisibilityValues(self):
        camouflageFactor = self.__factors.get('camouflage', 1)
        moving, still = items_utils.getClientInvisibility(self._itemDescr, camouflageFactor, self.__factors)
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
            if self._itemDescr.gun['staticPitch'] is not None:
                return (hullAimingPitchMin, hullAimingPitchMax)
            else:
                pitchLimits = self._itemDescr.gun['pitchLimits']
                minPitch = pitchLimits['minPitch']
                maxPitch = pitchLimits['maxPitch']
                hullAimingPitchMin = wheelsCorrectionAngles['pitchMin']
                hullAimingPitchMax = wheelsCorrectionAngles['pitchMax']
                return (min([ key for _, key in minPitch ]) + hullAimingPitchMin, max([ key for _, key in maxPitch ]) + hullAimingPitchMax)
        else:
            return self._itemDescr.gun['pitchLimits']['absolute']
        return

    def __hasClipGun(self):
        return self._itemDescr.gun['clip'][0] != 1

    def __getChassisPhysics(self):
        chassisName = self._itemDescr.chassis.get('name', '')
        return self._itemDescr.type.xphysics['chassis'][chassisName]

    def __getEnginePhysics(self):
        engineName = self._itemDescr.engine.get('name', '')
        return self._itemDescr.type.xphysics['engines'][engineName]

    @staticmethod
    def __mapGrounds(itemsDict):
        return (itemsDict['firm'], itemsDict['medium'], itemsDict['soft'])

    def __currentShot(self):
        return self._itemDescr.gun['shots'][self._itemDescr.activeGunShotIndex]

    def __getTerrainResistanceFactors(self):
        return map(operator.mul, self.__factors['chassis/terrainResistance'], self._itemDescr.physics['rollingFrictionFactors'])


class GunParams(WeightedParam):

    @property
    def caliber(self):
        return self._itemDescr['shots'][0]['shell']['caliber']

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
        return self._getRawParams()[RELOAD_TIME_PROP_NAME]

    @property
    def avgPiercingPower(self):
        return self._getRawParams()[PIERCING_POWER_PROP_NAME]

    @property
    def avgDamageList(self):
        """
        Returns: list of average damage for all possible shells
        """
        return self._getRawParams()[DAMAGE_PROP_NAME]

    @property
    def dispertionRadius(self):
        return self._getRawParams()[DISPERSION_RADIUS_PROP_NAME]

    @property
    def aimingTime(self):
        return self._getRawParams()[AIMING_TIME_PROP_NAME]

    @property
    def compatibles(self):
        allVehiclesNames = set(g_paramsCache.getComponentVehiclesNames(self._itemDescr['compactDescr']))
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
        return self._itemDescr['shots'][0]['maxDistance']

    @property
    def turretsCompatibles(self):
        return self._getPrecachedInfo().turrets

    @property
    def clipVehiclesCD(self):
        return self._getPrecachedInfo().clipVehicles

    @property
    def avgDamagePerMinute(self):
        return round(self.reloadTime[0] * self.avgDamageList[0])

    def _extractRawParams(self):
        if self._vehicleDescr is not None:
            descriptors = getGunDescriptors(self._itemDescr, self._vehicleDescr)
            params = calcGunParams(self._itemDescr, descriptors)
        else:
            params = self._getPrecachedInfo().params
        return params

    def getParamsDict(self):
        return _ParamsDictProxy(self, conditions=((['maxShotDistance'], lambda v: v == _AUTOCANNON_SHOT_DISTANCE),))

    def getReloadingType(self, vehicleCD=None):
        return self._getPrecachedInfo().getReloadingType(vehicleCD)

    def getAllDataDict(self):
        result = super(GunParams, self).getAllDataDict()
        vehicleCD = self._vehicleDescr.type.compactDescr if self._vehicleDescr is not None else None
        reloadingType = self.getReloadingType(vehicleCD)
        result['extras'] = {'gunReloadingType': reloadingType,
         'excludedParams': _GUN_EXCLUDED_PARAMS.get(reloadingType, tuple())}
        return result

    def _getCompatible(self):
        vehiclesNamesList = self.compatibles
        clipVehicleNamesList = self.clipVehiclesCompatibles
        curVehicle = _getInstalledModuleVehicle(self._vehicleDescr, self._itemDescr)
        result = []
        if len(clipVehicleNamesList) != 0:
            if len(vehiclesNamesList):
                result.append(('uniChargedVehicles', _formatCompatibles(curVehicle, vehiclesNamesList)))
            result.append(('clipVehicles', _formatCompatibles(curVehicle, clipVehicleNamesList)))
        else:
            result.append(('vehicles', _formatCompatibles(curVehicle, vehiclesNamesList)))
        result.append(('shells', ', '.join(self.shellsCompatibles)))
        return tuple(result)


class ShellParams(CompatibleParams):

    @property
    def caliber(self):
        return self._itemDescr['caliber']

    @property
    def piercingPower(self):
        return self._getRawParams()[PIERCING_POWER_PROP_NAME]

    @property
    def damage(self):
        return self._getRawParams()[DAMAGE_PROP_NAME]

    @property
    def avgDamage(self):
        return self._itemDescr[DAMAGE_PROP_NAME][0]

    @property
    def avgPiercingPower(self):
        return _average(self.piercingPower)

    @property
    def explosionRadius(self):
        if self._itemDescr['kind'] == SHELL_TYPES.HIGH_EXPLOSIVE:
            return self._itemDescr['explosionRadius']
        else:
            return 0

    @property
    def piercingPowerTable(self):
        if self._itemDescr['kind'] in (SHELL_TYPES.ARMOR_PIERCING, SHELL_TYPES.ARMOR_PIERCING_CR):
            if self._vehicleDescr is None:
                return NO_DATA
            result = []
            shellDescriptor = getShellDescriptors(self._itemDescr, self._vehicleDescr)[0]
            piercingMax, piercingMin = shellDescriptor[PIERCING_POWER_PROP_NAME]
            lossPerMeter = (piercingMax - piercingMin) / 400.0
            maxDistance = self.maxShotDistance
            for distance in PIERCING_DISTANCES:
                if distance > maxDistance:
                    distance = int(maxDistance)
                currPiercing = piercingMax - lossPerMeter * (distance - 100.0)
                result.append((distance, currPiercing))

            return result
        else:
            return
            return

    @property
    def maxShotDistance(self):
        if self._itemDescr['kind'] in _SHELL_KINDS:
            if self._vehicleDescr is not None:
                return getShellDescriptors(self._itemDescr, self._vehicleDescr)[0]['maxDistance']
        return

    @property
    def isBasic(self):
        return self._vehicleDescr is not None and getBasicShell(self._vehicleDescr)['compactDescr'] == self._itemDescr['compactDescr']

    @property
    def compatibles(self):
        return self._getPrecachedInfo().guns

    def getParamsDict(self):
        return _ParamsDictProxy(self, conditions=((['maxShotDistance'], lambda v: v == _AUTOCANNON_SHOT_DISTANCE),))

    def _extractRawParams(self):
        if self._vehicleDescr is not None:
            descriptors = getShellDescriptors(self._itemDescr, self._vehicleDescr)
            params = calcShellParams(descriptors)
        else:
            params = self._getPrecachedInfo().params
        return params

    def _getCompatible(self):
        return (('shellGuns', ', '.join(self.compatibles)),)


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
    def nations(self):
        return self._getPrecachedInfo().nations

    def getParamsDict(self):
        params = {'nations': self.nations}
        params.update(self._getPrecachedInfo().params)
        return params


class _ParamsDictProxy(dict):

    def __init__(self, calculator, preload=False, conditions=None):
        """
        Args:
            calculator: object which is used for calculation of returned params
            preload: boolean, if true - all possible values are calculated and loaded
                     immediately during initialization
            conditions: (([key1, key2..], condition), ...) custom conditions for specialized keys
                        for the same key can be added different conditions
                        each condition is presented by function which takes value corresponding to specified key
                        and returns boolean.
                        If any of condition functions returns False __getitem__ will raise KeyError
        """
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
        if k in self:
            return self[k]
        else:
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
        return self.__cachedParams.get(item)

    def __iter__(self):
        self.__loadAllValues()
        for k in self.__cachedParams.keys():
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
        """
        scans calculator object and loads all its properties, which fits conditions.
        Is necessary for proper work of __iter__ an __len__
        """
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
