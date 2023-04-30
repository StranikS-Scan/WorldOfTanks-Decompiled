# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/periodic/prime_helpers.py
from gui.impl import backport
from gui.impl.gen import R
from helpers import time_utils
from gui.shared.formatters import text_styles
from gui.shared.formatters.time_formatters import formatDate
from gui.shared.tooltips import formatters

def getPrimeTableBlocks(primeTime, currentCycleEnd, resRoot):
    primeTableBlocks = [_packTimeTableHeaderBlock(resRoot)]
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
    todayStr = _packPeriods(todayPeriods, resRoot)
    primeTableBlocks.append(_packTimeBlock(message=text_styles.main(backport.text(resRoot.timeTable.today())), timeStr=text_styles.bonusPreviewText(todayStr)))
    tomorrowStr = _packPeriods(tomorrowPeriods, resRoot)
    primeTableBlocks.append(_packTimeBlock(message=text_styles.main(backport.text(resRoot.timeTable.tomorrow())), timeStr=text_styles.stats(tomorrowStr)))
    return primeTableBlocks


def getPrimeTableWidgetBlocks(primeTime, currentCycleEnd, resRoot, tableTopPadding=-15, ignoreHeaderImageSize=False):
    primeTableBlocks = [_packTimeTableHeaderBlock(resRoot, ignoreHeaderImageSize)]
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
    todayStr = _packPeriods(todayPeriods, resRoot)
    primeTableBlocks.append(_packTimeBlock(message=text_styles.main(backport.text(resRoot.today())), timeStr=text_styles.stats(todayStr), topPadding=tableTopPadding, leftPadding=10, bottomPadding=-10, gap=10))
    tomorrowStr = _packPeriods(tomorrowPeriods, resRoot)
    primeTableBlocks.append(_packTimeBlock(message=text_styles.main(backport.text(resRoot.tomorrow())), timeStr=text_styles.main(tomorrowStr), leftPadding=10, gap=10))
    return primeTableBlocks


def _packTimeTableHeaderBlock(resRoot, ignoreImageSize=False):
    return formatters.packImageTextBlockData(title=text_styles.stats(backport.text(resRoot.timeTable.title())), img=backport.image(R.images.gui.maps.icons.buttons.calendar()), imgPadding=formatters.packPadding(top=2), txtPadding=formatters.packPadding(left=5), ignoreImageSize=ignoreImageSize)


def _packPeriods(periods, resRoot):
    if periods:
        periodsStr = []
        for periodStart, periodEnd in periods:
            startTime = formatDate('%H:%M', periodStart)
            endTime = formatDate('%H:%M', periodEnd)
            periodsStr.append(backport.text(resRoot.timeTable.time(), start=startTime, end=endTime))

        return '\n'.join(periodsStr)
    return backport.text(resRoot.timeTable.empty())


def _packTimeBlock(message, timeStr, leftPadding=0, bottomPadding=0, topPadding=0, gap=0):
    return formatters.packTextParameterBlockData(value=timeStr, name=message, valueWidth=97, padding=formatters.packPadding(left=leftPadding, bottom=bottomPadding, top=topPadding), gap=gap)
