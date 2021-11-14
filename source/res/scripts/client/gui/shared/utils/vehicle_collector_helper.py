# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/vehicle_collector_helper.py
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import MODULES_ANIMATION_SHOWN
from constants import MIN_VEHICLE_LEVEL
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers.dependency import replace_none_kwargs
from nations import ALL_NATIONS_INDEX
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.gui_items import ItemsCollection
    from gui.shared.gui_items.Vehicle import Vehicle

@replace_none_kwargs(itemsCache=IItemsCache)
def isAvailableForPurchase(vehicle, itemsCache=None):
    if vehicle is None:
        return False
    else:
        maxUnlockedLevel = itemsCache.items.stats.getMaxResearchedLevelByNations().get(vehicle.nationID, MIN_VEHICLE_LEVEL)
        return maxUnlockedLevel >= vehicle.level


def wasModulesAnimationShown():
    wasAnimShown = AccountSettings.getSettings(MODULES_ANIMATION_SHOWN)
    if not wasAnimShown:
        AccountSettings.setSettings(MODULES_ANIMATION_SHOWN, True)
    return wasAnimShown


@replace_none_kwargs(itemsCache=IItemsCache)
def getCollectibleVehicles(nationID=ALL_NATIONS_INDEX, itemsCache=None):
    criteria = REQ_CRITERIA.COLLECTIBLE if nationID == ALL_NATIONS_INDEX else REQ_CRITERIA.NATIONS((nationID,)) | REQ_CRITERIA.COLLECTIBLE | ~REQ_CRITERIA.HIDDEN
    items = itemsCache.items.getVehicles(criteria)
    return items


@replace_none_kwargs(itemsCache=IItemsCache)
def getCollectibleVehiclesInInventory(nationID=ALL_NATIONS_INDEX, itemsCache=None):
    if nationID == ALL_NATIONS_INDEX:
        criteria = REQ_CRITERIA.COLLECTIBLE | REQ_CRITERIA.INVENTORY
    else:
        criteria = REQ_CRITERIA.NATIONS((nationID,)) | REQ_CRITERIA.COLLECTIBLE | REQ_CRITERIA.INVENTORY
    items = itemsCache.items.getVehicles(criteria)
    return items


def hasCollectibleVehicles(nationID=ALL_NATIONS_INDEX):
    collectibleVehicles = getCollectibleVehicles(nationID)
    return len(collectibleVehicles) > 0


def isAllCollectionPurchased(nationID):
    purchasedVehicles = getCollectibleVehiclesInInventory(nationID)
    totalVehicles = getCollectibleVehicles(nationID)
    return totalVehicles != 0 and purchasedVehicles == totalVehicles
