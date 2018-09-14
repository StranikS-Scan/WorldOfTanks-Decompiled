# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/ranked_calendar_day_tooltip.py
import BigWorld
from gui.Scaleform.locale.RANKED_BATTLES import RANKED_BATTLES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency, i18n
from helpers import time_utils
from predefined_hosts import g_preDefinedHosts, HOST_AVAILABILITY
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
        blocks = [self._packHeaderBlock()]
        hostsList = g_preDefinedHosts.getSimpleHostsList(g_preDefinedHosts.hostsWithRoaming())
        if self.connectionMgr.peripheryID == 0:
            hostsList.insert(0, (self.connectionMgr.url,
             self.connectionMgr.serverUserName,
             HOST_AVAILABILITY.IGNORED,
             0))
        primeTimes = self.rankedController.getPrimeTimes()
        dayStart, dayEnd = time_utils.getDayTimeBoundsForLocal(selectedTime)
        dayEnd += 1
        frmt = BigWorld.wg_getShortTimeFormat
        for _, name, _, peripheryID in hostsList:
            if peripheryID in primeTimes:
                dayPeriods = primeTimes[peripheryID].getPeriodsBetween(dayStart, dayEnd)
                if not dayPeriods:
                    continue
                periodsStr = []
                for periodStart, periodEnd in dayPeriods:
                    periodsStr.append(i18n.makeString(RANKED_BATTLES.CALENDARDAY_TIME, start=frmt(periodStart), end=frmt(periodEnd)))

                blocks.append(self._packServerTimeBlock(serverStr=text_styles.main(i18n.makeString(RANKED_BATTLES.CALENDARDAY_SERVERNAME, server=name)), timeStr=text_styles.stats('\n'.join(periodsStr))))

        items.append(formatters.packBuildUpBlockData(blocks, 13))
        return items

    def _packHeaderBlock(self):
        return formatters.packImageTextBlockData(title=text_styles.highTitle(RANKED_BATTLES.CALENDARDAY_TITLE), img=RES_ICONS.MAPS_ICONS_BUTTONS_CALENDAR, imgPadding=formatters.packPadding(top=5), txtPadding=formatters.packPadding(left=10))

    def _packServerTimeBlock(self, serverStr, timeStr):
        return formatters.packTextParameterBlockData(value=serverStr, name=timeStr, valueWidth=55, padding=formatters.packPadding(left=10))
