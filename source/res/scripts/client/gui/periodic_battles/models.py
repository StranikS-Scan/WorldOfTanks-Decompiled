# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/periodic_battles/models.py
import logging
from functools import partial
import typing
from enum import Enum
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.genConsts.ALERTMESSAGE_CONSTANTS import ALERTMESSAGE_CONSTANTS
from gui.shared.formatters import text_styles
from gui.shared.utils.decorators import ReprInjector
from gui.shared.utils.functions import makeTooltip
from helpers import time_utils
from shared_utils import collapseIntervals, findFirst, first, CONST_CONTAINER
if typing.TYPE_CHECKING:
    from gui.impl.gen_utils import DynAccessor
    from season_common import GameSeason, GameSeasonCycle
_logger = logging.getLogger(__name__)

class PrimeTimeStatus(CONST_CONTAINER):
    NOT_SET = 1
    FROZEN = 2
    NOT_AVAILABLE = 3
    AVAILABLE = 4


class PeriodType(Enum):
    UNDEFINED = 'undefined'
    BEFORE_SEASON = 'beforeSeason'
    BETWEEN_SEASONS = 'betweenSeasons'
    AFTER_SEASON = 'afterSeason'
    BEFORE_CYCLE = 'beforeCycle'
    BETWEEN_CYCLES = 'betweenCycles'
    AFTER_CYCLE = 'afterCycle'
    AVAILABLE = 'available'
    FROZEN = 'frozen'
    NOT_AVAILABLE = 'notAvailable'
    ALL_NOT_AVAILABLE = 'allNotAvailable'
    STANDALONE_NOT_AVAILABLE = 'standaloneNotAvailable'
    NOT_AVAILABLE_END = 'notAvailableEnd'
    ALL_NOT_AVAILABLE_END = 'allNotAvailableEnd'
    STANDALONE_NOT_AVAILABLE_END = 'standaloneNotAvailableEnd'
    NOT_SET = 'notSet'
    ALL_NOT_SET = 'allNotSet'
    STANDALONE_NOT_SET = 'standaloneNotSet'


PERIOD_TO_STANDALONE = {PeriodType.FROZEN: PeriodType.FROZEN,
 PeriodType.AVAILABLE: PeriodType.AVAILABLE,
 PeriodType.NOT_AVAILABLE: PeriodType.STANDALONE_NOT_AVAILABLE,
 PeriodType.ALL_NOT_AVAILABLE: PeriodType.STANDALONE_NOT_AVAILABLE,
 PeriodType.NOT_SET: PeriodType.STANDALONE_NOT_SET,
 PeriodType.ALL_NOT_SET: PeriodType.STANDALONE_NOT_SET,
 PeriodType.NOT_AVAILABLE_END: PeriodType.STANDALONE_NOT_AVAILABLE_END,
 PeriodType.ALL_NOT_AVAILABLE_END: PeriodType.STANDALONE_NOT_AVAILABLE_END}

@ReprInjector.simple('userName', 'timestamp', 'techData')
class PeriodBorder(object):
    __slots__ = ('userName', 'timestamp', 'techData')
    _TECH_FIELD_FMT = '{techName}{fieldName}'

    def __init__(self, userName, timestamp):
        self.userName = userName
        self.timestamp = timestamp
        self.techData = {'Name': '',
         'Time': '',
         'Date': '',
         'Delta': ''}

    def delta(self, now):
        return abs(now - self.timestamp)

    def setTechName(self, techName):
        data = self.techData
        for fieldName in data:
            data[fieldName] = self._TECH_FIELD_FMT.format(techName=techName, fieldName=fieldName)


