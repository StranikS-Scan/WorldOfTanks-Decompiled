# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/items_parameters/params.py
import collections
import copy
import math
import operator
from collections import namedtuple
from operator import itemgetter
from constants import SHELL_TYPES
from gui.shared.items_parameters import calcGunParams, calcShellParams, getShotsPerMinute, getGunDescriptors, getShellDescriptors, getOptionalDeviceWeight, NO_DATA
from gui.shared.items_parameters.comparator import BACKWARD_QUALITY_PARAMS
from gui.shared.items_parameters.params_cache import g_paramsCache
from gui.shared.items_parameters import functions
from gui.shared.utils import DAMAGE_PROP_NAME, PIERCING_POWER_PROP_NAME, AIMING_TIME_PROP_NAME, DISPERSION_RADIUS_PROP_NAME, SHELLS_PROP_NAME, GUN_NORMAL, SHELLS_COUNT_PROP_NAME, RELOAD_MAGAZINE_TIME_PROP_NAME, SHELL_RELOADING_TIME_PROP_NAME, GUN_CLIP, RELOAD_TIME_PROP_NAME, GUN_CAN_BE_CLIP
from helpers import time_utils
from items import getTypeOfCompactDescr, vehicles, getTypeInfoByIndex, ITEM_TYPES
from items.utils import getRadioDistance, getCircularVisionRadius, getTurretRotationSpeed, getChassisRotationSpeed, getReloadTime, getCrewAffectedFactors, getGunAimingTime, getClientInvisibility, getClientShotDispersion
from gui.shared.items_parameters import formatters
MAX_VISION_RADIUS = 500
MIN_VISION_RADIUS = 150
PIERCING_DISTANCES = (100, 250, 500)
ONE_HUNDRED_PERCENTS = 100
MIN_RELATIVE_VALUE = 1
_Weight = namedtuple('_Weight', 'current, max')
_Invisibility = namedtuple('_Invisibility', 'current, atShot')
MODULES = {ITEM_TYPES.vehicleRadio: lambda vehicleDescr: vehicleDescr.radio,
 ITEM_TYPES.vehicleEngine: lambda vehicleDescr: vehicleDescr.engine,
 ITEM_TYPES.vehicleChassis: lambda vehicleDescr: vehicleDescr.chassis,
 ITEM_TYPES.vehicleTurret: lambda vehicleDescr: vehicleDescr.turret,
 ITEM_TYPES.vehicleGun: lambda vehicleDescr: vehicleDescr.gun}
_METERS_PER_SECOND_TO_KILOMETERS_PER_HOUR = 3.6
_GUN_EXCLUDED_PARAMS = {GUN_NORMAL: (SHELLS_COUNT_PROP_NAME, RELOAD_MAGAZINE_TIME_PROP_NAME, SHELL_RELOADING_TIME_PROP_NAME),
 GUN_CLIP: (RELOAD_TIME_PROP_NAME,),
 GUN_CAN_BE_CLIP: (SHELLS_COUNT_PROP_NAME, RELOAD_MAGAZINE_TIME_PROP_NAME, SHELL_RELOADING_TIME_PROP_NAME)}
