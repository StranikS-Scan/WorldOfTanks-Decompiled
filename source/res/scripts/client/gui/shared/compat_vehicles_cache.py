# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/compat_vehicles_cache.py
from collections import defaultdict
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters import REQ_CRITERIA
from skeletons.gui.shared import IItemsCache

def getItemsByType(itemType, proxy):
    return proxy.items.getItems(itemType, ~REQ_CRITERIA.HIDDEN | ~REQ_CRITERIA.SECRET).itervalues()


class CompatVehiclesCache(object):
    __slots__ = ('__compatCache', '__invVehicles', '__fittedCache')
    _COMPAT_TYPES = (GUI_ITEM_TYPE.OPTIONALDEVICE,)
    _FITTED_TYPES = (GUI_ITEM_TYPE.OPTIONALDEVICE, GUI_ITEM_TYPE.EQUIPMENT, GUI_ITEM_TYPE.BATTLE_BOOSTER)

    def __init__(self):
        self.__compatCache = {}
        self.__fittedCache = {}
        self.__invVehicles = set()

    def clear(self):
        self.__compatCache.clear()
        self.__invVehicles.clear()
        self.__fittedCache.clear()

    def getCompatCache(self, proxy):
        if not self.__compatCache:
            self.__compatCache.update({itemType:defaultdict(list) for itemType in self._COMPAT_TYPES})
            vehicles = proxy.items.getItems(GUI_ITEM_TYPE.VEHICLE, REQ_CRITERIA.INVENTORY, onlyWithPrices=False)
            self.__invalidateCompatCache(proxy, vehicles.itervalues(), [])
        return self.__compatCache

    def getFittedCache(self, proxy):
        if not self.__fittedCache:
            self.__invalidateFittedCache(proxy)
        return self.__fittedCache

    def invalidateFullData(self, proxy):
        self.clear()

    def invalidateData(self, proxy, invalidItems):
        if GUI_ITEM_TYPE.VEHICLE not in invalidItems:
            return
        self.__fittedCache.clear()
        if not self.__compatCache:
            return
        invalidVehicles = invalidItems[GUI_ITEM_TYPE.VEHICLE]
        inventoryVehicles = proxy.items.getItems(GUI_ITEM_TYPE.VEHICLE, REQ_CRITERIA.INVENTORY, onlyWithPrices=False)
        addedVehicles = []
        removedVehicles = []
        for vehID in invalidVehicles:
            if vehID not in self.__invVehicles and vehID in inventoryVehicles:
                addedVehicles.append(inventoryVehicles[vehID])
            if vehID in self.__invVehicles and vehID not in inventoryVehicles:
                removedVehicles.append(vehID)

        self.__invalidateCompatCache(proxy, addedVehicles, removedVehicles)

    def __invalidateFittedCache(self, proxy):
        self.__fittedCache.update({itemType:defaultdict(list) for itemType in self._FITTED_TYPES})
        inventoryVehicles = proxy.items.getItems(GUI_ITEM_TYPE.VEHICLE, REQ_CRITERIA.INVENTORY, onlyWithPrices=False)
        for veh in inventoryVehicles.itervalues():
            for optDevice in veh.optDevices.installed:
                if optDevice is not None:
                    self.__fittedCache[GUI_ITEM_TYPE.OPTIONALDEVICE][optDevice.intCD].append(veh.intCD)

            for cons in veh.consumables.installed:
                if cons is not None:
                    self.__fittedCache[GUI_ITEM_TYPE.EQUIPMENT][cons.intCD].append(veh.intCD)

            for battleBooster in veh.battleBoosters.installed:
                if battleBooster is not None:
                    self.__fittedCache[GUI_ITEM_TYPE.BATTLE_BOOSTER][battleBooster.intCD].append(veh.intCD)

        return

    def __invalidateCompatCache(self, proxy, addedVehicle, removedVehicle):
        if not addedVehicle and not removedVehicle:
            return
        collectItems = [ (itemType, item) for itemType in self._COMPAT_TYPES for item in getItemsByType(itemType, proxy) ]
        for vehicle in addedVehicle:
            self.__addCacheForVehicle(vehicle, collectItems)

        for vehicleIntCD in removedVehicle:
            self.__removeCacheForVehicle(vehicleIntCD, collectItems)

    def __addCacheForVehicle(self, vehicle, collectItems):
        vehDescr = vehicle.descriptor
        for itemType, item in collectItems:
            if item.descriptor.checkCompatibilityWithVehicle(vehDescr):
                self.__compatCache[itemType][item.intCD].append(vehicle.intCD)

        self.__invVehicles.add(vehicle.intCD)

    def __removeCacheForVehicle(self, vehicleIntCD, collectItems):
        for itemType, item in collectItems:
            try:
                self.__compatCache[itemType][item.intCD].remove(vehicleIntCD)
            except ValueError:
                pass
