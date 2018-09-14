# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/events_helpers.py
import time
import BigWorld
from gui import makeHtmlString
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.server_events import formatters
from helpers import time_utils, i18n
from shared_utils import CONST_CONTAINER
FINISH_TIME_LEFT_TO_SHOW = time_utils.ONE_DAY
START_TIME_LIMIT = 5 * time_utils.ONE_DAY
AWARDS_PER_PAGE = 3
AWARDS_PER_SINGLE_PAGE = 4

class EventInfoModel(object):
    NO_BONUS_COUNT = -1

    def __init__(self, event):
        self.event = event

    def getTimerMsg(self, key=None):
        startTimeLeft = self.event.getStartTimeLeft()
        if startTimeLeft > 0:
            if startTimeLeft > START_TIME_LIMIT:
                fmt = self._getDateTimeString(self.event.getStartTime())
            else:
                fmt = self._getTillTimeString(startTimeLeft)
            return makeHtmlString('html_templates:lobby/quests', 'timerTillStart', {'time': fmt})
        if FINISH_TIME_LEFT_TO_SHOW > self.event.getFinishTimeLeft() > 0:
            gmtime = time.gmtime(self.event.getFinishTimeLeft())
            if gmtime.tm_hour > 0:
                fmt = i18n.makeString('#quests:item/timer/tillFinish/onlyHours')
            else:
                fmt = i18n.makeString('#quests:item/timer/tillFinish/lessThanHour')
            fmt %= {'hours': time.strftime('%H', gmtime),
             'min': time.strftime('%M', gmtime),
             'days': str(gmtime.tm_mday)}
            return makeHtmlString('html_templates:lobby/quests', 'timerTillFinish', {'time': fmt})

    def _getStatus(self, pCur=None):
        return (EVENT_STATUS.NONE, '')

    @classmethod
    def _getTillTimeString(cls, timeValue):
        return time_utils.getTillTimeString(timeValue, MENU.TIME_TIMEVALUE)

    @classmethod
    def _getDailyProgressResetTimeOffset(cls):
        regionalSettings = BigWorld.player().serverSettings['regional_settings']
        if 'starting_time_of_a_new_game_day' in regionalSettings:
            newDayOffset = regionalSettings['starting_time_of_a_new_game_day']
        elif 'starting_time_of_a_new_day' in regionalSettings:
            newDayOffset = regionalSettings['starting_time_of_a_new_day']
        else:
            newDayOffset = 0
        return newDayOffset

    def _getActiveDateTimeString(self):
        i18nKey, args = None, {}
        if self.event.getFinishTimeLeft() <= time_utils.ONE_DAY:
            gmtime = time.gmtime(self.event.getFinishTimeLeft())
            if gmtime.tm_hour > 0:
                fmt = i18n.makeString(QUESTS.ITEM_TIMER_TILLFINISH_LONGFULLFORMAT)
            else:
                fmt = i18n.makeString(QUESTS.ITEM_TIMER_TILLFINISH_SHORTFULLFORMAT)
            fmt %= {'hours': time.strftime('%H', gmtime)}
            return fmt
        else:
            if self.event.getStartTimeLeft() > 0:
                i18nKey = '#quests:details/header/activeDuration'
                args = {'startTime': self._getDateTimeString(self.event.getStartTime()),
                 'finishTime': self._getDateTimeString(self.event.getFinishTime())}
            elif self.event.getFinishTimeLeft() <= time_utils.HALF_YEAR:
                i18nKey = '#quests:details/header/tillDate'
                args = {'finishTime': self._getDateTimeString(self.event.getFinishTime())}
            weekDays = self.event.getWeekDays()
            intervals = self.event.getActiveTimeIntervals()
            if len(weekDays) or len(intervals):
                if i18nKey is None:
                    i18nKey = '#quests:details/header/schedule'
                if len(weekDays):
                    days = ', '.join([ i18n.makeString('#menu:dateTime/weekDays/full/%d' % idx) for idx in self.event.getWeekDays() ])
                    i18nKey += 'Days'
                    args['days'] = days
                if len(intervals):
                    times = []
                    for low, high in intervals:
                        times.append('%s - %s' % (BigWorld.wg_getShortTimeFormat(low), BigWorld.wg_getShortTimeFormat(high)))

                    i18nKey += 'Times'
                    times = ', '.join(times)
                    args['times'] = times
            return None if i18nKey is None else i18n.makeString(i18nKey, **args)

    @classmethod
    def _getDateTimeString(cls, timeValue):
        return '{0:>s} {1:>s}'.format(BigWorld.wg_getLongDateFormat(timeValue), BigWorld.wg_getShortTimeFormat(timeValue))