_UI_TO_SERVER_MAP = {'turret/rotationSpeed': ('turretRotationSpeed', 'relativePower'),
 'circularVisionRadius': ('circularVisionRadius', 'relativeVisibility'),
 'radio/distance': ('radioDistance', 'relativeVisibility'),
 'gun/rotationSpeed': ('gunRotationSpeed', 'relativePower'),
 'gun/reloadTime': ('reloadTime',
                    'damageAvgPerMinute',
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
    if any(map(itemgetter(0), vehicle.descriptor.camouflages)):
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


class _ParameterBase(object):

    def __init__(self, itemDescr, vehicleDescr=None):
        self._itemDescr = itemDescr
        self._vehicleDescr = vehicleDescr
        self.__preCached = None
        self.__avgParams = None
        return

    def getParamsDict(self):
        return {}

    @property
    def precachedParams(self):
        if self.__preCached is None:
            self.__preCached = g_paramsCache.getPrecachedParameters(self._itemDescr['compactDescr'])
        return self.__preCached

    @property
    def avgParams(self):
        if self.__avgParams is None:
            self.__avgParams = self.getAvgParams()
        return self.__avgParams

    def getAvgParams(self):
        return self.precachedParams.avgParams

    def getAllDataDict(self):
        return {'parameters': self.getParamsDict(),
         'compatible': self._getCompatible()}

    def _getCompatible(self):
        return tuple()


class CompatibleParams(_ParameterBase):

    @property
    def compatibles(self):
        return g_paramsCache.getComponentVehiclesNames(self._itemDescr['compactDescr'])

    def _getCompatible(self):
        curVehicle = _getInstalledModuleVehicle(self._vehicleDescr, self._itemDescr)
        return (('vehicles', formatters.formatCompatibles(curVehicle, self.compatibles)),)


class WeightedParam(CompatibleParams):

    @property
    def weight(self):
        return self._itemDescr['weight']


class RadioParams(WeightedParam):

    @property
    def radioDistance(self):
        return int(round(self._itemDescr['distance']))

    def getParamsDict(self):
        return {'radioDistance': self.radioDistance,
         'weight': self.weight}


class EngineParams(WeightedParam):

    @property
    def enginePower(self):
        return int(round(self._itemDescr['power'] / vehicles.HP_TO_WATTS, 0))

    @property
    def fireStartingChance(self):
        return int(round(self._itemDescr['fireStartingChance'] * ONE_HUNDRED_PERCENTS))

    def getParamsDict(self):
        return {'enginePower': self.enginePower,
         'fireStartingChance': self.fireStartingChance,
         'weight': self.weight}


class ChassisParams(WeightedParam):

    @property
    def maxLoad(self):
        return self._itemDescr['maxLoad'] / 1000

    @property
    def rotationSpeed(self):
        return int(round(math.degrees(self._itemDescr['rotationSpeed'])))

    def getParamsDict(self):
        return {'maxLoad': self.maxLoad,
         'rotationSpeed': self.rotationSpeed,
         'weight': self.weight}


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

    def getParamsDict(self):
        return {'armor': self.armor,
         'rotationSpeed': self.rotationSpeed,
         'circularVisionRadius': self.circularVisionRadius,
         'weight': self.weight}

    def _getCompatible(self):
        if self._vehicleDescr is not None:
            curGun = self._vehicleDescr.gun['userString']
        else:
            curGun = None
        compatibleVehicles = list(super(TurretParams, self)._getCompatible())
        compatibleVehicles.append(('guns', formatters.formatCompatibles(curGun, self.gunCompatibles)))
        return tuple(compatibleVehicles)


class VehicleParams(_ParameterBase):

    def __init__(self, vehicle):
        super(VehicleParams, self).__init__(vehicle.getCustomizedDescriptor())
        self.__factors = functions.getVehicleFactors(vehicle)
        self.__coefficients = g_paramsCache.getSimplifiedCoefficients()
        self.__compatibleBonuses = g_paramsCache.getCompatibleBonuses(vehicle.descriptor)
        self.__penalties = self.__getPenalties(vehicle)
        self.__bonuses = self.__getBonuses(vehicle)

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
        return map(lambda speed: round(speed * _METERS_PER_SECOND_TO_KILOMETERS_PER_HOUR, 2), limits)

    @property
    def chassisRotationSpeed(self):
        allTrfs = self.__factors['chassis/terrainResistance']
        avgTrf = sum(allTrfs) / len(allTrfs)
        return math.degrees(getChassisRotationSpeed(self._itemDescr, self.__factors)) / avgTrf

    @property
    def hullArmor(self):
        return self._itemDescr.hull['primaryArmor']

    @property
    def damage(self):
        shotShell = self._itemDescr.shot['shell']
        damage = shotShell[DAMAGE_PROP_NAME][0]
        damageRandomization = shotShell['damageRandomization']
        return (round(damage - damage * damageRandomization), round(damage + damage * damageRandomization))

    @property
    def damageAvg(self):
        return self._itemDescr.shot['shell'][DAMAGE_PROP_NAME][0]

    @property
    def damageAvgPerMinute(self):
        return round(self.reloadTime * self._itemDescr.shot['shell'][DAMAGE_PROP_NAME][0])

    @property
    def piercingPower(self):
        shot = self._itemDescr.shot
        piercingPower = shot[PIERCING_POWER_PROP_NAME][0]
        piercingPowerRandomization = shot['shell']['piercingPowerRandomization']
        return (round(piercingPower - piercingPower * piercingPowerRandomization), round(piercingPower + piercingPower * piercingPowerRandomization))

    @property
    def reloadTime(self):
        reloadTime = getReloadTime(self._itemDescr, self.__factors)
        return getShotsPerMinute(self._itemDescr.gun, reloadTime)

    @property
    def turretRotationSpeed(self):
        return round(math.degrees(getTurretRotationSpeed(self._itemDescr, self.__factors)), 2) if self.__hasTurret() else None

    @property
    def gunRotationSpeed(self):
        return round(math.degrees(getTurretRotationSpeed(self._itemDescr, self.__factors)), 2) if not self.__hasTurret() else None

    @property
    def circularVisionRadius(self):
        return round(getCircularVisionRadius(self._itemDescr, self.__factors))

    @property
    def radioDistance(self):
        return round(getRadioDistance(self._itemDescr, self.__factors))

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
        return getGunAimingTime(self._itemDescr, self.__factors)

    @property
    def shotDispersionAngle(self):
        shotDispersion = getClientShotDispersion(self._itemDescr, self.__factors['shotDispersion'][0])
        return round(shotDispersion * 100, 2)

    @property
    def reloadTimeSecs(self):
        if self.__hasClipGun():
            return None
        else:
            return round(time_utils.ONE_MINUTE / self.reloadTime, 1)
            return None

    @property
    def relativePower(self):
        coeffs = self.__coefficients['power']
        penetration = self._itemDescr.shot[PIERCING_POWER_PROP_NAME][0]
        rotationSpeed = self.turretRotationSpeed or self.gunRotationSpeed
        turretCoefficient = 1 if self.__hasTurret() else coeffs['turretCoefficient']
        spgCorrection = 6 if 'SPG' in self._itemDescr.type.tags else 1
        gunCorrection = self.__adjustmentCoefficient('guns').get(self._itemDescr.gun['name'], {})
        gunCorrection = gunCorrection.get('caliberCorrection', 1)
        value = round(self.damageAvgPerMinute * penetration / self.shotDispersionAngle * (coeffs['rotationIntercept'] + coeffs['rotationSlope'] * rotationSpeed) * turretCoefficient * coeffs['normalization'] * self.__adjustmentCoefficient('power') * spgCorrection * gunCorrection)
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
        if self.__hasTurret():
            return None
        else:
            return self.__getGunYawLimits()
            return None

    @property
    def pitchLimits(self):
        limits = []
        for limit in self._itemDescr.gun['pitchLimits']['absolute']:
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
            reloadTime = getReloadTime(self._itemDescr, self.__factors)
            return (reloadTime, clipData[1], clipData[0])
        else:
            return None
            return None

    def getParamsDict(self):
        result = {'maxHealth': self.maxHealth,
         'vehicleWeight': self.vehicleWeight,
         'enginePower': self.enginePower,
         'enginePowerPerTon': self.enginePowerPerTon,
         'speedLimits': self.speedLimits,
         'chassisRotationSpeed': self.chassisRotationSpeed,
         'hullArmor': self.hullArmor,
         DAMAGE_PROP_NAME: self.damage,
         'damageAvg': self.damageAvg,
         'damageAvgPerMinute': self.damageAvgPerMinute,
         PIERCING_POWER_PROP_NAME: self.piercingPower,
         RELOAD_TIME_PROP_NAME: self.reloadTime,
         'circularVisionRadius': self.circularVisionRadius,
         'radioDistance': self.radioDistance,
         'explosionRadius': self.explosionRadius,
         AIMING_TIME_PROP_NAME: self.aimingTime,
         'shotDispersionAngle': self.shotDispersionAngle,
         'relativePower': self.relativePower,
         'relativeArmor': self.relativeArmor,
         'relativeMobility': self.relativeMobility,
         'relativeVisibility': self.relativeVisibility,
         'relativeCamouflage': self.relativeCamouflage,
         'pitchLimits': self.pitchLimits,
         'invisibilityStillFactor': self.invisibilityStillFactor,
         'invisibilityMovingFactor': self.invisibilityMovingFactor}
        conditionalParams = ('turretYawLimits', 'gunYawLimits', 'clipFireRate', 'gunRotationSpeed', 'turretRotationSpeed', 'turretArmor', 'reloadTimeSecs')
        result.update(self.__packConditionalParams(conditionalParams))
        return result

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

    def getBonuses(self):
        return self.__bonuses

    def getPenalties(self):
        return self.__penalties

    def __getBonuses(self, vehicle):
        result = map(lambda eq: (eq.name, eq.itemTypeName), [ item for item in vehicle.eqs if item is not None ])
        optDevs = map(lambda device: (device.name, device.itemTypeName), [ item for item in vehicle.optDevices if item is not None ])
        result.extend(optDevs)
        for _, tankman in vehicle.crew:
            if tankman is None:
                continue
            if tankman.roleLevel >= ONE_HUNDRED_PERCENTS:
                for role in tankman.combinedRoles:
                    result.append((role, 'role'))

            for skill in tankman.skills:
                if skill.isEnable and skill.isActive:
                    result.append((skill.name, 'skill'))

        result.extend(_processExtraBonuses(vehicle))
        return set(result)

    def __getPenalties(self, vehicle):
        crew, emptySlots, otherVehicleSlots = functions.extractCrewDescrs(vehicle, replaceNone=False)
        crewFactors = getCrewAffectedFactors(vehicle.descriptor, crew)
        result = {}
        currParams = self.getParamsDict()
        roles = vehicle.descriptor.type.crewRoles
        for slotId, factors in crewFactors.iteritems():
            for factor, factorValue in factors.iteritems():
                if factor in _UI_TO_SERVER_MAP:
                    oldFactor = copy.copy(self.__factors[factor])
                    self.__factors[factor] = _universalSum(oldFactor, factorValue)
                    params = _UI_TO_SERVER_MAP[factor]
                    for paramName in params:
                        paramPenalties = result.setdefault(paramName, {})
                        if slotId not in emptySlots:
                            newValue = getattr(self, paramName)
                            if newValue is None:
                                continue
                            if isinstance(newValue, collections.Iterable):
                                delta = sum(currParams[paramName]) - sum(newValue)
                            else:
                                delta = currParams[paramName] - newValue
                            if delta > 0 and paramName in BACKWARD_QUALITY_PARAMS or delta < 0 and paramName not in BACKWARD_QUALITY_PARAMS:
                                paramPenalties[slotId] = delta
                        paramPenalties[slotId] = 0

                    self.__factors[factor] = oldFactor

        for paramName, penalties in result.items():
            result[paramName] = [ (roles[slotId][0], value, slotId in otherVehicleSlots) for slotId, value in penalties.iteritems() ]

        return result

    def __adjustmentCoefficient(self, paramName):
        return self._itemDescr.type.clientAdjustmentFactors[paramName]

    def __packConditionalParams(self, params):
        result = {}
        for paramName in params:
            paramValue = getattr(self, paramName)
            if paramValue is not None:
                result[paramName] = paramValue

        return result

    def __getGunYawLimits(self):
        limits = self._itemDescr.gun['turretYawLimits']
        if limits is not None:
            limits = map(lambda limit: abs(math.degrees(limit)), limits[:])
        return limits

    def __hasTurret(self):
        vDescr = self._itemDescr
        return len(vDescr.hull['fakeTurrets']['lobby']) != len(vDescr.turrets)

    def __getRealSpeedLimit(self):
        engineName = self._itemDescr.engine.get('name', '')
        chassisName = self._itemDescr.chassis.get('name', '')
        enginePower = self.__adjustmentCoefficient('engines')[engineName]['smplEnginePower'] * 4
        rollingFriction = self.__adjustmentCoefficient('chassis')[chassisName]['rollingFriction']
        return enginePower / self.vehicleWeight.current * _METERS_PER_SECOND_TO_KILOMETERS_PER_HOUR * self.__factors['engine/power'] / 12.25 / rollingFriction

    def __getInvisibilityValues(self):
        camouflageFactor = self.__factors.get('camouflage', 1)
        moving, still = getClientInvisibility(self._itemDescr, camouflageFactor, self.__factors)
        moving *= ONE_HUNDRED_PERCENTS
        still *= ONE_HUNDRED_PERCENTS
        movingAtShot = moving * self.invisibilityFactorAtShot
        stillAtShot = still * self.invisibilityFactorAtShot
        return (_Invisibility(moving, movingAtShot), _Invisibility(still, stillAtShot))

    def __hasClipGun(self):
        return self._itemDescr.gun['clip'][0] != 1


class GunParams(WeightedParam):

    @property
    def caliber(self):
        return self._itemDescr['shots'][0]['shell']['caliber']

    @property
    def shellsCount(self):
        return self.avgParams[SHELLS_COUNT_PROP_NAME]

    @property
    def shellReloadingTime(self):
        return self.avgParams[SHELL_RELOADING_TIME_PROP_NAME]

    @property
    def reloadMagazineTime(self):
        return self.avgParams[RELOAD_MAGAZINE_TIME_PROP_NAME]

    @property
    def reloadTime(self):
        return self.avgParams[RELOAD_TIME_PROP_NAME]

    @property
    def avgPiercingPower(self):
        return self.avgParams[PIERCING_POWER_PROP_NAME]

    @property
    def avgDamage(self):
        return self.avgParams[DAMAGE_PROP_NAME]

    @property
    def dispertionRadius(self):
        return self.avgParams[DISPERSION_RADIUS_PROP_NAME]

    @property
    def aimingTime(self):
        return self.avgParams[AIMING_TIME_PROP_NAME]

    @property
    def compatibles(self):
        allVehiclesNames = set(g_paramsCache.getComponentVehiclesNames(self._itemDescr['compactDescr']))
        clipVehiclesNames = set(self.precachedParams.clipVehiclesNames)
        return allVehiclesNames.difference(clipVehiclesNames)

    @property
    def clipVehiclesCompatibles(self):
        return set(self.precachedParams.clipVehiclesNames)

    @property
    def shellsCompatibles(self):
        return self.avgParams.get(SHELLS_PROP_NAME, tuple())

    @property
    def maxShotDistance(self):
        return self._itemDescr['shots'][0]['maxDistance']

    @property
    def turretsCompatibles(self):
        return self.precachedParams.turrets

    @property
    def clipVehiclesCD(self):
        return self.precachedParams.clipVehicles

    def getAvgParams(self):
        if self._vehicleDescr is not None:
            descriptors = getGunDescriptors(self._itemDescr, self._vehicleDescr)
            avgParams = calcGunParams(self._itemDescr, descriptors)
        else:
            avgParams = self.precachedParams.avgParams
        return avgParams

    def getParamsDict(self):
        result = {'caliber': self.caliber,
         'shellsCount': self.shellsCount,
         'shellReloadingTime': self.shellReloadingTime,
         'reloadMagazineTime': self.reloadMagazineTime,
         'reloadTime': self.reloadTime,
         'avgPiercingPower': self.avgPiercingPower,
         'avgDamage': self.avgDamage,
         'dispertionRadius': self.dispertionRadius,
         'aimingTime': self.aimingTime,
         'weight': self.weight}
        if self.maxShotDistance == _AUTOCANNON_SHOT_DISTANCE:
            result.update({'maxShotDistance': self.maxShotDistance})
        return result

    def getReloadingType(self, vehicleCD=None):
        return self.precachedParams.getReloadingType(vehicleCD)

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
                result.append(('uniChargedVehicles', formatters.formatCompatibles(curVehicle, vehiclesNamesList)))
            result.append(('clipVehicles', formatters.formatCompatibles(curVehicle, clipVehicleNamesList)))
        else:
            result.append(('vehicles', formatters.formatCompatibles(curVehicle, vehiclesNamesList)))
        result.append(('shells', ', '.join(self.shellsCompatibles)))
        return tuple(result)


class ShellParams(CompatibleParams):

    def getAvgParams(self):
        if self._vehicleDescr is not None:
            descriptors = getShellDescriptors(self._itemDescr, self._vehicleDescr)
            avgParams = calcShellParams(descriptors)
        else:
            avgParams = self.precachedParams.avgParams
        return avgParams

    @property
    def caliber(self):
        return self._itemDescr['caliber']

    @property
    def piercingPower(self):
        return self.avgParams[PIERCING_POWER_PROP_NAME]

    @property
    def damage(self):
        return self.avgParams[DAMAGE_PROP_NAME]

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
            randFactor = self._itemDescr['piercingPowerRandomization']
            lossPerMeter = (piercingMax - piercingMin) / 400.0
            maxDistance = self.maxShotDistance
            for distance in PIERCING_DISTANCES:
                if distance > maxDistance:
                    distance = int(maxDistance)
                currPiercing = piercingMax - lossPerMeter * (distance - 100.0)
                result.append((distance, (currPiercing - randFactor * currPiercing, currPiercing + randFactor * currPiercing)))

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
    def compatibles(self):
        return self.precachedParams.guns

    def getParamsDict(self):
        result = {'caliber': self.caliber,
         'piercingPower': self.piercingPower,
         'damage': self.damage,
         'explosionRadius': self.explosionRadius,
         'piercingPowerTable': self.piercingPowerTable}
        maxShotDistance = self.maxShotDistance
        if maxShotDistance == _AUTOCANNON_SHOT_DISTANCE:
            result.update({'maxShotDistance': maxShotDistance})
        return result

    def _getCompatible(self):
        return (('shellGuns', ', '.join(self.compatibles)),)


class OptionalDeviceParams(WeightedParam):

    @property
    def weight(self):
        return _Weight(*getOptionalDeviceWeight(self._itemDescr, self._vehicleDescr)) if self._vehicleDescr is not None else _Weight(*self.precachedParams.weight)

    @property
    def nations(self):
        return self.precachedParams.nations

    def getParamsDict(self):
        return {'weight': self.weight,
         'nations': self.nations}

    def _getCompatible(self):
        return tuple()


class EquipmentParams(_ParameterBase):

    @property
    def nations(self):
        return self.precachedParams.nations

    def getParamsDict(self):
        params = {'nations': self.nations}
        params.update(self.avgParams)
        return params
