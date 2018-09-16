# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/ranked_calendar_day_tooltip.py
from datetime import datetime
import BigWorld
from gui.Scaleform.locale.COMMON import COMMON
from gui.Scaleform.locale.RANKED_BATTLES import RANKED_BATTLES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency, i18n
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IRankedBattlesController
_TOOLTIP_MIN_WIDTH = 200

class RankedCalendarDayTooltip(BlocksTooltipData):
    rankedController = dependency.descriptor(IRankedBattlesController)
    connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self, ctx):
        super(RankedCalendarDayTooltip, self).__init__(ctx, TOOLTIP_TYPE.RANKED_CALENDAR_DAY)
        self._setContentMargin(top=18, left=20, bottom=18, right=20)
        self._setMargins(afterBlock=13)
        self._setWidth(_TOOLTIP_MIN_WIDTH)

    def _packBlocks(self, selectedTime):
        items = super(RankedCalendarDayTooltip, self)._packBlocks()
        seasonEnd = None
        if self.rankedController.getCurrentSeason():
            seasonEnd = self.rankedController.getCurrentSeason().getEndDate()
            seasonEnd = datetime.fromtimestamp(seasonEnd).date()
        if datetime.fromtimestamp(selectedTime).date() > seasonEnd:
            return items
        else:
            blocks = [self._packHeaderBlock()]
            serversPeriodsMapping = self.rankedController.getPrimeTimesForDay(selectedTime, groupIdentical=True)
            frmt = BigWorld.wg_getShortTimeFormat
            for serverName in sorted(serversPeriodsMapping.keys()):
                periodsStr = []
                dayPeriods = serversPeriodsMapping[serverName]
                if dayPeriods:
                    for periodStart, periodEnd in dayPeriods:
                        periodsStr.append(i18n.makeString(RANKED_BATTLES.CALENDARDAY_TIME, start=frmt(periodStart), end=frmt(periodEnd)))

                else:
                    periodsStr = i18n.makeString(COMMON.COMMON_DASH)
                blocks.append(self._packServerTimeBlock(serverStr=text_styles.main(i18n.makeString(RANKED_BATTLES.CALENDARDAY_SERVERNAME, server=serverName)), timeStr=text_styles.stats('\n'.join(periodsStr))))

            items.append(formatters.packBuildUpBlockData(blocks, 13))
            return items

    def _packHeaderBlock(self):
        return formatters.packImageTextBlockData(title=text_styles.highTitle(RANKED_BATTLES.CALENDARDAY_TITLE), img=RES_ICONS.MAPS_ICONS_BUTTONS_CALENDAR, imgPadding=formatters.packPadding(top=5), txtPadding=formatters.packPadding(left=10))

    def _packServerTimeBlock(self, serverStr, timeStr):
        return formatters.packTextParameterBlockData(value=serverStr, name=timeStr, valueWidth=55, padding=formatters.packPadding(left=10))
