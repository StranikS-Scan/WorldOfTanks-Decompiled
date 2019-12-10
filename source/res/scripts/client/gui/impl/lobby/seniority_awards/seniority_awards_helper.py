# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/seniority_awards/seniority_awards_helper.py
import logging
import BigWorld
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
MAX_BOXES_TO_OPEN = 5
ADDITIONAL_AWARDS_COUNT = 6
_logger = logging.getLogger(__name__)

def showRestrictedSysMessage():

    def _showRestrictedSysMessage():
        SystemMessages.pushMessage(text=backport.text(R.strings.lootboxes.restrictedMessage.body()), type=SystemMessages.SM_TYPE.ErrorHeader, priority=NotificationPriorityLevel.HIGH, messageData={'header': backport.text(R.strings.lootboxes.restrictedMessage.header())})

    BigWorld.callback(0.0, _showRestrictedSysMessage)


def showSeniorityAwardsMultyOpen():
    from gui.impl.lobby.seniority_awards.seniority_awards_multi_open_view import SeniorityAwardsMultiOpenWindow
    window = SeniorityAwardsMultiOpenWindow()
    window.load()


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
