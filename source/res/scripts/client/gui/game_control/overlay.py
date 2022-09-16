# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/overlay.py
import typing
import GUI
from wg_async import wg_async, wg_await, AsyncEvent
from frameworks.wulf import WindowLayer
from gui.Scaleform.lobby_entry import LobbyEntry
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents, CameraMovementStates
from gui.shared import g_eventBus
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IOverlayController, IHeroTankController
from skeletons.gui.shared.utils import IHangarSpace
if typing.TYPE_CHECKING:
    pass
_ANIMATION_DURATION = 300
_LAYERS = (WindowLayer.MARKER,
 WindowLayer.VIEW,
 WindowLayer.WINDOW,
 WindowLayer.WAITING,
 WindowLayer.SYSTEM_MESSAGE,
 WindowLayer.FULLSCREEN_WINDOW)

class OverlayController(IOverlayController):
    _hangarSpace = dependency.descriptor(IHangarSpace)
    _appLoader = dependency.descriptor(IAppLoader)
    _heroTankCtrl = dependency.descriptor(IHeroTankController)
    _c11n = dependency.descriptor(ICustomizationService)

    def __init__(self):
        self._selectableObjectsPrevState = []
        self._stateOn = False
        self._backgroundAlpha = 1
        self._optimizationEnabled = True
        self._globalBlur = GUI.WGUIBackgroundBlur()
        self._wasBlurEnabled = False
        self._showEvent = AsyncEvent()
        self._cameraState = CameraMovementStates.ON_OBJECT
        super(OverlayController, self).__init__()

    def init(self):
        g_eventBus.addListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self._onCameraEntityUpdated)

    def fini(self):
        g_eventBus.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self._onCameraEntityUpdated)
        self._showEvent.set()
        self._showEvent.destroy()

    @wg_async
    def waitShow(self):
        if self._canShow():
            return
        yield wg_await(self._showEvent.wait())

    @property
    def isActive(self):
        return self._stateOn

    def setOverlayState(self, state):
        if self._stateOn != state:
            self._stateOn = state
            self._changeGUIVisibility()

    @property
    def _guiState(self):
        return not self._stateOn

    def _changeGUIVisibility(self):
        lobby = self._appLoader.getDefLobbyApp()
        if self._guiState:
            lobby.containerManager.showContainers(_LAYERS, _ANIMATION_DURATION)
            if self._wasBlurEnabled:
                self._globalBlur.enable = True
                self._wasBlurEnabled = False
            self._c11n.resumeHighlighter()
            self._restoreGraphics()
        else:
            self._optimizationEnabled = lobby.graphicsOptimizationManager.getEnable()
            lobby.graphicsOptimizationManager.switchOptimizationEnabled(False)
            self._backgroundAlpha = lobby.getBackgroundAlpha()
            lobby.setBackgroundAlpha(0)
            lobby.containerManager.hideContainers(_LAYERS, _ANIMATION_DURATION)
            if self._globalBlur.enable:
                self._globalBlur.enable = False
                self._wasBlurEnabled = True
            self._c11n.suspendHighlighter()

    def _restoreGraphics(self):
        lobby = self._appLoader.getDefLobbyApp()
        lobby.graphicsOptimizationManager.switchOptimizationEnabled(self._optimizationEnabled)
        lobby.setBackgroundAlpha(self._backgroundAlpha)

    def _onCameraEntityUpdated(self, event):
        state = event.ctx['state']
        self._cameraState = state
        if state == CameraMovementStates.ON_OBJECT:
            self._showEvent.set()
        else:
            self._showEvent.clear()

    def _canShow(self):
        return self._cameraState == CameraMovementStates.ON_OBJECT
