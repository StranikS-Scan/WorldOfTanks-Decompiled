# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/ranked/ranked_calendar_day_extended_tooltip.py
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.tooltips import formatters
from gui.shared.tooltips.ranked.ranked_calendar_day_tooltip import RankedCalendarDayTooltip
from helpers import dependency, time_utils
from skeletons.gui.game_control import IRankedBattlesController
_TOOLTIP_MIN_WIDTH = 200

class RankedCalendarDayExtendedTooltip(RankedCalendarDayTooltip):
    rankedController = dependency.descriptor(IRankedBattlesController)

    def _packBlocks(self, selectedTime):
        items = []
        if self._isSeasonEnded(selectedTime):
            return items
        blocks = []
        currentSeason = self.rankedController.getCurrentSeason()
        if currentSeason:
            daysLeft = int((currentSeason.getEndDate() - time_utils.getServerUTCTime()) / time_utils.ONE_DAY)
            seasonName = currentSeason.getUserName() or currentSeason.getNumber()
            blocks.append(self.__packTimeLeftBlock(seasonName, daysLeft))
        blocks.append(self._packHeaderBlock())
        blocks += self._packCalendarBlock(selectedTime)
        items.append(formatters.packBuildUpBlockData(blocks, 13))
        return items

    def __packTimeLeftBlock(self, name, daysLeft):
        return formatters.packTextBlockData(text=text_styles.stats(backport.text(R.strings.ranked_battles.calendarDay.timeLeft(), seasonName=name, days=daysLeft)), blockWidth=_TOOLTIP_MIN_WIDTH)
