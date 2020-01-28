# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/bob_announcement_controller.py
import logging
import BigWorld
import Event
from adisp import process
from skeletons.gui.game_control import IBobAnnouncementController, IBobController, IBootcampController
from helpers import dependency, time_utils
from skeletons.gui.shared import IItemsCache
from helpers.time_utils import ONE_DAY
from account_helpers.AccountSettings import AccountSettings, BOB_BANNER_COUNTER
from gui.ranked_battles.constants import PrimeTimeStatus
from constants import ARENA_BONUS_TYPE, QUEUE_TYPE, PREBATTLE_TYPE
from gui.shared import event_dispatcher
from shared_utils import first
from gui.game_control.bob_announcement_helpers import AnnouncementType, ANNOUNCEMENT_PRIORITY
from gui.marathon.bob_event import BobEvent
from gui.server_events.events_dispatcher import showMissionsMarathon
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.prb_control import prbEntityProperty
from gui.prb_control.entities.listener import IGlobalListener
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_data_provider import CarouselDataProvider
_logger = logging.getLogger(__name__)

class BobAnnouncementController(IBobAnnouncementController, IGlobalListener):
    __itemsCache = dependency.descriptor(IItemsCache)
    __bobController = dependency.descriptor(IBobController)
    __bootcampController = dependency.descriptor(IBootcampController)

    def __init__(self):
        super(BobAnnouncementController, self).init()
        self.onAnnouncementUpdated = Event.Event()
        self.__announcementsData = []
        self.__currentAnnouncement = None
        return

    @property
    def currentAnnouncement(self):
        return self.__currentAnnouncement.announcementType if self.__currentAnnouncement is not None else None

    def clickAnnouncement(self):
        if self.__currentAnnouncement is not None:
            self.__currentAnnouncement.onClick()
        else:
            _logger.warning('No announcement to click!')
        self.__updateAnnouncements()
        return

    def onLobbyInited(self, event):
        self.__start()

    def onAvatarBecomePlayer(self):
        if self.__bootcampController.isInBootcamp():
            _logger.debug('Skip Announcement logic because Bootcamp')
        else:
            for announcement in self.__announcementsData:
                announcement.onAvatarBecomePlayer()

            self.__saveSettings()
        self.__stop()

    def onDisconnected(self):
        self.__stop()

    def onPrbEntitySwitched(self):
        self.__updatePrb()
        self.__updateAnnouncements()

    def __start(self):
        if self.__bootcampController.isInBootcamp():
            _logger.debug('Skip Announcement initialization because Bootcamp')
            return
        settings = AccountSettings.getCounters(BOB_BANNER_COUNTER)
        self.__announcementsData = [_RegistrationAnnouncement(AnnouncementType.REGISTRATION, settings.get(AnnouncementType.REGISTRATION, {})), _EventFinishAnnouncement(AnnouncementType.EVENT_FINISH, settings.get(AnnouncementType.EVENT_FINISH, {}))]
        if self.__bobController.isRuEuRealm():
            self.__announcementsData.extend([_EventStartRuEuAnnouncement(AnnouncementType.EVENT_START, settings.get(AnnouncementType.EVENT_START, {})), _PrimeTimeAnnouncement(AnnouncementType.PRIME_TIME, settings.get(AnnouncementType.PRIME_TIME, {})), _SkillActiveAnnouncement(AnnouncementType.SKILL_ACTIVE, settings.get(AnnouncementType.SKILL_ACTIVE, {}))])
        elif self.__bobController.isNaAsiaRealm():
            self.__announcementsData.append(_EventStartNaAsiaAnnouncement(AnnouncementType.EVENT_START, settings.get(AnnouncementType.EVENT_START, {})))
        self.__itemsCache.onSyncCompleted += self.__updateAnnouncements
        self.__bobController.onUpdated += self.__updateAnnouncements
        self.__bobController.onPrimeTimeStatusUpdated += self.__updateAnnouncements
        self.__bobController.onSkillActivated += self.__updateAnnouncements
        self.startGlobalListening()
        self.__updatePrb()
        self.__updateAnnouncements()

    def __stop(self):
        self.__bobController.onUpdated -= self.__updateAnnouncements
        self.__bobController.onPrimeTimeStatusUpdated -= self.__updateAnnouncements
        self.__bobController.onSkillActivated -= self.__updateAnnouncements
        self.__itemsCache.onSyncCompleted -= self.__updateAnnouncements
        self.stopGlobalListening()
        self.__announcementsData = []
        self.__currentAnnouncement = None
        return

    def __saveSettings(self):
        accSettings = {}
        for announcement in self.__announcementsData:
            accSettings[announcement.announcementType] = announcement.getSettings()

        AccountSettings.setCounters(BOB_BANNER_COUNTER, accSettings)

    def __updateAnnouncements(self, *_):
        couldShow = [ b for b in self.__announcementsData if b.couldBeShown() ]
        topAnnouncement = min(couldShow, key=lambda banner: banner.priority) if couldShow else None
        if topAnnouncement != self.__currentAnnouncement:
            if self.__currentAnnouncement is not None:
                self.__currentAnnouncement.onHide()
            self.__currentAnnouncement = topAnnouncement
            if self.__currentAnnouncement is not None:
                self.onAnnouncementUpdated(self.__currentAnnouncement.announcementType)
                self.__currentAnnouncement.onShow()
            else:
                self.onAnnouncementUpdated(None)
            self.__saveSettings()
        return

    def __updatePrb(self):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is None:
            return
        else:
            state = dispatcher.getFunctionalState()
            isBobPrb = state.isInPreQueue(queueType=QUEUE_TYPE.BOB) or state.isInUnit(PREBATTLE_TYPE.BOB)
            for announcement in self.__announcementsData:
                announcement.updatePrb(isBobPrb)

            return


