# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/resource_well/resource_well_helpers.py
import logging
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import GUI_START_BEHAVIOR
from account_helpers.settings_core.settings_constants import GuiSettingsBehavior
from constants import RESOURCE_WELL_FORBIDDEN_TOKEN
from gui.resource_well.resource_well_constants import ProgressionState, CHANNEL_NAME_PREFIX
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency, time_utils
from shared_utils import findFirst
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IResourceWellController
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.customization.c11n_items import Style
_logger = logging.getLogger(__name__)

@dependency.replace_none_kwargs(resourceWell=IResourceWellController)
def isEventEndingsSoon(resourceWell=None):
    return resourceWell.getReminderTime() <= time_utils.getServerUTCTime()


@dependency.replace_none_kwargs(resourceWell=IResourceWellController)
def getProgressionState(resourceWell=None):
    if isForbiddenAccount(resourceWell=resourceWell):
        return ProgressionState.FORBIDDEN
    if resourceWell.isRewardCountAvailable() and not resourceWell.getRewardLeftCount(True) and not resourceWell.getRewardLeftCount(False):
        return ProgressionState.NO_VEHICLES
    return ProgressionState.ACTIVE if resourceWell.getCurrentPoints() else ProgressionState.NO_PROGRESS


@dependency.replace_none_kwargs(resourceWell=IResourceWellController)
def getForbiddenAccountToken(resourceWell=None):
    return RESOURCE_WELL_FORBIDDEN_TOKEN.format(resourceWell.getSeason())


@dependency.replace_none_kwargs(itemsCache=IItemsCache, resourceWell=IResourceWellController)
def isForbiddenAccount(itemsCache=None, resourceWell=None):
    return itemsCache.items.tokens.getToken(getForbiddenAccountToken(resourceWell=resourceWell)) is not None


@dependency.replace_none_kwargs(resourceWell=IResourceWellController, itemsCache=IItemsCache)
def getSerialNumber(resourceWell=None, itemsCache=IItemsCache):
    style = getRewardStyle(resourceWell=resourceWell)
    return itemsCache.items.inventory.getC11nSerialNumber(itemCD=style.intCD) or ''


@dependency.replace_none_kwargs(resourceWell=IResourceWellController)
def getAvailableRewardData(resourceWell=None):
    rewards = resourceWell.getRewards()
    if resourceWell.getRewardLeftCount(True):
        return (findFirst(lambda (rewardID, reward): reward.isSerial, rewards.iteritems())[0], True)
    elif resourceWell.getRewardLeftCount(False):
        return (findFirst(lambda (rewardID, reward): not reward.isSerial, rewards.iteritems())[0], False)
    else:
        _logger.warning('No available rewards for resource well!')
        return (None, False)


@dependency.replace_none_kwargs(resourceWell=IResourceWellController, c11nService=ICustomizationService)
def getRewardStyle(resourceWell=None, c11nService=None):
    return c11nService.getItemByID(GUI_ITEM_TYPE.STYLE, resourceWell.getRewardStyleID())


def isIntroShown():
    settingsCore = dependency.instance(ISettingsCore)
    defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
    settings = settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
    return settings.get(GuiSettingsBehavior.RESOURCE_WELL_INTRO_SHOWN, False)


def setIntroShown():
    settingsCore = dependency.instance(ISettingsCore)
    defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
    settings = settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
    settings[GuiSettingsBehavior.RESOURCE_WELL_INTRO_SHOWN] = True
    settingsCore.serverSettings.setSectionSettings(GUI_START_BEHAVIOR, settings)


@dependency.replace_none_kwargs(resourceWell=IResourceWellController)
def getNumberChannelName(isSerial, resourceWell=None):
    return CHANNEL_NAME_PREFIX + resourceWell.getRewardSequence(isSerial)


@dependency.replace_none_kwargs(resourceWell=IResourceWellController)
def isResourceWellRewardVehicle(vehicleCD, resourceWell=None):
    return resourceWell.isActive() and resourceWell.getRewardVehicle() == vehicleCD
