# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/bob/bob_prime_time.py
from constants import AUTH_REALM
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.formatters.time_formatters import formatDate
from gui.shared.tooltips import TOOLTIP_TYPE, formatters, ToolTipBaseData
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency, time_utils
from predefined_hosts import g_preDefinedHosts
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IBobController
_SELECTOR_TOOLTIP_MIN_WIDTH = 280

class BobSelectorTooltip(BlocksTooltipData):
    __connectionMgr = dependency.descriptor(IConnectionManager)
    __bobController = dependency.descriptor(IBobController)

    def __init__(self, ctx):
        super(BobSelectorTooltip, self).__init__(ctx, TOOLTIP_TYPE.BOB_SELECTOR_INFO)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setMargins(afterBlock=20)
        self._setWidth(_SELECTOR_TOOLTIP_MIN_WIDTH)

    def _packBlocks(self, *args):
        items = super(BobSelectorTooltip, self)._packBlocks()
        items.append(self._packHeaderBlock())
        timeTableBlocks = [self._packTimeTableHeaderBlock()]
        if not self.__bobController.isModeActive():
            return items
        else:
            primeTime = self.__bobController.getPrimeTimes().get(self.__connectionMgr.peripheryID)
            currentCycleEnd = self.__bobController.getCurrentSeason().getCycleEndDate()
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
            timeTableBlocks.append(self._packTimeBlock(message=text_styles.main(backport.text(R.strings.bob.selectorTooltip.timeTable.today())), timeStr=text_styles.bonusPreviewText(todayStr)))
            tomorrowStr = self._packPeriods(tomorrowPeriods)
            timeTableBlocks.append(self._packTimeBlock(message=text_styles.main(backport.text(R.strings.bob.selectorTooltip.timeTable.tomorrow())), timeStr=text_styles.stats(tomorrowStr)))
            items.append(formatters.packBuildUpBlockData(timeTableBlocks, 7, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))
            if currentCycleEnd is not None:
                items.append(self._getTillEndBlock(time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(currentCycleEnd))))
            return items

    def _packHeaderBlock(self):
        descR = R.strings.bob.selectorTooltip.desc.dyn(AUTH_REALM)
        if descR.exists():
            desc = descR()
        else:
            desc = R.strings.bob.selectorTooltip.desc()
        return formatters.packTitleDescBlock(title=text_styles.highTitle(backport.text(R.strings.bob.selectorTooltip.title())), desc=text_styles.main(backport.text(desc)))

    def _packTimeTableHeaderBlock(self):
        return formatters.packImageTextBlockData(title=text_styles.stats(backport.text(R.strings.bob.selectorTooltip.timeTable.title())), img=backport.image(R.images.gui.maps.icons.buttons.calendar()), imgPadding=formatters.packPadding(top=2), txtPadding=formatters.packPadding(left=5))

    def _packTimeBlock(self, message, timeStr):
        return formatters.packTextParameterBlockData(value=timeStr, name=message, valueWidth=97)

    def _packPeriods(self, periods):
        if periods:
            periodsStr = []
            for periodStart, periodEnd in periods:
                startTime = formatDate('%H:%M', periodStart)
                endTime = formatDate('%H:%M', periodEnd)
                periodsStr.append(backport.text(R.strings.bob.calendarDay.time(), start=startTime, end=endTime))

            return '\n'.join(periodsStr)
        return backport.text(R.strings.bob.selectorTooltip.timeTable.empty())

    def _getTillEndBlock(self, timeLeft):
        return formatters.packTextBlockData(text_styles.main(backport.text(R.strings.bob.selectorTooltip.tillEnd())) + ' ' + text_styles.stats(backport.getTillTimeStringByRClass(timeLeft, R.strings.bob.selectorTooltip.availability)))


class BobServerPrimeTime(ToolTipBaseData):
    __bobController = dependency.descriptor(IBobController)

    def __init__(self, context):
        super(BobServerPrimeTime, self).__init__(context, TOOLTIP_TYPE.CONTROL)

    def getDisplayableData(self, peripheryID):
        hostsList = g_preDefinedHosts.getSimpleHostsList(g_preDefinedHosts.hostsWithRoaming(), withShortName=True)
        serverName = ''
        for _, serverData in enumerate(hostsList):
            _, serverName, _, _, pID = serverData
            if pID == peripheryID:
                break

        timeLeftStr = '-'
        isNow = False
        primeTime = self.__bobController.getPrimeTimes().get(peripheryID)
        if primeTime:
            currentCycleEnd = self.__bobController.getCurrentSeason().getCycleEndDate()
            isNow, timeLeft = primeTime.getAvailability(time_utils.getCurrentLocalServerTimestamp(), currentCycleEnd)
            timeLeftStr = backport.getTillTimeStringByRClass(timeLeft, R.strings.bob.status.timeLeft)
        formatedTime = text_styles.neutral(timeLeftStr)
        if isNow:
            descriptionID = R.strings.bob.primeTime.tooltip.server.available.until()
        else:
            descriptionID = R.strings.bob.primeTime.tooltip.server.unavailable.inTime()
        sName = backport.text(R.strings.bob.primeTime.tooltip.server.onServer(), server=serverName)
        description = backport.text(descriptionID, time=formatedTime)
        return {'body': '{}\n{}'.format(sName, description)}
