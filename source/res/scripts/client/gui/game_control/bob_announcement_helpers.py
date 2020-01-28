# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/bob_announcement_helpers.py
from collections import namedtuple
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency, time_utils
from skeletons.gui.game_control import IBobController

class AnnouncementType(object):
    REGISTRATION = 0
    EVENT_START = 1
    EVENT_FINISH = 2
    PRIME_TIME = 3
    SKILL_ACTIVE = 4


ANNOUNCEMENT_PRIORITY = {AnnouncementType.REGISTRATION: 1,
 AnnouncementType.EVENT_START: 2,
 AnnouncementType.EVENT_FINISH: 3,
 AnnouncementType.PRIME_TIME: 4,
 AnnouncementType.SKILL_ACTIVE: 2}
_AnnouncementWidgetData = namedtuple('_AnnouncementWidgetData', ('header', 'body', 'hasTimerIcon', 'hasLockerIcon'))
_AnnouncementWidgetData.__new__.__defaults__ = ('',
 '',
 False,
 False)
_ANNOUNCEMENT_WIDGET_HEADER = {AnnouncementType.EVENT_START: R.strings.bob.announcement.eventStart.header,
 AnnouncementType.EVENT_FINISH: R.strings.bob.announcement.eventFinish.header,
 AnnouncementType.PRIME_TIME: R.strings.bob.announcement.primeTime.header,
 AnnouncementType.SKILL_ACTIVE: R.strings.bob.announcement.skillActivated.header}

@dependency.replace_none_kwargs(bobCtrl=IBobController)
def getAnnouncementWidgetData(announcementType, bobCtrl=None):
    if announcementType == AnnouncementType.REGISTRATION:
        return _AnnouncementWidgetData(header=backport.text(R.strings.bob.announcement.registration.header()), body=_getRegistrationDueDateStr())
    if announcementType == AnnouncementType.EVENT_START:
        if bobCtrl.isRuEuRealm():
            timeStr, isLocked = _getTimeToPrimeTime()
            return _AnnouncementWidgetData(header=backport.text(R.strings.bob.announcement.eventStart.header()), body=timeStr, hasLockerIcon=isLocked)
        if bobCtrl.isNaAsiaRealm():
            return _AnnouncementWidgetData(header=backport.text(R.strings.bob.announcement.selectTearX.header()), body=_getEventDueDateStr())
    if announcementType == AnnouncementType.EVENT_FINISH:
        return _AnnouncementWidgetData(header=backport.text(R.strings.bob.announcement.eventFinish.header()), body=backport.text(R.strings.bob.announcement.eventFinish.description()))
    if announcementType == AnnouncementType.PRIME_TIME:
        return _AnnouncementWidgetData(header=backport.text(R.strings.bob.announcement.primeTime.header()), body=_getTimeToPrimeTimeEndStr(), hasTimerIcon=True)
    return _AnnouncementWidgetData(header=backport.text(R.strings.bob.announcement.skillActivated.header()), body=backport.text(R.strings.bob.announcement.skillActivated.description())) if announcementType == AnnouncementType.SKILL_ACTIVE else _AnnouncementWidgetData()


@dependency.replace_none_kwargs(bobCtrl=IBobController)
def _getRegistrationDueDateStr(bobCtrl=None):
    config = bobCtrl.getConfig()
    if config is not None:
        dueDateTimestamp = config.registration['end']
        dueDate = time_utils.getTimeStructInLocal(dueDateTimestamp)
        return _getTillDateText(dueDate)
    else:
        return ''


@dependency.replace_none_kwargs(bobCtrl=IBobController)
def _getTimeToPrimeTime(bobCtrl=None):
    _, timeTillUpdate, isNow = bobCtrl.getPrimeTimeStatus()
    return (_getTimeDescription(timeTillUpdate), True) if not isNow else ('', False)


@dependency.replace_none_kwargs(bobCtrl=IBobController)
def _getTimeToPrimeTimeEndStr(bobCtrl=None):
    _, timeTillUpdate, isNow = bobCtrl.getPrimeTimeStatus()
    return _getTimeDescription(timeTillUpdate) if isNow else ''


@dependency.replace_none_kwargs(bobCtrl=IBobController)
def _getEventDueDateStr(bobCtrl=None):
    season = bobCtrl.getCurrentSeason() or bobCtrl.getNextSeason()
    endDate = time_utils.getTimeStructInLocal(season.getEndDate())
    return _getTillDateText(endDate)


def _getTillDateText(dateTime):
    return backport.text(R.strings.bob.announcement.tillDate.description(), day=dateTime.tm_mday, month=backport.text(R.strings.menu.dateTime.months.num(dateTime.tm_mon)()))


def _getTimeDescription(timeValue):
    return backport.backport_time_utils.getTillTimeStringByRClass(timeValue=timeValue, stringRClass=R.strings.menu.Time.timeValue, removeLeadingZeros=True)
