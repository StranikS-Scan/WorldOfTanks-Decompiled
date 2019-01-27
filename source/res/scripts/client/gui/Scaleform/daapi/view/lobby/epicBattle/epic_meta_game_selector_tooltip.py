# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/epic_meta_game_selector_tooltip.py
from gui.Scaleform import MENU
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.locale.RANKED_BATTLES import RANKED_BATTLES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.formatters.time_formatters import formatDate
from helpers import dependency, i18n, time_utils
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IEpicBattleMetaGameController
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.game_control.epic_meta_game_ctrl import EPIC_PERF_GROUP
from gui.shared.formatters import text_styles, icons

class EpicSelectorWarningTooltip(BlocksTooltipData):
    epicController = dependency.descriptor(IEpicBattleMetaGameController)
    connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self, context):
        super(EpicSelectorWarningTooltip, self).__init__(context, None)
        self._setContentMargin(top=17, left=18, bottom=20, right=20)
        self._setMargins(afterBlock=20)
        self._setWidth(367)
        self.__boundaryTime = None
        self.__isFrozen = False
        return

    def _packBlocks(self, *args, **kwargs):
        items = super(EpicSelectorWarningTooltip, self)._packBlocks(*args, **kwargs)
        self.__isFrozen = self.epicController.isFrozen()
        items.append(self.__packHeaderBlock())
        self.__boundaryTime, cycleIsActive = self.epicController.getCurrentCycleInfo()
        if not self.__isFrozen and cycleIsActive:
            scheduleBlock = self.__buildScheduleBlock()
            if scheduleBlock is not None:
                items.append(formatters.packBuildUpBlockData(blocks=scheduleBlock, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=formatters.packPadding(bottom=-13)))
        items.append(formatters.packBuildUpBlockData(blocks=self.__buildBottomBlocks(), padding=formatters.packPadding(bottom=-10)))
        return items

    def __buildScheduleBlock(self):
        primeTime = self.epicController.getPrimeTimes().get(self.connectionMgr.peripheryID, None)
        if primeTime is None or self.epicController.hasAnySeason() is None:
            return
        else:
            timeTableBlocks = [self.__packTimeTableHeaderBlock()]
            todayStart, todayEnd = time_utils.getDayTimeBoundsForLocal()
            todayEnd += 1
            tomorrowStart, tomorrowEnd = todayStart + time_utils.ONE_DAY, todayEnd + time_utils.ONE_DAY
            tomorrowPeriods = ()
            todayPeriods = primeTime.getPeriodsBetween(todayStart, min(todayEnd, self.__boundaryTime))
            if tomorrowStart < self.__boundaryTime:
                tomorrowPeriods = primeTime.getPeriodsBetween(tomorrowStart, min(tomorrowEnd, self.__boundaryTime))
            todayStr = self.__packPeriods(todayPeriods)
            timeTableBlocks.append(self.__packTimeBlock(message=text_styles.main(EPIC_BATTLE.SELECTORTOOLTIP_EPICBATTLE_TIMETABLE_TODAY), timeStr=text_styles.neutral(todayStr)))
            tomorrowStr = self.__packPeriods(tomorrowPeriods)
            timeTableBlocks.append(self.__packTimeBlock(message=text_styles.main(EPIC_BATTLE.SELECTORTOOLTIP_EPICBATTLE_TIMETABLE_TOMORROW), timeStr=text_styles.stats(tomorrowStr)))
            return timeTableBlocks

    def __buildBottomBlocks(self):
        if self.__isFrozen:
            return [self.__packFrozenBlock()]
        else:
            result = []
            if self.__boundaryTime is not None:
                result.append(self.__getTillEndBlock(time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(self.__boundaryTime))))
            result.append(self.__getPerformanceWarningText())
            return result

    def __packHeaderBlock(self):
        return formatters.packTitleDescBlock(title=text_styles.highTitle(EPIC_BATTLE.SELECTORTOOLTIP_EPICBATTLE_HEADER), desc=text_styles.main(EPIC_BATTLE.SELECTORTOOLTIP_EPICBATTLE_BODY), gap=1, padding=formatters.packPadding(bottom=-6))

    def __packTimeTableHeaderBlock(self):
        return formatters.packImageTextBlockData(title=text_styles.middleTitle(EPIC_BATTLE.SELECTORTOOLTIP_EPICBATTLE_TIMETABLE_TITLE), img=RES_ICONS.MAPS_ICONS_BUTTONS_CALENDAR, imgPadding=formatters.packPadding(top=-3, left=1), txtPadding=formatters.packPadding(left=10, top=-4), padding=formatters.packPadding(bottom=4))

    def __packPeriods(self, periods):
        if periods:
            periodsStr = []
            for periodStart, periodEnd in periods:
                startTime = formatDate('%H:%M', periodStart)
                endTime = formatDate('%H:%M', periodEnd)
                periodsStr.append(i18n.makeString(RANKED_BATTLES.CALENDARDAY_TIME, start=startTime, end=endTime))

            return '\n'.join(periodsStr)
        return i18n.makeString(EPIC_BATTLE.SELECTORTOOLTIP_EPICBATTLE_TIMETABLE_DASH)

    def __packTimeBlock(self, message, timeStr):
        return formatters.packTextParameterBlockData(value=timeStr, name=message, valueWidth=97, gap=10, padding=formatters.packPadding(left=7, bottom=2))

    def __getTillEndBlock(self, timeLeft):
        _, status = self.epicController.getCurrentCycleInfo()
        if status:
            endKey = EPIC_BATTLE.SELECTORTOOLTIP_EPICBATTLE_TIMELEFT
        else:
            endKey = EPIC_BATTLE.SELECTORTOOLTIP_EPICBATTLE_STARTIN
        return formatters.packTextBlockData(text_styles.concatStylesToSingleLine(text_styles.main(endKey), text_styles.middleTitle(time_utils.getTillTimeString(timeLeft, MENU.HEADERBUTTONS_BATTLE_TYPES_RANKED_AVAILABILITY))), padding=formatters.packPadding(top=2))

    def __packFrozenBlock(self):
        return formatters.packTextBlockData(text_styles.concatStylesToSingleLine(icons.alert(), text_styles.alert(EPIC_BATTLE.SELECTORTOOLTIP_EPICBATTLE_FROZEN)), padding=formatters.packPadding(top=16))

    def __getPerformanceWarningText(self):
        performanceGroup = self.epicController.getPerformanceGroup()
        if performanceGroup == EPIC_PERF_GROUP.HIGH_RISK:
            block = formatters.packTitleDescBlock(title=text_styles.concatStylesWithSpace(icons.markerBlocked(), text_styles.error(EPIC_BATTLE.SELECTORTOOLTIP_EPICBATTLE_ATTENTION_ASSUREDLOWPERFORMANCE_TITLE)), desc=text_styles.main(EPIC_BATTLE.SELECTORTOOLTIP_EPICBATTLE_ATTENTION_ASSUREDLOWPERFORMANCE_DESCRIPTION), padding=formatters.packPadding(top=15))
        elif performanceGroup == EPIC_PERF_GROUP.MEDIUM_RISK:
            block = formatters.packTitleDescBlock(title=text_styles.concatStylesWithSpace(icons.alert(), text_styles.alert(EPIC_BATTLE.SELECTORTOOLTIP_EPICBATTLE_ATTENTION_POSSIBLELOWPERFORMANCE_TITLE)), desc=text_styles.main(EPIC_BATTLE.SELECTORTOOLTIP_EPICBATTLE_ATTENTION_POSSIBLELOWPERFORMANCE_DESCRIPTION), padding=formatters.packPadding(top=15))
        else:
            block = formatters.packTextBlockData(text=text_styles.concatStylesWithSpace(icons.info(), text_styles.main(EPIC_BATTLE.SELECTORTOOLTIP_EPICBATTLE_ATTENTION_INFORMATIVELOWPERFORMANCE_DESCRIPTION)), padding=formatters.packPadding(top=15))
        return block
