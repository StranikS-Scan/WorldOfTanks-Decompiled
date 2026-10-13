# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/items_parameters/params_cache.py
from __future__ import absolute_import
import itertools
import math
import sys
import typing
from collections import namedtuple, defaultdict
from functools import partial
from future.utils import iteritems, itervalues, viewitems
import nations
import persistent_data_cache_common as pdc
from constants import BonusTypes
from gui.shared.items_parameters import calcGunParams, calcShellParams, getEquipmentParameters
from gui.shared.items_parameters import xml_reader
from gui.shared.utils.decorators import debugTime
from items import vehicles, ITEM_TYPES, EQUIPMENT_TYPES
from items.vehicle_mechanics_types import VehicleMechanicKeys
from items.vehicles import getVehicleType
from gui.shared.utils import GUN_NORMAL
from gui.shared.gui_items.vehicle_mechanics.mechanic_detectors import ENGINE_MECHANICS_BITS, ENGINE_MECHANIC_DETECTORS, CHASSIS_MECHANIC_DETECTORS, GUN_MECHANICS_TO_RELOAD_TYPES, GUN_MECHANIC_DETECTORS, hasChassisMechanicBit
from post_progression_common import ACTION_TYPES
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from items.vehicle_mechanics_types import VehicleMechanicKey
    from gui.shared.gui_items.vehicle_mechanics.mechanic_detectors import ChassisTypes
PrecachedShell = namedtuple('PrecachedShell', 'guns params')
PrecachedEquipment = namedtuple('PrecachedEquipment', 'nations params')
PrecachedOptionalDevice = namedtuple('PrecachedOptionalDevice', 'weight nations')

class PrecachedGun(namedtuple('PrecachedGun', ('mechanics', 'params', 'turretsByVehicles'))):

    @property
    def clipVehicles(self):
        return self.mechanics.get(VehicleMechanicKeys.MAGAZINE_GUN)

    @property
    def clipVehiclesNames(self):
        vehSet = self.clipVehicles
        if vehSet:
            return [ getVehicleType(cd).userString for cd in vehSet ]
        return []

    def hasMechanicForVehicle(self, mechanic, vehicleCD):
        vehSet = self.mechanics.get(mechanic)
        return vehSet is not None and vehicleCD in vehSet

    def hasMechanic(self, mechanic):
        return mechanic in self.mechanics

    def getReloadingType(self, vehicleCD=None):
        for mechanic, (canBeType, activeType) in iteritems(GUN_MECHANICS_TO_RELOAD_TYPES):
            if vehicleCD is not None:
                if self.hasMechanicForVehicle(mechanic, vehicleCD):
                    return activeType
            if self.hasMechanic(mechanic):
                return canBeType

        return GUN_NORMAL

    def getTurretsForVehicle(self, vehicleCD):
        return self.turretsByVehicles.get(vehicleCD, ())


def _getVehicleSuitablesByType(vehicleType, itemTypeId, turretPID=0):
    result = []
    if itemTypeId == ITEM_TYPES.vehicleChassis:
        result = vehicleType.chassis
    elif itemTypeId == ITEM_TYPES.vehicleEngine:
        result = vehicleType.engines
    elif itemTypeId == ITEM_TYPES.vehicleRadio:
        result = vehicleType.radios
    elif itemTypeId == ITEM_TYPES.vehicleFuelTank:
        result = vehicleType.fuelTanks
    elif itemTypeId == ITEM_TYPES.vehicleTurret:
        result = vehicleType.turrets[turretPID]
    elif itemTypeId == ITEM_TYPES.vehicleGun:
        for turret in vehicleType.turrets[turretPID]:
            for gun in turret.guns:
                result.append(gun)

    elif itemTypeId == ITEM_TYPES.shell:
        for turret in vehicleType.turrets[turretPID]:
            for gun in turret.guns:
                for shot in gun.shots:
                    result.append(shot.shell)

    else:
        raise SoftException('Type ID {} is not supported'.format(itemTypeId))
    return result


