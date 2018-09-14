# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ClientSelectableCameraObject.py
import BigWorld
import math
import Math
import SoundGroups
from ClientSelectableObject import ClientSelectableObject
from helpers.CallbackDelayer import CallbackDelayer
from AvatarInputHandler import cameras, mathUtils
from gui.shared.utils import HangarSpace

class CameraMovementStates:
    ON_OBJECT = 0
    MOVING_TO_OBJECT = 1
    FROM_OBJECT = 2


class ClientSelectableCameraObject(ClientSelectableObject, CallbackDelayer):
    allCameraObjects = list()
    UPDATE_CALLBACK_DT = 0.01
    UPDATE_CAMERA_DS = 0.01
    UPDATE_CAMERA_MULTIPLIER = 10.0

    def __init__(self):
        ClientSelectableObject.__init__(self)
        CallbackDelayer.__init__(self)
        self.state = CameraMovementStates.FROM_OBJECT
        self.isRoot = False
        self.__camera = cameras.FreeCamera()
        self.__cameraDoneCallback = None
        self.goalPosition = Math.Vector3(0.0, 0.0, 0.0)
        self.goalYaw = self.camera_yaw
        self.goalPitch = mathUtils.clamp(-math.pi / 2 * 0.99, math.pi / 2 * 0.99, self.camera_pitch)
        self.goalPivot = Math.Vector3(self.camera_pivot_x, self.camera_pivot_y, self.camera_pivot_z)
        self.goalDistance = 0
        self.goalTarget = Math.Vector3(0.0, 0.0, 0.0)
        self.shift = Math.Vector3(self.camera_shift_x, self.camera_shift_y, self.camera_shift_z)
        return

    def destroy(self):
        CallbackDelayer.destroy(self)

    def onEnterWorld(self, prereqs):
        ClientSelectableObject.onEnterWorld(self, prereqs)
        ClientSelectableCameraObject.allCameraObjects.append(self)

    def onLeaveWorld(self):
        ClientSelectableCameraObject.allCameraObjects.remove(self)
        self.stopCallback(self.__update)
        if self.__camera == BigWorld.camera():
            BigWorld.camera(None)
            BigWorld.worldDrawEnabled(False)
        self.__camera.destroy()
        self.__camera = None
        ClientSelectableObject.onLeaveWorld(self)
        return

    @staticmethod
    def switchCamera(clickedObject=None, callback=None):
        if clickedObject is None:
            for cameraObject in ClientSelectableCameraObject.allCameraObjects:
                if cameraObject.isRoot:
                    clickedObject = cameraObject
                    break

        if clickedObject is None:
            return
        elif clickedObject.state != CameraMovementStates.FROM_OBJECT:
            return
        else:
            for cameraObject in ClientSelectableCameraObject.allCameraObjects:
                if cameraObject.state != CameraMovementStates.FROM_OBJECT:
                    cameraObject.onDeselect()

            clickedObject.onSelect(callback)
            return

    def playSelectedSound(self):
        SoundGroups.g_instance.playSound2D('hangar_activeview_mark')

    def onSelect(self, callback=None):
        self.enable(False)
        self.state = CameraMovementStates.MOVING_TO_OBJECT
        self.playSelectedSound()
        self.__startCameraMovement()
        self.__cameraDoneCallback = callback
        self.delayCallback(self.UPDATE_CALLBACK_DT, self.__update)

    def onDeselect(self):
        self.stopCallback(self.__update)
        self.__cameraDoneCallback = None
        self.enable(True)
        self.state = CameraMovementStates.FROM_OBJECT
        return

    def setStartValues(self):
        height = self.model.height / (2.0 * self.camera_object_aspect)
        self.goalDistance = height / math.tan(BigWorld.projection().fov / 2.0)
        self.goalTarget = Math.Matrix(self.model.matrix).translation + self.shift

    def __startCameraMovement(self):
        self.setStartValues()
        camera = BigWorld.camera()
        startMatrix = Math.Matrix(camera.matrix)
        self.__teleportHangarSpaceCamera()
        self.__camera.enable(startMatrix)

    def __teleportHangarSpaceCamera(self):
        clientSpace = HangarSpace.g_hangarSpace.space
        clientSpace.setCameraLocation(self.goalTarget, self.goalPivot, self.goalYaw, self.getPitchMultiplier() * self.goalPitch, self.goalDistance, True)
        hangarCamera = clientSpace.getCamera()
        hangarCamera.forceUpdate()
        self.goalPosition = hangarCamera.position

    def getPitchMultiplier(self):
        pass

    def __update(self):
        self.__updateCameraLocation()
        isCameraDone = (self.goalPosition - BigWorld.camera().position).length < self.UPDATE_CAMERA_DS
        if isCameraDone:
            self.stopCallback(self.__update)
            self.__finishCameraMovement()
        else:
            return self.UPDATE_CALLBACK_DT

    def __updateCameraLocation(self):
        position = self.__interpolateValue(self.__camera.getWorldMatrix().translation, self.goalPosition)
        yaw = self.__interpolateValue(self.__camera.getWorldMatrix().yaw, self.goalYaw)
        pitch = self.__interpolateValue(self.__camera.getWorldMatrix().pitch, self.goalPitch)
        mat = mathUtils.createRTMatrix(Math.Vector3(yaw, pitch, 0.0), position)
        self.__camera.setWorldMatrix(mat)

    def __interpolateValue(self, currentValue, goalValue):
        delta = goalValue - currentValue
        return currentValue + delta * self.UPDATE_CAMERA_MULTIPLIER * self.UPDATE_CALLBACK_DT

    def __finishCameraMovement(self):
        self.state = CameraMovementStates.ON_OBJECT
        self.__camera.disable()
        self.setCursorCameraDistance()
        BigWorld.camera(HangarSpace.g_hangarSpace.space.getCamera())
        if self.__cameraDoneCallback is not None:
            self.__cameraDoneCallback()
            self.__cameraDoneCallback = None
        return

    def setCursorCameraDistance(self):
        HangarSpace.g_hangarSpace.space.setCameraDistance(self.goalDistance)

    def onReleased(self):
        ClientSelectableObject.onReleased(self)
        ClientSelectableCameraObject.switchCamera(self)
