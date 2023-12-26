# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/seniority_awards/seniority_awards_helper.py
import logging
import BigWorld
from account_helpers.settings_core.settings_constants import SeniorityAwardsStorageKeys
from frameworks.wulf import ViewFlags
from gui import SystemMessages
from gui.impl import backport
from gui.impl.auxiliary.rewards_helper import getRewardRendererModelPresenter, DEF_COMPENSATION_PRESENTERS
from gui.impl.auxiliary.tooltips.compensation_tooltip import CompensationTooltipContent, VehicleCompensationTooltipContent
from gui.impl.gen import R
from gui.impl.gen.view_models.views.loot_box_compensation_tooltip_model import LootBoxCompensationTooltipModel
from gui.impl.lobby.seniority_awards.seniority_awards_sounds import playSound, LootBoxViewEvents
from gui.shared import g_eventBus
from gui.shared.events import GameEvent
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import ISeniorityAwardsController
_logger = logging.getLogger(__name__)

def getVehicleCD(value):
    try:
        vehicleCD = int(value)
    except ValueError:
        _logger.warning('Wrong vehicle compact descriptor: %s!', value)
        return None

    return vehicleCD
    return None


@dependency.replace_none_kwargs(settings=ISettingsCore)
def isSeniorityAwardsSystemNotificationShowed(notification, settings=None):
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    return settings.serverSettings.getSection(SETTINGS_SECTIONS.SENIORITY_AWARDS_STORAGE).get(notification)


def setSeniorityAwardEventStateSetting(value):
    setSeniorityAwardsServerSetting({SeniorityAwardsStorageKeys.SENIORITY_AWARDS_ON_PAUSE_NOTIFICATION_SHOWED: value})


@dependency.replace_none_kwargs(settings=ISettingsCore)
def setSeniorityAwardsServerSetting(settingsSection, settings=None):
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    settings.serverSettings.setSections([SETTINGS_SECTIONS.SENIORITY_AWARDS_STORAGE], settingsSection)


@dependency.replace_none_kwargs(seniorityAwardsController=ISeniorityAwardsController)
def getRewardCategoryForUI(seniorityAwardsController=None):
    return '{}_{}'.format(seniorityAwardsController.rewardCategory, seniorityAwardsController.testGroup) if seniorityAwardsController.rewardCategory and seniorityAwardsController.testGroup else seniorityAwardsController.rewardCategory or seniorityAwardsController.testGroup


def showRestrictedSysMessage():

    def _showRestrictedSysMessage():
        SystemMessages.pushMessage(text=backport.text(R.strings.lootboxes.restrictedMessage.body()), type=SystemMessages.SM_TYPE.ErrorHeader, priority=NotificationPriorityLevel.HIGH, messageData={'header': backport.text(R.strings.lootboxes.restrictedMessage.header())})

    BigWorld.callback(0.0, _showRestrictedSysMessage)


def showVehicleSelectionTimeoutError():
    SystemMessages.pushI18nMessage('#system_messages:seniority_awards/selection_timeout', type=SystemMessages.SM_TYPE.Warning, priority='medium')


def showVehicleSelectionMultipleTokensError():
    SystemMessages.pushI18nMessage('#system_messages:seniority_awards/selection_multiple_tokens', type=SystemMessages.SM_TYPE.Error, priority='medium')


def fireCloseToHangar():
    playSound(LootBoxViewEvents.ENTRY_VIEW_EXIT)
    _closeLootBoxWindows()


def getLootboxRendererModelPresenter(reward):
    return getRewardRendererModelPresenter(reward, None, DEF_COMPENSATION_PRESENTERS)


def getRewardTooltipContent(event):
    tContent = R.views.common.tooltip_window.loot_box_compensation_tooltip.LootBoxCompensationTooltipContent()
    if event.contentID == tContent:
        tooltipData = {'iconBefore': event.getArgument('iconBefore', ''),
         'labelBefore': event.getArgument('labelBefore', ''),
         'iconAfter': event.getArgument('iconAfter', ''),
         'labelAfter': event.getArgument('labelAfter', ''),
         'bonusName': event.getArgument('bonusName', '')}
        return CompensationTooltipContent(content=tContent, viewFlag=ViewFlags.VIEW, model=LootBoxCompensationTooltipModel, **tooltipData)
    else:
        tContent = R.views.common.tooltip_window.loot_box_compensation_tooltip.LootBoxVehicleCompensationTooltipContent()
        if event.contentID == tContent:
            tooltipData = {'iconBefore': event.getArgument('iconBefore', ''),
             'labelBefore': event.getArgument('labelBefore', ''),
             'iconAfter': event.getArgument('iconAfter', ''),
             'labelAfter': event.getArgument('labelAfter', ''),
             'bonusName': event.getArgument('bonusName', ''),
             'vehicleName': event.getArgument('vehicleName', ''),
             'vehicleType': event.getArgument('vehicleType', ''),
             'isElite': event.getArgument('isElite', True),
             'vehicleLvl': event.getArgument('vehicleLvl', '')}
            return VehicleCompensationTooltipContent(**tooltipData)
        return None


def _closeLootBoxWindows():
    g_eventBus.handleEvent(GameEvent(GameEvent.CLOSE_LOOT_BOX_WINDOWS))
