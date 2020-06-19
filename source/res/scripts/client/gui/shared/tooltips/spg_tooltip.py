# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/spg_tooltip.py
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency, time_utils
from skeletons.gui.game_control import IWOTSPGController
_TOOLTIP_MIN_WIDTH = 200

class SPGCalendarDayTooltip(BlocksTooltipData):
    _spgEvent = dependency.descriptor(IWOTSPGController)

    def __init__(self, ctx):
        super(SPGCalendarDayTooltip, self).__init__(ctx, TOOLTIP_TYPE.RANKED_CALENDAR_DAY)
        self._setContentMargin(top=18, left=20, bottom=18, right=20)
        self._setMargins(afterBlock=13)
        self._setWidth(_TOOLTIP_MIN_WIDTH)

    def _packBlocks(self, selectedTime):
        if selectedTime is None:
            selectedTime = time_utils.getCurrentLocalServerTimestamp()
        items = super(SPGCalendarDayTooltip, self)._packBlocks()
        blocks = [self.__packHeaderBlock()]
        serversPeriodsMapping = self._spgEvent.getPrimeTimesForDay(selectedTime)
        frmt = backport.getShortTimeFormat
        blocksCount = 0
        for serverName in sorted(serversPeriodsMapping.keys()):
            periodsStr = []
            dayPeriods = serversPeriodsMapping[serverName]
            if dayPeriods:
                for periodStart, periodEnd in dayPeriods:
                    periodsStr.append(backport.text(R.strings.ranked_battles.calendarDay.time(), start=frmt(periodStart), end=frmt(periodEnd)))

                blocksCount += 1
                blocks.append(self.__packServerTimeBlock(serverStr=text_styles.main(backport.text(R.strings.ranked_battles.calendarDay.serverName(), server=serverName)), timeStr=text_styles.stats('\n'.join(periodsStr))))

        if blocksCount == 0:
            return []
        else:
            items.append(formatters.packBuildUpBlockData(blocks, 13))
            return items

    def __packHeaderBlock(self):
        return formatters.packImageTextBlockData(title=text_styles.highTitle(backport.text(R.strings.ranked_battles.calendarDay.title())), img=backport.image(R.images.gui.maps.icons.buttons.calendar()), imgPadding=formatters.packPadding(top=5), txtPadding=formatters.packPadding(left=10))

    def __packServerTimeBlock(self, serverStr, timeStr):
        return formatters.packTextParameterBlockData(value=serverStr, name=timeStr, valueWidth=55, padding=formatters.packPadding(left=10))