class VehicleDescrsCache(object):
    __slots__ = ('_local',)

    def __init__(self):
        super(VehicleDescrsCache, self).__init__()
        self._local = {}

    def clear(self):
        self._local.clear()

    def load(self):
        vehilesList = vehicles.g_list.getList
        for nationID in itervalues(nations.INDICES):
            self._local[nationID] = [ vehicles.VehicleDescr(typeID=(nationID, cd)) for cd in vehilesList(nationID) ]

    def generator(self, nationID=None):
        if nationID is None:
            nationIDs = itervalues(nations.INDICES)
        else:
            nationIDs = (nationID,)
        for nextID in nationIDs:
            if nextID not in self._local:
                continue
            for descr in self._local[nextID]:
                yield descr

        return


ParamsCacheData = namedtuple('ParamsCacheData', 'cache, wheeledChassisParams, noCamouflageVehicles, vehiclesCache')

def _readCache(vehiclesCache):
    if vehiclesCache is None:
        vehiclesCache = VehicleDescrsCache()
    data = ParamsCacheData({}, {}, [], vehiclesCache)
    vehiclesCache.load()
    _precacheOptionalDevices(data)
    _precacheGuns(data)
    _precacheShells(data)
    _precacheEquipments(data)
    _precacheChassis(data)
    _getVehiclesWithoutCamouflage(data)
    _precacheEngines(data)
    vehiclesCache.clear()
    del vehiclesCache
    coefficients, bonuses = xml_reader.read()
    return (coefficients,
     bonuses,
     data.cache,
     data.wheeledChassisParams,
     tuple(data.noCamouflageVehicles))


def _precacheEquipments(data):
    data.cache.setdefault(nations.NONE_INDEX, {})[ITEM_TYPES.equipment] = {}
    for eqpDescr in itervalues(vehicles.g_cache.equipments()):
        equipmentNations = set()
        for vDescr in data.vehiclesCache.generator():
            if not eqpDescr.checkCompatibilityWithVehicle(vDescr)[0]:
                continue
            nation, _ = vDescr.type.id
            equipmentNations.add(nation)

        data.cache[nations.NONE_INDEX][ITEM_TYPES.equipment][eqpDescr.compactDescr] = PrecachedEquipment(nations=equipmentNations, params=getEquipmentParameters(eqpDescr))


def _precacheOptionalDevices(data):
    data.cache.setdefault(nations.NONE_INDEX, {})[ITEM_TYPES.optionalDevice] = {}
    for deviceDescr in itervalues(vehicles.g_cache.optionalDevices()):
        wmin, wmax = sys.maxsize, -1
        deviceNations = set()
        for vDescr in data.vehiclesCache.generator():
            if not deviceDescr.checkCompatibilityWithVehicle(vDescr)[0]:
                continue
            nation, _ = vDescr.type.id
            deviceNations.add(nation)
            mods = deviceDescr.weightOnVehicle(vDescr)
            weightOnVehicle = math.ceil(vDescr.physics['weight'] * mods[0] + mods[1])
            wmin, wmax = min(wmin, weightOnVehicle), max(wmax, weightOnVehicle)

        data.cache[nations.NONE_INDEX][ITEM_TYPES.optionalDevice][deviceDescr.compactDescr] = PrecachedOptionalDevice(weight=(wmin, wmax), nations=deviceNations)


def _precacheGuns(data):
    descriptors = []
    curVehicleTurretsCDs = []
    getter = vehicles.g_cache.guns
    for nationIdx in itervalues(nations.INDICES):
        data.cache.setdefault(nationIdx, {})[ITEM_TYPES.vehicleGun] = {}
        for g in itervalues(getter(nationIdx)):
            del descriptors[:]
            turretsIntCDs = {}
            vehiclesByMechanics = defaultdict(set)
            for vDescr in data.vehiclesCache.generator(nationIdx):
                del curVehicleTurretsCDs[:]
                vehCD = vDescr.type.compactDescr
                for vTurrets in vDescr.type.turrets:
                    for turret in vTurrets:
                        for gun in turret.guns:
                            if gun.id[1] == g.id[1]:
                                descriptors.append(gun)
                                if len(vDescr.hull.fakeTurrets['lobby']) != len(vDescr.turrets):
                                    curVehicleTurretsCDs.append(turret.compactDescr)
                                for mechanic, detector in viewitems(GUN_MECHANIC_DETECTORS):
                                    if detector(gun, vDescr):
                                        vehiclesByMechanics[mechanic].add(vehCD)

                if curVehicleTurretsCDs:
                    turretsIntCDs[vDescr.type.compactDescr] = tuple(curVehicleTurretsCDs)

            data.cache[nationIdx][ITEM_TYPES.vehicleGun][g.compactDescr] = PrecachedGun(mechanics={m:frozenset(v) for m, v in viewitems(vehiclesByMechanics)}, params=calcGunParams(g, descriptors), turretsByVehicles=turretsIntCDs)


