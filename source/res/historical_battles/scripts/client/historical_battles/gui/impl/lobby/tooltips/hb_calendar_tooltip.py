# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/tooltips/hb_calendar_tooltip.py
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles, time_formatters
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency, time_utils
from historical_battles.skeletons.gui.game_event_controller import IGameEventController

class HBCalendarTooltipData(BlocksTooltipData):
    __gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, context):
        super(HBCalendarTooltipData, self).__init__(context, None)
        self.item = None
        self._setContentMargin(top=13, left=20, bottom=10, right=5)
        self._setMargins(afterBlock=2)
        self._setWidth(264)
        return

    def _packBlocks(self, *args, **kwargs):
        items = super(HBCalendarTooltipData, self)._packBlocks()
        buildUpItems = []
        buildUpItems.append(formatters.packTextBlockData(text=text_styles.middleTitle(backport.text(R.strings.hb_tooltips.calendarTooltip.title())), padding=formatters.packPadding(bottom=3)))
        startDate = time_utils.getTimeStructInLocal(self.__gameEventController.getEventStartTime())
        endDate = time_utils.getTimeStructInLocal(self.__gameEventController.getEventFinishTime())
        buildUpItems.append(formatters.packTextBlockData(text=text_styles.main(backport.text(R.strings.hb_tooltips.calendarTooltip.duration(), period=text_styles.neutral(backport.text(R.strings.hb_tooltips.calendarTooltip.period(), start=backport.text(R.strings.hb_tooltips.calendarTooltip.date(), day=startDate.tm_mday, month=backport.text(R.strings.menu.dateTime.months.num(startDate.tm_mon)()), time=time_formatters.formatDate('%H:%M', self.__gameEventController.getEventStartTime())), end=backport.text(R.strings.hb_tooltips.calendarTooltip.date(), day=endDate.tm_mday, month=backport.text(R.strings.menu.dateTime.months.num(endDate.tm_mon)()), time=time_formatters.formatDate('%H:%M', self.__gameEventController.getEventFinishTime()))))))))
        items.append(formatters.packBuildUpBlockData(buildUpItems))
        return items
