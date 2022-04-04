# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ClientSelectableRTSObject.py
import enum
import logging
import Math
from ClientSelectableCameraObject import ClientSelectableCameraObject
from HangarVehicle import HangarVehicle
from constants import ARENA_BONUS_TYPE
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents, CameraMovementStates
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import CameraMoveEvent
from helpers import dependency
from skeletons.gui.game_control import IRTSBattlesController
from skeletons.gui.shared.utils import IHangarSpace
_logger = logging.getLogger(__name__)
_MIN_CAM_DISTANCE = 4.0
_MAX_CAM_DISTANCE = 5.0

class RTS_CAMERA_LOCATION(enum.Enum):
    TANKER = 'tanker'
    STRATEGIST_1V7 = 'strategist_1v7'
    STRATEGIST_1V1 = 'strategist_1v1'


class ClientSelectableRTSObject(ClientSelectableCameraObject):
    __rtsController = dependency.descriptor(IRTSBattlesController)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        super(ClientSelectableRTSObject, self).__init__()
        self.__currentCamLocation = None
        self.P1_DELTA_X_Z = 4.0
        self._distLimits = Math.Vector2(_MIN_CAM_DISTANCE, _MAX_CAM_DISTANCE)
        return

    def onEnterWorld(self, prereqs):
        super(ClientSelectableRTSObject, self).onEnterWorld(prereqs)
        self.__rtsController.onUpdated += self._onUpdate
        self.__rtsController.onIsPrbActive += self.__onIsRTSActive
        self.__hangarSpace.onSpaceCreate += self.__onSpaceCreateOrRefresh
        self.__hangarSpace.onSpaceRefreshCompleted += self.__onSpaceCreateOrRefresh
        self.setEnable(True)
        self._onUpdate()

    def onLeaveWorld(self):
        self.setEnable(False)
        self.__rtsController.onUpdated -= self._onUpdate
        self.__rtsController.onIsPrbActive -= self.__onIsRTSActive
        self.__hangarSpace.onSpaceCreate -= self.__onSpaceCreateOrRefresh
        self.__hangarSpace.onSpaceRefreshCompleted -= self.__onSpaceCreateOrRefresh
        self._removeListeners()
        super(ClientSelectableRTSObject, self).onLeaveWorld()

    def _removeListeners(self):
        g_eventBus.removeListener(CameraMoveEvent.ON_HANGAR_VEHICLE, self._eventHandler, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__hangarSpace.onVehicleChangeStarted -= self._onUpdate

    def _addListeners(self):
        g_eventBus.addListener(CameraMoveEvent.ON_HANGAR_VEHICLE, self._eventHandler, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__hangarSpace.onVehicleChangeStarted += self._onUpdate

    def onMouseClick(self):
        self.__rtsController.enterRTSPrebattle()

    def __onIsRTSActive(self, isPrbActive):
        if isPrbActive:
            self._addListeners()
        else:
            self._removeListeners()
        self._onUpdate()

    def _eventHandler(self, event=None):
        if self.__currentCamLocation != RTS_CAMERA_LOCATION.TANKER:
            self.__currentCamLocation = cameraLocation = RTS_CAMERA_LOCATION.TANKER
            self._CAM_TRANSITION_DICT[cameraLocation](self)

    def _onUpdate(self):
        if not self.__hangarSpace.spaceInited:
            return
        else:
            if self.__rtsController.isPrbActive():
                self._updateCamera()
            else:
                self.__currentCamLocation = None
                self.onDeselect(None)
                self.switchCamera()
            return

    def _updateCamera(self):
        cameraLocation = self.__getRequiredCameraLocation()
        if self.__currentCamLocation == cameraLocation:
            return
        if not self.__currentCamLocation and cameraLocation == RTS_CAMERA_LOCATION.TANKER:
            self.__deselectOtherCameraObjectsExceptHangarVehicle()
            self.setEnable(False)
        self.__currentCamLocation = cameraLocation
        self._CAM_TRANSITION_DICT[cameraLocation or RTS_CAMERA_LOCATION.TANKER](self)

    def __onSpaceCreateOrRefresh(self):
        self._onUpdate()

    def __getRequiredCameraLocation(self):
        battleMode = self.__rtsController.getBattleMode()
        if battleMode == ARENA_BONUS_TYPE.RTS_BOOTCAMP:
            return None
        elif battleMode == ARENA_BONUS_TYPE.RTS:
            if self.__rtsController.isCommander():
                return RTS_CAMERA_LOCATION.STRATEGIST_1V7
            return RTS_CAMERA_LOCATION.TANKER
        else:
            return RTS_CAMERA_LOCATION.STRATEGIST_1V1 if battleMode == ARENA_BONUS_TYPE.RTS_1x1 else None

    def __setupTankerLocation(self):
        _logger.debug('[ClientSelectableRTSObject] moving camera to tanker position.')
        self.__setIdleAndParalaxMovement(True)
        self.onDeselect(self)
        self.setEnable(False)
        self.__pointCameraTowardsHangarTank()
        self.hangarSpace.space.getCameraManager().enableMovementByMouse(enableZoom=True)

    def __setupStrategist1x1Location(self):
        _logger.debug('[ClientSelectableRTSObject] moving camera to strategist 1x1 position.')
        self.__setIdleAndParalaxMovement(False)
        self.__deselectPlayerVehicle()
        self.cameraYaw = self.cameraYaw1v1
        self.cameraPitch = self.cameraPitch1v1
        self.yawLimitMin = self.cameraYaw - self.cameraYawRange1v1
        self.yawLimitMax = self.cameraYaw + self.cameraYawRange1v1
        self.onSelect()
        self.hangarSpace.space.getCameraManager().enableMovementByMouse(enableZoom=False)

    def __setupStrategist1x7Location(self):
        _logger.debug('[ClientSelectableRTSObject] moving camera to strategist 1x7 position.')
        self.__setIdleAndParalaxMovement(False)
        self.__deselectPlayerVehicle()
        self.cameraYaw = self.cameraYaw1v7
        self.cameraPitch = self.cameraPitch1v7
        self.yawLimitMin = self.cameraYaw - self.cameraYawRange1v7
        self.yawLimitMax = self.cameraYaw + self.cameraYawRange1v7
        self.onSelect()
        self.hangarSpace.space.getCameraManager().enableMovementByMouse(enableZoom=False)

    def __setIdleAndParalaxMovement(self, isEnabled):
        g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, ctx={'isDisable': not isEnabled,
         'setIdle': True,
         'setParallax': True}), EVENT_BUS_SCOPE.LOBBY)

    def __deselectOtherCameraObjectsExceptHangarVehicle(self):
        for cameraObject in ClientSelectableCameraObject.allCameraObjects:
            if cameraObject.state != CameraMovementStates.FROM_OBJECT and not isinstance(cameraObject, HangarVehicle):
                cameraObject.onDeselect(self)

    def __pointCameraTowardsHangarTank(self):
        playerVehicle = self.hangarSpace.space.getVehicleEntity()
        if playerVehicle.state == CameraMovementStates.FROM_OBJECT:
            playerVehicle.cameraUpcomingDuration = self.cameraBackwardDuration
            playerVehicle.onSelect()

    def __deselectPlayerVehicle(self):
        playerVehicle = self.hangarSpace.space.getVehicleEntity()
        if playerVehicle.state != CameraMovementStates.FROM_OBJECT:
            playerVehicle.onDeselect(self)
            playerVehicle.setEnable(False)

    _CAM_TRANSITION_DICT = {RTS_CAMERA_LOCATION.TANKER: __setupTankerLocation,
     RTS_CAMERA_LOCATION.STRATEGIST_1V7: __setupStrategist1x7Location,
     RTS_CAMERA_LOCATION.STRATEGIST_1V1: __setupStrategist1x1Location}
