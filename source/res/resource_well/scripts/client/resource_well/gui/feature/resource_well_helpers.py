# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/feature/resource_well_helpers.py
import logging
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import RESOURCE_WELL_END_SHOWN, RESOURCE_WELL_START_SHOWN, RESOURCE_WELL_NOTIFICATIONS
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency, time_utils
from resource_well.gui.feature.constants import CHANNEL_NAME_PREFIX, PurchaseMode
from resource_well.gui.impl.gen.view_models.views.lobby.enums import EventMode
from resource_well.gui.impl.gen.view_models.views.lobby.vehicle_counter_model import VehicleCounterModel
from resource_well_common.feature_constants import RESOURCE_WELL_FORBIDDEN_TOKEN
from shared_utils import findFirst
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.resource_well import IResourceWellController
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Optional, List
    from gui.shared.gui_items.customization.c11n_items import Style
    from gui.shared.gui_items.Vehicle import Vehicle
    from resource_well.helpers.server_settings import RewardConfig
_logger = logging.getLogger(__name__)
_PurchaseModeToEventModeMap = {PurchaseMode.ONE_SERIAL_PRODUCT: EventMode.ONE_SERIAL_PRODUCT,
 PurchaseMode.SEQUENTIAL_PRODUCT: EventMode.SEQUENTIAL_PRODUCT,
 PurchaseMode.TWO_PARALLEL_PRODUCTS: EventMode.TWO_PARALLEL_PRODUCTS}

def convertPurchaseToEventMode(mode):
    return _PurchaseModeToEventModeMap.get(mode, EventMode.ONE_SERIAL_PRODUCT)


@dependency.replace_none_kwargs(resourceWell=IResourceWellController)
def isEventEndingsSoon(resourceWell=None):
    return resourceWell.config.remindTime <= time_utils.getServerUTCTime()


@dependency.replace_none_kwargs(resourceWell=IResourceWellController)
def getForbiddenAccountToken(resourceWell=None):
    return RESOURCE_WELL_FORBIDDEN_TOKEN.format(resourceWell.config.season)


@dependency.replace_none_kwargs(resourceWell=IResourceWellController, itemsCache=IItemsCache)
def getSerialNumber(rewardID, resourceWell=None, itemsCache=IItemsCache):
    style = getRewardStyle(rewardID, resourceWell=resourceWell)
    serialNumber = None
    if style is not None:
        serialNumber = itemsCache.items.inventory.getC11nSerialNumber(itemCD=style.intCD)
    return serialNumber or ''


@dependency.replace_none_kwargs(resourceWell=IResourceWellController)
def getNextSerialRewardID(rewardID, resourceWell=None):
    mode = resourceWell.getPurchaseMode()
    if mode is not PurchaseMode.SEQUENTIAL_PRODUCT:
        return None
    else:
        result = findFirst(lambda item: item[1].availableAfter == rewardID, resourceWell.config.rewards.items())
        return result[0] if result is not None else None


@dependency.replace_none_kwargs(resourceWell=IResourceWellController, c11nService=ICustomizationService)
def getRewardStyle(rewardID, resourceWell=None, c11nService=None):
    styleID = resourceWell.getRewardStyleID(rewardID)
    return None if styleID is None else c11nService.getItemByID(GUI_ITEM_TYPE.STYLE, styleID)


@dependency.replace_none_kwargs(resourceWell=IResourceWellController)
def hasRequiredStyle(rewardID, rewardConfig=None, resourceWell=None):
    if rewardConfig is None:
        rewardConfig = resourceWell.config.getRewardConfig(rewardID)
    if not rewardConfig.isSerial:
        return True
    else:
        style = getRewardStyle(rewardID, resourceWell=resourceWell)
        return style.fullCount() > 0 if style is not None else False


@dependency.replace_none_kwargs(resourceWell=IResourceWellController)
def getNumberChannelName(rewardID, resourceWell=None):
    return CHANNEL_NAME_PREFIX + resourceWell.getRewardSequence(rewardID)


@dependency.replace_none_kwargs(resourceWell=IResourceWellController)
def fillVehicleCounter(rewardID, vehicleCounterModel, resourceWell=None):
    rewardConfig = resourceWell.config.getRewardConfig(rewardID)
    vehicleCounterModel.setVehicleCount(resourceWell.getRewardLeftCount(rewardID))
    vehicleCounterModel.setIsSerial(rewardConfig.isSerial)
    vehicleCounterModel.setIsVehicleCountAvailable(resourceWell.isRewardCountAvailable(rewardID))


@dependency.replace_none_kwargs(resourceWell=IResourceWellController)
def getRewardVehiclesInInventory(resourceWell=None):
    result = []
    for rewardID in resourceWell.config.rewards:
        rewardVehicle = resourceWell.getRewardVehicle(rewardID)
        if rewardVehicle and rewardVehicle.isInInventory:
            result.append(rewardVehicle)

    return result


def getNotificationSettings():
    defaults = AccountSettings.getNotificationDefault(RESOURCE_WELL_NOTIFICATIONS)
    settings = AccountSettings.getNotifications(RESOURCE_WELL_NOTIFICATIONS, defaults)
    return settings


@dependency.replace_none_kwargs(resourceWell=IResourceWellController)
def isNotificationShown(sectionName, resourceWell=None):
    season = resourceWell.config.season
    settings = getNotificationSettings()
    return season in settings.get(sectionName, set())


@dependency.replace_none_kwargs(resourceWell=IResourceWellController)
def setIsNotificationShown(sectionName, resourceWell=None):
    settings = getNotificationSettings()
    settings[sectionName].add(resourceWell.config.season)
    AccountSettings.setNotifications(RESOURCE_WELL_NOTIFICATIONS, settings)


def isStartNotificationShown():
    return isNotificationShown(RESOURCE_WELL_START_SHOWN)


def isFinishNotificationShown():
    return isNotificationShown(RESOURCE_WELL_END_SHOWN)


def setStartNotificationShown():
    return setIsNotificationShown(RESOURCE_WELL_START_SHOWN)


def setFinishNotificationShown():
    return setIsNotificationShown(RESOURCE_WELL_END_SHOWN)