def _precacheShells(data):
    descriptors = []
    gunsCDs = []
    gunsGetter = vehicles.g_cache.guns
    shellsGetter = vehicles.g_cache.shells
    for nationIdx in itervalues(nations.INDICES):
        data.cache.setdefault(nationIdx, {})[ITEM_TYPES.shell] = {}
        for sDescr in itervalues(shellsGetter(nationIdx)):
            del descriptors[:]
            del gunsCDs[:]
            for gDescr in itervalues(gunsGetter(nationIdx)):
                for shot in gDescr.shots:
                    if shot.shell.id[1] == sDescr.id[1]:
                        if gDescr.compactDescr not in gunsCDs:
                            gunsCDs.append(gDescr.compactDescr)
                            descriptors.append(shot)

            data.cache[nationIdx][ITEM_TYPES.shell][sDescr.compactDescr] = PrecachedShell(guns=tuple(gunsCDs), params=calcShellParams(descriptors))


def _precacheChassis(data):
    getter = vehicles.g_cache.chassis
    chassisItemType = ITEM_TYPES.vehicleChassis
    processedItems = set()
    for nationIdx in itervalues(nations.INDICES):
        data.cache.setdefault(nationIdx, {})[chassisItemType] = {}
        cachedChassisByNation = data.cache[nationIdx][chassisItemType]
        for vDescr in data.vehiclesCache.generator(nationIdx):
            for vChs in vDescr.type.chassis:
                mask = 0
                for hasMechanic, detector in itervalues(CHASSIS_MECHANIC_DETECTORS):
                    if detector(vChs, vDescr):
                        mask |= hasMechanic

                chassisCD = vChs.compactDescr
                cachedChassisByNation[chassisCD] = cachedChassisByNation.get(chassisCD, 0) | mask
                if vDescr.isWheeledVehicle:
                    chassisPhysics = vDescr.type.xphysics['chassis'][vChs.name]
                    data.wheeledChassisParams[chassisCD] = chassisPhysics['axleSteeringLockAngles']
                processedItems.add(chassisCD)

        for chs in itervalues(getter(nationIdx)):
            if chs.compactDescr not in processedItems:
                cachedChassisByNation[chs.compactDescr] = 0


def _precacheEngines(data):
    getter = vehicles.g_cache.engines
    engineItemType = ITEM_TYPES.vehicleEngine
    processedItems = set()
    for nationIdx in itervalues(nations.INDICES):
        data.cache.setdefault(nationIdx, {})[engineItemType] = {}
        cachedEngineByNation = data.cache[nationIdx][engineItemType]
        for vDescr in data.vehiclesCache.generator(nationIdx):
            mask = 0
            for hasMechanic, detector in itervalues(ENGINE_MECHANIC_DETECTORS):
                if detector(vDescr):
                    mask |= hasMechanic

            for vEng in vDescr.type.engines:
                engineCD = vEng.compactDescr
                cachedEngineByNation[engineCD] = cachedEngineByNation.get(engineCD, 0) | mask
                processedItems.add(engineCD)

        for eng in itervalues(getter(nationIdx)):
            if eng.compactDescr not in processedItems:
                cachedEngineByNation[eng.compactDescr] = 0


def _getVehiclesWithoutCamouflage(data):
    deniedVehicles = {}
    allowedVehicles = set()
    customization = vehicles.g_cache.customization
    for nationID in itervalues(nations.INDICES):
        deniedVehicles.clear()
        allowedVehicles.clear()
        restrictedCamouflages = 0
        camouflages = customization(nationID)['camouflages']
        totalCount = len(camouflages)
        for camouflage in itervalues(camouflages):
            currentAllowed = camouflage.get('allow', ())
            for vehCD in camouflage.get('deny', ()):
                deniedVehicles[vehCD] = deniedVehicles.get(vehCD, 0) + 1

            allowedVehicles.update(currentAllowed)
            if currentAllowed:
                restrictedCamouflages += 1

        for vehCD, count in iteritems(deniedVehicles):
            if vehCD not in allowedVehicles and count + restrictedCamouflages >= totalCount:
                data.noCamouflageVehicles.append(vehCD)


