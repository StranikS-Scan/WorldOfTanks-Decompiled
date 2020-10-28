# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/reusable/vehicles.py
import weakref
from collections import defaultdict, namedtuple
import typing
from constants import DEATH_REASON_ALIVE
from gui.battle_results.reusable import shared
from helpers import dependency
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from players import PlayerInfo
_VehicleShortInfo = namedtuple('_ShortVehicleInfo', ('intCD', 'team', 'accountDBID', 'deathReason', 'isTeamKiller'))
_VehicleShortInfo.__new__.__defaults__ = (0,
 0,
 0,
 DEATH_REASON_ALIVE,
 False)

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
            info = _VehicleShortInfo(intCD, item.get('team', 0), accountDBID, item.get('deathReason', DEATH_REASON_ALIVE), item.get('isTeamKiller', False))
            items.append(info)

        yield (vehicleID, accountDBID, items)

    return


class VehiclesInfo(shared.UnpackedInfo):
    __slots__ = ('__vehicles', '__vehicleToAccountID', '__accountToVehicleID', '__details')
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, vehicles):
        super(VehiclesInfo, self).__init__()
        self.__vehicles = defaultdict(list)
        self.__vehicleToAccountID = {}
        self.__accountToVehicleID = {}
        self.__details = {}
        getItemByCD = self.itemsCache.items.getItemByCD

        def _getKey(value):
            return getItemByCD(value.intCD)

        for vehicleID, accountDBID, items in _getVehiclesGenerator(vehicles):
            if not items:
                self._addUnpackedItemID(vehicleID)
            self.__vehicles[vehicleID] = sorted(items, key=_getKey)
            for idx, info in enumerate(self.__vehicles[vehicleID]):
                self.__details[vehicleID, info.intCD] = idx

            if accountDBID and vehicleID:
                self.__vehicleToAccountID[vehicleID] = accountDBID
                self.__accountToVehicleID[accountDBID] = vehicleID

    def getAccountDBID(self, vehicleID):
        if vehicleID in self.__vehicleToAccountID:
            accountDBID = self.__vehicleToAccountID[vehicleID]
        else:
            accountDBID = 0
        return accountDBID

    def getVehicleID(self, accountDBID):
        if accountDBID in self.__accountToVehicleID:
            vehicleID = self.__accountToVehicleID[accountDBID]
        else:
            vehicleID = 0
        return vehicleID

    def getVehicleInfo(self, vehicleID):
        if vehicleID in self.__vehicles and self.__vehicles[vehicleID]:
            info = self.__vehicles[vehicleID][0]
        else:
            info = _VehicleShortInfo()
        return info

    def getVehicleSummarizeInfo(self, player, result):
        dbID = player.dbID
        if dbID in self.__accountToVehicleID:
            vehicleID = self.__accountToVehicleID[dbID]
        else:
            vehicleID = 0
        return self.__getVehicleSummarize(vehicleID, player, result)

    def getAIBotVehicleSummarizeInfo(self, vehicleID, player, result):
        return self.__getVehicleSummarize(vehicleID, player, result)

    def __getVehicleSummarize(self, vehicleID, player, result):
        if vehicleID in result:
            result = result[vehicleID]
        else:
            result = {}
        if vehicleID in self.__vehicles:
            items = self.__vehicles[vehicleID]
        else:
            items = []
        info = shared.VehicleSummarizeInfo(vehicleID, player)
        getItemByCD = self.itemsCache.items.getItemByCD

        def getVehicleResult(intCD):
            for veh in result:
                if veh['typeCompDescr'] == intCD:
                    return veh

            return None

        for idx, item in enumerate(items):
            if idx >= len(result):
                continue
            info.addVehicleInfo(shared.VehicleDetailedInfo.makeForVehicle(vehicleID, getItemByCD(item.intCD), weakref.proxy(player), getVehicleResult(item.intCD)))

        return info
