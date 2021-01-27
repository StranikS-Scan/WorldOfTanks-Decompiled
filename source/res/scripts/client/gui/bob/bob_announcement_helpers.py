# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/bob/bob_announcement_helpers.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import BOB_BANNERS_VIEWED
from adisp import process
from constants import QUEUE_TYPE
from gui.bob.bob_constants import ANNOUNCEMENT_PRIORITY, AnnouncementType, EntryPointData
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.bob.bob_entry_point_view_model import BobEntryPointViewModel
from gui.marathon.bob_event import BobEvent
from gui.prb_control import prbEntityProperty
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.shared.prime_time_constants import PrimeTimeStatus
from gui.server_events.events_dispatcher import showMissionsMarathon
from helpers import dependency, time_utils
from skeletons.gui.game_control import IBobController, IBobAnnouncementController

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

    @process
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

    def _getSettings(self):
        return AccountSettings.getSettings(BOB_BANNERS_VIEWED).get(self.type, {})

    def _saveSettings(self, settings):
        accSettings = dict()
        accSettings[self.type] = settings
        AccountSettings.setSettings(BOB_BANNERS_VIEWED, accSettings)


class RegistrationBeforeEventStartAnnouncement(Announcement):

    @property
    def type(self):
        return AnnouncementType.REGISTRATION_BEFORE_EVENT_START

    def couldBeShown(self):
        return super(RegistrationBeforeEventStartAnnouncement, self).couldBeShown() and self._bobController.isRegistrationEnabled() and not self._bobController.isRegistered() and self._bobController.getCurrentSeason() is None

    def onClick(self):
        self._openEventWeb()

    def getEntryPointData(self):
        return EntryPointData(header=backport.text(R.strings.bob.entryPoint.title()), body=backport.text(R.strings.bob.entryPoint.registration.beforeStart.body()), footer=_getRegistrationDueDateStr(), state=BobEntryPointViewModel.REGISTRATION_BEFORE_EVENT_START, deltaFunc=_getTimeTillStartEvent)


class RegistrationAfterEventStartAnnouncement(Announcement):

    @property
    def type(self):
        return AnnouncementType.REGISTRATION_AFTER_EVENT_START

    def couldBeShown(self):
        return super(RegistrationAfterEventStartAnnouncement, self).couldBeShown() and self._bobController.isRegistrationEnabled() and not self._bobController.isRegistered() and self._bobController.isModeActive()

    def onClick(self):
        self._openEventWeb()

    def getEntryPointData(self):
        return EntryPointData(header='', body=backport.text(R.strings.bob.entryPoint.registration.afterStart.body()), footer=backport.text(R.strings.bob.entryPoint.registration.afterStart.footer()), state=BobEntryPointViewModel.REGISTRATION_AFTER_EVENT_START)


class RegistrationLastTimeAnnouncement(Announcement):

    @property
    def type(self):
        return AnnouncementType.REGISTRATION_LAST_TIME

    def couldBeShown(self):
        isLastTime = 0 < _getTimeTillRegistrationEnd() < time_utils.ONE_DAY
        return super(RegistrationLastTimeAnnouncement, self).couldBeShown() and self._bobController.isRegistrationEnabled() and not self._bobController.isRegistered() and self._bobController.isModeActive() and isLastTime

    def onClick(self):
        self._openEventWeb()

    def getEntryPointData(self):
        return EntryPointData(header=backport.text(R.strings.bob.entryPoint.title()), body=backport.text(R.strings.bob.entryPoint.registration.lastTime.body()), footer=_getTimeDescription(_getTimeTillRegistrationEnd()), state=BobEntryPointViewModel.REGISTRATION_LAST_TIME, deltaFunc=_getTimeTillRegistrationEnd)


class WaitingEventStartAnnouncement(Announcement):

    @property
    def type(self):
        return AnnouncementType.WAITING_EVENT_START

    def couldBeShown(self):
        return super(WaitingEventStartAnnouncement, self).couldBeShown() and self._bobController.isRegistered() and self._bobController.getCurrentSeason() is None and not self._bobController.isPostEventTime()

    def onClick(self):
        self._openEventWeb()

    def getEntryPointData(self):
        return EntryPointData(header=backport.text(R.strings.bob.entryPoint.title()), body=backport.text(R.strings.bob.entryPoint.waiting.body()), footer=_getTimeDescription(_getTimeTillStartEvent()), state=BobEntryPointViewModel.WAITING_EVENT_START, deltaFunc=_getTimeTillStartEvent)


class WaitingEventFinishAnnouncement(Announcement):

    @property
    def type(self):
        return AnnouncementType.WAITING_EVENT_FINISH

    def couldBeShown(self):
        return super(WaitingEventFinishAnnouncement, self).couldBeShown() and not self._bobController.isRegistrationEnabled() and not self._bobController.isRegistered() and self._bobController.isModeActive()

    def onClick(self):
        self._openEventWeb()

    def getEntryPointData(self):
        return EntryPointData(header='', body=backport.text(R.strings.bob.entryPoint.title()), footer=_getEventDueDateStr(), state=BobEntryPointViewModel.WAITING_EVENT_FINISH)


class AvailablePrimeTimeAnnouncement(Announcement):

    @property
    def type(self):
        return AnnouncementType.AVAILABLE_PRIME_TIME

    def couldBeShown(self):
        return super(AvailablePrimeTimeAnnouncement, self).couldBeShown() and self._bobController.isModeActive() and self._bobController.getPrimeTimeStatus()[0] == PrimeTimeStatus.AVAILABLE

    def onClick(self):
        self._selectEventMode()

    def getEntryPointData(self):
        return EntryPointData(header=backport.text(R.strings.bob.entryPoint.title()), body=backport.text(R.strings.bob.entryPoint.availablePrimeTime.body()), footer=_getEventDueDateStr(), state=BobEntryPointViewModel.AVAILABLE_PRIME_TIME)