@ReprInjector.simple('now', 'periodType', 'seasonBorderLeft', 'seasonBorderRight', 'cycleBorderLeft', 'cycleBorderRight', 'primeDelta')
class PeriodInfo(object):
    __slots__ = ('now', 'periodType', 'seasonBorderLeft', 'seasonBorderRight', 'cycleBorderLeft', 'cycleBorderRight', 'primeDelta', 'borders')

    def __init__(self, now, pType, seasonLeft=None, seasonRight=None, cycleLeft=None, cycleRight=None, primeDelta=0):
        self.now = now
        self.periodType = pType
        self.seasonBorderLeft = self.__addBorderTechName(seasonLeft, 'leftSeason')
        self.seasonBorderRight = self.__addBorderTechName(seasonRight, 'rightSeason')
        self.cycleBorderLeft = self.__addBorderTechName(cycleLeft, 'leftCycle')
        self.cycleBorderRight = self.__addBorderTechName(cycleRight, 'rightCycle')
        self.primeDelta = primeDelta
        bordersWithNones = (self.seasonBorderLeft,
         self.cycleBorderLeft,
         self.cycleBorderRight,
         self.seasonBorderRight)
        self.borders = tuple((border for border in bordersWithNones if border is not None))

    @staticmethod
    def defaultDeltaFormatter(resRoot):
        return partial(backport.getTillTimeStringByRClass, stringRClass=resRoot)

    @staticmethod
    def leftSeasonBorder(season):
        return PeriodBorder(season.getUserName(), season.getStartDate()) if season else None

    @staticmethod
    def rightSeasonBorder(season):
        return PeriodBorder(season.getUserName(), season.getEndDate()) if season else None

    @staticmethod
    def leftCycleBorder(cycle):
        return PeriodBorder(cycle.getUserName(), cycle.startDate) if cycle else None

    @staticmethod
    def rightCycleBorder(cycle):
        return PeriodBorder(cycle.getUserName(), cycle.endDate) if cycle else None

    def getVO(self, withBNames=False, withBDeltas=False, deltaFmt=None, timeFmt=None, dateFmt=None):
        result = self.__buildNames() if withBNames else {}
        if deltaFmt is not None:
            self.__buildDeltas(result, deltaFmt, withBDeltas)
        if timeFmt is not None or dateFmt is not None:
            self.__buildDates(result, timeFmt, dateFmt)
        return result

    def __addBorderTechName(self, border, techName):
        if border is not None:
            border.setTechName(techName)
        return border

    def __buildDeltas(self, result, deltaFormatter, bordersDeltas):
        result['primeDelta'] = deltaFormatter(self.primeDelta)
        if bordersDeltas:
            for border in self.borders:
                result[border.techData['Delta']] = deltaFormatter(border.delta(self.now))

    def __buildDates(self, result, timeFormatter, dateFormatter):
        primeDeltaStamp = self.primeDelta + self.now
        if timeFormatter is not None:
            result['primeDeltaTime'] = timeFormatter(primeDeltaStamp)
            for border in self.borders:
                result[border.techData['Time']] = timeFormatter(border.timestamp)

        if dateFormatter is not None:
            result['primeDeltaDate'] = dateFormatter(primeDeltaStamp)
            for border in self.borders:
                result[border.techData['Date']] = dateFormatter(border.timestamp)

        return

    def __buildNames(self):
        return {border.techData['Name']:border.userName for border in self.borders}


class PrimeTime(object):

    def __init__(self, peripheryID, periods=None):
        super(PrimeTime, self).__init__()
        self.__peripheryID = peripheryID
        self.__periods = periods or {}

    def hasAnyPeriods(self):
        return bool(self.__periods)

    def getAvailability(self, forTime, cycleEnd):
        periods = self.getPeriodsBetween(forTime, cycleEnd)
        if periods:
            periodsIter = iter(periods)
            currentPeriod = findFirst(lambda (pS, pE): pS <= forTime < pE, periodsIter)
            if currentPeriod is not None:
                _, currentPeriodEnd = currentPeriod
                return (True, currentPeriodEnd - forTime)
            nextPeriod = first(periods)
            if nextPeriod is not None:
                nextPeriodStart, _ = nextPeriod
                return (False, nextPeriodStart - forTime)
        return (False, 0)

    def getNextPeriodStart(self, fromTime, tillTime, includeBeginning=False):
        periods = self.getPeriodsBetween(fromTime, tillTime, includeBeginning=includeBeginning)
        if periods:
            nextPeriod = first(periods)
            if nextPeriod is not None:
                nextPeriodStart, _ = nextPeriod
                return nextPeriodStart
        return

    def getPeriodsActiveForTime(self, periodTime, preferPeriodBounds=False):
        return self.getPeriodsBetween(periodTime, periodTime, preferPeriodBounds=preferPeriodBounds)

    def getPeriodsBetween(self, startTime, endTime, includeBeginning=True, includeEnd=True, preferPeriodBounds=False):
        periods = []
        startDateTime = time_utils.getDateTimeInUTC(startTime)
        startTimeDayStart, _ = time_utils.getDayTimeBoundsForUTC(startTime)
        weekDay = startDateTime.isoweekday()
        while startTimeDayStart <= endTime:
            if weekDay in self.__periods:
                for (startH, startM), (endH, endM) in self.__periods[weekDay]:
                    periodStartTime = startTimeDayStart + startH * time_utils.ONE_HOUR + startM * time_utils.ONE_MINUTE
                    periodEndTime = startTimeDayStart + endH * time_utils.ONE_HOUR + endM * time_utils.ONE_MINUTE
                    if startTime < periodEndTime and periodStartTime <= endTime:
                        if not includeBeginning and startTime > periodStartTime:
                            continue
                        if not includeEnd and endTime < periodEndTime:
                            continue
                        if preferPeriodBounds:
                            periods.append((periodStartTime, periodEndTime))
                        else:
                            periods.append((max(startTime, periodStartTime), min(endTime, periodEndTime)))

            if weekDay == time_utils.WEEK_END:
                weekDay = time_utils.WEEK_START
            else:
                weekDay += 1
            startTimeDayStart += time_utils.ONE_DAY

        return collapseIntervals(periods)


