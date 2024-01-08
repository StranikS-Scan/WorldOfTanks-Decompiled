# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/module_upd_available_helper.py
from collections import namedtuple
import typing
from CurrentVehicle import g_currentVehicle
from account_helpers import isOutOfWallet
from account_helpers import AccountSettings
from constants import BATTLE_MODE_VEHICLE_TAGS
from helpers import dependency
from items import getTypeOfCompactDescr as getTypeOfCD
from gui.shared.gui_items import GUI_ITEM_TYPE
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Optional
    from gui.shared.gui_items.Vehicle import Vehicle

class _UnlockStats(namedtuple('UnlockStats', 'unlocked xps freeXP')):

    def isUnlocked(self, vehIntCD):
        return vehIntCD in self.unlocked

    def isSeqUnlocked(self, seq):
        return seq.issubset(self.unlocked)

    def getVehXP(self, vehIntCD):
        return self.xps.get(vehIntCD, 0)


class _VehicleResearchInfo(namedtuple('VehicleResearchInfo', 'vehIntCD wasSaved canBeSaved researched available viewedItems')):

    def __repr__(self):
        msg = '\n        [VehicleResearchInfo]:\n        vehIntCD: {} wasSaved: {} canBeSaved: {}\n        researched: {},\n        available: {},\n        viewed: {}\n        '
        return msg.format(self.vehIntCD, self.wasSaved, self.canBeSaved, self.researched, self.available, self.viewedItems)

    def hasUnviewedVehicles(self):
        notSeenItems = self.getUnviewedItems()
        return any((getTypeOfCD(itemCD) == GUI_ITEM_TYPE.VEHICLE for itemCD in notSeenItems))

    def hasUnviewedItems(self):
        return bool(self.getUnviewedItems())

    def getUnviewedItems(self):
        return self.available - self.viewedItems

    def getNewViewedItems(self):
        return (self.viewedItems | self.getUnviewedItems()) - self.researched

    def hasNewViewed(self):
        return self.viewedItems != self.getNewViewedItems()

    def updateViewed(self):
        return self._replace(viewedItems=self.getNewViewedItems())


def getResearchInfo(vehIntCD=None, vehicle=None):
    vehicle = _validateAndGetVehicle(vehIntCD, vehicle)
    if vehicle is None:
        return
    else:
        researchInfo = _getVehicleResearchInfo(vehicle)
        if not researchInfo.wasSaved:
            researchInfo = _marksAsViewedAndSave(vehicle, researchInfo)
        return researchInfo


def updateViewedItems(vehIntCD=None, vehicle=None):
    vehicle = _validateAndGetVehicle(vehIntCD, vehicle)
    if vehicle is None:
        return
    else:
        researchInfo = _getVehicleResearchInfo(vehicle)
        _marksAsViewedAndSave(vehicle, researchInfo)
        return


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _isValidAccountType(itemsCache=None):
    return not isOutOfWallet(itemsCache.items.stats.attributes)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _getVehicleResearchInfo(vehicle, itemsCache=None):
    viewedItems = AccountSettings.getVehicleViewedModules(vehicle.intCD)
    wasSaved = viewedItems is not None
    canBeSaved = not vehicle.isElite
    viewedItems = viewedItems or set()
    researched = set()
    availableToResearch = set()
    vehIntCD = vehicle.intCD
    vehType = vehicle.descriptor.type
    unlockStats = _getUnlockStats()
    vehXp = unlockStats.getVehXP(vehIntCD)
    for data in vehType.unlocksDescrs:
        xpCost, itemCD, required = data[0], data[1], set(data[2:])
        guiItem = itemsCache.items.getItemByCD(itemCD)
        itemTypeID = getTypeOfCD(itemCD)
        if guiItem.isUnlocked:
            researched.add(itemCD)
        discount = 0
        available = unlockStats.isSeqUnlocked(required) and unlockStats.isUnlocked(vehIntCD)
        if itemTypeID == GUI_ITEM_TYPE.VEHICLE:
            xpCost, discount = _getNewCost(itemCD, guiItem.level, xpCost)
        if available and vehXp >= xpCost - discount:
            availableToResearch.add(itemCD)

    return _VehicleResearchInfo(vehIntCD, wasSaved, canBeSaved, researched, availableToResearch, viewedItems)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _getNewCost(vehicleCD, level, oldCost, itemsCache=None):
    _items = itemsCache.items
    blueprintDiscount = _items.blueprints.getBlueprintDiscount(vehicleCD, level)
    xpCost = _items.blueprints.calculateCost(oldCost, blueprintDiscount)
    return (xpCost, blueprintDiscount)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _getUnlockStats(itemsCache=None):
    stats = itemsCache.items.stats
    return _UnlockStats(stats.unlocks, stats.vehiclesXPs, stats.freeXP)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _validateAndGetVehicle(vehIntCD, vehicle, itemsCache=None):
    if not _isValidAccountType():
        return
    else:
        if vehicle is None:
            if vehIntCD is not None and getTypeOfCD(vehIntCD) == GUI_ITEM_TYPE.VEHICLE:
                vehicle = itemsCache.items.getItemByCD(vehIntCD)
            elif g_currentVehicle.item:
                vehicle = g_currentVehicle.item
        return None if not _validateVehicle(vehicle) else vehicle


def _marksAsViewedAndSave(vehicle, researchInfo):
    if researchInfo.canBeSaved:
        researchInfo = researchInfo.updateViewed()
        AccountSettings.setVehicleViewedModules(vehicle.intCD, researchInfo.getNewViewedItems())
    elif researchInfo.wasSaved:
        AccountSettings.clearVehicleViewedModules(vehicle.intCD)
    return researchInfo


def _validateVehicle(vehicle):
    return False if vehicle is None or vehicle.isPremium or vehicle.isPremiumIGR or vehicle.isCollectible or vehicle.isSpecial or vehicle.isSecret or vehicle.tags & BATTLE_MODE_VEHICLE_TAGS else True
