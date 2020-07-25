# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/control/game_vars.py
import types
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.view.lobby.techtree.settings import RESEARCH_ITEMS
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.money import Money, MONEY_UNDEFINED, Currency
from gui.shared.utils.requesters.ItemsRequester import RESEARCH_CRITERIA
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IBootcampController
from tutorial.logger import LOG_ERROR
from tutorial.data.conditions import CONDITION_STATE
__all__ = ('getTutorialsCompleted', 'getRandomBattlesCount', 'getUnlockedItems', 'getFreeVehiclesSlots', 'getFreeXP', 'getItemByIntCD', 'getVehicleByIntCD', 'getVehiclesByLevel', 'getPremiumExpiryTime', 'getCurrentVehicleLevel', 'isCurrentVehiclePremium', 'getCurrentVehicleViewState', 'getTankmanCurrentPrice', 'getTankmanDefaultPrice', 'getItemStateGetter', 'getAttribute')

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getTutorialsCompleted(itemsCache=None):
    return itemsCache.items.stats.tutorialsCompleted if itemsCache is not None else 0


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getRandomBattlesCount(itemsCache=None):
    count = 0
    if itemsCache is not None:
        dossier = itemsCache.items.getAccountDossier()
        if dossier is not None:
            count = dossier.getRandomStats().getBattlesCount()
    return count


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getUnlockedItems(itemsCache=None):
    return itemsCache.items.stats.unlocks if itemsCache is not None else ()


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getFreeVehiclesSlots(itemsCache=None):
    return itemsCache.items.stats.vehicleSlots if itemsCache is not None else 0


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getFreeXP(itemsCache=None):
    return itemsCache.items.stats.actualFreeXP if itemsCache is not None else 0


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
def getVehiclesByLevel(level, researchOnly=True, itemsCache=None):
    criteria = REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.LEVEL(level)
    if researchOnly:
        criteria |= RESEARCH_CRITERIA.VEHICLE_TO_UNLOCK
    return itemsCache.items.getVehicles(criteria=criteria) if itemsCache is not None else {}


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getPremiumExpiryTime(itemsCache=None):
    return itemsCache.items.stats.activePremiumExpiryTime if itemsCache is not None else 0


def getCurrentVehicleLevel():
    return g_currentVehicle.item.level if g_currentVehicle.isPresent() else None


def getCurrentVehicleState():
    if g_currentVehicle.isPresent():
        state, _ = g_currentVehicle.item.getState()
        return state
    else:
        return None


def isCurrentVehiclePremium():
    return g_currentVehicle.item.isPremium if g_currentVehicle.isPresent() else None


def isCurrentVehicleRented():
    return g_currentVehicle.item.isRented if g_currentVehicle.isPresent() else None


def getCurrentVehicleViewState():
    return g_currentVehicle.getViewState()


def _getTankmanPrice(index, prices):
    return Money(**prices[index]) if index < len(prices) else MONEY_UNDEFINED


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getTankmanCurrentPrice(index, itemsCache=None):
    return _getTankmanPrice(index, itemsCache.items.shop.tankmanCostWithGoodyDiscount) if itemsCache is not None else MONEY_UNDEFINED


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getTankmanDefaultPrice(index, itemsCache=None):
    return _getTankmanPrice(index, itemsCache.items.shop.defaults.tankmanCost) if itemsCache is not None else MONEY_UNDEFINED


def _getCurrentVehicleCD():
    return g_currentVehicle.item.intCD if g_currentVehicle.isPresent() else None


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


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _getNextToUnlockItemCD(intCD, itemsCache=None):
    vehicle = getVehicleByIntCD(intCD)
    if vehicle is None or itemsCache is None:
        return
    else:
        stats = itemsCache.items.stats
        items = g_techTreeDP.getAllPossibleItems2Unlock(vehicle, stats.unlocks)
        getter = itemsCache.items.getItemByCD
        result = []
        for itemTypeCD, _ in items.iteritems():
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


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _getNextToBuyItemCD(intCD, itemsCache=None):
    vehicle = getVehicleByIntCD(intCD)
    if vehicle is None or itemsCache is None:
        return
    else:
        stats = itemsCache.items.stats
        items = g_techTreeDP.getUnlockedVehicleItems(vehicle, stats.unlocks)
        getter = itemsCache.items.getItemByCD
        result = []
        for itemTypeCD, _ in items.iteritems():
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


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _getEquipmentForCreditsCD(tag, itemsCache=None):
    if tag is None or itemsCache is None:
        return
    else:
        equipments = itemsCache.items.getItems(GUI_ITEM_TYPE.EQUIPMENT, REQ_CRITERIA.CUSTOM(lambda eq: tag in eq.tags and eq.buyPrices.hasPriceIn(Currency.CREDITS)))
        if equipments:
            result, _ = equipments.popitem()
        else:
            result = None
        return result


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _getOptionalDeviceCD(name, itemsCache=None):
    if name is None or itemsCache is None:
        return
    else:
        opts = itemsCache.items.getItems(GUI_ITEM_TYPE.OPTIONALDEVICE, REQ_CRITERIA.CUSTOM(lambda opt: name in opt.name))
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


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _getInventoryPremiumVehicleCD(itemsCache=None):
    if itemsCache is None:
        return
    else:
        vehicles = itemsCache.items.getVehicles(criteria=REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.PREMIUM)
        if vehicles:
            result, _ = vehicles.popitem()
        else:
            result = None
        return result


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


def _isCrewSkillLearned(intCD, tankmanRole, skillName):
    if intCD is None:
        return False
    else:
        vehicle = getItemByIntCD(intCD)
        if vehicle is not None and vehicle.invID != -1:
            for _, tman in vehicle.crew:
                if tman.isInTank and tman.vehicleInvID != vehicle.invID:
                    continue
                if tman.descriptor.role == tankmanRole:
                    for skill in tman.skills:
                        if skill.name == skillName:
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
 CONDITION_STATE.CREW_HAS_SKILL: _isCrewSkillLearned,
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


_AVAILABLE_ATTRIBUTES = {'CurrentVehicleCD': _getCurrentVehicleCD,
 'NextToUnlockItemCD': _getNextToUnlockItemCD,
 'NextToBuyItemCD': _getNextToBuyItemCD,
 'EquipmentForCreditsCD': _getEquipmentForCreditsCD,
 'OptionalDeviceCD': _getOptionalDeviceCD,
 'InventoryVehicleCDByLevel': _getInventoryVehicleCDByLevel,
 'PremiumVehicleCD': _getInventoryPremiumVehicleCD,
 'TankmanID': _getTankmanID,
 'BootcampNationID': _getBootcampNationID,
 'BootcampNationDataField': _getBootcampNationDataField}

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
