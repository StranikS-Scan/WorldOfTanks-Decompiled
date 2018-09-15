# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ClientSelectableCameraObject.py
import BigWorld
import math
import Math
from ClientSelectableObject import ClientSelectableObject
from helpers.CallbackDelayer import CallbackDelayer, TimeDeltaMeter
from AvatarInputHandler import cameras, mathUtils
from gui.shared.utils.HangarSpace import g_hangarSpace
from gui.Scaleform.Waiting import Waiting

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


def checkThreeInLine(P1, P2, P3, delta):
    A = P1.z - P2.z
    B = P2.x - P1.x
    C = P1.x * P2.z - P2.x * P1.z
    if A == 0.0 and B == 0.0:
        return False
    d = abs(A * P3.x + B * P3.z + C) / math.sqrt(A * A + B * B)
    return d < delta


class CameraMovementStates:
    ON_OBJECT = 0
    MOVING_TO_OBJECT = 1
    FROM_OBJECT = 2


class ClientSelectableCameraObject(ClientSelectableObject, CallbackDelayer, TimeDeltaMeter):
    allCameraObjects = list()
    P1_DELTA = Math.Vector3(0.0, 10.0, 0.0)
    P1_DELTA_IF_FLIP = Math.Vector3(-10.0, 0.0, -10.0)
    FLIP_DIST = 1.0

    def __init__(self):
        ClientSelectableObject.__init__(self)
        CallbackDelayer.__init__(self)
        TimeDeltaMeter.__init__(self)
        self.__state = CameraMovementStates.FROM_OBJECT
        self.isRoot = False
        self.__camera = cameras.FreeCamera()
        self.__cameraDoneCallback = None
        self.goalPosition = Math.Vector3(0.0, 0.0, 0.0)
        self.cameraPitch = mathUtils.clamp(-math.pi / 2 * 0.99, math.pi / 2 * 0.99, self.camera_pitch)
        self.cameraYaw = normalizeAngle(self.camera_yaw)
        self.cameraPivot = Math.Vector3(self.camera_pivot_x, self.camera_pivot_y, self.camera_pivot_z)
        self.goalDistance = Math.Vector2(0.0, 0.0)
        self.goalTarget = Math.Vector3(0.0, 0.0, 0.0)
        self.cameraShift = Math.Vector3(self.camera_shift_x, self.camera_shift_y, self.camera_shift_z)
        self.startPosition = Math.Vector3(0.0, 0.0, 0.0)
        self.startYaw = 0.0
        self.startPitch = 0.0
        self.curTime = 0.0
        self.easedInYaw = 0.0
        self.easedInPitch = 0.0
        self.easeInDuration = 0.0
        if self.enable_yaw_limits:
            self.yawLimits = Math.Vector2(self.yaw_limit_min, self.yaw_limit_max)
        else:
            self.yawLimits = None
        self.pitchLimits = Math.Vector2(math.degrees(self.pitch_limit_min), math.degrees(self.pitch_limit_max))
        self.P1 = Math.Vector3(0.0, 0.0, 0.0)
        self.P2 = Math.Vector3(0.0, 0.0, 0.0)
        self.__wasPreviousUpdateSkipped = False
        return

    def onEnterWorld(self, prereqs):
        ClientSelectableCameraObject.allCameraObjects.append(self)
        ClientSelectableObject.onEnterWorld(self, prereqs)

    def onLeaveWorld(self):
        ClientSelectableCameraObject.allCameraObjects.remove(self)
        self.stopCallback(self.__update)
        if self.__camera == BigWorld.camera():
            BigWorld.camera(None)
            BigWorld.worldDrawEnabled(False)
        self.__camera.destroy()
        self.__camera = None
        ClientSelectableObject.onLeaveWorld(self)
        CallbackDelayer.destroy(self)
        return

    def onClicked(self, cameraCallback=None):
        if self.cameraLocked is False:
            ClientSelectableObject.onClicked(self)
            return ClientSelectableCameraObject.switchCamera(self, cameraCallback)

    @staticmethod
    def switchCamera(clickedObject=None, callback=None):
        if clickedObject is None:
            for cameraObject in ClientSelectableCameraObject.allCameraObjects:
                try:
                    if cameraObject.isRoot:
                        clickedObject = cameraObject
                        break
                except:
                    break

        if clickedObject is None:
            return False
        elif clickedObject.state != CameraMovementStates.FROM_OBJECT:
            return False
        else:
            playingFlyOutTransition = False
            for cameraObject in ClientSelectableCameraObject.allCameraObjects:
                if cameraObject.state != CameraMovementStates.FROM_OBJECT:
                    playingFlyOutTransition |= cameraObject.onDeselect(clickedObject)

            if not playingFlyOutTransition:
                clickedObject.playCameraFlyToSound()
            clickedObject.onSelect(callback)
            return True

    def onSelect(self, callback=None):
        self.enable(False)
        self.setState(CameraMovementStates.MOVING_TO_OBJECT)
        self.resetTime()
        self.__startCameraMovement()
        self.__cameraDoneCallback = callback
        self.delayCallback(0.0, self.__update)

    def onDeselect(self, newSelectedObject):
        self.setState(CameraMovementStates.FROM_OBJECT)
        self.stopCallback(self.__update)
        self.__cameraDoneCallback = None
        self.enable(True)
        if newSelectedObject is not None and newSelectedObject.isRoot:
            newSelectedObject.camera_upcoming_duration = self.camera_backward_duration
        return self.playCameraFlyFromSound()

    def setState(self, state):
        self.__state = state

    @property
    def state(self):
        return self.__state

    def setStartValues(self):
        self.goalDistance[0] = self.camera_min_distance
        self.goalDistance[1] = self.camera_max_distance
        self.goalTarget = Math.Matrix(self.model.matrix).translation + self.cameraShift

    def __normalizeStartValues(self):
        yaw = calculateYaw(self.startPosition, self.goalPosition)
        dif = abs(yaw - self.startYaw)
        dif = dif if dif < math.pi else 2 * math.pi - dif
        self.easeInDuration = max(dif / math.pi, 0.1)
        _, self.easedInYaw, self.easedInPitch = self.__updateCalculateParams(self.easeInDuration)
        self.startYaw = updateStartAngleAccordingToGoal(self.startYaw, self.easedInYaw)
        self.startPitch = updateStartAngleAccordingToGoal(self.startPitch, self.easedInPitch)

    def __updateCalculateParams(self, time):
        easedTime = mathUtils.easeOutCubic(time, 1.0, 1.0)
        position = calculatePosition(self.startPosition, self.P1, self.goalPosition, easedTime)
        yaw = self.__interpolateAngle(self.startYaw, self.easedInYaw, position, self.P2, time, calculateYaw)
        pitch = self.__interpolateAngle(self.startPitch, self.easedInPitch, position, self.P2, time, calculatePitch)
        return (position, yaw, pitch)

    def __startCameraMovement(self):
        self.setStartValues()
        camera = BigWorld.camera()
        startMatrix = Math.Matrix(camera.matrix)
        self.__teleportHangarSpaceCamera()
        self.__camera.enable(startMatrix)
        self.startPosition = self.__camera.getWorldMatrix().translation
        self.startYaw = normalizeAngle(self.__camera.getWorldMatrix().yaw)
        self.startPitch = self.__camera.getWorldMatrix().pitch
        self.curTime = 0.0
        self.P1 = (self.startPosition + self.goalPosition) * 0.5
        self.P1 += self.P1_DELTA
        self.P2 = Math.Vector3(self.position)
        self.P2 += self.cameraPivot
        self.P2 += self.cameraShift
        if checkThreeInLine(BigWorld.camera().position, self.goalPosition, self.P2, self.FLIP_DIST):
            self.P1 += self.P1_DELTA_IF_FLIP
        self.__normalizeStartValues()
        self.__wasPreviousUpdateSkipped = False

    def __teleportHangarSpaceCamera(self):
        clientSpace = g_hangarSpace.space
        constr = clientSpace.getCameraLocation()['camConstraints']
        constr[0] = self.pitchLimits
        if self.enable_yaw_limits:
            constr[1] = self.yawLimits
        else:
            constr[1] = Math.Vector2(0, 2 * math.pi)
        yaw = self.cameraYaw
        pitch = -1 * self.cameraPitch
        clientSpace.setCameraLocation(self.goalTarget, self.cameraPivot, yaw, pitch, (self.goalDistance[0] + self.goalDistance[1]) * 0.5, constr, True)
        hangarCamera = clientSpace.getCamera()
        hangarCamera.update(1000)
        self.goalPosition = hangarCamera.position
        self.setCursorCameraDistance()

    def __update(self):
        isUpdateSkipped = Waiting.isVisible()
        if isUpdateSkipped or self.__wasPreviousUpdateSkipped:
            self.__wasPreviousUpdateSkipped = isUpdateSkipped
            self.measureDeltaTime()
            return 0.0
        self.curTime += self.measureDeltaTime() / self.camera_upcoming_duration
        isCameraDone = self.curTime >= 1.0
        if isCameraDone:
            self.stopCallback(self.__update)
            self._finishCameraMovement()
        else:
            self.__updateCameraLocation()
            return 0.0

    def __updateCameraLocation(self):
        position, yaw, pitch = self.__updateCalculateParams(self.curTime)
        mat = mathUtils.createRTMatrix(Math.Vector3(yaw, pitch, 0.0), position)
        self.__camera.setWorldMatrix(mat)

    def __interpolateAngle(self, startValue, easedInValue, currentPosition, goalPosition, time, angleCalculation):
        return mathUtils.easeOutQuad(time, easedInValue - startValue, self.easeInDuration) + startValue if time < self.easeInDuration else angleCalculation(currentPosition, goalPosition)

    def _finishCameraMovement(self):
        self.setState(CameraMovementStates.ON_OBJECT)
        self.__camera.disable()
        BigWorld.camera(g_hangarSpace.space.getCamera())
        if self.__cameraDoneCallback is not None:
            self.__cameraDoneCallback()
            self.__cameraDoneCallback = None
        return

    def setCursorCameraDistance(self):
        g_hangarSpace.space.setCameraDistance(self.goalDistance[0], self.goalDistance[1])

    def toggleCameraMovement(self, enabled):
        if enabled:
            self.__stableCamera = False
            ClientSelectableObject.lockCamera(False)
        else:
            self.__stableCamera = True
            self.__keepCameraStable_Repeat()
            ClientSelectableObject.lockCamera(True)

    def __keepCameraStable_Repeat(self):
        if self.__stableCamera is True:
            if self.state != CameraMovementStates.ON_OBJECT or self.enabled:
                self.toggleCameraMovement(True)
            else:
                self.__teleportHangarSpaceCamera()
                self.delayCallback(0.0, self.__keepCameraStable_Repeat)
