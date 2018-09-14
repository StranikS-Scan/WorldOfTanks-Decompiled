# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/items_parameters/params_cache.py
from collections import namedtuple
import math
import sys
from gui.shared.items_parameters import calcGunParams, calcShellParams, getEquipmentParameters
from gui.shared.items_parameters.xml_reader import ParamsXMLReader
from gui.shared.utils.decorators import debugTime
import nations
from debug_utils import LOG_CURRENT_EXCEPTION
from items import vehicles, ITEM_TYPES
from items.vehicles import getVehicleType
from gui.shared.utils import GUN_NORMAL, GUN_CAN_BE_CLIP, GUN_CLIP
CACHE_ITERATORS = {ITEM_TYPES.vehicle: lambda idx: vehicles.g_list.getList(idx).iterkeys(),
 ITEM_TYPES.vehicleRadio: lambda idx: vehicles.g_cache.radios(idx).itervalues(),
 ITEM_TYPES.vehicleEngine: lambda idx: vehicles.g_cache.engines(idx).itervalues(),
 ITEM_TYPES.vehicleChassis: lambda idx: vehicles.g_cache.chassis(idx).itervalues(),
 ITEM_TYPES.vehicleTurret: lambda idx: vehicles.g_cache.turrets(idx).itervalues(),
 ITEM_TYPES.vehicleGun: lambda idx: vehicles.g_cache.guns(idx).itervalues(),
 ITEM_TYPES.shell: lambda idx: vehicles.g_cache.shells(idx).itervalues(),
 ITEM_TYPES.optionalDevice: lambda idx: vehicles.g_cache.optionalDevices().itervalues(),
 ITEM_TYPES.equipment: lambda idx: vehicles.g_cache.equipments().itervalues()}
MODULES = (ITEM_TYPES.vehicle,
 ITEM_TYPES.vehicleRadio,
 ITEM_TYPES.vehicleEngine,
 ITEM_TYPES.vehicleChassis,
 ITEM_TYPES.vehicleTurret,
 ITEM_TYPES.vehicleGun,
 ITEM_TYPES.shell)
PrecachedShell = namedtuple('PrecachedShell', 'guns avgParams')
PrecachedEquipment = namedtuple('PrecachedEquipment', 'nations avgParams')
PrecachedOptionalDevice = namedtuple('PrecachedOptionalDevice', 'weight nations')

class PrecachedGun(namedtuple('PrecachedOptionalDevice', 'turrets clipVehicles avgParams turretsByVehicles')):

    @property
    def clipVehiclesNames(self):
        return [ getVehicleType(cd).userString for cd in self.clipVehicles ]

    def getReloadingType(self, vehicleCD=None):
        reloadingType = GUN_NORMAL
        if self.clipVehicles:
            reloadingType = GUN_CAN_BE_CLIP
            if vehicleCD is not None and vehicleCD in self.clipVehicles:
                reloadingType = GUN_CLIP
            elif vehicleCD is not None:
                reloadingType = GUN_NORMAL
        return reloadingType

    def getTurretsForVehicle(self, vehicleCD):
        return self.turretsByVehicles.get(vehicleCD, {})


