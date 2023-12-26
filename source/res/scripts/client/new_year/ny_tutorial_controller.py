# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_tutorial_controller.py
import logging
import CGF
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NY_INTRO_SHOWN
from cgf_components import hangar_camera_manager
from frameworks.wulf import WindowLayer, WindowStatus
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.sf_window import SFWindow
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from gui.shared.event_dispatcher import showNYHangarNameSelectionWindow
from gui.shared.lock_overlays import lockNotificationManager
from helpers import dependency
from new_year.ny_constants import NY_TUTORIAL_NOTIFICATION_LOCK_KEY
from new_year.ny_helper import getNYGeneralConfig
from shared_utils import nextTick
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IOverlayController, IBootcampController
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


def findWindowPredicate(window):
    return WindowLayer.SUB_VIEW <= window.layer <= WindowLayer.OVERLAY


def isInHangar():
    guiLoader = dependency.instance(IGuiLoader)
    openWindows = guiLoader.windowsManager.findWindows(findWindowPredicate)
    return openWindows and len(openWindows) == 1 and isinstance(openWindows[0], SFWindow) and openWindows[0].loadParams.viewKey.alias == VIEW_ALIAS.LOBBY_HANGAR


class NewYearTutorialController(INewYearTutorialController):
    _hangarSpace = dependency.descriptor(IHangarSpace)
    _overlay = dependency.descriptor(IOverlayController)
    _nyController = dependency.descriptor(INewYearController)
    _bootcampController = dependency.descriptor(IBootcampController)
    _settingsCore = dependency.descriptor(ISettingsCore)
    _itemsCache = dependency.descriptor(IItemsCache)
    _guiLoader = dependency.descriptor(IGuiLoader)

    def __init__(self):
        super(NewYearTutorialController, self).__init__()
        self.__wasStarted = False
        self.__inProgress = False
        self.__activeCameras = 0

    def startTutorial(self):
        self.__unsubscribe(self.__getWindowsStatusEvents())
        flag = AccountSettings.getUIFlag(NY_INTRO_SHOWN)
        if flag:
            self.__subscribe(self.__getCameraEvents())
            self.__wasStarted = True
            self.__inProgress = True
            self._cameraManager.switchByCameraName(_INTRO_CAMERA_END, instantly=True)
            return
        AccountSettings.setUIFlag(NY_INTRO_SHOWN, True)
        lockNotifications()
        self._overlay.setOverlayState(True)
        self._cameraManager.switchByCameraName(_INTRO_CAMERA_START, instantly=True)
        self._cameraManager.switchByCameraName(_INTRO_CAMERA_END, instantly=False)
        NewYearSoundsManager.playEvent(NewYearSoundEvents.TUTORIAL_START)
        self.__subscribe(self.__getCameraEvents())
        self.__wasStarted = True
        self.__inProgress = True

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
        self.__inProgress = False
        if self.__wasStarted:
            self.resetCameraToTank()

    def onConnected(self):
        super(NewYearTutorialController, self).onConnected()
        self.__subscribe(self.__getEvents())
        self.__subscribe(self.__getWindowsStatusEvents())

    def onDisconnected(self):
        super(NewYearTutorialController, self).onDisconnected()
        self.__unsubscribe(self.__getWindowsStatusEvents())
        self.__unsubscribe(self.__getEvents())
        if self.__wasStarted:
            unlockNotifications()
            self._overlay.setOverlayState(False)
        self.__inProgress = False
        self.__wasStarted = False
        self.__activeCameras = 0

    def inProgress(self):
        return self.__inProgress

    def overlayStateChanged(self):
        self.__updateState()

    @property
    def _cameraManager(self):
        return CGF.getManager(self._hangarSpace.spaceID, hangar_camera_manager.HangarCameraManager) if self._hangarSpace.spaceID is not None else None

    def _isNewYearSpace(self):
        return 'newyear' in self._hangarSpace.spacePath

    def __onSpaceCreate(self):
        self.__subscribe(self.__getCameraInitializeEvents())
        for cameraName in _INTRO_CAMERAS:
            if self._cameraManager.isCameraAdded(cameraName):
                self.__activeCameras += 1

        if self.__activeCameras == len(_INTRO_CAMERAS):
            self.__updateState()

    def __onSpaceDestroy(self, _):
        self.__activeCameras = 0
        self.__unsubscribe(self.__getCameraInitializeEvents())

    def __onNewCameraAdded(self, cameraName):
        if cameraName in _INTRO_CAMERAS:
            self.__activeCameras += 1
            if self.__activeCameras == len(_INTRO_CAMERAS):
                self.__updateState()

    def __updateState(self):
        if self.__canStartTutorial():
            nextTick(self.startTutorial)()

    def __onCameraSwitched(self, cameraName):
        if not self.__wasStarted or cameraName != _INTRO_CAMERA_END:
            return
        self.__unsubscribe(self.__getCameraEvents())
        showNYHangarNameSelectionWindow()

    def __onEventStateChanged(self):
        if not self._nyController.isEnabled():
            self.__onInterrupt()
        elif not self.__wasStarted:
            self.__updateState()

    def __onInterrupt(self):
        if self.__wasStarted and self.__inProgress:
            self.__inProgress = False
            if self._cameraManager:
                self._cameraManager.switchToTank()
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
        if self._cameraManager:
            events += ((self._cameraManager.onCameraSwitched, self.__onCameraSwitched),)
        return events

    def __getCameraInitializeEvents(self):
        events = tuple()
        if self._cameraManager:
            events += ((self._cameraManager.onNewCameraAdded, self.__onNewCameraAdded),)
        return events

    def __getWindowsStatusEvents(self):
        events = tuple()
        hangarNameSetToken = getNYGeneralConfig().getHangarNameSetToken()
        if self._itemsCache.items.tokens.getTokenCount(hangarNameSetToken) == 0 and self._nyController and not self._bootcampController.isInBootcamp():
            events += ((self._guiLoader.windowsManager.onWindowStatusChanged, self.__onWindowStatusChanged),)
        return events

    def __getEvents(self):
        events = tuple()
        if self._hangarSpace:
            events += ((self._hangarSpace.onSpaceCreate, self.__onSpaceCreate),)
            events += ((self._hangarSpace.onSpaceDestroy, self.__onSpaceDestroy),)
        if self._nyController:
            events += ((self._nyController.onStateChanged, self.__onEventStateChanged),)
        return events

    def __onWindowStatusChanged(self, _, newStatus):
        if newStatus == WindowStatus.LOADED or newStatus == WindowStatus.DESTROYED:
            self.__updateState()

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
            hangarNameSetToken = getNYGeneralConfig().getHangarNameSetToken()
            return False if self._itemsCache.items.tokens.getTokenCount(hangarNameSetToken) > 0 else isInHangar()