class _Announcement(object):
    _bobController = dependency.descriptor(IBobController)

    def __init__(self, announcementType):
        super(_Announcement, self).__init__()
        self.__announcementType = announcementType
        self.__isShown = False
        self.__isBobPrb = False
        self.__isClicked = False

    @property
    def priority(self):
        return ANNOUNCEMENT_PRIORITY[self.__announcementType]

    @property
    def announcementType(self):
        return self.__announcementType

    @property
    def isShown(self):
        return self.__isShown

    @prbEntityProperty
    def prbEntity(self):
        return None

    def getSettings(self):
        return {}

    def onAvatarBecomePlayer(self):
        pass

    def onShow(self):
        self.__isShown = True

    def onHide(self):
        self.__isShown = False

    def couldBeShown(self):
        return not self.__isBobPrb and not self.__isClicked

    def onClick(self):
        self.__isClicked = True

    def updatePrb(self, isBobPrb):
        self.__isBobPrb = isBobPrb

    @process
    def _selectEventMode(self):
        isPrbInited = g_prbLoader is not None and self.prbEntity is not None
        if isPrbInited:
            dispatcher = g_prbLoader.getDispatcher()
            state = dispatcher.getFunctionalState()
            if not state.isInPreQueue(queueType=QUEUE_TYPE.BOB):
                yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.BOB))
        return

    def _openEventWeb(self):
        showMissionsMarathon(marathonPrefix=BobEvent.BOB_EVENT_PREFIX)


class _EventLimitedAnnouncement(_Announcement):
    _SHOW_TOTAL = 0

    def __init__(self, announcementType, settings):
        super(_EventLimitedAnnouncement, self).__init__(announcementType)
        self.__shownPerEvent = settings.get('shownPerEvent', 0)

    def getSettings(self):
        return {'shownPerEvent': self.__shownPerEvent}

    def couldBeShown(self):
        return self.isShown or self.__shownPerEvent < self._SHOW_TOTAL if super(_EventLimitedAnnouncement, self).couldBeShown() else False

    def onShow(self):
        super(_EventLimitedAnnouncement, self).onShow()
        self.__shownPerEvent += 1


class _DayLimitedAnnouncement(_Announcement):

    def __init__(self, announcementType, settings):
        super(_DayLimitedAnnouncement, self).__init__(announcementType)
        self.__lastShownTime = settings.get('lastShownTime')

    def getSettings(self):
        return {'lastShownTime': self.__lastShownTime}

    def couldBeShown(self):
        return self.isShown or self.__lastShownTime is None or ONE_DAY < time_utils.getServerUTCTime() - self.__lastShownTime if super(_DayLimitedAnnouncement, self).couldBeShown() else False

    def onShow(self):
        super(_DayLimitedAnnouncement, self).onShow()
        self.__lastShownTime = time_utils.getServerUTCTime()