class _ParamsCache(object):

    def __init__(self):
        self.__xmlItems = {}
        self.__cache = {}
        self.__init = False
        self.__simplifiedParamsCoefficients = {}
        self.__bonuses = {}

    @property
    def initialized(self):
        return self.__init

    @debugTime
    def init(self):
        self.__init = False
        try:
            self.__xmlItems = self.__readXMLItems()
            self.__precachOptionalDevices()
            self.__precachGuns()
            self.__precachShells()
            self.__precachEquipments()
        except Exception:
            LOG_CURRENT_EXCEPTION()
            return False

        xmlReader = ParamsXMLReader()
        self.__simplifiedParamsCoefficients = xmlReader.readSimplifiedParamsCoefficients()
        self.__bonuses = xmlReader.readBonuses()
        self.__init = True
        return True

    def getGunReloadingSystemType(self, itemCD, vehicleCD=None):
        return self.getPrecachedParameters(itemCD).getReloadingType(vehicleCD)

    def getSimplifiedCoefficients(self):
        return self.__simplifiedParamsCoefficients

    def getBonuses(self):
        return self.__bonuses

    def getPrecachedParameters(self, typeCompactDescr, default=None):
        itemTypeID, nationID, typeID = vehicles.parseIntCompactDescr(typeCompactDescr)
        return self.__cache.get(nationID, {}).get(itemTypeID, {}).get(typeCompactDescr, default)

    def getComponentVehiclesNames(self, typeCompactDescr):
        from gui.shared.gui_items import getVehicleSuitablesByType
        itemTypeIdx, nationIdx, typeIdx = vehicles.parseIntCompactDescr(typeCompactDescr)
        result = list()
        for vDescr in self.__getItems(ITEM_TYPES.vehicle, nationIdx):
            components, _ = getVehicleSuitablesByType(vDescr, itemTypeIdx)
            filtered = filter(lambda item: item['compactDescr'] == typeCompactDescr, components)
            if len(filtered):
                result.append(vDescr.type.userString)

        return result

    def getCompatibleBonuses(self, vehicleDescr):
        compatibles = []
        for itemsList in self.__xmlItems[nations.NONE_INDEX].values():
            for item in itemsList:
                if item.checkCompatibilityWithVehicle(vehicleDescr)[0]:
                    compatibles.append((item.name, item.itemTypeName))

        return compatibles

    def __readXMLItems(self):
        result = dict()
        for _, idx in nations.INDICES.iteritems():
            section = result.setdefault(idx, dict())
            for itemType in MODULES:
                section[itemType] = self.__getItemsDescriptors(itemType, idx)

        section = result.setdefault(nations.NONE_INDEX, dict())
        for itemType in (ITEM_TYPES.equipment, ITEM_TYPES.optionalDevice):
            section[itemType] = self.__getItemsDescriptors(itemType, nations.NONE_INDEX)

        return result

    def __getItemsDescriptors(self, itemType, idx):
        iterator = CACHE_ITERATORS[itemType](idx)
        if itemType == ITEM_TYPES.vehicle:
            return [ vehicles.VehicleDescr(typeID=(idx, cd)) for cd in iterator ]
        else:
            return [ vehicles.getDictDescr(data['compactDescr']) for data in iterator ]

    def __getItems(self, typeIdx, nationIdx=None):
        if nationIdx is None:
            result = list()
            for idx in nations.INDICES.itervalues():
                result.extend(self.__getItems(typeIdx, idx))

            return result
        else:
            return self.__xmlItems.get(nationIdx, {}).get(typeIdx, list())

    def __precachEquipments(self):
        self.__cache.setdefault(nations.NONE_INDEX, {})[ITEM_TYPES.equipment] = {}
        equipments = self.__getItems(ITEM_TYPES.equipment, nations.NONE_INDEX)
        for eqpDescr in equipments:
            equipmentNations = set()
            for vDescr in self.__getItems(ITEM_TYPES.vehicle):
                if not eqpDescr.checkCompatibilityWithVehicle(vDescr)[0]:
                    continue
                nation, id = vDescr.type.id
                equipmentNations.add(nation)

            self.__cache[nations.NONE_INDEX][ITEM_TYPES.equipment][eqpDescr.compactDescr] = PrecachedEquipment(nations=equipmentNations, avgParams=getEquipmentParameters(eqpDescr))

    def __precachOptionalDevices(self):
        self.__cache.setdefault(nations.NONE_INDEX, {})[ITEM_TYPES.optionalDevice] = {}
        optDevs = self.__getItems(ITEM_TYPES.optionalDevice, nations.NONE_INDEX)
        for deviceDescr in optDevs:
            wmin, wmax = sys.maxint, -1
            deviceNations = set()
            for vDescr in self.__getItems(ITEM_TYPES.vehicle):
                if not deviceDescr.checkCompatibilityWithVehicle(vDescr)[0]:
                    continue
                nation, id = vDescr.type.id
                deviceNations.add(nation)
                mods = deviceDescr.weightOnVehicle(vDescr)
                weightOnVehicle = math.ceil(vDescr.physics['weight'] * mods[0] + mods[1])
                wmin, wmax = min(wmin, weightOnVehicle), max(wmax, weightOnVehicle)

            self.__cache[nations.NONE_INDEX][ITEM_TYPES.optionalDevice][deviceDescr.compactDescr] = PrecachedOptionalDevice(weight=(wmin, wmax), nations=deviceNations)

    def __precachGuns(self):
        for nationName, nationIdx in nations.INDICES.iteritems():
            self.__cache.setdefault(nationIdx, {})[ITEM_TYPES.vehicleGun] = {}
            vcls = self.__getItems(ITEM_TYPES.vehicle, nationIdx)
            guns = self.__getItems(ITEM_TYPES.vehicleGun, nationIdx)
            for g in guns:
                descriptors = list()
                turretsList = list()
                turretsIntCDs = dict()
                clipVehiclesList = set()
                for vDescr in vcls:
                    turretsIntCDs[vDescr.type.compactDescr] = curVehicleTurretsCDs = list()
                    for vTurrets in vDescr.type.turrets:
                        for turret in vTurrets:
                            for gun in turret['guns']:
                                if gun['id'][1] == g['id'][1]:
                                    descriptors.append(gun)
                                    if len(vDescr.hull['fakeTurrets']['lobby']) != len(vDescr.turrets):
                                        curVehicleTurretsCDs.append(turret['compactDescr'])
                                        turretsList.append(turret['userString'])
                                    if gun['clip'][0] > 1:
                                        clipVehiclesList.add(vDescr.type.compactDescr)

                self.__cache[nationIdx][ITEM_TYPES.vehicleGun][g['compactDescr']] = PrecachedGun(turrets=tuple(turretsList), clipVehicles=clipVehiclesList, avgParams=calcGunParams(g, descriptors), turretsByVehicles=turretsIntCDs)

    def __precachShells(self):
        for nationName, nationIdx in nations.INDICES.iteritems():
            self.__cache.setdefault(nationIdx, {})[ITEM_TYPES.shell] = {}
            guns = self.__getItems(ITEM_TYPES.vehicleGun, nationIdx)
            shells = self.__getItems(ITEM_TYPES.shell, nationIdx)
            for sDescr in shells:
                descriptors = list()
                gNames = list()
                for gDescr in guns:
                    if 'shots' in gDescr:
                        for shot in gDescr['shots']:
                            if shot['shell']['id'][1] == sDescr['id'][1]:
                                if gDescr['userString'] not in gNames:
                                    gNames.append(gDescr['userString'])
                                    descriptors.append(shot)

                self.__cache[nationIdx][ITEM_TYPES.shell][sDescr['compactDescr']] = PrecachedShell(guns=tuple(gNames), avgParams=calcShellParams(descriptors))


g_paramsCache = _ParamsCache()
