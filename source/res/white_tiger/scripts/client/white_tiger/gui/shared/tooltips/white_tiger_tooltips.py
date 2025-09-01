# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/shared/tooltips/white_tiger_tooltips.py
from frameworks.wulf import ViewSettings
from gui.battle_pass.battle_pass_helpers import getFormattedTimeLeft
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.shared.formatters import text_styles
from gui.shared.tooltips import WulfTooltipData, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from gui.Scaleform.daapi.view.lobby.formatters.tooltips import packTimeTableHeaderBlock, packCalendarBlock
from helpers import dependency, time_utils
from white_tiger.gui.impl.gen.view_models.views.lobby.tooltips.stamp_tooltip_view_model import StampTooltipViewModel
from white_tiger.gui.white_tiger_gui_constants import WHITE_TIGER_BATTLES_TICKET, WHITE_TIGER_STAMP, SELECTOR_BATTLE_TYPES
from white_tiger.gui.impl.lobby.tooltips.ticket_tooltip_view import TicketTooltipView
from white_tiger.skeletons.white_tiger_controller import IWhiteTigerController
from white_tiger.gui.impl.gen.view_models.views.lobby.mode_selector.tooltips.mode_selector_tooltips_constants import ModeSelectorTooltipsConstants
import logging
_logger = logging.getLogger(__name__)

class WhiteTigerTicketTooltipWindowData(WulfTooltipData):

    def __init__(self, context):
        super(WhiteTigerTicketTooltipWindowData, self).__init__(context, WHITE_TIGER_BATTLES_TICKET)

    def getTooltipContent(self, *args, **kwargs):
        return TicketTooltipView()


class WhiteTigerStampTooltipWindowData(WulfTooltipData):

    def __init__(self, context):
        super(WhiteTigerStampTooltipWindowData, self).__init__(context, WHITE_TIGER_STAMP)

    def getTooltipContent(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.white_tiger.mono.lobby.tooltips.stamp_tooltip(), model=StampTooltipViewModel())
        return ViewImpl(settings)


class WhiteTigerBattleCalendar(BlocksTooltipData):
    __wtCtrl = dependency.descriptor(IWhiteTigerController)
    _TOOLTIP_TYPE = ModeSelectorTooltipsConstants.WHITE_TIGER_BATTLES_CALENDAR_TOOLTIP

    def __init__(self, context):
        super(WhiteTigerBattleCalendar, self).__init__(context, ModeSelectorTooltipsConstants.WHITE_TIGER_BATTLES_CALENDAR_TOOLTIP)
        self._setWidth(320)

    def _packBlocks(self, *args, **kwargs):
        blocks = super(WhiteTigerBattleCalendar, self)._packBlocks(args, kwargs)
        if self.__wtCtrl.isAvailable():
            blocks.append(formatters.packBuildUpBlockData([self.__packHeader(), packTimeTableHeaderBlock(SELECTOR_BATTLE_TYPES.WHITE_TIGER), formatters.packBuildUpBlockData(packCalendarBlock(self.__wtCtrl, time_utils.getCurrentTimestamp(), SELECTOR_BATTLE_TYPES.WHITE_TIGER))]))
        return blocks

    def __packHeader(self):
        currentSeason = self.__wtCtrl.getCurrentSeason()
        return self.__packNextSeasonHeader(self.__wtCtrl.getNextSeason()) if not currentSeason else self.__packCurrentSeasonHeader(currentSeason)

    def __packCurrentSeasonHeader(self, currentSeason):
        cycleEndTime = currentSeason.getCycleEndDate()
        if cycleEndTime is None:
            _logger.error('There is not active cycle of the event battles')
            return ''
        else:
            timeLeft = getFormattedTimeLeft(max(0, cycleEndTime - time_utils.getServerUTCTime()))
            return formatters.packTextBlockData(text_styles.highlightText(backport.text(R.strings.white_tiger_lobby.selectorTooltip.timeTable.tillEnd(), time=timeLeft)), padding=formatters.packPadding(bottom=15))

    def __packNextSeasonHeader(self, nextSeason):
        nextCycle = nextSeason.getNextByTimeCycle(time_utils.getCurrentLocalServerTimestamp())
        time = backport.getDateTimeFormat(time_utils.makeLocalServerTime(nextCycle.startDate))
        return formatters.packTextBlockData(text_styles.highlightText(backport.text(R.strings.white_tiger_lobby.selectorTooltip.unavailable.nextSeason(), time=time)), padding=formatters.packPadding(bottom=15))
