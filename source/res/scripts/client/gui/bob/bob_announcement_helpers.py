# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/bob/bob_announcement_helpers.py
from adisp import adisp_process
from constants import QUEUE_TYPE
from gui.bob.bob_constants import ANNOUNCEMENT_PRIORITY, AnnouncementType, EntryPointData
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.bob.bob_entry_point_view_model import State as EntryPointState
from gui.marathon.bob_event import BobEvent
from gui.prb_control import prbEntityProperty
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.periodic_battles.models import PrimeTimeStatus
from gui.server_events.events_dispatcher import showMissionsMarathon
from helpers import dependency, time_utils
from skeletons.gui.game_control import IBobController, IBobAnnouncementController
from gui.marathon.marathon_constants import ZERO_TIME

class Announcement(object):
    _bobController = dependency.descriptor(IBobController)

    def __init__(self):
        super(Announcement, self).__init__()
        self.__isBobPrb = False

    @property
    def priority(self):
        return ANNOUNCEMENT_PRIORITY.get(self.type, 0)

    @property
    def type(self):
        return AnnouncementType.UNKNOWN

    @prbEntityProperty
    def prbEntity(self):
        return None

    def couldBeShown(self):
        return not self.__isBobPrb and self._bobController.isEnabled()

    def onClick(self):
        pass

    def updatePrb(self, isBobPrb):
        self.__isBobPrb = isBobPrb

    def getEntryPointData(self):
        return EntryPointData()

    @adisp_process
    def _selectEventMode(self):
        isPrbInited = self.prbEntity is not None
        if isPrbInited:
            dispatcher = g_prbLoader.getDispatcher()
            state = dispatcher.getFunctionalState()
            if not state.isInPreQueue(queueType=QUEUE_TYPE.BOB):
                yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.BOB))
        return

    def _openEventWeb(self):
        showMissionsMarathon(marathonPrefix=BobEvent.BOB_EVENT_PREFIX)


class BeforeEventStartAnnouncement(Announcement):

    @property
    def type(self):
        return AnnouncementType.BEFORE_EVENT_START

    def couldBeShown(self):
        beforeStartTime, _ = self._bobController.getTimeTillRegistrationStartOrEnd()
        isBeforeRegistration = beforeStartTime > ZERO_TIME
        return super(BeforeEventStartAnnouncement, self).couldBeShown() and isBeforeRegistration

    def onClick(self):
        pass

    def getEntryPointData(self):
        return EntryPointData(header=backport.text(R.strings.bob.entryPoint.title()), body=backport.text(R.strings.bob.entryPoint.beforeRegistration.body()), footer=_getTimeDescription(_getTimeTillRegistrationStart()), state=EntryPointState.BEFOREEVENTSTART, deltaFunc=_getTimeTillRegistrationStart)


class PausedAnnouncement(Announcement):

    @property
    def type(self):
        return AnnouncementType.PAUSED

    def couldBeShown(self):
        return super(PausedAnnouncement, self).couldBeShown() and self._bobController.isPaused()

    def onClick(self):
        pass

    def getEntryPointData(self):
        return EntryPointData(header='', body=backport.text(R.strings.bob.entryPoint.paused.body()), footer='', state=EntryPointState.PAUSED)


class RegistrationAfterEventStartAnnouncement(Announcement):

    @property
    def type(self):
        return AnnouncementType.REGISTRATION_AFTER_EVENT_START

    def couldBeShown(self):
        return super(RegistrationAfterEventStartAnnouncement, self).couldBeShown() and self._bobController.isRegistrationEnabled() and not self._bobController.isRegistered() and self._bobController.isModeActive()

    def onClick(self):
        self._openEventWeb()

    def getEntryPointData(self):
        return EntryPointData(header='', body=backport.text(R.strings.bob.entryPoint.registration.afterStart.body()), footer=backport.text(R.strings.bob.entryPoint.registration.afterStart.footer()), state=EntryPointState.REGISTRATIONAFTEREVENTSTART)


