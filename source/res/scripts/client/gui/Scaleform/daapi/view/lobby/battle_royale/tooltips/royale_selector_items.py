# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/battle_royale/tooltips/royale_selector_items.py
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.battle_royale.constants import BattleRoyalePerfProblems
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles, icons
from gui.shared.formatters.time_formatters import formatDate
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency, time_utils
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IBattleRoyaleController
_TOOLTIP_MIN_WIDTH = 280

class BattleRoyaleSelectorTooltip(BlocksTooltipData):
    connectionMgr = dependency.descriptor(IConnectionManager)
    battleRoyale = dependency.descriptor(IBattleRoyaleController)

    def __init__(self, ctx):
        super(BattleRoyaleSelectorTooltip, self).__init__(ctx, TOOLTIP_TYPE.BATTLE_ROYALE_SELECTOR_INFO)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setMargins(afterBlock=20)
        self._setWidth(_TOOLTIP_MIN_WIDTH)

    def _packBlocks(self, *args):
        items = super(BattleRoyaleSelectorTooltip, self)._packBlocks()
        items.append(self._packHeaderBlock())
        currentSeason = self.battleRoyale.getCurrentSeason()
        if currentSeason:
            timeTableBlocks = [self._packTimeTableHeaderBlock()]
            primeTime = self.battleRoyale.getPrimeTimes().get(self.connectionMgr.peripheryID)
            currentCycleEnd = currentSeason.getCycleEndDate()
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
            timeTableBlocks.append(self._packTimeBlock(message=text_styles.main(backport.text(R.strings.battle_royale.selectorTooltip.timeTable.today())), timeStr=text_styles.bonusPreviewText(todayStr)))
            tomorrowStr = self._packPeriods(tomorrowPeriods)
            timeTableBlocks.append(self._packTimeBlock(message=text_styles.main(backport.text(R.strings.battle_royale.selectorTooltip.timeTable.tomorrow())), timeStr=text_styles.stats(tomorrowStr)))
            items.append(formatters.packBuildUpBlockData(timeTableBlocks, 7, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))
            items.append(self.__getBottomStatusBlock(currentSeason))
        elif self.battleRoyale.getNextSeason():
            startDate = self.battleRoyale.getNextSeason().getCycleStartDate()
            timeLeft = time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(startDate))
            items.append(self._getTillStartBlock(timeLeft))
        elif self.battleRoyale.getPreviousSeason():
            items.append(self._getFinishEventBlock())
        items.append(self.__getPerformanceWarningText())
        return items

    def __getBottomStatusBlock(self, currentSeason):
        if self.battleRoyale.isFrozen():
            return self._getFrozenEventBlock()
        startDate = currentSeason.getCycleStartDate()
        if currentSeason.getCycleStartDate() > time_utils.getCurrentLocalServerTimestamp():
            timeLeft = time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(startDate))
            return self._getTillStartBlock(timeLeft)
        endDate = currentSeason.getCycleEndDate()
        timeLeft = time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(endDate))
        return self._getTillEndBlock(timeLeft) if timeLeft > 0 else self._getFinishEventBlock()

    def _packHeaderBlock(self):
        return formatters.packTitleDescBlock(title=text_styles.highTitle(backport.text(R.strings.battle_royale.selectorTooltip.title())), desc=text_styles.main(backport.text(R.strings.battle_royale.selectorTooltip.desc())))

    def _packTimeTableHeaderBlock(self):
        return formatters.packImageTextBlockData(title=text_styles.stats(backport.text(R.strings.battle_royale.selectorTooltip.timeTable.title())), img=backport.image(R.images.gui.maps.icons.buttons.calendar()), imgPadding=formatters.packPadding(top=2), txtPadding=formatters.packPadding(left=5))

    def _packTimeBlock(self, message, timeStr):
        return formatters.packTextParameterBlockData(value=timeStr, name=message, valueWidth=97)

    def _packPeriods(self, periods):
        if periods:
            periodsStr = []
            for periodStart, periodEnd in periods:
                startTime = formatDate('%H:%M', periodStart)
                endTime = formatDate('%H:%M', periodEnd)
                periodsStr.append(backport.text(R.strings.battle_royale.tooltips.calendarDay.time(), start=startTime, end=endTime))

            return '\n'.join(periodsStr)
        return backport.text(R.strings.battle_royale.selectorTooltip.timeTable.empty())

    def _getTillEndBlock(self, timeLeft):
        return formatters.packTextBlockData(text_styles.main(backport.text(R.strings.battle_royale.selectorTooltip.tillEnd())) + ' ' + text_styles.stats(backport.getTillTimeStringByRClass(timeLeft, R.strings.menu.headerButtons.battle.types.battleRoyale.availability)))

    def _getTillStartBlock(self, timeLeft):
        return formatters.packTextBlockData(text_styles.main(backport.text(R.strings.battle_royale.selectorTooltip.tillBegin())) + ' ' + text_styles.stats(backport.getTillTimeStringByRClass(timeLeft, R.strings.menu.headerButtons.battle.types.battleRoyale.availability)))

    def _getFinishEventBlock(self):
        return formatters.packTextBlockData(text_styles.main(backport.text(R.strings.battle_royale.selectorTooltip.finished())))

    def _getFrozenEventBlock(self):
        return formatters.packTextBlockData(text_styles.main(backport.text(R.strings.battle_royale.selectorTooltip.frozen())))

    def __getPerformanceWarningText(self):
        performanceGroup = self.battleRoyale.getPerformanceGroup()
        if performanceGroup == BattleRoyalePerfProblems.HIGH_RISK:
            block = formatters.packTitleDescBlock(title=text_styles.concatStylesWithSpace(icons.markerBlocked(), text_styles.error(backport.text(R.strings.battle_royale.selectorTooltip.attention.assuredLowPerformance.title()))), desc=text_styles.main(backport.text(R.strings.battle_royale.selectorTooltip.attention.assuredLowPerformance.description())), padding=formatters.packPadding(top=15))
        elif performanceGroup == BattleRoyalePerfProblems.MEDIUM_RISK:
            block = formatters.packTitleDescBlock(title=text_styles.concatStylesWithSpace(icons.alert(), text_styles.alert(backport.text(R.strings.battle_royale.selectorTooltip.attention.possibleLowPerformance.title()))), desc=text_styles.main(backport.text(R.strings.battle_royale.selectorTooltip.attention.possibleLowPerformance.description())), padding=formatters.packPadding(top=15))
        else:
            block = formatters.packTextBlockData(text=text_styles.concatStylesWithSpace(icons.info(), text_styles.main(backport.text(R.strings.battle_royale.selectorTooltip.attention.informativeLowPerformance.description()))), padding=formatters.packPadding(top=15))
        return block
