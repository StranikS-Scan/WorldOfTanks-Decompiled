# Embedded file name: scripts/client/tutorial/control/game_vars.py
import types
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.view.lobby.techtree.settings import RESEARCH_ITEMS
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.shared import g_itemsCache, REQ_CRITERIA
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters.ItemsRequester import RESEARCH_CRITERIA
from tutorial.logger import LOG_ERROR
from tutorial.data.conditions import CONDITION_STATE
__all__ = ('getTutorialCompleted', 'getRandomBattlesCount', 'getUnlockedItems', 'getFreeVehiclesSlots', 'getFreeXP', 'getItemByIntCD', 'getVehicleByIntCD', 'getVehiclesByLevel', 'getPremiumExpiryTime', 'getCurrentVehicleLevel', 'isCurrentVehiclePremium', 'getCurrentVehicleViewState', 'getTankmanCurrentPrice', 'getTankmanDefaultPrice', 'getItemStateGetter', 'getAttribute')

def getTutorialsCompleted():
    return g_itemsCache.items.stats.tutorialsCompleted


def getRandomBattlesCount():
    dossier = g_itemsCache.items.getAccountDossier()
    if dossier is not None:
        count = dossier.getRandomStats().getBattlesCount()
    else:
        count = 0
    return count


def getUnlockedItems():
    return g_itemsCache.items.stats.unlocks


def getFreeVehiclesSlots():
    return g_itemsCache.items.stats.vehicleSlots


def getFreeXP():
    return g_itemsCache.items.stats.actualFreeXP


def getItemByIntCD(intCD):
    if intCD is None or type(intCD) not in (types.IntType, types.LongType, types.FloatType):
        return
    else:
        return g_itemsCache.items.getItemByCD(intCD)


def getVehicleByIntCD(intCD):
    vehicle = getItemByIntCD(intCD)
    if vehicle is not None and vehicle.itemTypeID != GUI_ITEM_TYPE.VEHICLE:
        LOG_ERROR('IntCD of vehicle is invalid', intCD)
        vehicle = None
    return vehicle


def getVehiclesByLevel(level, researchOnly = True):
    criteria = REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.LEVEL(level)
    if researchOnly:
        criteria |= RESEARCH_CRITERIA.VEHICLE_TO_UNLOCK
    return g_itemsCache.items.getVehicles(criteria=criteria)


def getPremiumExpiryTime():
    return g_itemsCache.items.stats.premiumExpiryTime


def getCurrentVehicleLevel():
    if g_currentVehicle.isPresent():
        return g_currentVehicle.item.level
    else:
        return None
        return None


def getCurrentVehicleState():
    if g_currentVehicle.isPresent():
        state, _ = g_currentVehicle.item.getState()
        return state
    else:
        return None
        return None


def isCurrentVehiclePremium():
    if g_currentVehicle.isPresent():
        return g_currentVehicle.item.isPremium
    else:
        return None
        return None


def isCurrentVehicleRented():
    if g_currentVehicle.isPresent():
        return g_currentVehicle.item.isRented
    else:
        return None
        return None


def getCurrentVehicleViewState():
    return g_currentVehicle.getViewState()


def _getTankmanPrice(index, prices):
    if index < len(prices):
        price = prices[index]
        result = (price['gold'], price['credits'])
    else:
        result = (0, 0)
    return result


def getTankmanCurrentPrice(index):
    return _getTankmanPrice(index, g_itemsCache.items.shop.tankmanCostWithGoodyDiscount)


def getTankmanDefaultPrice(index):
    return _getTankmanPrice(index, g_itemsCache.items.shop.defaults.tankmanCost)


def _getCurrentVehicleCD():
    if g_currentVehicle.isPresent():
        return g_currentVehicle.item.intCD
    else:
        return None
        return None


_NOT_FOUND_INDEX = len(RESEARCH_ITEMS)

def _researchItemComparator(item, other):
    if item.itemTypeID in RESEARCH_ITEMS:
        itemIdx = RESEARCH_ITEMS.index(item.itemTypeID)
    else:
        itemIdx = len(RESEARCH_ITEMS)
    if other.itemTypeID in RESEARCH_ITEMS:
        otherIdx = RESEARCH_ITEMS.index(other.itemTypeID)
    else:
        otherIdx = len(RESEARCH_ITEMS)
    result = cmp(itemIdx, otherIdx)
    if not result:
        result = cmp(item.level, other.level)
    return result