class AvailablePrimeTimeAnnouncement(Announcement):

    @property
    def type(self):
        return AnnouncementType.AVAILABLE_PRIME_TIME

    def couldBeShown(self):
        return super(AvailablePrimeTimeAnnouncement, self).couldBeShown() and self._bobController.isModeActive() and self._bobController.getPrimeTimeStatus()[0] == PrimeTimeStatus.AVAILABLE

    def onClick(self):
        self._selectEventMode()

    def getEntryPointData(self):
        return EntryPointData(header=backport.text(R.strings.bob.entryPoint.title()), body=backport.text(R.strings.bob.entryPoint.availablePrimeTime.body()), footer=_getEventDueDateStr(), state=EntryPointState.AVAILABLEPRIMETIME)


class NotAvailablePrimeTimeAnnouncement(Announcement):

    @property
    def type(self):
        return AnnouncementType.NOT_AVAILABLE_PRIME_TIME

    def couldBeShown(self):
        return super(NotAvailablePrimeTimeAnnouncement, self).couldBeShown() and self._bobController.isModeActive() and self._bobController.getPrimeTimeStatus()[0] == PrimeTimeStatus.NOT_AVAILABLE

    def onClick(self):
        self._selectEventMode()

    def getEntryPointData(self):
        return EntryPointData(header='', body=backport.text(R.strings.bob.entryPoint.notAvailablePrimeTime.body()), footer=_getTimeDescription(_getTimeTillUpdatePrimeTime()), state=EntryPointState.NOTAVAILABLEPRIMETIME, deltaFunc=_getTimeTillUpdatePrimeTime)


class EventFinishAnnouncement(Announcement):

    @property
    def type(self):
        return AnnouncementType.EVENT_FINISH

    def couldBeShown(self):
        return super(EventFinishAnnouncement, self).couldBeShown() and self._bobController.isPostEventTime()

    def onClick(self):
        self._openEventWeb()

    def getEntryPointData(self):
        return EntryPointData(header='', body=backport.text(R.strings.bob.entryPoint.eventFinish.body()), footer=backport.text(R.strings.bob.entryPoint.eventFinish.footer()), state=EntryPointState.EVENTFINISH)


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
def _getTimeRegistrationStart(bobCtrl=None):
    config = bobCtrl.getConfig()
    if config is not None:
        dueDateTimestamp = config.registration['start']
        dueDate = time_utils.getTimeStructInLocal(dueDateTimestamp)
        return _getTillDateText(dueDate)
    else:
        return ''


@dependency.replace_none_kwargs(bobCtrl=IBobController)
def _getTimeTillUpdatePrimeTime(bobCtrl=None):
    _, timeTillUpdate, _ = bobCtrl.getPrimeTimeStatus()
    return timeTillUpdate


@dependency.replace_none_kwargs(bobCtrl=IBobController)
def _getEventDueDateStr(bobCtrl=None):
    season = bobCtrl.getCurrentSeason() or bobCtrl.getNextSeason()
    return _getTillDateText(time_utils.getTimeStructInLocal(season.getEndDate())) if season else ''


@dependency.replace_none_kwargs(bobCtrl=IBobController)
def _getTimeTillStartEvent(bobCtrl=None):
    season = bobCtrl.getCurrentSeason() or bobCtrl.getNextSeason()
    return max(season.getStartDate() - time_utils.getServerUTCTime(), 0) if season else 0


@dependency.replace_none_kwargs(bobCtrl=IBobController)
def _getTimeTillRegistrationEnd(bobCtrl=None):
    _, endTime = bobCtrl.getTimeTillRegistrationStartOrEnd()
    return endTime


@dependency.replace_none_kwargs(bobCtrl=IBobController)
def _getTimeTillRegistrationStart(bobCtrl=None):
    startTime, _ = bobCtrl.getTimeTillRegistrationStartOrEnd()
    return startTime


def _getTillDateText(dateTime):
    return backport.text(R.strings.bob.entryPoint.tillDate.description(), day=dateTime.tm_mday, month=backport.text(R.strings.menu.dateTime.months.num(dateTime.tm_mon)()))


def _getTimeDescription(timeValue):
    return backport.backport_time_utils.getTillTimeStringByRClass(timeValue=timeValue, stringRClass=R.strings.bob.entryPoint.timeLeft, removeLeadingZeros=True)


@dependency.replace_none_kwargs(bobAnnouncement=IBobAnnouncementController)
def getBobEntryPointIsActive(bobAnnouncement=None):
    return bobAnnouncement.currentAnnouncement is not None
