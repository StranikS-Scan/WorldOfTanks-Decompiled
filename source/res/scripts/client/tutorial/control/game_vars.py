# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/control/game_vars.py
import types
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from tutorial.logger import LOG_ERROR
from tutorial.data.conditions import CONDITION_STATE
__all__ = ('getUnlockedItems', 'getItemByIntCD', 'getVehicleByIntCD', 'getItemStateGetter')

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getUnlockedItems(itemsCache=None):
    return itemsCache.items.stats.unlocks if itemsCache is not None else ()


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getItemByIntCD(intCD, itemsCache=None):
    if intCD is None or not isinstance(intCD, (types.IntType, types.LongType, types.FloatType)):
        return
    else:
        return itemsCache.items.getItemByCD(intCD) if itemsCache is not None else None


def getVehicleByIntCD(intCD):
    vehicle = getItemByIntCD(intCD)
    if vehicle is not None and vehicle.itemTypeID != GUI_ITEM_TYPE.VEHICLE:
        LOG_ERROR('IntCD of vehicle is invalid', intCD)
        vehicle = None
    return vehicle


def _isItemSelected(intCD):
    if intCD is None:
        return False
    else:
        return g_currentVehicle.item.intCD == intCD if g_currentVehicle.isPresent() else False


def _isItemPremium(intCD):
    if intCD is None:
        return False
    else:
        vehicle = getVehicleByIntCD(intCD)
        return vehicle.isPremium if vehicle is not None else False


def _isItemUnlocked(intCD):
    return False if intCD is None else intCD in getUnlockedItems()


def _isItemInInventory(intCD):
    if intCD is None:
        return False
    else:
        vehicle = getItemByIntCD(intCD)
        return vehicle.invID != -1 if vehicle is not None else False


def _isAnyCrewSkillLearned(intCD, tankmanRole):
    if intCD is None:
        return False
    else:
        vehicle = getItemByIntCD(intCD)
        if vehicle is not None and vehicle.invID != -1:
            for _, tman in vehicle.crew:
                if tman.isInTank and tman.vehicleInvID != vehicle.invID:
                    continue
                if tman.descriptor.role == tankmanRole and tman.skills:
                    return True

        return False


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _isItemXPEnough(itemCD, vehicleCD, itemsCache=None):
    if itemCD is None or itemsCache is None:
        return False
    else:
        vehicle = getVehicleByIntCD(vehicleCD)
        if vehicle is None:
            return False
        stats = itemsCache.items.stats
        costs = g_techTreeDP.getUnlockPrices(itemCD)
        if vehicleCD in costs:
            xp = costs[vehicleCD]
        else:
            xp = 0
        return stats.vehiclesXPs.get(vehicleCD, 0) + stats.actualFreeXP >= xp


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _isItemMoneyEnough(itemCD, itemsCache=None):
    if itemCD is None or itemsCache is None:
        return False
    else:
        item = getItemByIntCD(itemCD)
        if item is not None:
            result, _ = item.mayPurchase(itemsCache.items.stats.money)
        else:
            result = False
        return result


def _isItemMayInstall(itemCD, vehicleCD):
    item = getItemByIntCD(itemCD)
    vehicle = getVehicleByIntCD(vehicleCD)
    if item is not None:
        result, _ = item.mayInstall(vehicle, 0)
    else:
        result = False
    return result


def _isItemInstalled(itemCD, vehicleCD):
    item = getItemByIntCD(itemCD)
    vehicle = getVehicleByIntCD(vehicleCD)
    if item is not None and vehicle is not None:
        result = item.isInstalled(vehicle)
    else:
        result = False
    return result


def _vehicleHasRegularConsumables(vehicleCD):
    vehicle = getVehicleByIntCD(vehicleCD)
    return False if vehicle is None or vehicle.invID == -1 else bool(filter(None, vehicle.consumables.installed))


def _vehicleHasOptionalDevices(vehicleCD):
    vehicle = getVehicleByIntCD(vehicleCD)
    return False if vehicle is None or vehicle.invID == -1 else bool(filter(None, vehicle.optDevices.installed))


def _isItemLevelEqual(itemCD, level):
    if level is None:
        return False
    else:
        item = getItemByIntCD(itemCD)
        if item is not None:
            result = item.level == level
        else:
            result = False
        return result


_ITEM_STATES = {CONDITION_STATE.SELECTED: _isItemSelected,
 CONDITION_STATE.PREMIUM: _isItemPremium,
 CONDITION_STATE.UNLOCKED: _isItemUnlocked,
 CONDITION_STATE.IN_INVENTORY: _isItemInInventory,
 CONDITION_STATE.CREW_HAS_ANY_SKILL: _isAnyCrewSkillLearned,
 CONDITION_STATE.XP_ENOUGH: _isItemXPEnough,
 CONDITION_STATE.MONEY_ENOUGH: _isItemMoneyEnough,
 CONDITION_STATE.LEVEL: _isItemLevelEqual,
 CONDITION_STATE.MAY_INSTALL: _isItemMayInstall,
 CONDITION_STATE.INSTALLED: _isItemInstalled,
 CONDITION_STATE.HAS_REGULAR_CONSUMABLES: _vehicleHasRegularConsumables,
 CONDITION_STATE.HAS_OPTIONAL_DEVICES: _vehicleHasOptionalDevices}

def getItemStateGetter(state):
    if state in _ITEM_STATES:
        getter = _ITEM_STATES[state]
    else:
        getter = None
    return getter
