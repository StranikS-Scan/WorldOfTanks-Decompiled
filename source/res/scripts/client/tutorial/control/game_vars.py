# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/control/game_vars.py
import types
from CurrentVehicle import g_currentVehicle
from gui.techtree.dumpers import StubDumper
from gui.techtree.research_items_data import ResearchItemsData
from gui.techtree.settings import NODE_STATE, RESEARCH_ITEMS
from gui.techtree.techtree_dp import g_techTreeDP
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IBootcampController
from tutorial.logger import LOG_ERROR
from tutorial.data.conditions import CONDITION_STATE
_RESEARCH_ITEM_TYPE_ORDER = dict(((itemTypeID, idx) for idx, itemTypeID in enumerate(RESEARCH_ITEMS)))
__all__ = ('getUnlockedItems', 'getItemByIntCD', 'getVehicleByIntCD', 'getItemStateGetter', 'getAttribute')

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


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _getTankmanID(vehicleCD, tankmanRole, itemsCache=None):
    if itemsCache is None:
        return
    else:
        vehicle = getVehicleByIntCD(vehicleCD)
        if vehicle is not None and vehicle.invID != -1:
            for _, tman in vehicle.crew:
                if tman.isInTank and tman.vehicleInvID != vehicle.invID:
                    continue
                if tman.descriptor.role == tankmanRole:
                    return tman.invID

        return


@dependency.replace_none_kwargs(bootcampCtrl=IBootcampController)
def _getBootcampNationID(bootcampCtrl=None):
    return None if bootcampCtrl is None else bootcampCtrl.nation


@dependency.replace_none_kwargs(bootcampCtrl=IBootcampController)
def _getBootcampNationDataField(fieldName, bootcampCtrl=None):
    if bootcampCtrl is None:
        return
    else:
        nationData = bootcampCtrl.nationData
        return None if nationData is None else nationData.get(fieldName, None)


def _getCurrentVehicleCD():
    return g_currentVehicle.item.intCD if g_currentVehicle.isPresent() else None


def _getCurrentResearchModule(column=None):
    column = int(column) if column is not None else None
    data = ResearchItemsData(StubDumper())
    try:
        data.setRootCD(g_currentVehicle.item.intCD)
        data.load()
        result = []
        for index, node in enumerate(data.getNodes()):
            if node is None:
                continue
            itemCD = node.getNodeCD()
            item = data.getItem(itemCD)
            if item is None or item.itemTypeID not in GUI_ITEM_TYPE.VEHICLE_MODULES:
                continue
            state = node.getState()
            if not NODE_STATE.isAvailable2Unlock(state):
                continue
            displayInfo = node.getDisplayInfo() or {}
            path = displayInfo.get('path') or ()
            if column is None or len(path) == column:
                order = _RESEARCH_ITEM_TYPE_ORDER.get(item.itemTypeID, len(RESEARCH_ITEMS))
                result.append((len(path),
                 order,
                 index,
                 itemCD))

        if result:
            return min(result)[3]
    finally:
        data.clear(full=True)

    return


def _getCurrentResearchVehicle():
    data = ResearchItemsData(StubDumper())
    try:
        data.setRootCD(g_currentVehicle.item.intCD)
        data.load()
        available = []
        fallback = []
        for index, node in enumerate(data.getNodes()):
            if node is None:
                continue
            itemCD = node.getNodeCD()
            item = data.getItem(itemCD)
            if item is None or item.itemTypeID != GUI_ITEM_TYPE.VEHICLE or item.isUnlocked:
                continue
            displayInfo = node.getDisplayInfo() or {}
            path = displayInfo.get('path') or ()
            candidate = (len(path), index, itemCD)
            if NODE_STATE.isAvailable2Unlock(node.getState()):
                available.append(candidate)
            fallback.append(candidate)

        if available:
            return min(available)[2]
        if fallback:
            return min(fallback)[2]
    finally:
        data.clear(full=True)

    return


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


def _vehicleHasAllEquipmentInstalled(vehicleCD):
    vehicle = getVehicleByIntCD(vehicleCD)
    if vehicle is None or vehicle.invID == -1:
        return False
    else:
        installed = vehicle.consumables.installed
        return bool(installed) and all(installed)


def _vehicleHasOptionalDevices(vehicleCD):
    vehicle = getVehicleByIntCD(vehicleCD)
    return False if vehicle is None or vehicle.invID == -1 else bool(filter(None, vehicle.optDevices.installed))


def _vehicleHasMultipliedXP(vehicleCD):
    vehicle = getVehicleByIntCD(vehicleCD)
    return False if vehicle is None or vehicle.invID == -1 else vehicle.dailyXPFactor > 1


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


def _isItemLevelInRange(itemCD, minLevel, maxLevel):
    if minLevel is None or maxLevel is None:
        return False
    else:
        item = getItemByIntCD(itemCD)
        if item is not None:
            result = int(minLevel) <= item.level <= int(maxLevel)
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
 CONDITION_STATE.LEVEL_RANGE: _isItemLevelInRange,
 CONDITION_STATE.MAY_INSTALL: _isItemMayInstall,
 CONDITION_STATE.INSTALLED: _isItemInstalled,
 CONDITION_STATE.HAS_REGULAR_CONSUMABLES: _vehicleHasRegularConsumables,
 CONDITION_STATE.ALL_EQUIPMENT_INSTALLED: _vehicleHasAllEquipmentInstalled,
 CONDITION_STATE.HAS_OPTIONAL_DEVICES: _vehicleHasOptionalDevices,
 CONDITION_STATE.HAS_MULTIPLIED_XP: _vehicleHasMultipliedXP}

def getItemStateGetter(state):
    if state in _ITEM_STATES:
        getter = _ITEM_STATES[state]
    else:
        getter = None
    return getter


_AVAILABLE_ATTRIBUTES = {'TankmanID': _getTankmanID,
 'BootcampNationID': _getBootcampNationID,
 'BootcampNationDataField': _getBootcampNationDataField,
 'CurrentVehicleCD': _getCurrentVehicleCD,
 'CurrentResearchModule': _getCurrentResearchModule,
 'CurrentResearchTopLockedModule': _getCurrentResearchModule,
 'CurrentResearchVehicle': _getCurrentResearchVehicle}

def getAttribute(name, *args):
    if name in _AVAILABLE_ATTRIBUTES:
        try:
            result = _AVAILABLE_ATTRIBUTES[name](*args)
        except Exception as e:
            LOG_ERROR('Can not get game attribute', name, e.message)
            result = None

    else:
        LOG_ERROR('Game attribute is not found', name)
        result = None
    return result
