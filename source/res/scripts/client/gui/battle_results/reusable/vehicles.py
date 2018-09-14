# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/reusable/vehicles.py
import weakref
from collections import defaultdict, namedtuple
from constants import DEATH_REASON_ALIVE
from gui.battle_results.reusable import shared
from gui.shared import g_itemsCache
_VehicleShortInfo = namedtuple('_ShortVehicleInfo', ('intCD', 'team', 'accountDBID', 'deathReason'))
_VehicleShortInfo.__new__.__defaults__ = (0,
 0,
 0,
 DEATH_REASON_ALIVE)

def _getVehiclesGenerator(vehicles):
    for vehicleID, data in vehicles.iteritems():
        accountDBID = 0L
        items = []
        if data is None:
            continue
        for item in data:
            if item is None:
                continue
            if 'typeCompDescr' not in item:
                continue
            accountDBID = item.get('accountDBID', 0L)
            intCD = item['typeCompDescr']
            if not intCD:
                continue
            info = _VehicleShortInfo(intCD, item.get('team', 0), accountDBID, item.get('deathReason', DEATH_REASON_ALIVE))
            items.append(info)

        yield (vehicleID, accountDBID, items)

    return


class VehiclesInfo(shared.UnpackedInfo):
    """Class contains reusable information about vehicles.
    This information is fetched from battle_results['vehicles']"""
    __slots__ = ('__vehicles', '__vehicleToAccountID', '__accountToVehicleID', '__details')

    def __init__(self, vehicles):
        super(VehiclesInfo, self).__init__()
        self.__vehicles = defaultdict(list)
        self.__vehicleToAccountID = {}
        self.__accountToVehicleID = {}
        self.__details = {}
        for vehicleID, accountDBID, items in _getVehiclesGenerator(vehicles):
            if not items:
                self._addUnpackedItemID(vehicleID)
            getItemByCD = g_itemsCache.items.getItemByCD

            def _getKey(value):
                return getItemByCD(value.intCD)

            self.__vehicles[vehicleID] = sorted(items, key=_getKey)
            for idx, info in enumerate(self.__vehicles[vehicleID]):
                self.__details[vehicleID, info.intCD] = idx

            if accountDBID and vehicleID:
                self.__vehicleToAccountID[vehicleID] = accountDBID
                self.__accountToVehicleID[accountDBID] = vehicleID

    def getAccountDBID(self, vehicleID):
        """Gets account's database ID by specified vehicle's ID.
        :param vehicleID: long containing vehicle's ID.
        :return: long containing account's database ID.
        """
        if vehicleID in self.__vehicleToAccountID:
            accountDBID = self.__vehicleToAccountID[vehicleID]
        else:
            accountDBID = 0
        return accountDBID

    def getVehicleID(self, accountDBID):
        """Gets vehicle's ID by specified account's database ID.
        :param accountDBID: long containing account's database ID.
        :return: long containing vehicle's ID.
        """
        if accountDBID in self.__accountToVehicleID:
            vehicleID = self.__accountToVehicleID[accountDBID]
        else:
            vehicleID = 0
        return vehicleID

    def getVehicleInfo(self, vehicleID):
        """Gets short information about first vehicle by given ID of vehicle.
        :param vehicleID: long containing vehicle's ID.
        :return: instance of _VehicleShortInfo.
        """
        if vehicleID in self.__vehicles and self.__vehicles[vehicleID]:
            info = self.__vehicles[vehicleID][0]
        else:
            info = _VehicleShortInfo()
        return info

    def getVehicleSummarizeInfo(self, player, result):
        """Gets information about all vehicles by specified account's database ID.
        :param player: instance of PlayerInfo.
        :param result: dictionary containing battle_results['vehicles'].
        :return: instance of VehicleSummarizeInfo.
        """
        dbID = player.dbID
        if dbID in self.__accountToVehicleID:
            vehicleID = self.__accountToVehicleID[dbID]
        else:
            vehicleID = 0
        if vehicleID in result:
            result = result[vehicleID]
        else:
            result = {}
        if vehicleID in self.__vehicles:
            items = self.__vehicles[vehicleID]
        else:
            items = []
        info = shared.VehicleSummarizeInfo(vehicleID, player)
        getItemByCD = g_itemsCache.items.getItemByCD
        for idx, item in enumerate(items):
            if idx >= len(result):
                continue
            info.addVehicleInfo(shared.VehicleDetailedInfo.makeForVehicle(vehicleID, getItemByCD(item.intCD), weakref.proxy(player), result[idx]))

        return info
