# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/ranked/ranked_selector_tooltip.py
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.formatters.time_formatters import formatDate
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency, time_utils
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
        timeTableBlocks.append(self._packTimeBlock(message=text_styles.main(backport.text(R.strings.ranked_battles.selectorTooltip.timeTable.today())), timeStr=text_styles.bonusPreviewText(todayStr)))
        tomorrowStr = self._packPeriods(tomorrowPeriods)
        timeTableBlocks.append(self._packTimeBlock(message=text_styles.main(backport.text(R.strings.ranked_battles.selectorTooltip.timeTable.tomorrow())), timeStr=text_styles.stats(tomorrowStr)))
        items.append(formatters.packBuildUpBlockData(timeTableBlocks, 7, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))
        items.append(self._getTillEndBlock(time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(currentCycleEnd))))
        return items

    def _packHeaderBlock(self):
        return formatters.packTitleDescBlock(title=text_styles.highTitle(backport.text(R.strings.ranked_battles.selectorTooltip.title())), desc=text_styles.main(backport.text(R.strings.ranked_battles.selectorTooltip.desc())))

    def _packTimeTableHeaderBlock(self):
        return formatters.packImageTextBlockData(title=text_styles.stats(backport.text(R.strings.ranked_battles.selectorTooltip.timeTable.title())), img=backport.image(R.images.gui.maps.icons.buttons.calendar()), imgPadding=formatters.packPadding(top=2), txtPadding=formatters.packPadding(left=5))

    def _packTimeBlock(self, message, timeStr):
        return formatters.packTextParameterBlockData(value=timeStr, name=message, valueWidth=97)

    def _packPeriods(self, periods):
        if periods:
            periodsStr = []
            for periodStart, periodEnd in periods:
                startTime = formatDate('%H:%M', periodStart)
                endTime = formatDate('%H:%M', periodEnd)
                periodsStr.append(backport.text(R.strings.ranked_battles.calendarDay.time(), start=startTime, end=endTime))

            return '\n'.join(periodsStr)
        return backport.text(R.strings.ranked_battles.selectorTooltip.timeTable.empty())

    def _getTillEndBlock(self, timeLeft):
        return formatters.packTextBlockData(text_styles.main(backport.text(R.strings.ranked_battles.selectorTooltip.tillEnd())) + ' ' + text_styles.stats(backport.getTillTimeStringByRClass(timeLeft, R.strings.menu.headerButtons.battle.types.ranked.availability)))


class RankedUnavailableTooltip(BlocksTooltipData):
    rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, context):
        super(RankedUnavailableTooltip, self).__init__(context, None)
        self._setWidth(540)
        return

    def _packBlocks(self, *args, **kwargs):
        items = super(RankedUnavailableTooltip, self)._packBlocks(*args, **kwargs)
        hasSuitableVehicles = self.rankedController.hasSuitableVehicles()
        tooltipData = R.strings.tooltips.battleTypes.ranked
        header = backport.text(tooltipData.header())
        body = backport.text(tooltipData.body())
        nextSeason = self.rankedController.getNextSeason()
        if hasSuitableVehicles:
            if self.rankedController.isFrozen() and self.rankedController.getCurrentSeason() is not None:
                additionalInfo = backport.text(tooltipData.body.frozen())
            elif nextSeason is not None:
                additionalInfo = backport.text(tooltipData.body.coming(), date=backport.getShortDateFormat(time_utils.makeLocalServerTime(nextSeason.getStartDate())))
            else:
                additionalInfo = backport.text(tooltipData.body.disabled())
            body = '%s\n\n%s' % (body, additionalInfo)
        items.append(formatters.packImageTextBlockData(title=text_styles.middleTitle(header), desc=text_styles.main(body)))
        return items