class _RegistrationAnnouncement(_EventLimitedAnnouncement):
    _SHOW_TOTAL = 3

    def couldBeShown(self):
        return super(_RegistrationAnnouncement, self).couldBeShown() and self._bobController.isRegistrationEnabled() and not self._bobController.isRegistered()

    def onClick(self):
        super(_RegistrationAnnouncement, self).onClick()
        self._openEventWeb()


class _EventStartRuEuAnnouncement(_EventLimitedAnnouncement):
    _SHOW_TOTAL = 3

    def __init__(self, announcementType, settings):
        super(_EventStartRuEuAnnouncement, self).__init__(announcementType, settings)
        self.__playerHasBobBattles = settings.get('playerHasBobBattles', False)

    def onAvatarBecomePlayer(self):
        if not self.__playerHasBobBattles and BigWorld.player().arenaBonusType == ARENA_BONUS_TYPE.BOB:
            self.__playerHasBobBattles = True

    def couldBeShown(self):
        return super(_EventStartRuEuAnnouncement, self).couldBeShown() and not self.__playerHasBobBattles and self._bobController.isModeActive()

    def getSettings(self):
        settings = super(_EventStartRuEuAnnouncement, self).getSettings()
        settings['playerHasBobBattles'] = self.__playerHasBobBattles
        return settings

    def onClick(self):
        super(_EventStartRuEuAnnouncement, self).onClick()
        self._selectEventMode()


class _EventStartNaAsiaAnnouncement(_EventLimitedAnnouncement):
    _SHOW_TOTAL = 3

    def couldBeShown(self):
        return super(_EventStartNaAsiaAnnouncement, self).couldBeShown() and self._bobController.getPlayerPoints() == 0 and self._bobController.isModeActive()

    def onClick(self):
        super(_EventStartNaAsiaAnnouncement, self).onClick()
        vehicles = self._bobController.getSuitableVehicles().values()
        vehicles.sort(key=CarouselDataProvider._vehicleComparisonKey)
        if vehicles:
            event_dispatcher.selectVehicleInHangar(first(vehicles).intCD)
        else:
            _logger.warning('No 10-Level vehicle to select!')


class _EventFinishAnnouncement(_EventLimitedAnnouncement):
    _SHOW_TOTAL = 1

    def couldBeShown(self):
        return super(_EventFinishAnnouncement, self).couldBeShown() and self._bobController.isRegistered() and self._bobController.isPostEventTime()

    def onClick(self):
        super(_EventFinishAnnouncement, self).onClick()
        self._openEventWeb()


class _PrimeTimeAnnouncement(_DayLimitedAnnouncement):

    def couldBeShown(self):
        return super(_PrimeTimeAnnouncement, self).couldBeShown() and self._bobController.isModeActive() and self._bobController.getPrimeTimeStatus()[0] == PrimeTimeStatus.AVAILABLE

    def onClick(self):
        super(_PrimeTimeAnnouncement, self).onClick()
        self._selectEventMode()


class _SkillActiveAnnouncement(_Announcement):

    def __init__(self, announcementType, settings):
        super(_SkillActiveAnnouncement, self).__init__(announcementType)
        self.__lastShownSkills = settings.copy()
        self.__shownSkill = None
        return

    def getSettings(self):
        return self.__lastShownSkills.copy()

    def couldBeShown(self):
        if super(_SkillActiveAnnouncement, self).couldBeShown():
            if self._bobController.isModeActive():
                activeSkill = self._bobController.getActiveSkill()
                if activeSkill:
                    if self.isShown and activeSkill == self.__shownSkill:
                        return True
                    lastShownTime = self.__lastShownSkills.get(activeSkill)
                    if lastShownTime is None:
                        return True
                    return ONE_DAY < time_utils.getServerUTCTime() - lastShownTime
        return False

    def onShow(self):
        super(_SkillActiveAnnouncement, self).onShow()
        self.__shownSkill = self._bobController.getActiveSkill()
        self.__lastShownSkills[self.__shownSkill] = time_utils.getServerUTCTime()

    def onHide(self):
        super(_SkillActiveAnnouncement, self).onHide()
        self.__shownSkill = None
        return

    def onClick(self):
        super(_SkillActiveAnnouncement, self).onClick()
        self._selectEventMode()
