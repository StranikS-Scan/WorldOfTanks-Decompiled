# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/formatters/tooltips.py
import typing
from gui.impl.gen import R
from gui.impl import backport
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.shared.formatters.time_formatters import formatDate
from gui.shared.tooltips import formatters
from helpers import time_utils, dependency
from gui.shared.formatters import text_styles
from skeletons.connection_mgr import IConnectionManager
from items.writers.c11n_writers import natsorted
from gui.prb_control.settings import SELECTOR_BATTLE_TYPES
if typing.TYPE_CHECKING:
    from season_common import GameSeason
    from skeletons.gui.game_control import ISeasonProvider
_MODENAME_TO_PO_FILE = {SELECTOR_BATTLE_TYPES.RANKED: 'ranked_battles',
 SELECTOR_BATTLE_TYPES.MAPBOX: 'mapbox',
 SELECTOR_BATTLE_TYPES.COMP7: 'comp7'}

@dependency.replace_none_kwargs(connectionMgr=IConnectionManager)
def getTimeTableBlock(modeCtrl, modeName, leftPadding=0, connectionMgr=None):
    timeTableBlocks = [packTimeTableHeaderBlock(modeName)]
    primeTime = modeCtrl.getPrimeTimes().get(connectionMgr.peripheryID)
    currentCycleEnd = modeCtrl.getCurrentSeason().getCycleEndDate()
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
    todayStr = _packPeriods(todayPeriods, modeName)
    timeTableBlocks.append(_packTimeBlock(message=text_styles.main(backport.text(R.strings.dyn(modeName).selectorTooltip.timeTable.today())), timeStr=text_styles.bonusPreviewText(todayStr)))
    tomorrowStr = _packPeriods(tomorrowPeriods, modeName)
    timeTableBlocks.append(_packTimeBlock(message=text_styles.main(backport.text(R.strings.dyn(modeName).selectorTooltip.timeTable.tomorrow())), timeStr=text_styles.stats(tomorrowStr)))
    return formatters.packBuildUpBlockData(timeTableBlocks, 7, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=formatters.packPadding(left=leftPadding))


def packCalendarBlock(modeCtrl, selectedTime, modeName):
    serversPeriodsMapping = modeCtrl.getPrimeTimesForDay(selectedTime)
    frmt = backport.getShortTimeFormat
    blocks = []
    modeName = _MODENAME_TO_PO_FILE[modeName]
    for serverName in natsorted(serversPeriodsMapping.keys()):
        periodsStr = []
        dayPeriods = serversPeriodsMapping[serverName]
        if dayPeriods:
            for periodStart, periodEnd in dayPeriods:
                periodsStr.append(backport.text(R.strings.dyn(modeName).calendarDay.time(), start=frmt(periodStart), end=frmt(periodEnd)))

        else:
            periodsStr = backport.text(R.strings.common.common.dash())
        blocks.append(__packServerTimeBlock(serverStr=text_styles.main(backport.text(R.strings.dyn(modeName).calendarDay.serverName(), server=serverName)), timeStr=text_styles.stats('\n'.join(periodsStr))))

    return blocks


def packTimeTableHeaderBlock(modeName):
    return formatters.packImageTextBlockData(title=text_styles.stats(backport.text(R.strings.dyn(_MODENAME_TO_PO_FILE[modeName]).selectorTooltip.timeTable.title())), img=backport.image(R.images.gui.maps.icons.buttons.calendar()), imgPadding=formatters.packPadding(top=2), txtPadding=formatters.packPadding(left=5))


def _packTimeBlock(message, timeStr):
    return formatters.packTextParameterBlockData(value=timeStr, name=message, valueWidth=97)


def _packPeriods(periods, modeName):
    if periods:
        periodsStr = []
        for periodStart, periodEnd in periods:
            startTime = formatDate('%H:%M', periodStart)
            endTime = formatDate('%H:%M', periodEnd)
            periodsStr.append(backport.text(R.strings.dyn(modeName).calendarDay.time(), start=startTime, end=endTime))

        return '\n'.join(periodsStr)
    return backport.text(R.strings.dyn(modeName).selectorTooltip.timeTable.empty())


def __packServerTimeBlock(serverStr, timeStr):
    return formatters.packTextParameterBlockData(value=serverStr, name=timeStr, valueWidth=55, padding=formatters.packPadding(left=10))


def getScheduleBlock(modeCtrl, modeName, actualSeason, seasonIsStarted, timeStringGetter):
    block = []
    if actualSeason.hasActiveCycle(time_utils.getCurrentLocalServerTimestamp()):
        currentCycle = actualSeason.getCycleInfo()
        block.append(getTimeTableBlock(modeCtrl, modeName))
        block.append(_getTimeBlock(seasonIsStarted, True, time_utils.makeLocalServerTime(currentCycle.endDate), modeName, timeStringGetter))
    elif actualSeason is not None:
        nextCycle = actualSeason.getNextByTimeCycle(time_utils.getCurrentLocalServerTimestamp())
        if nextCycle:
            block.append(_getTimeBlock(seasonIsStarted, False, time_utils.makeLocalServerTime(nextCycle.startDate), modeName, timeStringGetter))
        else:
            wait = backport.text(R.strings.menu.headerButtons.battle.types.dyn(modeName).extra.finished())
            block.append(formatters.packTitleDescBlock(title=text_styles.main(wait)))
    return block


def _getTimeBlock(isSeasonStarted, tillEnd, timeStamp, modeName, timeStringGetter, leftPadding=0):
    if isSeasonStarted:
        tillStartStr = R.strings.tooltips.battleTypes.dyn(modeName).tillStart
        tillEndStr = R.strings.tooltips.battleTypes.dyn(modeName).tillEnd
    else:
        tillStartStr = R.strings.tooltips.battleTypes.dyn(modeName).tillStartCycle
        tillEndStr = R.strings.tooltips.battleTypes.dyn(modeName).tillEndCycle
    return formatters.packTextBlockData('{} {}'.format(text_styles.main(backport.text(tillEndStr() if tillEnd else tillStartStr())), text_styles.stats(timeStringGetter(timeStamp))), padding=formatters.packPadding(left=leftPadding))
