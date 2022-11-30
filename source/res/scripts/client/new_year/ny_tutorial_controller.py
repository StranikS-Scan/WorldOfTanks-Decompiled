# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_tutorial_controller.py
import typing
import CGF
import logging
from account_helpers.settings_core.settings_constants import NewYearStorageKeys
from cgf_components import hangar_camera_manager
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from gui.shared.event_dispatcher import showNYHangarNameSelectionWindow
from gui.shared.lock_overlays import lockNotificationManager
from helpers import dependency
from new_year.ny_constants import NY_TUTORIAL_NOTIFICATION_LOCK_KEY
from new_year.ny_level_helper import getNYGeneralConfig
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IOverlayController, IBootcampController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.new_year import INewYearTutorialController, INewYearController
if typing.TYPE_CHECKING:
    from Event import Event
    from typing import Tuple, Callable
_logger = logging.getLogger(__name__)
_TUTORIAL_CAMERA_START = 'Camera_Intro'
_TUTORIAL_CAMERA_END = 'Camera_Intro_End'

def lockNotifications():
    lockNotificationManager(lock=True, postponeActive=True, source=NY_TUTORIAL_NOTIFICATION_LOCK_KEY)


def unlockNotifications():
    lockNotificationManager(lock=False, releasePostponed=True, source=NY_TUTORIAL_NOTIFICATION_LOCK_KEY)


class NewYearTutorialController(INewYearTutorialController):
    _hangarSpace = dependency.descriptor(IHangarSpace)
    _overlay = dependency.descriptor(IOverlayController)
    _nyController = dependency.descriptor(INewYearController)
    _bootcampController = dependency.descriptor(IBootcampController)
    _settingsCore = dependency.descriptor(ISettingsCore)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(NewYearTutorialController, self).__init__()
        self.__wasStarted = False
        self.__inProgress = False

    def startTutorial(self):
        cameraManager = self._cameraManager
        if cameraManager is None:
            return
        else:
            lockNotifications()
            self._overlay.setOverlayState(True)
            if not self._isIntroSceneViewed():
                cameraManager.switchByCameraName(_TUTORIAL_CAMERA_START, instantly=True)
                cameraManager.switchByCameraName(_TUTORIAL_CAMERA_END, instantly=False)
                NewYearSoundsManager.playEvent(NewYearSoundEvents.TUTORIAL_START)
            else:
                cameraManager.switchByCameraName(_TUTORIAL_CAMERA_END, instantly=True)
                showNYHangarNameSelectionWindow()
            self.__subscribe(self.__getCameraEvents())
            self.__wasStarted = True
            self.__inProgress = True
            return

    def markNameSelected(self):
        self.__inProgress = False
        if self.__wasStarted:
            self._cameraManager.switchToTank()
            unlockNotifications()

    def onConnected(self):
        super(NewYearTutorialController, self).onConnected()
        self.__subscribe(self.__getEvents())

    def onDisconnected(self):
        super(NewYearTutorialController, self).onDisconnected()
        self.__unsubscribe(self.__getEvents())
        if self.__wasStarted:
            unlockNotifications()
            self._overlay.setOverlayState(False)
        self.__inProgress = False
        self.__wasStarted = False

    def inProgress(self):
        return self.__inProgress

    def overlayStateChanged(self):
        self.__updateState()

    @property
    def _cameraManager(self):
        return CGF.getManager(self._hangarSpace.spaceID, hangar_camera_manager.HangarCameraManager) if self._hangarSpace.spaceID is not None else None

    def _isNewYearSpace(self):
        return 'newyear' in self._hangarSpace.spacePath

    def _isIntroSceneViewed(self):
        return self._settingsCore.serverSettings.getNewYearStorage().get(NewYearStorageKeys.INTRO_SCENE_VIEWED, False)

    def __onHangarLoaded(self):
        self.__updateState()

    def __updateState(self):
        if not self._nyController.isEnabled() or self._overlay.isActive:
            return
        elif not self._isNewYearSpace():
            return
        elif self._nyController.getHangarNameMask() is None:
            self.startTutorial()
            return
        else:
            generalConfig = getNYGeneralConfig()
            rerollToken = generalConfig.getHangarNameRerollToken()
            if self._itemsCache.items.tokens.getTokenCount(rerollToken) > 0:
                showNYHangarNameSelectionWindow()
            return

    def __onCameraSwitched(self, cameraName):
        if not self.__wasStarted or cameraName != _TUTORIAL_CAMERA_END:
            return
        self._settingsCore.serverSettings.saveInNewYearStorage({NewYearStorageKeys.INTRO_SCENE_VIEWED: True})
        self.__unsubscribe(self.__getCameraEvents())
        showNYHangarNameSelectionWindow()

    def __onCameraSwitchCancel(self, fromCam, _):
        if not self.__inProgress or fromCam != _TUTORIAL_CAMERA_START:
            return
        self.__unsubscribe(self.__getCameraEvents())

    def __onEventStateChanged(self):
        if not self._nyController.isEnabled():
            self.__onInterrupt()
        elif not self.__wasStarted:
            self.__updateState()

    def __onInterrupt(self):
        if self.__wasStarted and self.__inProgress:
            self.__inProgress = False
            cameraManager = self._cameraManager
            if cameraManager:
                cameraManager.switchToTank()
            self._overlay.setOverlayState(False)
            unlockNotifications()

    def __subscribe(self, handlers):
        for event, handler in handlers:
            event += handler

    def __unsubscribe(self, handlers):
        for event, handler in handlers:
            event -= handler

    def __getCameraEvents(self):
        events = tuple()
        cameraManager = self._cameraManager
        if cameraManager:
            events += ((cameraManager.onCameraSwitched, self.__onCameraSwitched), (self._cameraManager.onCameraSwitchCancel, self.__onCameraSwitchCancel))
        return events

    def __getEvents(self):
        events = tuple()
        if self._hangarSpace:
            events += ((self._hangarSpace.onSpaceCreate, self.__onHangarLoaded),)
        if self._nyController:
            events += ((self._nyController.onStateChanged, self.__onEventStateChanged),)
        return events
