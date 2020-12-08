# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ClientSelectableCameraObject.py
import math
from functools import partial
import BigWorld
import Math
import math_utils
from ClientSelectableObject import ClientSelectableObject
from helpers.CallbackDelayer import CallbackDelayer, TimeDeltaMeter
from AvatarInputHandler import cameras
from gui.Scaleform.Waiting import Waiting
from gui.hangar_cameras.hangar_camera_common import CameraMovementStates, CameraRelatedEvents
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from skeletons.account_helpers.settings_core import ISettingsCore
from helpers import dependency
from AvatarInputHandler.cameras import FovExtended
from gui.hangar_cameras.hangar_camera_manager import IMMEDIATE_CAMERA_MOVEMENT_MODE
from skeletons.gui.shared.utils import IHangarSpace

def normalizeAngle(angle):
    return angle if angle > 0 else angle + 2 * math.pi


def updateStartAngleAccordingToGoal(startAngle, goalAngle):
    if goalAngle - startAngle > math.pi:
        startAngle += 2 * math.pi
    if goalAngle - startAngle < -math.pi:
        startAngle -= 2 * math.pi
    return startAngle


def calculateYaw(currentPosition, goalPosition):
    goalDirection = goalPosition - currentPosition
    goalDirection.normalise()
    return normalizeAngle(math.atan2(goalDirection.x, goalDirection.z))


def calculatePitch(currentPosition, goalPosition):
    goalDirection = goalPosition - currentPosition
    goalDirection.normalise()
    return normalizeAngle(-math.asin(goalDirection.y))


def calculatePosition(P0, P1, P2, time):
    b1 = (1.0 - time) * (1.0 - time) * P0
    b2 = 2.0 * time * (1.0 - time) * P1
    b3 = time * time * P2
    B = b1 + b2 + b3
    return B


def getXZDeltaDirection(P1, P2, entityPosition):
    V1 = Math.Vector3(P1.x - entityPosition.x, 0.0, P1.z - entityPosition.z)
    V2 = Math.Vector3(P2.x - entityPosition.x, 0.0, P2.z - entityPosition.z)
    V1.normalise()
    V2.normalise()
    direction = 1.0 if (V1 * V2).y < 0 else -1
    result = Math.Vector3(0.0, 0.0, 0.0)
    result.z = direction * V1.x
    result.x = -direction * V1.z
    return result


