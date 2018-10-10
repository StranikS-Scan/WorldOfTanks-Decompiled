# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/items_parameters/params_cache.py
from collections import namedtuple
import itertools
import math
import sys
from gui.shared.items_parameters import calcGunParams, calcShellParams, getEquipmentParameters, isAutoReloadGun
from gui.shared.items_parameters import xml_reader
from gui.shared.utils.decorators import debugTime
import nations
from debug_utils import LOG_CURRENT_EXCEPTION
from items import vehicles, ITEM_TYPES, EQUIPMENT_TYPES
from items.vehicles import getVehicleType
from gui.shared.utils import GUN_NORMAL, GUN_CAN_BE_CLIP, GUN_CLIP, GUN_CAN_BE_AUTO_RELOAD, GUN_AUTO_RELOAD
from soft_exception import SoftException
PrecachedShell = namedtuple('PrecachedShell', 'guns params')
PrecachedEquipment = namedtuple('PrecachedEquipment', 'nations params')
PrecachedOptionalDevice = namedtuple('PrecachedOptionalDevice', 'weight nations')
PrecachedChassis = namedtuple('PrecachedChassis', 'isHydraulic')

class PrecachedGun(namedtuple('PrecachedGun', 'clipVehicles autoReloadVehicles params turretsByVehicles')):

    @property
    def clipVehiclesNames(self):
        if self.clipVehicles is not None:
            return [ getVehicleType(cd).userString for cd in self.clipVehicles ]
        else:
            return []

    def getReloadingType(self, vehicleCD=None):
        reloadingType = GUN_NORMAL
        if vehicleCD is None:
            if self.autoReloadVehicles:
                reloadingType = GUN_CAN_BE_AUTO_RELOAD
            elif self.clipVehicles:
                reloadingType = GUN_CAN_BE_CLIP
        elif self.autoReloadVehicles and vehicleCD in self.autoReloadVehicles:
            reloadingType = GUN_AUTO_RELOAD
        elif self.clipVehicles is not None and vehicleCD in self.clipVehicles:
            reloadingType = GUN_CLIP
        return reloadingType

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
        for nationID in nations.INDICES.itervalues():
            self._local[nationID] = [ vehicles.VehicleDescr(typeID=(nationID, cd)) for cd in vehilesList(nationID).iterkeys() ]

    def generator(self, nationID=None):
        if nationID is None:
            nationIDs = nations.INDICES.values()
        else:
            nationIDs = (nationID,)
        for nextID in nationIDs:
            if nextID not in self._local:
                continue
            for descr in self._local[nextID]:
                yield descr

        return


