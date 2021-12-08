# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/ny_views_helpers.py
import logging
import typing
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared.event_dispatcher import showBrowserOverlayView
from helpers import time_utils
from new_year.ny_constants import PERCENT, NY_GIFT_SYSTEM_TOKEN_PREFIX, NY_GIFT_SYSTEM_SUBPROGRESS_PREFIX, NY_GIFT_SYSTEM_PROGRESSION_PREFIX
from new_year.vehicle_branch import getSlotBonusChoicesConfig
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from typing import Union
    from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_vehicle_slot_tooltip_model import NyVehicleSlotTooltipModel
    from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_tank_extra_slot_tooltip_model import NyTankExtraSlotTooltipModel
    from gui.server_events.event_items import TokenQuest

def setSlotTooltipBonuses(viewModel):
    for bonusType, bonusValue in getSlotBonusChoicesConfig().itervalues():
        if bonusValue:
            mutatorName = 'set{}{}'.format(bonusType[:1].upper(), bonusType[1:])
            setValue = getattr(viewModel, mutatorName, None)
            if setValue is None:
                _logger.warning('%s object has no attribute %s.', viewModel, mutatorName)
                continue
            if not callable(setValue):
                _logger.warning('%s.%s is not callable.', viewModel, mutatorName)
                continue
            setValue(PERCENT * bonusValue)

    return


def getGiftsTokensCountByID(questID):
    return int(questID.split(':')[-1]) if questID.startswith(NY_GIFT_SYSTEM_TOKEN_PREFIX) else 0


def giftsPogressQuestFilter(quest):
    return quest.getID().startswith(NY_GIFT_SYSTEM_PROGRESSION_PREFIX)


def giftsSubprogressQuestFilter(quest):
    return quest.getID().startswith(NY_GIFT_SYSTEM_SUBPROGRESS_PREFIX)


def getTimerGameDayLeft():
    return time_utils.getDayTimeLeft() + 1


def showInfoVideo():
    url = GUI_SETTINGS.newYearInfo.get('baseURL')
    if url is None:
        _logger.error('newYearInfo.baseURL is missed')
    showBrowserOverlayView(url, alias=VIEW_ALIAS.NY_BROWSER_VIEW)
    return
