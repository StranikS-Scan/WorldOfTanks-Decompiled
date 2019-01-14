# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/epic_meta_game_selector_tooltip.py
from gui.Scaleform import MENU
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.locale.RANKED_BATTLES import RANKED_BATTLES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.formatters.time_formatters import formatDate
from helpers import dependency, i18n, time_utils
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IEpicBattleMetaGameController
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.game_control.epic_meta_game_ctrl import EPIC_PERF_GROUP
from gui.shared.formatters import text_styles, icons
_TOOLTIP_MIN_WIDTH = 280

class EpicMetaGameUnavailableTooltip(BlocksTooltipData):
    connectionMgr = dependency.descriptor(IConnectionManager)
    epicController = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self, ctx):
        super(EpicMetaGameUnavailableTooltip, self).__init__(ctx, TOOLTIP_TYPE.EPIC_SELECTOR_UNAVAILABLE_INFO)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setMargins(afterBlock=20)
        self._setWidth(_TOOLTIP_MIN_WIDTH)

    def _packBlocks(self, *args):
        items = super(EpicMetaGameUnavailableTooltip, self)._packBlocks()
        items.append(self._packHeaderBlock())
        timeTableBlocks = [self._packTimeTableHeaderBlock()]
        primeTime = self.epicController.getPrimeTimes().get(self.connectionMgr.peripheryID, None)
        if primeTime is None or self.epicController.hasAnySeason() is None:
            return items
        else:
            todayStart, todayEnd = time_utils.getDayTimeBoundsForLocal()
            todayEnd += 1
            tomorrowStart, tomorrowEnd = todayStart + time_utils.ONE_DAY, todayEnd + time_utils.ONE_DAY
            todayPeriods = ()
            tomorrowPeriods = ()
            time, status = self.epicController.getCurrentCycleInfo()
            if status:
                todayPeriods = primeTime.getPeriodsBetween(todayStart, min(todayEnd, time))
                if tomorrowStart < time:
                    tomorrowPeriods = primeTime.getPeriodsBetween(tomorrowStart, min(tomorrowEnd, time))
                todayStr = self._packPeriods(todayPeriods)
                timeTableBlocks.append(self._packTimeBlock(message=text_styles.main(EPIC_BATTLE.SELECTORTOOLTIP_EPICBATTLE_DISABLED_TIMETABLE_TODAY), timeStr=text_styles.bonusPreviewText(todayStr)))
                tomorrowStr = self._packPeriods(tomorrowPeriods)
                timeTableBlocks.append(self._packTimeBlock(message=text_styles.main(EPIC_BATTLE.SELECTORTOOLTIP_EPICBATTLE_DISABLED_TIMETABLE_TOMORROW), timeStr=text_styles.stats(tomorrowStr)))
                items.append(formatters.packBuildUpBlockData(timeTableBlocks, 7, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))
            if time is not None:
                items.append(self._getTillEndBlock(time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(time))))
            return items

    def _packHeaderBlock(self):
        return formatters.packTitleDescBlock(title=text_styles.highTitle(EPIC_BATTLE.SELECTORTOOLTIP_EPICBATTLE_DISABLED_TITLE), desc=text_styles.main(EPIC_BATTLE.SELECTORTOOLTIP_EPICBATTLE_DISABLED_DESC))

    def _packTimeTableHeaderBlock(self):
        return formatters.packImageTextBlockData(title=text_styles.stats(EPIC_BATTLE.SELECTORTOOLTIP_EPICBATTLE_DISABLED_TIMETABLE_TITLE), img=RES_ICONS.MAPS_ICONS_BUTTONS_CALENDAR, imgPadding=formatters.packPadding(top=2), txtPadding=formatters.packPadding(left=5))

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
        return i18n.makeString(EPIC_BATTLE.SELECTORTOOLTIP_EPICBATTLE_DISABLED_TIMETABLE_EMPTY)

    def _getTillEndBlock(self, timeLeft):
        _, status = self.epicController.getCurrentCycleInfo()
        if status:
            endKey = EPIC_BATTLE.SELECTORTOOLTIP_EPICBATTLE_DISABLED_TILLEND
        else:
            endKey = EPIC_BATTLE.SELECTORTOOLTIP_EPICBATTLE_DISABLED_STARTIN
        return formatters.packTextBlockData(text_styles.main(endKey) + ' ' + text_styles.stats(time_utils.getTillTimeString(timeLeft, MENU.HEADERBUTTONS_BATTLE_TYPES_RANKED_AVAILABILITY)))


class EpicSelectorWarningTooltip(BlocksTooltipData):
    epicController = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self, context):
        super(EpicSelectorWarningTooltip, self).__init__(context, None)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setMargins(afterBlock=20)
        self._setWidth(540)
        return

    def _packBlocks(self, *args, **kwargs):
        items = super(EpicSelectorWarningTooltip, self)._packBlocks(*args, **kwargs)
        bodyKey = EPIC_BATTLE.SELECTORTOOLTIP_EPICBATTLE_ENABLED_BODY
        additionalInfo = self.__getPerformanceWarningText()
        body = '%s\n\n%s' % (i18n.makeString(bodyKey), additionalInfo)
        items.append(formatters.packImageTextBlockData(title=text_styles.middleTitle(EPIC_BATTLE.SELECTORTOOLTIP_EPICBATTLE_ENABLED_HEADER), desc=text_styles.main(body)))
        return items

    def __getPerformanceWarningText(self):
        performanceGroup = self.epicController.getPerformanceGroup()
        attentionText = text_styles.main(EPIC_BATTLE.SELECTORTOOLTIP_EPICBATTLE_ENABLED_ATTENTION_INFORMATIVELOWPERFORMANCE)
        iconSrc = RES_ICONS.MAPS_ICONS_LIBRARY_INFORMATIONICON
        if performanceGroup == EPIC_PERF_GROUP.HIGH_RISK:
            attentionText = text_styles.error(EPIC_BATTLE.SELECTORTOOLTIP_EPICBATTLE_ENABLED_ATTENTION_ASSUREDLOWPERFORMANCE)
            iconSrc = RES_ICONS.MAPS_ICONS_LIBRARY_MARKER_BLOCKED
        elif performanceGroup == EPIC_PERF_GROUP.MEDIUM_RISK:
            attentionText = text_styles.neutral(EPIC_BATTLE.SELECTORTOOLTIP_EPICBATTLE_ENABLED_ATTENTION_POSSIBLELOWPERFORMANCE)
            iconSrc = RES_ICONS.MAPS_ICONS_LIBRARY_ATTENTIONICON
        return icons.makeImageTag(iconSrc, vSpace=-3) + ' ' + attentionText
