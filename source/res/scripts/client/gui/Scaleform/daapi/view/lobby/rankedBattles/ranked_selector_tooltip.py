# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/ranked_selector_tooltip.py
from gui.Scaleform import MENU
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.locale.RANKED_BATTLES import RANKED_BATTLES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.formatters.time_formatters import formatDate
from helpers import dependency, i18n, time_utils
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IRankedBattlesController
_TOOLTIP_MIN_WIDTH = 280

class RankedSelectorTooltip(BlocksTooltipData):
    connectionMgr = dependency.descriptor(IConnectionManager)
    rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, ctx):
        super(RankedSelectorTooltip, self).__init__(ctx, TOOLTIP_TYPE.RANKED_SELECTOR_INFO)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setMargins(afterBlock=20)
        self._setWidth(_TOOLTIP_MIN_WIDTH)

    def _packBlocks(self, *args):
        items = super(RankedSelectorTooltip, self)._packBlocks()
        items.append(self._packHeaderBlock())
        timeTableBlocks = [self._packTimeTableHeaderBlock()]
        primeTime = self.rankedController.getPrimeTimes().get(self.connectionMgr.peripheryID)
        currentCycleEnd = self.rankedController.getCurrentSeason().getCycleEndDate()
        todayStart, todayEnd = time_utils.getDayTimeBoundsForLocal()
        todayEnd += 1
        tomorrowStart, tomorrowEnd = todayStart + time_utils.ONE_DAY, todayEnd + time_utils.ONE_DAY
        tomorrowEnd += 1
        todayPeriods = ()
        tomorrowPeriods = ()
        if primeTime is not None:
            todayPeriods = primeTime.getPeriodsBetween(todayStart, min(todayEnd, currentCycleEnd))
            if tomorrowStart < currentCycleEnd:
                tomorrowPeriods = primeTime.getPeriodsBetween(tomorrowStart, min(tomorrowEnd, currentCycleEnd))
        todayStr = self._packPeriods(todayPeriods)
        timeTableBlocks.append(self._packTimeBlock(message=text_styles.main(RANKED_BATTLES.SELECTORTOOLTIP_TIMETABLE_TODAY), timeStr=text_styles.bonusPreviewText(todayStr)))
        tomorrowStr = self._packPeriods(tomorrowPeriods)
        timeTableBlocks.append(self._packTimeBlock(message=text_styles.main(RANKED_BATTLES.SELECTORTOOLTIP_TIMETABLE_TOMORROW), timeStr=text_styles.stats(tomorrowStr)))
        items.append(formatters.packBuildUpBlockData(timeTableBlocks, 7, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))
        items.append(self._getTillEndBlock(time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(currentCycleEnd))))
        return items

    def _packHeaderBlock(self):
        return formatters.packTitleDescBlock(title=text_styles.highTitle(RANKED_BATTLES.SELECTORTOOLTIP_TITLE), desc=text_styles.main(RANKED_BATTLES.SELECTORTOOLTIP_DESC))

    def _packTimeTableHeaderBlock(self):
        return formatters.packImageTextBlockData(title=text_styles.stats(RANKED_BATTLES.SELECTORTOOLTIP_TIMETABLE_TITLE), img=RES_ICONS.MAPS_ICONS_BUTTONS_CALENDAR, imgPadding=formatters.packPadding(top=2), txtPadding=formatters.packPadding(left=5))

    def _packTimeBlock(self, message, timeStr):
        return formatters.packTextParameterBlockData(value=timeStr, name=message, valueWidth=97)

    def _packPeriods(self, periods):
        if periods:
            periodsStr = []
            for periodStart, periodEnd in periods:
                startTime = formatDate('%H:%M', periodStart)
                endTime = formatDate('%H:%M', periodEnd)
                periodsStr.append(i18n.makeString(RANKED_BATTLES.CALENDARDAY_TIME, start=startTime, end=endTime))

            return '\n'.join(periodsStr)
        return i18n.makeString(RANKED_BATTLES.SELECTORTOOLTIP_TIMETABLE_EMPTY)

    def _getTillEndBlock(self, timeLeft):
        return formatters.packTextBlockData(text_styles.main(RANKED_BATTLES.SELECTORTOOLTIP_TILLEND) + ' ' + text_styles.stats(time_utils.getTillTimeString(timeLeft, MENU.HEADERBUTTONS_BATTLE_TYPES_RANKED_AVAILABILITY)))
