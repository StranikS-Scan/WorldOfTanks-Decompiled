# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/tooltips/epic_battle_selector_tooltip.py
from gui.Scaleform.daapi.view.lobby.epicBattle.tooltips.common_blocks import packEpicBattleInfoBlock, packEpicBattleSeasonBlock
from gui.game_control.epic_meta_game_ctrl import EPIC_PERF_GROUP
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles, icons
from gui.shared.formatters.time_formatters import formatDate
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency, time_utils
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IEpicBattleMetaGameController
_R_TIMETABLE = R.strings.epic_battle.selectorTooltip.epicBattle.timeTable

class EpicBattleSelectorTooltip(BlocksTooltipData):
    __connectionMgr = dependency.descriptor(IConnectionManager)
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)
    __slots__ = ()

    def __init__(self, context):
        super(EpicBattleSelectorTooltip, self).__init__(context, None)
        self._setContentMargin(top=0, left=0, bottom=12, right=0)
        self._setWidth(320)
        return

    def _packBlocks(self, *args, **kwargs):
        season = self.__epicController.getCurrentSeason()
        if season is not None and season.getLastCycleInfo().endDate >= time_utils.getCurrentLocalServerTimestamp():
            if self.__epicController.isEnabled() and self.__epicController.isCurrentCycleActive():
                packers = self.__getPackersInProgress()
            else:
                packers = self.__getPackersBeforeStart()
        elif self.__epicController.getNextSeason() is not None:
            packers = self.__getPackersBeforeStart()
        else:
            packers = self.__getPackersAfterEnd()
        return [ p for p in [ pack() for pack in packers ] if p is not None ]

    def __getPackersBeforeStart(self):
        return (packEpicBattleInfoBlock, packEpicBattleSeasonBlock)

    def __getPackersInProgress(self):
        return (packEpicBattleInfoBlock,
         self.__packScheduleBlock,
         packEpicBattleSeasonBlock,
         self.__packPerformanceWarningBlock)

    def __getPackersAfterEnd(self):
        return (packEpicBattleInfoBlock, packEpicBattleSeasonBlock)

    def __packScheduleBlock(self):
        primeTime = self.__epicController.getPrimeTimes().get(self.__connectionMgr.peripheryID)
        if primeTime is None or self.__epicController.hasAnySeason() is None:
            return
        else:
            timeTableBlocks = [self.__packTimeTableHeaderBlock()]
            todayStart, todayEnd = time_utils.getDayTimeBoundsForLocal()
            todayEnd += 1
            tomorrowStart, tomorrowEnd = todayStart + time_utils.ONE_DAY, todayEnd + time_utils.ONE_DAY
            boundaryTime, _ = self.__epicController.getCurrentCycleInfo()
            tomorrowPeriods = ()
            todayPeriods = primeTime.getPeriodsBetween(todayStart, min(todayEnd, boundaryTime))
            if tomorrowStart < boundaryTime:
                tomorrowPeriods = primeTime.getPeriodsBetween(tomorrowStart, min(tomorrowEnd, boundaryTime))
            todayStr = self.__packPeriods(todayPeriods)
            timeTableBlocks.append(self.__packTimeBlock(message=text_styles.main(backport.text(_R_TIMETABLE.today())), timeStr=text_styles.stats(todayStr)))
            tomorrowStr = self.__packPeriods(tomorrowPeriods)
            timeTableBlocks.append(self.__packTimeBlock(message=text_styles.main(backport.text(_R_TIMETABLE.tomorrow())), timeStr=text_styles.main(tomorrowStr)))
            return formatters.packBuildUpBlockData(timeTableBlocks)

    def __packPerformanceWarningBlock(self):
        performanceGroup = self.__epicController.getPerformanceGroup()
        attention = R.strings.epic_battle.selectorTooltip.epicBattle.attention
        if performanceGroup == EPIC_PERF_GROUP.HIGH_RISK:
            icon = icons.markerBlocked()
            titleStyle = text_styles.error
            attention = attention.assuredLowPerformance
        elif performanceGroup == EPIC_PERF_GROUP.MEDIUM_RISK:
            icon = icons.alert()
            titleStyle = text_styles.alert
            attention = attention.possibleLowPerformance
        else:
            icon = icons.attention()
            titleStyle = text_styles.stats
            attention = attention.informativeLowPerformance
        return formatters.packTitleDescBlock(title=text_styles.concatStylesWithSpace(icon, titleStyle(backport.text(attention.title()))), desc=text_styles.main(backport.text(attention.description())), padding=formatters.packPadding(left=20, right=20))

    def __packTimeTableHeaderBlock(self):
        return formatters.packImageTextBlockData(title=text_styles.middleTitle(backport.text(_R_TIMETABLE.title())), img=backport.image(R.images.gui.maps.icons.buttons.calendar()), imgPadding=formatters.packPadding(top=-1, left=20), txtPadding=formatters.packPadding(left=5, top=-4))

    def __packPeriods(self, periods):
        if periods:
            periodsStr = []
            for periodStart, periodEnd in periods:
                startTime = formatDate('%H:%M', periodStart)
                endTime = formatDate('%H:%M', periodEnd)
                periodsStr.append(backport.text(R.strings.ranked_battles.calendarDay.time(), start=startTime, end=endTime))

            return '\n'.join(periodsStr)
        return backport.text(_R_TIMETABLE.dash())

    def __packTimeBlock(self, message, timeStr):
        return formatters.packTextParameterBlockData(value=timeStr, name=message, valueWidth=97, gap=8, padding=formatters.packPadding(top=-2, left=60))