class _ParamsCache(object):
    __slots__ = ('__cache', '__init', '__simplifiedParamsCoefficients', '__bonuses', '__noCamouflageVehicles')

    def __init__(self):
        super(_ParamsCache, self).__init__()
        self.__cache = {}
        self.__init = False
        self.__simplifiedParamsCoefficients = {}
        self.__bonuses = {}
        self.__noCamouflageVehicles = ()

    @property
    def initialized(self):
        return self.__init

    @debugTime
    def init(self, vehiclesCache=None):
        self.__init = False
        try:
            if vehiclesCache is None:
                vehiclesCache = VehicleDescrsCache()
            vehiclesCache.load()
            self.__precacheOptionalDevices(vehiclesCache)
            self.__precacheGuns(vehiclesCache)
            self.__precacheShells()
            self.__precacheEquipments(vehiclesCache)
            self.__precacheChassis(vehiclesCache)
            self.__cacheVehiclesWithoutCamouflage()
            vehiclesCache.clear()
            del vehiclesCache
        except Exception:
            LOG_CURRENT_EXCEPTION()
            return False

        coefficients, bonuses = xml_reader.read()
        self.__simplifiedParamsCoefficients = coefficients
        self.__bonuses = bonuses
        self.__init = True
        return True

    def getGunReloadingSystemType(self, itemCD, vehicleCD=None):
        return self.getPrecachedParameters(itemCD).getReloadingType(vehicleCD)

    def isChassisHydraulic(self, itemCD):
        return self.getPrecachedParameters(itemCD).isHydraulic

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
        for itemID in vehicles.g_list.getList(nationIdx).iterkeys():
            vehicleType = getter(nationIdx, itemID)
            components = _getVehicleSuitablesByType(vehicleType, itemTypeIdx)
            filtered = [ item for item in components if item.compactDescr == typeCompactDescr ]
            if filtered:
                result.append(vehicleType.userString)

        return result

    def getCompatibleArtefacts(self, vehicleDescr):
        compatibles = []
        for item in itertools.chain(vehicles.g_cache.equipments().itervalues(), vehicles.g_cache.optionalDevices().itervalues()):
            if item.checkCompatibilityWithVehicle(vehicleDescr)[0]:
                itemTypeName = item.itemTypeName
                if itemTypeName == 'equipment':
                    if item.equipmentType == EQUIPMENT_TYPES.battleBoosters:
                        itemTypeName = 'battleBooster'
                compatibles.append((item.name, itemTypeName))

        return compatibles

    def getVehiclesWithoutCamouflage(self):
        return self.__noCamouflageVehicles

    def __precacheEquipments(self, vehiclesCache):
        self.__cache.setdefault(nations.NONE_INDEX, {})[ITEM_TYPES.equipment] = {}
        for eqpDescr in vehicles.g_cache.equipments().itervalues():
            equipmentNations = set()
            for vDescr in vehiclesCache.generator():
                if not eqpDescr.checkCompatibilityWithVehicle(vDescr)[0]:
                    continue
                nation, _ = vDescr.type.id
                equipmentNations.add(nation)

            self.__cache[nations.NONE_INDEX][ITEM_TYPES.equipment][eqpDescr.compactDescr] = PrecachedEquipment(nations=equipmentNations, params=getEquipmentParameters(eqpDescr))

    def __precacheOptionalDevices(self, vehiclesCache):
        self.__cache.setdefault(nations.NONE_INDEX, {})[ITEM_TYPES.optionalDevice] = {}
        for deviceDescr in vehicles.g_cache.optionalDevices().itervalues():
            wmin, wmax = sys.maxint, -1
            deviceNations = set()
            for vDescr in vehiclesCache.generator():
                if not deviceDescr.checkCompatibilityWithVehicle(vDescr)[0]:
                    continue
                nation, _ = vDescr.type.id
                deviceNations.add(nation)
                mods = deviceDescr.weightOnVehicle(vDescr)
                weightOnVehicle = math.ceil(vDescr.physics['weight'] * mods[0] + mods[1])
                wmin, wmax = min(wmin, weightOnVehicle), max(wmax, weightOnVehicle)

            self.__cache[nations.NONE_INDEX][ITEM_TYPES.optionalDevice][deviceDescr.compactDescr] = PrecachedOptionalDevice(weight=(wmin, wmax), nations=deviceNations)

    def __precacheGuns(self, vehiclesCache):
        descriptors = []
        curVehicleTurretsCDs = []
        getter = vehicles.g_cache.guns
        for nationIdx in nations.INDICES.itervalues():
            self.__cache.setdefault(nationIdx, {})[ITEM_TYPES.vehicleGun] = {}
            for g in getter(nationIdx).itervalues():
                del descriptors[:]
                turretsIntCDs = {}
                clipVehiclesList = set()
                autoReloadVehsList = set()
                for vDescr in vehiclesCache.generator(nationIdx):
                    del curVehicleTurretsCDs[:]
                    vehCD = vDescr.type.compactDescr
                    for vTurrets in vDescr.type.turrets:
                        for turret in vTurrets:
                            for gun in turret.guns:
                                if gun.id[1] == g.id[1]:
                                    descriptors.append(gun)
                                    if len(vDescr.hull.fakeTurrets['lobby']) != len(vDescr.turrets):
                                        curVehicleTurretsCDs.append(turret.compactDescr)
                                    if gun.clip[0] > 1:
                                        clipVehiclesList.add(vehCD)
                                    if isAutoReloadGun(gun):
                                        autoReloadVehsList.add(vehCD)

                    if curVehicleTurretsCDs:
                        turretsIntCDs[vDescr.type.compactDescr] = tuple(curVehicleTurretsCDs)

                self.__cache[nationIdx][ITEM_TYPES.vehicleGun][g.compactDescr] = PrecachedGun(clipVehicles=clipVehiclesList if clipVehiclesList else None, autoReloadVehicles=frozenset(autoReloadVehsList) if autoReloadVehsList else None, params=calcGunParams(g, descriptors), turretsByVehicles=turretsIntCDs)

        return

    def __precacheShells(self):
        descriptors = []
        gunsCDs = []
        gunsGetter = vehicles.g_cache.guns
        shellsGetter = vehicles.g_cache.shells
        for nationIdx in nations.INDICES.values():
            self.__cache.setdefault(nationIdx, {})[ITEM_TYPES.shell] = {}
            for sDescr in shellsGetter(nationIdx).itervalues():
                del descriptors[:]
                del gunsCDs[:]
                for gDescr in gunsGetter(nationIdx).itervalues():
                    for shot in gDescr.shots:
                        if shot.shell.id[1] == sDescr.id[1]:
                            if gDescr.compactDescr not in gunsCDs:
                                gunsCDs.append(gDescr.compactDescr)
                                descriptors.append(shot)

                self.__cache[nationIdx][ITEM_TYPES.shell][sDescr.compactDescr] = PrecachedShell(guns=tuple(gunsCDs), params=calcShellParams(descriptors))

    def __precacheChassis(self, vehiclesCache):
        getter = vehicles.g_cache.chassis
        hydraulic = PrecachedChassis(isHydraulic=True)
        noHydraulic = PrecachedChassis(isHydraulic=False)
        for nationIdx in nations.INDICES.itervalues():
            self.__cache.setdefault(nationIdx, {})[ITEM_TYPES.vehicleChassis] = {}
            siegeVcls = [ vDescr for vDescr in vehiclesCache.generator(nationIdx) if vDescr.hasSiegeMode ]
            for chs in getter(nationIdx).itervalues():
                result = noHydraulic
                for vDescr in siegeVcls:
                    for vChs in vDescr.type.chassis:
                        if chs.compactDescr == vChs.compactDescr:
                            result = hydraulic

                self.__cache[nationIdx][ITEM_TYPES.vehicleChassis][chs.compactDescr] = result

    def __cacheVehiclesWithoutCamouflage(self):
        vehicleCDs = []
        deniedVehicles = {}
        allowedVehicles = set()
        customization = vehicles.g_cache.customization
        for nationID in nations.INDICES.itervalues():
            deniedVehicles.clear()
            allowedVehicles.clear()
            restrictedCamouflages = 0
            camouflages = customization(nationID)['camouflages']
            totalCount = len(camouflages)
            for camouflage in camouflages.itervalues():
                currentAllowed = camouflage.get('allow', ())
                for vehCD in camouflage.get('deny', ()):
                    deniedVehicles[vehCD] = deniedVehicles.get(vehCD, 0) + 1

                allowedVehicles.update(currentAllowed)
                if currentAllowed:
                    restrictedCamouflages += 1

            for vehCD, count in deniedVehicles.iteritems():
                if vehCD not in allowedVehicles and count + restrictedCamouflages >= totalCount:
                    vehicleCDs.append(vehCD)

        self.__noCamouflageVehicles = tuple(vehicleCDs)


g_paramsCache = _ParamsCache()
