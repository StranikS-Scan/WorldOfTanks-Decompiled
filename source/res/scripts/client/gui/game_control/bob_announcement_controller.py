# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/bob_announcement_controller.py
import logging
import Event
from constants import QUEUE_TYPE, PREBATTLE_TYPE
from gui.bob.bob_announcement_helpers import RegistrationBeforeEventStartAnnouncement, RegistrationAfterEventStartAnnouncement, RegistrationLastTimeAnnouncement, TeamRewardAnnouncement, EventFinishAnnouncement, WaitingEventFinishAnnouncement, WaitingEventStartAnnouncement, AddTeamExtraPointsAnnouncement, AvailablePrimeTimeAnnouncement, NotAvailablePrimeTimeAnnouncement, LastAvailablePrimeTimeAnnouncement
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.listener import IGlobalListener
from helpers import dependency
from skeletons.gui.game_control import IBobAnnouncementController, IBobController, IBootcampController
_logger = logging.getLogger(__name__)

class BobAnnouncementController(IBobAnnouncementController, IGlobalListener):
    __bobController = dependency.descriptor(IBobController)
    __bootcampController = dependency.descriptor(IBootcampController)

    def __init__(self):
        super(BobAnnouncementController, self).init()
        self.onAnnouncementUpdated = Event.Event()
        self.__announcements = []
        self.__currentAnnouncement = None
        return

    @property
    def currentAnnouncement(self):
        if self.__currentAnnouncement is not None and not self.__currentAnnouncement.couldBeShown():
            self.__updateAnnouncements()
        return self.__currentAnnouncement

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
        self.__stop()

    def onDisconnected(self):
        self.__stop()

    def onPrbEntitySwitched(self):
        self.__updatePrb()
        self.__updateAnnouncements()

    def __start(self):
        if self.__bootcampController.isInBootcamp():
            return
        self.__announcements = [RegistrationBeforeEventStartAnnouncement(),
         RegistrationAfterEventStartAnnouncement(),
         RegistrationLastTimeAnnouncement(),
         WaitingEventStartAnnouncement(),
         WaitingEventFinishAnnouncement(),
         AvailablePrimeTimeAnnouncement(),
         NotAvailablePrimeTimeAnnouncement(),
         LastAvailablePrimeTimeAnnouncement(),
         AddTeamExtraPointsAnnouncement(),
         TeamRewardAnnouncement(),
         EventFinishAnnouncement()]
        self.__bobController.onUpdated += self.__updateAnnouncements
        self.__bobController.onPrimeTimeStatusUpdated += self.__updateAnnouncements
        self.__bobController.onTokensUpdated += self.__updateAnnouncements
        self.startGlobalListening()
        self.__updatePrb()
        self.__updateAnnouncements()

    def __stop(self):
        self.__bobController.onUpdated -= self.__updateAnnouncements
        self.__bobController.onPrimeTimeStatusUpdated -= self.__updateAnnouncements
        self.__bobController.onTokensUpdated -= self.__updateAnnouncements
        self.stopGlobalListening()
        self.__announcements = []
        self.__currentAnnouncement = None
        return

    def __updateAnnouncements(self, *_):
        couldShow = [ b for b in self.__announcements if b.couldBeShown() ]
        topAnnouncement = min(couldShow, key=lambda banner: banner.priority) if couldShow else None
        if topAnnouncement != self.__currentAnnouncement:
            self.__currentAnnouncement = topAnnouncement
            if self.__currentAnnouncement is not None:
                self.onAnnouncementUpdated(self.__currentAnnouncement.type)
            else:
                self.onAnnouncementUpdated(None)
        return

    def __updatePrb(self):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is None:
            return
        else:
            state = dispatcher.getFunctionalState()
            isBobPrb = state.isInPreQueue(queueType=QUEUE_TYPE.BOB) or state.isInUnit(PREBATTLE_TYPE.BOB)
            for announcement in self.__announcements:
                announcement.updatePrb(isBobPrb)

            return
