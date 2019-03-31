# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/graphs/data.py
# Compiled at: 2011-10-20 18:37:36
from collections import defaultdict
from items import vehicles, ITEM_TYPE_INDICES
from gui.Scaleform.graphs import _VEHICLE_TYPE_IDX
from gui.Scaleform.graphs.dumpers import VehicleComponentsGraphDumper
from gui.Scaleform.graphs.trees_display_info import g_treeDisplayInfo
from collections import namedtuple
import types

class _VehicleComponentsPoint(namedtuple('VehicleComponentsPoint', 'compactDescr unlockIdx unlocked experience relations')):
    """
    Graph Point, where:
    compactDescr - compact description for component or vehicle.
    unlockIdx - index of the unlock.
    unlocked - is unlocked.
    experience - amount of experience necessary to study the node.
    relations - all required nodes (compactDescr) from root node to given node
            (exclude root and given node).
    """

    def __eq__(self, other):
        compactDescr = other if type(other) == types.IntType else other.compactDescr
        return self.compactDescr == compactDescr


class _VehiclePoint(namedtuple('VehiclePoint', 'compactDescr earnedExperience unlocked elite displayInfo')):
    """
    Graph Point, where:
    compactDescr - compact description for component or vehicle.
    earnedExperience - earned experience for given vehicle
    unlocked - is vehicle unlocked.
    elite - is vehicle elite.
    displayInfo - information required to display node in view.
    """

    def __eq__(self, other):
        compactDescr = other if type(other) == types.IntType else other.compactDescr
        return self.compactDescr == compactDescr


class _ItemsData(object):

    def __init__(self):
        super(_ItemsData, self).__init__()
        self.invItems = {}
        self.shopPrices = {}

    def setInvItem(self, compactDescr, item):
        """
        Collects inventory information (custom_items._InventoryItem or
                custom_items._InventoryVehicle ) for points.
        @param compactDescr: item compact descriptor (int type).
        """
        self.invItems[compactDescr] = item

    def getInvItem(self, compactDescr):
        """
        Gets inventory information (custom_items._InventoryItem or
                custom_items._InventoryVehicle ) by compactDescr
        @param compactDescr: item compact descriptor (int type).
        """
        return self.invItems.get(compactDescr)

    def hasInvItem(self, compactDescr):
        """
        Has item in inventory.
        @param compactDescr: item compact descriptor (int type).
        """
        return compactDescr in self.invItems.keys()

    def getInventoryItemsCDs(self):
        """
        Gets list of compact descriptors for inventory items
        """
        return self.invItems.keys()

    def setShopPrice(self, compactDesc, price):
        """
        Collects shop prices for points.
        @param compactDescr: item compact descriptor (int type).
        @param price: tuple(<credits>, <gold>).
        """
        self.shopPrices[compactDesc] = price

    def getShopPrice(self, compactDesc):
        """
        Gets item prices (<credits>, <gold>) by compactDescr
        @param compactDescr: item compact descriptor (int type).
        """
        return self.shopPrices.get(compactDesc)


