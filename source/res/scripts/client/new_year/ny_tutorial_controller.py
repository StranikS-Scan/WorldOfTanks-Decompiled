# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_tutorial_controller.py
import logging
from CurrentVehicle import g_currentVehicle
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NY_INTRO_SEEN
from chat_shared import SYS_MESSAGE_TYPE
from Event import EventManager, Event
from frameworks.wulf import WindowLayer
from gui.impl.common.fade_manager import FadeManager, DefaultFadingCover
from gui.impl.gen import R
import ScaleformFileLoader
from gui.impl.lobby.loot_box.loot_box_sounds import PausedSoundManager, LootBoxVideos, LootBoxVideoStartStopHandler
from gui.impl.new_year.navigation import NewYearNavigation
from gui.server_events.bonuses import getAllNonQuestBonuses
from gui.shared.event_dispatcher import showVideoView, showNYLevelUpWindow
from helpers import dependency
from helpers.events_handler import EventsHandler
from messenger.proto.events import g_messengerEvents
from new_year.ny_constants import NY_TUTORIAL_NOTIFICATION_LOCK_KEY
from new_year.ny_level_helper import parseNYLevelToken
from shared_utils import first, findFirst
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IOverlayController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.new_year import INewYearController, INewYearTutorialController
from gui.shared.lock_overlays import lockNotificationManager
from wg_async import wg_async, wg_await
_logger = logging.getLogger(__name__)
_FIRST_LEVEL = 1
_FADE_IN_DURATION = 0
_FADE_OUT_DURATION = 1

def lockNotifications():
    lockNotificationManager(lock=True, postponeActive=True, source=NY_TUTORIAL_NOTIFICATION_LOCK_KEY)


def unlockNotifications():
    lockNotificationManager(lock=False, releasePostponed=True, source=NY_TUTORIAL_NOTIFICATION_LOCK_KEY)


class NYFadingCover(DefaultFadingCover):

    def __init__(self):
        super(NYFadingCover, self).__init__(fadeInDuration=_FADE_IN_DURATION, fadeOutDuration=_FADE_OUT_DURATION)


class NewYearTutorialController(INewYearTutorialController, EventsHandler):
    __slots__ = ('__levelRewards', '__isActive', '__fadeManager', '__videoStartStopHandler')
    _hangarSpace = dependency.descriptor(IHangarSpace)
    _settingsCore = dependency.descriptor(ISettingsCore)
    _nyController = dependency.descriptor(INewYearController)
    _overlay = dependency.descriptor(IOverlayController)
    _gui = dependency.descriptor(IGuiLoader)
    _eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        super(NewYearTutorialController, self).__init__()
        self.__levelRewards = None
        self.__isActive = False
        self.__fadeManager = FadeManager(layer=WindowLayer.TOP_WINDOW, coverFactory=NYFadingCover)
        self.__videoStartStopHandler = LootBoxVideoStartStopHandler(checkPauseOnStart=False)
        self.__isStreamingEnabled = False
        self.__em = EventManager()
        self.onTutorialComplete = Event(self.__em)
        return

    def fini(self):
        self.__em.clear()
        super(NewYearTutorialController, self).fini()

    def onConnected(self):
        super(NewYearTutorialController, self).onConnected()
        self._subscribe()

    def onDisconnected(self):
        super(NewYearTutorialController, self).onDisconnected()
        self.__clear()

    def onAvatarBecomePlayer(self):
        self.__clear()

    def onAccountBecomePlayer(self):
        if not self.__isIntroSceneViewed():
            self._subscribe()

    @property
    def isActive(self):
        return self.__isActive

    def shouldStartIntro(self):
        return self._nyController.isEnabled() and not self.__isIntroSceneViewed()

    def tryStartIntro(self):
        if self.__isIntroSceneViewed():
            self._unsubscribe()
            return
        if not self._nyController.isEnabled():
            return
        self.__enableVideoStreaming()
        self.__setIntroSceneViewed()
        self.__isActive = True
        lockNotifications()
        self._overlay.setOverlayState(True)
        self.__showHangarVideo()

    def _getEvents(self):
        return ((self._hangarSpace.onSpaceCreate, self.__onHangarSpaceCreated), (g_messengerEvents.serviceChannel.onChatMessageReceived, self.__onChatMessageReceived), (g_messengerEvents.onNotificationPopUpViewerStarted, self.__onStartListening))

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

    def __onChatMessageReceived(self, *args):
        _, message = args
        if message is not None and message.type == SYS_MESSAGE_TYPE.tokenQuests.index() and message.data is not None and message.data:
            questID = first((questID for questID in message.data.get('completedQuestIDs', set()) if parseNYLevelToken(questID) == _FIRST_LEVEL))
            if not questID:
                return
            self.__levelRewards = {_FIRST_LEVEL: getAllNonQuestBonuses(message.data.get('detailedRewards', {}).get(questID, {}))}
        return

    def __onStartListening(self):
        g_messengerEvents.onLockPopUpMessages(lockHigh=True)

    def __disableVideoStreaming(self):
        if self.__isStreamingEnabled:
            ScaleformFileLoader.disableStreaming()
            self.__isStreamingEnabled = False

    def __enableVideoStreaming(self):
        if not self.__isStreamingEnabled:
            self.__isStreamingEnabled = True
            ScaleformFileLoader.enableStreaming(['gui/flash/videos/new_year/ng_startup.usm'])

    def __showHangarVideo(self):
        showVideoView(R.videos.new_year.ng_startup(), onVideoStarted=self.__onHangarVideoStarted, onVideoClosed=self.__onHangarVideoDone, isAutoClose=True, soundControl=PausedSoundManager(), canEscape=False)

    def __onHangarVideoStarted(self):
        self.__videoStartStopHandler.onVideoStart(LootBoxVideos.START)
        self.__fadeManager.show()

    def __onHangarVideoDone(self):
        self.__videoStartStopHandler.onVideoDone()
        self.__showFirstLevelUp()
        self.__disableVideoStreaming()

    @wg_async
    def __showFirstLevelUp(self):
        if not self.__levelRewards:
            _logger.error("Server doesn't sent first level up message")
            self.__showHangar()
            return
        NewYearNavigation.switchToIntro()
        yield wg_await(self.__fadeManager.hide())
        if not self.__isActive:
            _logger.warning('Account is not player')
            return
        showNYLevelUpWindow(useQueue=False, blurBackground=True, worldDrawEnabled=True, completedLevels=self.__levelRewards.keys(), levelRewards=self.__levelRewards, backCallback=self.__showHangar)

    def __showHangar(self):
        if self.__levelRewards:
            vehicleBonus = findFirst(lambda bonus: bonus.getName() == 'vehicles', self.__levelRewards[_FIRST_LEVEL])
            if vehicleBonus is not None:
                vehicle, _ = first(vehicleBonus.getVehicles(), (None, None))
                if vehicle is not None:
                    g_currentVehicle.selectVehicle(vehicle.invID)
            NewYearNavigation.switchTo(None, instantly=True, withFade=True)
        self.__clear()
        self.onTutorialComplete()
        return

    def __clear(self):
        self._unsubscribe()
        self.__disableVideoStreaming()
        if self.__isActive:
            self.__levelRewards = None
            unlockNotifications()
            g_messengerEvents.onUnlockPopUpMessages()
            self._overlay.setOverlayState(False)
            self.__fadeManager.hideImmediately()
            self.__isActive = False
        return
