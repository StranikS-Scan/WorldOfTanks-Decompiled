# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_tutorial_controller.py
import logging
import typing
import BigWorld
import CGF
from account_helpers.settings_core.settings_constants import NewYearStorageKeys
from cgf_components import hangar_camera_manager
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from gui.shared.event_dispatcher import showNYHangarNameSelectionWindow
from gui.shared.lock_overlays import lockNotificationManager
from helpers import dependency
from new_year.ny_constants import NY_TUTORIAL_NOTIFICATION_LOCK_KEY
from new_year.ny_helper import getNYGeneralConfig
from shared_utils import nextTick
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IOverlayController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.new_year import INewYearTutorialController, INewYearController
if typing.TYPE_CHECKING:
    from Event import Event
    from typing import Tuple, Callable
_logger = logging.getLogger(__name__)
_INTRO_CAMERA_START = 'Camera_Intro'
_INTRO_CAMERA_END = 'Camera_Intro_End'
_INTRO_CAMERAS = (_INTRO_CAMERA_START, _INTRO_CAMERA_END)

def lockNotifications():
    lockNotificationManager(lock=True, postponeActive=True, source=NY_TUTORIAL_NOTIFICATION_LOCK_KEY)


def unlockNotifications():
    lockNotificationManager(lock=False, releasePostponed=True, source=NY_TUTORIAL_NOTIFICATION_LOCK_KEY)


class NewYearTutorialController(INewYearTutorialController):
    _hangarSpace = dependency.descriptor(IHangarSpace)
    _overlay = dependency.descriptor(IOverlayController)
    _nyController = dependency.descriptor(INewYearController)
    _settingsCore = dependency.descriptor(ISettingsCore)
    _itemsCache = dependency.descriptor(IItemsCache)
    _guiLoader = dependency.descriptor(IGuiLoader)

    def __init__(self):
        super(NewYearTutorialController, self).__init__()
        self.__wasStarted = False
        self.__inProgress = False
        self.__activeCameras = 0
        self.__wasOnlineWhenEventStarted = False
        self.__onIntroEnd = None
        return

    def moveCameraToTop(self):
        if self._cameraManager is None:
            return
        else:
            self._cameraManager.switchByCameraName(_INTRO_CAMERA_END, instantly=True)
            return

    def resetCameraToTank(self):
        self._cameraManager.switchToTank()
        unlockNotifications()

    def markNameSelected(self):
        self.__setHangarNameSetToken()
        self._settingsCore.serverSettings.saveInNewYearStorage({NewYearStorageKeys.NY_INTRO_SHOWN: True})
        self.__inProgress = False
        if self.__onIntroEnd:
            self.__onIntroEnd()
        else:
            self._cameraManager.switchToTank()
        unlockNotifications()

    def onConnected(self):
        super(NewYearTutorialController, self).onConnected()
        self.__subscribe(self.__getEvents())

    def onDisconnected(self):
        self.__unsubscribe(self.__getEvents())
        if self.__wasStarted:
            unlockNotifications()
            self._overlay.setOverlayState(False)
        self.__inProgress = False
        self.__wasStarted = False
        self.__activeCameras = 0
        self.__wasOnlineWhenEventStarted = False
        self.__onIntroEnd = None
        return

    def inProgress(self):
        return self.__inProgress

    def startIntro(self, callback=None):
        self.__updateState()
        self.__onIntroEnd = callback

    @property
    def _cameraManager(self):
        return CGF.getManager(self._hangarSpace.spaceID, hangar_camera_manager.HangarCameraManager) if self._hangarSpace.spaceID is not None else None

    def _isNewYearSpace(self):
        return 'newyear' in self._hangarSpace.spacePath

    def __startTutorial(self):
        lockNotifications()
        self._overlay.setOverlayState(True)
        self._cameraManager.switchByCameraName(_INTRO_CAMERA_START, instantly=True)
        self._cameraManager.switchByCameraName(_INTRO_CAMERA_END, instantly=False)
        NewYearSoundsManager.playEvent(NewYearSoundEvents.TUTORIAL_START)
        self.__subscribe(self.__getCameraEvents())
        self.__wasStarted = True
        self.__inProgress = True

    def __setHangarNameSetToken(self):
        hangarNameSetToken = getNYGeneralConfig().getHangarNameSetToken()
        if not self._itemsCache.items.tokens.isTokenAvailable(hangarNameSetToken):
            BigWorld.player().requestSingleToken(hangarNameSetToken)

    def __onSpaceCreate(self):
        self.__subscribe(self.__getCameraInitializeEvents())
        for cameraName in _INTRO_CAMERAS:
            if self._cameraManager.isCameraAdded(cameraName):
                self.__activeCameras += 1

        if self.__activeCameras == len(_INTRO_CAMERAS) and not self.__wasOnlineWhenEventStarted:
            self.__updateState()

    def __onSpaceDestroy(self, _):
        self.__activeCameras = 0
        self.__unsubscribe(self.__getCameraInitializeEvents())

    def __onNewCameraAdded(self, cameraName):
        if cameraName in _INTRO_CAMERAS:
            self.__activeCameras += 1
        if self.__activeCameras == len(_INTRO_CAMERAS) and not self.__wasOnlineWhenEventStarted:
            self.__updateState()

    def __updateState(self):
        if self.__canStartTutorial():
            nextTick(self.__startTutorial)()

    def __onCameraSwitched(self, cameraName):
        if not self.__wasStarted or cameraName != _INTRO_CAMERA_END:
            return
        self.__unsubscribe(self.__getCameraEvents())
        showNYHangarNameSelectionWindow()

    def __onEventStateChanged(self):
        if not self._nyController.isEnabled():
            self.__onInterrupt()
        elif not self.__wasStarted:
            self.__setHangarNameSetToken()
            self.__wasOnlineWhenEventStarted = True

    def __onInterrupt(self):
        if self.__wasStarted and self.__inProgress:
            self.__inProgress = False
            if self._cameraManager:
                self._cameraManager.switchToTank()
            self._overlay.setOverlayState(False)
            unlockNotifications()

    @staticmethod
    def __subscribe(handlers):
        for event, handler in handlers:
            event += handler

    @staticmethod
    def __unsubscribe(handlers):
        for event, handler in handlers:
            event -= handler

    def __getCameraEvents(self):
        events = tuple()
        if self._cameraManager:
            events += ((self._cameraManager.onCameraSwitched, self.__onCameraSwitched),)
        return events

    def __getCameraInitializeEvents(self):
        events = tuple()
        if self._cameraManager:
            events += ((self._cameraManager.onNewCameraAdded, self.__onNewCameraAdded),)
        return events

    def __getEvents(self):
        events = tuple()
        if self._hangarSpace:
            events += ((self._hangarSpace.onSpaceCreate, self.__onSpaceCreate),)
            events += ((self._hangarSpace.onSpaceDestroy, self.__onSpaceDestroy),)
        if self._nyController:
            events += ((self._nyController.onStateChanged, self.__onEventStateChanged),)
        return events

    def __canStartTutorial(self):
        if not self._nyController.isEnabled() or self._overlay.isActive:
            return False
        elif not self._hangarSpace.spaceInited:
            return False
        elif not self._isNewYearSpace():
            return False
        elif self._cameraManager is None:
            return False
        else:
            if self._settingsCore.serverSettings.getNewYearStorage().get(NewYearStorageKeys.NY_INTRO_SHOWN, False):
                hangarNameSetToken = getNYGeneralConfig().getHangarNameSetToken()
                if self._itemsCache.items.tokens.isTokenAvailable(hangarNameSetToken):
                    return False
            return True
