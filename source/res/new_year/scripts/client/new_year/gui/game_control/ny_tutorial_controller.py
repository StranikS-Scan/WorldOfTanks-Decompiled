# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/game_control/ny_tutorial_controller.py
import logging
import ScaleformFileLoader
from adisp import adisp_process
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NY_INTRO_SEEN, NY_GREETINGS_SEEN
from Event import EventManager, Event
from gui.impl.gen import R
from gui.impl.lobby.loot_box.loot_box_sounds import PausedSoundManager, LootBoxVideos, LootBoxVideoStartStopHandler
from new_year.helpers.server_settings import getNewYearGeneralConfig
from gui.shared.event_dispatcher import showVideoView
from helpers import dependency, time_utils
from helpers.events_handler import EventsHandler
from messenger.proto.events import g_messengerEvents
from new_year.ny_constants import NY_TUTORIAL_NOTIFICATION_LOCK_KEY
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IOverlayController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared.utils import IHangarSpace
from new_year.skeletons.new_year import INewYearController, INewYearTutorialController
from gui.shared.lock_overlays import lockNotificationManager
from gui.Scaleform.managers.fade_manager import FadeManager
from gui.shared.utils import isPopupsWindowsOpenDisabled
_logger = logging.getLogger(__name__)
_FADE_IN_DURATION = 0
_FADE_OUT_DURATION = 1
_NY_VIDEOS = ['gui/flash/videos/new_year/ng_startup.usm', 'gui/flash/videos/new_year/ng_post.usm']

def lockNotifications():
    lockNotificationManager(lock=True, postponeActive=True, source=NY_TUTORIAL_NOTIFICATION_LOCK_KEY)


def unlockNotifications():
    lockNotificationManager(lock=False, releasePostponed=True, source=NY_TUTORIAL_NOTIFICATION_LOCK_KEY)


class NewYearTutorialController(INewYearTutorialController, EventsHandler):
    __slots__ = ('__fadeManager', '__videoStartStopHandler', '__isIntroActive')
    _hangarSpace = dependency.descriptor(IHangarSpace)
    _settingsCore = dependency.descriptor(ISettingsCore)
    _nyController = dependency.descriptor(INewYearController)
    _overlay = dependency.descriptor(IOverlayController)
    _gui = dependency.descriptor(IGuiLoader)
    _eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        super(NewYearTutorialController, self).__init__()
        self.__fadeManager = FadeManager()
        self.__videoStartStopHandler = LootBoxVideoStartStopHandler(checkPauseOnStart=False)
        self.__isStreamingEnabled = False
        self.__isIntroActive = False
        self.__em = EventManager()
        self.onIntroComplete = Event(self.__em)

    def fini(self):
        self.__em.clear()
        super(NewYearTutorialController, self).fini()

    def onConnected(self):
        super(NewYearTutorialController, self).onConnected()
        self._subscribe()
        self.__fadeManager.setup()

    def onDisconnected(self):
        super(NewYearTutorialController, self).onDisconnected()
        self.__clear()
        self.__fadeManager.destroy()

    def onAvatarBecomePlayer(self):
        self.__clear()
        self.__fadeManager.destroy()

    def onAccountBecomePlayer(self):
        if not self.__isIntroSceneViewed():
            self._subscribe()
            self.__fadeManager.setup()

    @property
    def isActive(self):
        return self.__isIntroActive

    @classmethod
    def __setActive(cls, value):
        cls.__isIntroActive = value

    def shouldStartIntro(self):
        return False if isPopupsWindowsOpenDisabled() else self.__shouldPlayFirstHangarVideo() or self.__shouldPlayNewYearGreeting()

    def __shouldPlayFirstHangarVideo(self):
        return self._nyController.isEnabled() and not self.__isIntroSceneViewed()

    def __shouldPlayNewYearGreeting(self):
        return self._nyController.isEnabled() and not self.__isNYGreetingsViewed() and time_utils.getServerUTCTime() >= getNewYearGeneralConfig().getNewYearGreetingsDate()

    def tryStartIntro(self):
        if isPopupsWindowsOpenDisabled():
            return False
        if self.isActive:
            return
        if self.__isNYGreetingsViewed():
            self._unsubscribe()
            return
        self.__setActive(self.__showNextHangarVideo())
        if self.isActive:
            lockNotifications()
            self.__enableVideoStreaming()
            self._overlay.setOverlayState(True)

    def __showNextHangarVideo(self):
        if self.__shouldPlayFirstHangarVideo():
            self.__showNYFirstVideo()
            return True
        if self.__shouldPlayNewYearGreeting():
            self.__showNYGreetingsVideo()
            return True
        return False

    def _getEvents(self):
        return ((self._hangarSpace.onSpaceCreate, self.__onHangarSpaceCreated), (g_messengerEvents.onNotificationPopUpViewerStarted, self.__onStartListening))

    def _unsubscribe(self):
        super(NewYearTutorialController, self)._unsubscribe()
        self._nyController.onStateChanged -= self.tryStartIntro

    def __onHangarSpaceCreated(self):
        self.tryStartIntro()
        if not self.__isIntroSceneViewed():
            self._nyController.onStateChanged += self.tryStartIntro

    def __isIntroSceneViewed(self):
        return AccountSettings.getNewYear(NY_INTRO_SEEN)

    def __setIntroSceneViewed(self):
        AccountSettings.setNewYear(NY_INTRO_SEEN, True)

    def __isNYGreetingsViewed(self):
        return AccountSettings.getNewYear(NY_GREETINGS_SEEN)

    def __setINYGreetingsViewed(self):
        AccountSettings.setNewYear(NY_GREETINGS_SEEN, True)

    def __onStartListening(self):
        g_messengerEvents.onLockPopUpMessages(lockHigh=True)

    def __enableVideoStreaming(self):
        if not self.__isStreamingEnabled:
            self.__isStreamingEnabled = True
            ScaleformFileLoader.enableStreaming(_NY_VIDEOS)

    def __disableVideoStreaming(self):
        if self.__isStreamingEnabled:
            ScaleformFileLoader.disableStreaming()
            self.__isStreamingEnabled = False

    def __showNYFirstVideo(self):
        self.__setIntroSceneViewed()
        self.__showHangarVideo(R.videos.new_year.ng_startup())

    def __showNYGreetingsVideo(self):
        self.__setINYGreetingsViewed()
        self.__showHangarVideo(R.videos.new_year.ng_greetings())

    def __showHangarVideo(self, videoResID):
        showVideoView(videoResID, onVideoStarted=self.__onHangarVideoStarted, onVideoClosed=self.__onHangarVideoDone, isAutoClose=True, soundControl=PausedSoundManager(), canEscape=False, isUIVisible=True, uiShowDelay=1)

    @adisp_process
    def __onHangarVideoStarted(self):
        self.__videoStartStopHandler.onVideoStart(LootBoxVideos.START)
        yield self.__fadeManager.startFade()

    @adisp_process
    def __onHangarVideoDone(self):
        self.__videoStartStopHandler.onVideoDone()
        if not self.__showNextHangarVideo():
            yield self.__fadeManager.startFade(fadeIn=False)
            self.__clear()
            self.onIntroComplete()

    def __clear(self):
        self._unsubscribe()
        if self.isActive:
            self.__disableVideoStreaming()
            unlockNotifications()
            g_messengerEvents.onUnlockPopUpMessages()
            self._overlay.setOverlayState(False)
            self.__setActive(False)