class _ParamsCache(object):
    __slots__ = ('__cache', '__simplifiedParamsCoefficients', '__bonuses', '__noCamouflageVehicles', '__wheeledChassisParams')

    def __init__(self):
        super(_ParamsCache, self).__init__()
        self.__cache = {}
        self.__simplifiedParamsCoefficients = {}
        self.__bonuses = {}
        self.__noCamouflageVehicles = ()
        self.__wheeledChassisParams = {}

    @debugTime
    def init(self, vehiclesCache=None):
        self.__simplifiedParamsCoefficients, self.__bonuses, self.__cache, self.__wheeledChassisParams, self.__noCamouflageVehicles = pdc.load('gui_items_params_cache', partial(_readCache, vehiclesCache))

    def getGunReloadingSystemType(self, itemCD, vehicleCD=None):
        return self.getPrecachedParameters(itemCD).getReloadingType(vehicleCD)

    def getWheeledChassisAxleLockAngles(self, itemCD):
        return self.__wheeledChassisParams.get(itemCD)

    def hasGunMechanic(self, itemCD, mechanic, vehicleCD=None):
        gun = self.getPrecachedParameters(itemCD)
        return gun.hasMechanicForVehicle(mechanic, vehicleCD) if vehicleCD is not None else gun.hasMechanic(mechanic)

    def hasEngineMechanic(self, itemCD, mechanic):
        mask = self.getPrecachedParameters(itemCD) or 0
        return bool(mask & ENGINE_MECHANICS_BITS.get(mechanic, 0))

    def hasChassisMechanic(self, itemCD, mechanic):
        mask = self.getPrecachedParameters(itemCD) or 0
        return hasChassisMechanicBit(mask, mechanic)

    def getSimplifiedCoefficients(self):
        return self.__simplifiedParamsCoefficients

    def getBonuses(self):
        return self.__bonuses

    def getPrecachedParameters(self, typeCompactDescr, default=None):
        itemTypeID, nationID, _ = vehicles.parseIntCompactDescr(typeCompactDescr)
        return self.__cache.get(nationID, {}).get(itemTypeID, {}).get(typeCompactDescr, default)

    def getComponentVehiclesNames(self, typeCompactDescr):
        itemTypeIdx, nationIdx, _ = vehicles.parseIntCompactDescr(typeCompactDescr)
        getter = vehicles.g_cache.vehicle
        result = []
        for itemID in vehicles.g_list.getList(nationIdx):
            vehicleType = getter(nationIdx, itemID)
            components = _getVehicleSuitablesByType(vehicleType, itemTypeIdx)
            filtered = [ item for item in components if item.compactDescr == typeCompactDescr ]
            if filtered:
                result.append(vehicleType.userString)

        return result

    def getCompatibleArtefacts(self, vehicle):
        compatibles = []
        receivedBaseMod = {}
        lockedBaseMod = {}
        for step in vehicle.postProgression.iterOrderedSteps():
            action = step.action
            if action.actionType == ACTION_TYPES.MODIFICATION and not step.isRestricted():
                if step.isReceived():
                    receivedBaseMod[action.getLocName()] = action.getTechName()
                elif action.getLocName() not in lockedBaseMod and action.getLocName() not in receivedBaseMod:
                    lockedBaseMod[action.getLocName()] = action.getTechName()
            if action.actionType == ACTION_TYPES.PAIR_MODIFICATION and not step.isRestricted():
                for subAction in action.modifications:
                    compatibles.append((subAction.getTechName(), BonusTypes.PAIR_MODIFICATION))

        for baseMod in itertools.chain(itervalues(receivedBaseMod), itervalues(lockedBaseMod)):
            compatibles.append((baseMod, BonusTypes.BASE_MODIFICATION))

        for item in itertools.chain(itervalues(vehicles.g_cache.equipments()), itervalues(vehicles.g_cache.optionalDevices())):
            if item.checkCompatibilityWithVehicle(vehicle.descriptor)[0]:
                itemTypeName = item.itemTypeName
                if itemTypeName == 'equipment':
                    if item.equipmentType == EQUIPMENT_TYPES.battleBoosters:
                        itemTypeName = 'battleBooster'
                compatibles.append((item.name, itemTypeName))

        return compatibles

    def getVehiclesWithoutCamouflage(self):
        return self.__noCamouflageVehicles


g_paramsCache = _ParamsCache()