def _getNextToUnlockItemCD(intCD):
    vehicle = getVehicleByIntCD(intCD)
    if vehicle is None:
        return False
    else:
        stats = g_itemsCache.items.stats
        items = g_techTreeDP.getAllPossibleItems2Unlock(vehicle, stats.unlocks)
        getter = g_itemsCache.items.getItemByCD
        result = []
        for itemTypeCD, unlockProps in items.iteritems():
            item = getter(itemTypeCD)
            if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
                continue
            result.append(item)

        if result:
            result = sorted(result, cmp=_researchItemComparator)
            intCD = result[0].intCD
        else:
            intCD = None
        return intCD


def _getNextToBuyItemCD(intCD):
    vehicle = getVehicleByIntCD(intCD)
    if vehicle is None:
        return False
    else:
        stats = g_itemsCache.items.stats
        items = g_techTreeDP.getUnlockedVehicleItems(vehicle, stats.unlocks)
        getter = g_itemsCache.items.getItemByCD
        result = []
        for itemTypeCD, unlockProps in items.iteritems():
            item = getter(itemTypeCD)
            if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
                continue
            if item.isInInventory or item.isInstalled(vehicle):
                continue
            result.append(item)

        if result:
            result = sorted(result, cmp=_researchItemComparator)
            intCD = result[0].intCD
        else:
            intCD = None
        return intCD


def _getEquipmentForCreditsCD(tag):
    if tag is None:
        return
    else:
        equipments = g_itemsCache.items.getItems(GUI_ITEM_TYPE.EQUIPMENT, REQ_CRITERIA.CUSTOM(lambda eq: tag in eq.tags and eq.buyPrice[0] > 0))
        if equipments:
            result, _ = equipments.popitem()
        else:
            result = None
        return result


def _getOptionalDeviceCD(name):
    if name is None:
        return
    else:
        opts = g_itemsCache.items.getItems(GUI_ITEM_TYPE.OPTIONALDEVICE, REQ_CRITERIA.CUSTOM(lambda opt: name in opt.name))
        if opts:
            result, _ = opts.popitem()
        else:
            result = None
        return result


def _getInventoryVehicleCDByLevel(level):
    vehicles = getVehiclesByLevel(level, researchOnly=False)
    if vehicles:
        result, _ = vehicles.popitem()
    else:
        result = None
    return result


def _getInventoryPremiumVehicleCD():
    vehicles = g_itemsCache.items.getVehicles(criteria=REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.PREMIUM)
    if vehicles:
        result, _ = vehicles.popitem()
    else:
        result = None
    return result


def _isItemSelected(intCD):
    if intCD is None:
        return False
    elif g_currentVehicle.isPresent():
        return g_currentVehicle.item.intCD == intCD
    else:
        return False
        return


def _isItemPremium(intCD):
    if intCD is None:
        return False
    else:
        vehicle = getVehicleByIntCD(intCD)
        if vehicle is not None:
            return vehicle.isPremium
        return False
        return


def _isItemUnlocked(intCD):
    if intCD is None:
        return False
    else:
        return intCD in getUnlockedItems()


def _isItemXPEnough(itemCD, vehicleCD):
    if itemCD is None:
        return False
    else:
        vehicle = getVehicleByIntCD(vehicleCD)
        if vehicle is None:
            return False
        stats = g_itemsCache.items.stats
        costs = g_techTreeDP.getUnlockPrices(itemCD)
        if vehicleCD in costs:
            xp = costs[vehicleCD]
        else:
            xp = 0
        return stats.vehiclesXPs.get(vehicleCD, 0) + stats.actualFreeXP >= xp


def _isItemMoneyEnough(itemCD):
    item = getItemByIntCD(itemCD)
    if item is not None:
        result, _ = item.mayPurchase(g_itemsCache.items.stats.money)
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
 CONDITION_STATE.XP_ENOUGH: _isItemXPEnough,
 CONDITION_STATE.MONEY_ENOUGH: _isItemMoneyEnough,
 CONDITION_STATE.LEVEL: _isItemLevelEqual,
 CONDITION_STATE.MAY_INSTALL: _isItemMayInstall}

def getItemStateGetter(state):
    if state in _ITEM_STATES:
        getter = _ITEM_STATES[state]
    else:
        getter = None
    return getter


_AVAILABLE_ATTRIBUTES = {'CurrentVehicleCD': _getCurrentVehicleCD,
 'NextToUnlockItemCD': _getNextToUnlockItemCD,
 'NextToBuyItemCD': _getNextToBuyItemCD,
 'EquipmentForCreditsCD': _getEquipmentForCreditsCD,
 'OptionalDeviceCD': _getOptionalDeviceCD,
 'InventoryVehicleCDByLevel': _getInventoryVehicleCDByLevel,
 'PremiumVehicleCD': _getInventoryPremiumVehicleCD}

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