class ClientSelectableCameraObject(ClientSelectableObject, CallbackDelayer, TimeDeltaMeter):
    settingsCore = dependency.descriptor(ISettingsCore)
    hangarSpace = dependency.descriptor(IHangarSpace)
    allCameraObjects = set()
    P1_DELTA_X_Z = 10.0

    def __init__(self):
        ClientSelectableObject.__init__(self)
        CallbackDelayer.__init__(self)
        TimeDeltaMeter.__init__(self)
        self.__state = CameraMovementStates.FROM_OBJECT
        self.__camera = cameras.FreeCamera()
        self.cameraPitch = math_utils.clamp(-math.pi / 2 * 0.99, math.pi / 2 * 0.99, self.cameraPitch)
        self.cameraYaw = normalizeAngle(self.cameraYaw)
        self.__goalPosition = Math.Vector3(0.0, 0.0, 0.0)
        self.__goalDistance = None
        self.__goalTarget = Math.Vector3(0.0, 0.0, 0.0)
        self.__startPosition = Math.Vector3(0.0, 0.0, 0.0)
        self.__startYaw = 0.0
        self.__startPitch = 0.0
        self.__curTime = None
        self.__easedInYaw = 0.0
        self.__easedInPitch = 0.0
        self.__easeInDuration = 0.0
        self.__startFov = None
        self.__goalFov = None
        if self.enableYawLimits:
            self.__yawLimits = Math.Vector2(self.yawLimitMin, self.yawLimitMax)
        else:
            self.__yawLimits = None
        self.__pitchLimits = Math.Vector2(math.degrees(self.pitchLimitMin), math.degrees(self.pitchLimitMax))
        self.__p1 = Math.Vector3(0.0, 0.0, 0.0)
        self.__p2 = Math.Vector3(0.0, 0.0, 0.0)
        self.__wasPreviousUpdateSkipped = False
        return

    def onEnterWorld(self, prereqs):
        ClientSelectableCameraObject.allCameraObjects.add(self)
        ClientSelectableObject.onEnterWorld(self, prereqs)
        g_eventBus.addListener(CameraRelatedEvents.CUSTOMIZATION_CAMERA_ACTIVATED, self.__forcedFinish)

    def onLeaveWorld(self):
        if self in ClientSelectableCameraObject.allCameraObjects:
            ClientSelectableCameraObject.allCameraObjects.remove(self)
        self.stopCallback(self.__update)
        if self.__camera == BigWorld.camera():
            BigWorld.worldDrawEnabled(False)
        self.__camera.destroy()
        self.__camera = None
        g_eventBus.removeListener(CameraRelatedEvents.CUSTOMIZATION_CAMERA_ACTIVATED, self.__forcedFinish)
        ClientSelectableObject.onLeaveWorld(self)
        CallbackDelayer.destroy(self)
        return

    def onMouseClick(self):
        ClientSelectableCameraObject.switchCamera(self)
        return self.state != CameraMovementStates.FROM_OBJECT

    @classmethod
    def switchCamera(cls, clickedObject=None):
        if not cls.hangarSpace.spaceInited:
            return
        else:
            if not clickedObject:
                clickedObject = cls.hangarSpace.space.getVehicleEntity()
            if clickedObject is None:
                return
            if clickedObject.state != CameraMovementStates.FROM_OBJECT:
                return
            for cameraObject in ClientSelectableCameraObject.allCameraObjects:
                if cameraObject.state != CameraMovementStates.FROM_OBJECT:
                    cameraObject.onDeselect(clickedObject)

            clickedObject.onSelect()
            return

    def onSelect(self):
        self.setEnable(False)
        self.setState(CameraMovementStates.MOVING_TO_OBJECT)
        self._startCameraMovement()

    def onDeselect(self, newSelectedObject):
        if self.state == CameraMovementStates.ON_OBJECT:
            hangarCamera = self.hangarSpace.space.camera
            hangarCameraLocation = self.hangarSpace.space.getCameraLocation()
            self.__goalPosition = hangarCamera.position
            self.cameraYaw = normalizeAngle(Math.Matrix(hangarCamera.source).yaw)
            self.cameraPitch = -1.0 * Math.Matrix(hangarCamera.source).pitch
            self.__goalTarget = Math.Matrix(hangarCamera.target).translation
            self.__pitchLimits = hangarCameraLocation['camConstraints'][0]
            self.__goalDistance = hangarCameraLocation['pivotDist']
        self.setState(CameraMovementStates.FROM_OBJECT)
        self.stopCallback(self.__update)
        self.setEnable(True)
        if newSelectedObject and newSelectedObject == self.hangarSpace.space.getVehicleEntity():
            newSelectedObject.cameraUpcomingDuration = self.cameraBackwardDuration
            newSelectedObject.movementYDelta = self.movementYDelta

    def setState(self, state):
        self.__state = state
        g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, ctx={'state': self.__state,
         'entityId': self.id}), scope=EVENT_BUS_SCOPE.DEFAULT)

    @property
    def state(self):
        return self.__state

    def _setStartValues(self):
        size = self._getModelHeight() / (2.0 * self.cameraObjectAspect)
        self.__goalTarget = Math.Matrix(self.model.matrix).translation + self.cameraShift
        if not self.__goalDistance:
            distConstr = self.hangarSpace.space.getCameraLocation()['camConstraints'][2]
            self.__goalDistance = math_utils.clamp(distConstr[0], distConstr[1], size / math.tan(BigWorld.projection().fov / 2.0))

    def __normalizeStartValues(self):
        yaw1 = calculateYaw(self.__startPosition, self.__goalPosition)
        dif1 = abs(yaw1 - self.__startYaw)
        dif1 = dif1 if dif1 < math.pi else 2.0 * math.pi - dif1
        dif2 = abs(self.cameraYaw - self.__startYaw)
        dif2 = dif2 if dif2 < math.pi else 2.0 * math.pi - dif2
        self.__easeInDuration = max(dif1 / math.pi, dif2 / math.pi, 0.1)
        _, self.__easedInYaw, self.__easedInPitch = self.__updateCalculateParams(self.__easeInDuration)
        self.__startYaw = updateStartAngleAccordingToGoal(self.__startYaw, self.__easedInYaw)
        self.__startPitch = updateStartAngleAccordingToGoal(self.__startPitch, self.__easedInPitch)

    def __updateCalculateParams(self, time):
        easedTime = math_utils.easeOutCubic(time, 1.0, 1.0)
        position = calculatePosition(self.__startPosition, self.__p1, self.__goalPosition, easedTime)
        yaw = self.__interpolateAngle(self.__startYaw, self.__easedInYaw, position, self.__p2, time, calculateYaw)
        pitch = self.__interpolateAngle(self.__startPitch, self.__easedInPitch, position, self.__p2, time, calculatePitch)
        return (position, yaw, pitch)

    def _startCameraMovement(self):
        hangarCamera = self.hangarSpace.space.camera
        self._setStartValues()
        startMatrix = Math.Matrix(BigWorld.camera().matrix)
        self.__teleportHangarSpaceCamera()
        self.__goalPosition = hangarCamera.position
        self.__startFovIfDynamic()
        self.__camera.enable(startMatrix)
        self.__startPosition = self.__camera.getWorldMatrix().translation
        self.__startYaw = normalizeAngle(self.__camera.getWorldMatrix().yaw)
        self.__startPitch = self.__camera.getWorldMatrix().pitch
        self.__curTime = 0.0
        self.__p2 = self.__goalTarget + self.cameraPivot
        self.__p1 = (self.__startPosition + self.__goalPosition) * 0.5
        self.__p1.y += self.movementYDelta
        self.__p1 += getXZDeltaDirection(self.__startPosition, self.__goalPosition, self.__p2) * self.P1_DELTA_X_Z
        self.__normalizeStartValues()
        self.__wasPreviousUpdateSkipped = True
        self.measureDeltaTime()
        self.delayCallback(0.0, self.__update)

    def __startFovIfDynamic(self):
        if not self.settingsCore.getSetting('dynamicFov'):
            return
        _, minFov, maxFov = self.settingsCore.getSetting('fov')
        distConstr = self.hangarSpace.space.getCameraLocation()['camConstraints'][2]
        if distConstr[1] != distConstr[0]:
            relativeDist = (self.__goalDistance - distConstr[0]) / (distConstr[1] - distConstr[0])
        else:
            relativeDist = 1.0
        self.__startFov = math.degrees(BigWorld.projection().fov)
        self.__goalFov = math_utils.lerp(minFov, maxFov, relativeDist)

    def __teleportHangarSpaceCamera(self):
        yaw = self.cameraYaw
        pitch = -1 * self.cameraPitch
        camLimits = (self.__pitchLimits, self.__yawLimits, None)
        self.hangarSpace.space.setCameraLocation(self.__goalTarget, self.cameraPivot, yaw, pitch, self.__goalDistance, camLimits, False, IMMEDIATE_CAMERA_MOVEMENT_MODE)
        return

    def __update(self):
        isUpdateSkipped = Waiting.isVisible()
        if isUpdateSkipped or self.__wasPreviousUpdateSkipped:
            self.__wasPreviousUpdateSkipped = isUpdateSkipped
            self.measureDeltaTime()
            return 0.0
        self.__curTime += self.measureDeltaTime() / self.cameraUpcomingDuration
        isCameraDone = self.__curTime >= 1.0
        if isCameraDone:
            self._finishCameraMovement()
        else:
            self.__updateCameraLocation()
            return 0.0

    def __updateCameraLocation(self):
        position, yaw, pitch = self.__updateCalculateParams(self.__curTime)
        mat = math_utils.createRTMatrix(Math.Vector3(yaw, pitch, 0.0), position)
        self.__camera.setWorldMatrix(mat)
        self.__updateDynamicFOV(self.__curTime)

    def __updateDynamicFOV(self, time):
        if not self.__goalFov or not self.__startFov:
            return
        if time > self.__easeInDuration:
            return
        time /= self.__easeInDuration
        fov = math_utils.lerp(self.__startFov, self.__goalFov, time)
        BigWorld.callback(0.0, partial(FovExtended.instance().setFovByAbsoluteValue, fov, 0.1))

    def __interpolateAngle(self, startValue, easedInValue, currentPosition, goalPosition, time, angleCalculation):
        return math_utils.easeOutQuad(time, easedInValue - startValue, self.__easeInDuration) + startValue if time < self.__easeInDuration else angleCalculation(currentPosition, goalPosition)

    def _finishCameraMovement(self):
        self.stopCallback(self.__update)
        self.setState(CameraMovementStates.ON_OBJECT)
        self.__camera.disable()
        BigWorld.camera(self.hangarSpace.space.camera)
        self.__startFov = None
        self.__goalFov = None
        self.__curTime = None
        return

    def __forcedFinish(self, _):
        if self.__state == CameraMovementStates.MOVING_TO_OBJECT:
            self._finishCameraMovement()