class AlertData(object):
    _RES_ROOT = None
    _PERIOD_TYPES_WITH_BUTTON = (PeriodType.NOT_AVAILABLE, PeriodType.NOT_AVAILABLE_END, PeriodType.NOT_SET)
    _PERIOD_TYPES_PRIME_ALERT = (PeriodType.AVAILABLE,
     PeriodType.NOT_AVAILABLE_END,
     PeriodType.NOT_SET,
     PeriodType.ALL_NOT_SET,
     PeriodType.STANDALONE_NOT_SET,
     PeriodType.NOT_AVAILABLE,
     PeriodType.ALL_NOT_AVAILABLE,
     PeriodType.STANDALONE_NOT_AVAILABLE)
    _RES_REASON_ROOT = None
    __slots__ = ('state', 'alertIcon', 'buttonIcon', 'buttonLabel', 'buttonVisible', 'buttonTooltip', 'statusText', 'additionalText', 'popoverAlias', 'bgVisible', 'shadowFilterVisible', 'tooltip', 'isSimpleTooltip')

    def __init__(self, state=ALERTMESSAGE_CONSTANTS.ALERT_MESSAGE_STATE_DEFAULT, alertIcon=None, buttonIcon='', buttonLabel='', buttonVisible=False, buttonTooltip=None, statusText='', additionalText='', popoverAlias=None, bgVisible=True, shadowFilterVisible=False, tooltip=None, isSimpleTooltip=False):
        self.state = state
        self.alertIcon = alertIcon
        self.buttonIcon = buttonIcon
        self.buttonLabel = buttonLabel
        self.buttonVisible = buttonVisible
        self.buttonTooltip = buttonTooltip
        self.statusText = statusText
        self.additionalText = additionalText
        self.popoverAlias = popoverAlias
        self.bgVisible = bgVisible
        self.shadowFilterVisible = shadowFilterVisible
        self.tooltip = tooltip
        self.isSimpleTooltip = isSimpleTooltip

    @classmethod
    def construct(cls, periodInfo, serverShortName):
        isPrimeAlert = periodInfo.periodType in cls._PERIOD_TYPES_PRIME_ALERT
        return cls(alertIcon=backport.image(R.images.gui.maps.icons.library.alertBigIcon()) if isPrimeAlert else None, buttonLabel=backport.text(cls._RES_ROOT.button.changeServer()), buttonVisible=periodInfo.periodType in cls._PERIOD_TYPES_WITH_BUTTON, statusText=text_styles.vehicleStatusCriticalText(cls._getAlertLabel(periodInfo, serverShortName)), shadowFilterVisible=isPrimeAlert, tooltip=cls._getTooltip(periodInfo))

    @classmethod
    def constructForVehicle(cls, levelsStr, vehicleIsAvailableForBuy, vehicleIsAvailableForRestore, tooltip=None):
        if cls._RES_REASON_ROOT is None:
            _logger.error('AlertData._RES_REASON_ROOT is None. Please define it to use constructForVehicle method!')
        reason = cls._RES_REASON_ROOT.vehicleUnavailable()
        if vehicleIsAvailableForBuy:
            reason = cls._RES_REASON_ROOT.vehicleAvailableForBuy()
        elif vehicleIsAvailableForRestore:
            reason = cls._RES_REASON_ROOT.vehicleAvailableForRestore()
        tooltipValue = tooltip if tooltip is not None else makeTooltip(body=backport.text(reason, levels=levelsStr))
        return cls(alertIcon=backport.image(R.images.gui.maps.icons.library.alertBigIcon()), buttonLabel=backport.text(cls._RES_ROOT.button.moreInfo()), buttonVisible=True, statusText=text_styles.vehicleStatusCriticalText(backport.text(cls._RES_ROOT.unsuitableVehicles(), levels=levelsStr)), shadowFilterVisible=True, tooltip=tooltipValue, isSimpleTooltip=tooltip is None)

    def asDict(self):
        return {'state': self.state,
         'alertIcon': self.alertIcon,
         'buttonIcon': self.buttonIcon,
         'buttonLabel': self.buttonLabel,
         'buttonVisible': self.buttonVisible,
         'buttonTooltip': self.buttonTooltip,
         'statusText': self.statusText,
         'additionalText': self.additionalText,
         'popoverAlias': self.popoverAlias,
         'bgVisible': self.bgVisible,
         'shadowFilterVisible': self.shadowFilterVisible,
         'tooltip': self.tooltip,
         'isSimpleTooltip': self.isSimpleTooltip}

    @classmethod
    def _getAlertLabel(cls, periodInfo, serverShortName):
        params = cls._getAlertLabelParams(periodInfo)
        params['serverName'] = serverShortName
        return backport.text(cls._RES_ROOT.dyn(periodInfo.periodType.value, cls._RES_ROOT.undefined)(), **params)

    @classmethod
    def _getAlertLabelParams(cls, periodInfo):
        return periodInfo.getVO(withBNames=True, deltaFmt=PeriodInfo.defaultDeltaFormatter(cls._RES_ROOT.timeLeft))

    @classmethod
    def _getTooltip(cls, periodInfo):
        return None
