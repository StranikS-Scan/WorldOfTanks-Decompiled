# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/game_control/ny_tutorial_controller.py
from adisp import adisp_process
from new_year.gui.impl.new_year.sounds import VideoStartStopHandler, Videos
from new_year.helpers.ny_helpers import showWebmVideoView
from new_year_account_settings import getNYSetting, setNYSettings
from new_year.ny_constants import NY_GREETINGS_SEEN
from Event import EventManager, Event
from gui.impl.gen import R
from new_year.helpers.server_settings import getNewYearGeneralConfig
from gui.shared.event_dispatcher import getParentWindow
from helpers import dependency
from helpers.time_utils import getCurrentTimestamp, getDateTimeInLocal, getDateTimeInUTC
from helpers.events_handler import EventsHandler
from new_year.ny_constants import NY_TUTORIAL_NOTIFICATION_LOCK_KEY
from skeletons.gui.game_control import IOverlayController
from skeletons.gui.shared.utils import IHangarSpace
from new_year.skeletons.new_year import INewYearController, INewYearTutorialController
from gui.shared.lock_overlays import lockNotificationManager
from gui.Scaleform.managers.fade_manager import FadeManager
from gui.shared.utils import isPopupsWindowsOpenDisabled

def lockNotifications():
    lockNotificationManager(lock=True, postponeActive=True, source=NY_TUTORIAL_NOTIFICATION_LOCK_KEY)


def unlockNotifications():
    lockNotificationManager(lock=False, releasePostponed=True, source=NY_TUTORIAL_NOTIFICATION_LOCK_KEY)


class NewYearTutorialController(INewYearTutorialController, EventsHandler):
    __slots__ = ('__fadeManager', '__videoStartStopHandler', '__isIntroActive', '__em')
    _hangarSpace = dependency.descriptor(IHangarSpace)
    _nyController = dependency.descriptor(INewYearController)
    _overlay = dependency.descriptor(IOverlayController)

    def __init__(self):
        super(NewYearTutorialController, self).__init__()
        self.__fadeManager = FadeManager()
        self.__videoStartStopHandler = None
        self.__isIntroActive = False
        self.__em = EventManager()
        self.onIntroComplete = Event(self.__em)
        return

    def fini(self):
        self.__em.clear()
        super(NewYearTutorialController, self).fini()

    def onConnected(self):
        super(NewYearTutorialController, self).onConnected()
        self.__activateAction()

    def onDisconnected(self):
        super(NewYearTutorialController, self).onDisconnected()
        self.__deactivateAction()

    def onAvatarBecomePlayer(self):
        self.__deactivateAction()

    def onAccountBecomePlayer(self):
        self.__activateAction()

    @property
    def isActive(self):
        return self.__isIntroActive

    @classmethod
    def __setActive(cls, value):
        cls.__isIntroActive = value

    def shouldStartIntro(self):
        return False if isPopupsWindowsOpenDisabled() else self.__shouldPlayNewYearGreeting()

    def __activateAction(self):
        if not self.__isNYGreetingsViewed():
            self._subscribe()
            self.__fadeManager.setup()

    def __deactivateAction(self):
        self.__clear()
        self.__fadeManager.destroy()

    def __shouldPlayNewYearGreeting(self):
        localTime = getDateTimeInLocal(getCurrentTimestamp())
        newYearGreetingsDateTime = getDateTimeInUTC(getNewYearGeneralConfig().getNewYearGreetingsDate())
        return self._nyController.isEnabled() and not self.__isNYGreetingsViewed() and getNewYearGeneralConfig().getNewYearGreetingsVideoVisible() and localTime >= newYearGreetingsDateTime

    def tryStartIntro(self):
        if isPopupsWindowsOpenDisabled() or self.isActive:
            return
        if self.__isNYGreetingsViewed():
            self._unsubscribe()
            return
        if not self.__shouldPlayNewYearGreeting():
            return
        self.__setActive(True)
        lockNotifications()
        self._overlay.setOverlayState(True)
        self.__showNYGreetingsVideo()

    def _getEvents(self):
        return ((self._hangarSpace.onSpaceCreate, self.__onHangarSpaceCreated),)

    def _unsubscribe(self):
        super(NewYearTutorialController, self)._unsubscribe()
        self._nyController.onStateChanged -= self.tryStartIntro
        self._nyController.onNySettingsChanged -= self.tryStartIntro

    def __onHangarSpaceCreated(self):
        self.tryStartIntro()
        if not self.__isNYGreetingsViewed():
            self._nyController.onStateChanged += self.tryStartIntro
            self._nyController.onNySettingsChanged += self.tryStartIntro

    def __isNYGreetingsViewed(self):
        return getNYSetting(NY_GREETINGS_SEEN)

    def __setINYGreetingsViewed(self):
        setNYSettings(NY_GREETINGS_SEEN, True)

    def __showNYGreetingsVideo(self):
        self.__videoStartStopHandler = VideoStartStopHandler(checkPauseOnStart=False)
        showWebmVideoView(videoSource=R.videos.new_year.greetings.ng_greetings(), parent=getParentWindow(), onVideoStarted=self.__onCelebSpeechVideoStarted, onVideoClosed=self.__onCelebSpeechVideoDone, isAutoClose=True, canEscape=False, isUIVisible=True, uiShowDelay=1)

    @adisp_process
    def __onCelebSpeechVideoStarted(self):
        self.__setINYGreetingsViewed()
        self.__videoStartStopHandler.onVideoStart(Videos.CELEB_SPEECH)
        yield self.__fadeManager.startFade()

    @adisp_process
    def __onCelebSpeechVideoDone(self):
        self.__videoStartStopHandler.onVideoDone()
        self.__videoStartStopHandler = None
        yield self.__fadeManager.startFade(fadeIn=False)
        self.__clear()
        self.onIntroComplete()
        return

    def __clear(self):
        self._unsubscribe()
        if self.isActive:
            unlockNotifications()
            self._overlay.setOverlayState(False)
            self.__setActive(False)
