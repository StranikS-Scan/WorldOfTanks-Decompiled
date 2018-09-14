# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ClientSelectableCameraObject.py
import BigWorld
import math
import Math
from ClientSelectableObject import ClientSelectableObject
from helpers.CallbackDelayer import CallbackDelayer
from AvatarInputHandler import cameras, mathUtils
import ChristmassTreeManager as _ctm
import WWISE

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
        self.goalDistance = Math.Vector2(0.0, 0.0)
        self.goalTarget = Math.Vector3(0.0, 0.0, 0.0)
        self.shift = Math.Vector3(self.camera_shift_x, self.camera_shift_y, self.camera_shift_z)
        if self.enable_yaw_limits:
            self.yawLimits = Math.Vector2(self.yaw_limit_min, self.yaw_limit_max)
        else:
            self.yawLimits = None
        self.pitchLimits = Math.Vector2(math.degrees(self.pitch_limit_min), math.degrees(self.pitch_limit_max))
        self.__hackPivot()
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
                try:
                    if cameraObject.isRoot:
                        clickedObject = cameraObject
                        break
                except:
                    break

        if clickedObject is None:
            return
        elif clickedObject.state != CameraMovementStates.FROM_OBJECT:
            return
        else:
            if _ctm.isTreeEntity(clickedObject) or _ctm.isTankEntity(clickedObject):
                WWISE.WW_setRTCPGlobal('RTPC_ext_ev_christmas_tree_decorating', 1)
            else:
                WWISE.WW_setRTCPGlobal('RTPC_ext_ev_christmas_tree_decorating', 0)
            for cameraObject in ClientSelectableCameraObject.allCameraObjects:
                if cameraObject.state != CameraMovementStates.FROM_OBJECT:
                    cameraObject.onDeselect()

            clickedObject.onSelect(callback)
            return

    @staticmethod
    def onSettingsChanged():
        for cameraObject in ClientSelectableCameraObject.allCameraObjects:
            cameraObject.delayCallback(0.01, cameraObject.onSettingChanged)

    def onSettingChanged(self):
        self.__hackPivot()
        if self.state == CameraMovementStates.ON_OBJECT or self.state == CameraMovementStates.MOVING_TO_OBJECT:
            self.setStartValues()
            self._teleportHangarSpaceCamera(True)

    CONST_UI_WIDTH = 480.0
    CONST_RATIO_DELTA = 0.05

    def __hackPivot(self):
        if self.hack_enabled:
            res = BigWorld.wg_getCurrentResolution(True)
            currentRatio = (res[0] - self.CONST_UI_WIDTH) / res[1]
            if currentRatio <= self.hacked_ratio:
                dR = self.hacked_ratio - currentRatio
                dP = min(1.0, dR / self.CONST_RATIO_DELTA) * (self.hacked_pivot_x - self.camera_pivot_x)
                self.goalPivot.x = self.camera_pivot_x + dP
            else:
                self.goalPivot.x = self.camera_pivot_x

    def onSelect(self, callback=None):
        self.enable(False)
        self.state = CameraMovementStates.MOVING_TO_OBJECT
        self.__startCameraMovement()
        self.__cameraDoneCallback = callback
        self.delayCallback(self.UPDATE_CALLBACK_DT, self.__update)

    def onDeselect(self):
        self.state = CameraMovementStates.FROM_OBJECT
        self.stopCallback(self.__update)
        self.__cameraDoneCallback = None
        self.enable(True)
        return

    def setStartValues(self):
        size = max(self.camera_object_width / BigWorld.getAspectRatio(), self.model.height)
        size /= 2.0 * self.camera_object_aspect
        self.goalDistance[0] = size / math.tan(BigWorld.projection().fov / 2.0)
        self.goalDistance[1] = self.goalDistance[0] * self.camera_max_distance_multiplier
        self.goalTarget = Math.Matrix(self.model.matrix).translation + self.shift

    def __startCameraMovement(self):
        self.setStartValues()
        camera = BigWorld.camera()
        startMatrix = Math.Matrix(camera.matrix)
        self._teleportHangarSpaceCamera()
        self.__camera.enable(startMatrix)

    def _teleportHangarSpaceCamera(self, useCurrentAngles=False):
        from gui.shared.utils.HangarSpace import g_hangarSpace
        clientSpace = g_hangarSpace.space
        constr = clientSpace.getCameraLocation()['camConstraints']
        constr[0] = self.pitchLimits
        if self.enable_yaw_limits:
            constr[1] = self.yawLimits
        else:
            constr[1] = Math.Vector2(-math.pi, math.pi)
        yaw = pitch = None
        if not useCurrentAngles:
            yaw = self.goalYaw
            pitch = -1 * self.goalPitch
        clientSpace.setCameraLocation(self.goalTarget, self.goalPivot, yaw, pitch, (self.goalDistance[0] + self.goalDistance[1]) * 0.5, constr, True)
        hangarCamera = clientSpace.getCamera()
        hangarCamera.forceUpdate()
        self.goalPosition = hangarCamera.position
        self.setCursorCameraDistance()
        return

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
        from gui.shared.utils.HangarSpace import g_hangarSpace
        BigWorld.camera(g_hangarSpace.space.getCamera())
        if self.__cameraDoneCallback is not None:
            self.__cameraDoneCallback()
            self.__cameraDoneCallback = None
        return

    def setCursorCameraDistance(self):
        from gui.shared.utils.HangarSpace import g_hangarSpace
        g_hangarSpace.space.setCameraDistance(self.goalDistance[0], self.goalDistance[1])