class QuestInfoModel(EventInfoModel):

    def _getActiveDateTimeString(self):
        timeLeft = self.event.getFinishTimeLeft()
        return formatters.formatYellow(QUESTS.DETAILS_HEADER_COMETOENDINMINUTES, minutes=getMinutesRoundByTime(timeLeft)) if timeLeft <= time_utils.THREE_QUARTER_HOUR else super(QuestInfoModel, self)._getActiveDateTimeString()

    def getTimerMsg(self, key='comeToEndInMinutes'):
        timeLeft = self.event.getFinishTimeLeft()
        return makeHtmlString('html_templates:lobby/quests/', key, {'minutes': getMinutesRoundByTime(timeLeft)}) if timeLeft <= time_utils.THREE_QUARTER_HOUR else super(QuestInfoModel, self).getTimerMsg()

    def _getDailyResetStatus(self, resetLabelKey, labeFormatter):
        if self.event.bonusCond.isDaily():
            resetHourOffset = (time_utils.ONE_DAY - self._getDailyProgressResetTimeOffset()) / time_utils.ONE_HOUR
            if resetHourOffset >= 0:
                return labeFormatter(resetLabelKey) % {'time': time.strftime(i18n.makeString('#quests:details/conditions/postBattle/dailyReset/timeFmt'), time_utils.getTimeStructInLocal(time_utils.getTimeTodayForUTC(hour=resetHourOffset)))}

    def _getCompleteDailyStatus(self, completeKey):
        return i18n.makeString(completeKey, time=self._getTillTimeString(time_utils.ONE_DAY - time_utils.getServerRegionalTimeCurrentDay()))


def getCarouselAwardVO(bonuses, isReceived=False):
    """ Generate award VOs for carousel.
    
    :param bonuses: list of bonuses (instances of gui.server_events.SimpleBonus).
    :param isReceived: flag describing whether this is 'already received' context.
    """
    result = []
    for bonus in bonuses:
        if not bonus.isShowInGUI():
            continue
        result.extend(bonus.getCarouselList(isReceived))

    while len(result) % AWARDS_PER_PAGE != 0 and len(result) > AWARDS_PER_SINGLE_PAGE:
        result.append({})

    return result


class EVENT_STATUS(CONST_CONTAINER):
    COMPLETED = 'done'
    NOT_AVAILABLE = 'notAvailable'
    WRONG_TIME = 'wrongTime'
    NONE = ''


def getMinutesRoundByTime(timeLeft):
    timeLeft = int(timeLeft)
    return (timeLeft / time_utils.QUARTER_HOUR + cmp(timeLeft % time_utils.QUARTER_HOUR, 0)) * time_utils.QUARTER


def missionsSortFunc(a, b):
    """ Sort function for common quests (all except potapov and motive).
    """
    res = cmp(a.isAvailable()[0] and not a.isCompleted(), b.isAvailable()[0] and not b.isCompleted())
    if res:
        return res
    res = cmp(a.getPriority(), b.getPriority())
    if res:
        return res
    res = cmp(a.isAvailable()[1] == 'requirement', b.isAvailable()[1] == 'requirement')
    if res:
        return res
    res = cmp(bool(a.isAvailable()[1]), bool(b.isAvailable()[1]))
    if res:
        return res
    res = cmp(a.isCompleted(), b.isCompleted())
    return res if res else cmp(a.getUserName(), b.getUserName())
