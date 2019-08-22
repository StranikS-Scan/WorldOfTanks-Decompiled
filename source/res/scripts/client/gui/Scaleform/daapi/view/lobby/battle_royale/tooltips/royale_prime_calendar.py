# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/battle_royale/tooltips/royale_prime_calendar.py
from datetime import datetime
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency, time_utils
from skeletons.gui.game_control import IBattleRoyaleController
_TOOLTIP_MIN_WIDTH = 200

class RoyalePrimeTimeCalendarTooltip(BlocksTooltipData):
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)

    def __init__(self, ctx):
        super(RoyalePrimeTimeCalendarTooltip, self).__init__(ctx, TOOLTIP_TYPE.BATTLE_ROYALE_PRIME_TIMES)
        self._setContentMargin(top=18, left=20, bottom=18, right=20)
        self._setMargins(afterBlock=13)
        self._setWidth(_TOOLTIP_MIN_WIDTH)

    def _packBlocks(self, selectedTime):
        if selectedTime is None:
            selectedTime = time_utils.getCurrentLocalServerTimestamp()
        items = super(RoyalePrimeTimeCalendarTooltip, self)._packBlocks()
        seasonEnd = None
        if self.__battleRoyaleController.getCurrentSeason():
            seasonEnd = self.__battleRoyaleController.getCurrentSeason().getEndDate()
            seasonEnd = datetime.fromtimestamp(seasonEnd).date()
        if not seasonEnd or datetime.fromtimestamp(selectedTime).date() > seasonEnd:
            return items
        else:
            blocks = [self.__packHeaderBlock()]
            serversPeriodsMapping = self.__battleRoyaleController.getPrimeTimesForDay(selectedTime)
            formatter = backport.getShortTimeFormat
            for serverName in sorted(serversPeriodsMapping.keys()):
                periodsStr = []
                dayPeriods = serversPeriodsMapping[serverName]
                if dayPeriods:
                    for periodStart, periodEnd in dayPeriods:
                        periodsStr.append(backport.text(R.strings.battle_royale.tooltips.calendarDay.time(), start=formatter(periodStart), end=formatter(periodEnd)))

                else:
                    periodsStr = backport.text(R.strings.common.common.dash())
                blocks.append(self.__packServerTimeBlock(serverStr=text_styles.main(backport.text(R.strings.battle_royale.tooltips.calendarDay.serverName(), server=serverName)), timeStr=text_styles.stats('\n'.join(periodsStr))))

            items.append(formatters.packBuildUpBlockData(blocks, 13))
            return items

    @staticmethod
    def __packHeaderBlock():
        return formatters.packImageTextBlockData(title=text_styles.highTitle(backport.text(R.strings.battle_royale.tooltips.calendarDay.title())), img=backport.image(R.images.gui.maps.icons.buttons.calendar()), imgPadding=formatters.packPadding(top=5), txtPadding=formatters.packPadding(left=10))

    @staticmethod
    def __packServerTimeBlock(serverStr, timeStr):
        return formatters.packTextParameterBlockData(value=serverStr, name=timeStr, valueWidth=55, padding=formatters.packPadding(left=10))