class VehicleComponentsGraph(_ItemsData):

    def __init__(self):
        super(VehicleComponentsGraph, self).__init__()
        self.__dumper = VehicleComponentsGraphDumper()
        self.points = []
        self.autounlockedPoints = []
        self.compactDescrByTypeId = defaultdict(list)

    def load(self, vehicleType, vehicleTypeCompactDesc, unlocks):
        """
        Parse unlocks data to vehicle type - vehicleType.
        @param vehicleType: vehicle type. @see: items.vehicles.VehicleType
        @param vehicleTypeCompactDesc: vehicle type compact description.
        Note: int type.
        @param unlocks: list of unlocked component compact description. 
        Note: int type.
        """
        self.compactDescrByTypeId = defaultdict(list)
        self.invItems = {}
        self.shopPrices = {}
        self.__buildListOfAutounlockedPoints(vehicleType, vehicleTypeCompactDesc, unlocks)
        self.__buildListOfProcessedPoints(vehicleType, vehicleTypeCompactDesc, unlocks)

    def __buildListOfAutounlockedPoints(self, vehicleType, vehicleTypeCompactDesc, unlocks):
        """
        Collects autounlocked components to given vehicle type
        @param vehicleType: vehicle type. @see: items.vehicles.VehicleType
        @param vehicleTypeCompactDesc: vehicle type compact description.
        Note: int type.
        @param unlocks: list of unlocked component compact description.
        Note: int type
        """
        points = vehicleType.autounlockedItems[:]
        rootUnlocked = vehicleTypeCompactDesc in unlocks
        hasFakeTurrets = len(vehicleType.hull.get('fakeTurrets', {}).get('lobby', ())) != 0 and vehicleType.tags & set(['SPG', 'AT-SPG'])
        self.autounlockedPoints = []
        for point in points:
            descr = vehicles.getDictDescr(point)
            type = descr.get('itemTypeName')
            if type == 'vehicleFuelTank':
                continue
            elif type == 'vehicleTurret' and hasFakeTurrets:
                continue
            self.autounlockedPoints.append(_VehicleComponentsPoint(point, -1, point in unlocks and rootUnlocked, 0, set()))
            self.compactDescrByTypeId[ITEM_TYPE_INDICES[type]].append(point)

    def __buildListOfProcessedPoints(self, vehicleType, vehicleTypeCompactDescr, unlocks):
        """
        Based on the unlockDescr computed points - dependencies of one
        component from another.
        @param vehicleType: vehicle type. @see: items.vehicles.VehicleType
        @param vehicleTypeCompactDesc: vehicle type compact description. 
        Note: int type.
        @param unlocks: list of unlocked component compact description.
        Note: int type.
        """
        unlocksDescrs = vehicleType.unlocksDescrs
        self.points = []
        rootUnlocked = vehicleTypeCompactDescr in unlocks
        self.compactDescrByTypeId[_VEHICLE_TYPE_IDX].append(vehicleTypeCompactDescr)
        self.points.append(_VehicleComponentsPoint(vehicleTypeCompactDescr, 0, rootUnlocked, 0, set()))
        for unlockIdx, unlockDescr in enumerate(unlocksDescrs):
            experience = unlockDescr[0]
            compactDescr = unlockDescr[1]
            requiredCompactDescrs = unlockDescr[2:]
            relations = set()
            for requiredCompactDescr in requiredCompactDescrs:
                if requiredCompactDescr in self.autounlockedPoints:
                    requiredCompactDescr = vehicleTypeCompactDescr
                relations.add(requiredCompactDescr)

            self.points.append(_VehicleComponentsPoint(compactDescr, unlockIdx, compactDescr in unlocks, experience, relations))
            itemTypeID, _, _ = vehicles.parseIntCompactDescr(compactDescr)
            self.compactDescrByTypeId[itemTypeID].append(compactDescr)

    def setDumper(self, dumper):
        """
        Sets dumper, witch called in function dump.
        @param dumper: dumper object. 
        @see: gui.Scaleform.graphs.dumpers.VehicleComponentsGraphDumper
        """
        if dumper is not None and isinstance(dumper, VehicleComponentsGraphDumper):
            self.__dumper = dumper
        return

    def dump(self):
        """
        Gets data dump
        @return: dump
        """
        return self.__dumper.dump(self)


class VehiclesGraph(_ItemsData):

    def __init__(self):
        super(VehiclesGraph, self).__init__()
        self.points = []

    def load(self, nationId, unlocks=set(), elite=set(), experiences=None):
        self.points = []
        vehicleList = vehicles.g_list.getList(nationId)
        g_treeDisplayInfo.load()
        if experiences is None:
            experiences = {}
        for item in vehicleList.values():
            displayInfo = g_treeDisplayInfo.getDisplayInfo(item['name'])
            if displayInfo is not None:
                compactDescr = item['compactDescr']
                earnedExperience = experiences.get(compactDescr, 0)
                self.points.append(_VehiclePoint(compactDescr, earnedExperience, compactDescr in unlocks, compactDescr in elite, displayInfo))

        return

    def setDumper(self, dumper):
        """
        Sets dumper, witch called in function dump.
        @param dumper: dumper object. 
        @see: gui.Scaleform.graphs.dumpers.VehicleComponentsGraphDumper
        """
        if dumper is not None and isinstance(dumper, VehicleComponentsGraphDumper):
            self.__dumper = dumper
        return

    def dump(self):
        """
        Gets data dump
        @return: dump
        """
        return self.__dumper.dump(self)