class NotAvailablePrimeTimeAnnouncement(Announcement):

    @property
    def type(self):
        return AnnouncementType.NOT_AVAILABLE_PRIME_TIME

    def couldBeShown(self):
        return super(NotAvailablePrimeTimeAnnouncement, self).couldBeShown() and self._bobController.isModeActive() and self._bobController.getPrimeTimeStatus()[0] == PrimeTimeStatus.NOT_AVAILABLE

    def onClick(self):
        self._selectEventMode()

    def getEntryPointData(self):
        return EntryPointData(header='', body=backport.text(R.strings.bob.entryPoint.notAvailablePrimeTime.body()), footer=_getTimeDescription(_getTimeTillUpdatePrimeTime()), state=BobEntryPointViewModel.NOT_AVAILABLE_PRIME_TIME, deltaFunc=_getTimeTillUpdatePrimeTime)


class LastAvailablePrimeTimeAnnouncement(Announcement):

    @property
    def type(self):
        return AnnouncementType.LAST_AVAILABLE_PRIME_TIME

    def couldBeShown(self):
        isLastTime = False
        season = self._bobController.getCurrentSeason() or self._bobController.getNextSeason()
        if season is not None:
            timeTillEventEnd = season.getEndDate() - time_utils.getServerUTCTime()
            isLastTime = 0 < timeTillEventEnd < time_utils.ONE_DAY
        return super(LastAvailablePrimeTimeAnnouncement, self).couldBeShown() and self._bobController.isModeActive() and self._bobController.getPrimeTimeStatus()[0] == PrimeTimeStatus.AVAILABLE and isLastTime

    def onClick(self):
        self._selectEventMode()

    def getEntryPointData(self):
        return EntryPointData(header='', body=backport.text(R.strings.bob.entryPoint.lastAvailablePrimeTime.body()), footer=_getTimeDescription(_getTimeTillUpdatePrimeTime()), state=BobEntryPointViewModel.LAST_AVAILABLE_PRIME_TIME, deltaFunc=_getTimeTillUpdatePrimeTime)


class AddTeamExtraPointsAnnouncement(Announcement):

    @property
    def type(self):
        return AnnouncementType.ADD_TEAM_EXTRA_POINTS

    def couldBeShown(self):
        nextRecalculation = self._bobController.teamsRequester.getNextRecalculation()
        if nextRecalculation is None:
            return False
        else:
            lastUpdateTeamPointsTime = nextRecalculation.next_recalculation_timestamp
            lastViewedTime = self._getSettings().get('lastViewedTime', 0)
            return super(AddTeamExtraPointsAnnouncement, self).couldBeShown() and self._bobController.isRegistered() and lastViewedTime < lastUpdateTeamPointsTime < time_utils.getServerUTCTime()

    def onClick(self):
        self._openEventWeb()
        self._saveSettings({'lastViewedTime': time_utils.getServerUTCTime()})

    def getEntryPointData(self):
        return EntryPointData(header='', body=backport.text(R.strings.bob.entryPoint.addTeamExtraPoints.body()), footer=backport.text(R.strings.bob.entryPoint.addTeamExtraPoints.footer()), state=BobEntryPointViewModel.ADD_TEAM_EXTRA_POINTS)


class TeamRewardAnnouncement(Announcement):

    @property
    def type(self):
        return AnnouncementType.TEAM_REWARD

    def couldBeShown(self):
        lastViewedTeamReward = self._getSettings().get('lastViewedTeamReward', 0)
        teamLevelTokenCount = self._bobController.getTeamLevelTokensCount()
        return super(TeamRewardAnnouncement, self).couldBeShown() and self._bobController.isRegistered() and lastViewedTeamReward < teamLevelTokenCount and self._bobController.getReceivedTeamRewards() < teamLevelTokenCount

    def onClick(self):
        self._openEventWeb()
        self._saveSettings({'lastViewedTeamReward': self._bobController.getTeamLevelTokensCount()})

    def getEntryPointData(self):
        return EntryPointData(header='', body=backport.text(R.strings.bob.entryPoint.teamReward.body()), footer=backport.text(R.strings.bob.entryPoint.teamReward.footer()), state=BobEntryPointViewModel.TEAM_REWARD)


class EventFinishAnnouncement(Announcement):

    @property
    def type(self):
        return AnnouncementType.EVENT_FINISH

    def couldBeShown(self):
        return super(EventFinishAnnouncement, self).couldBeShown() and self._bobController.isPostEventTime()

    def onClick(self):
        self._openEventWeb()

    def getEntryPointData(self):
        return EntryPointData(header='', body=backport.text(R.strings.bob.entryPoint.eventFinish.body()), footer=backport.text(R.strings.bob.entryPoint.eventFinish.footer()), state=BobEntryPointViewModel.EVENT_FINISH)


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


def _getTillDateText(dateTime):
    return backport.text(R.strings.bob.entryPoint.tillDate.description(), day=dateTime.tm_mday, month=backport.text(R.strings.menu.dateTime.months.num(dateTime.tm_mon)()))


def _getTimeDescription(timeValue):
    return backport.backport_time_utils.getTillTimeStringByRClass(timeValue=timeValue, stringRClass=R.strings.bob.entryPoint.timeLeft, removeLeadingZeros=True)


@dependency.replace_none_kwargs(bobAnnouncement=IBobAnnouncementController)
def getBobEntryPointIsActive(bobAnnouncement=None):
    return bobAnnouncement.currentAnnouncement is not None
