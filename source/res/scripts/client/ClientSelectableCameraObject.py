# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ClientSelectableCameraObject.py
import BigWorld
import math
import Math
from ClientSelectableObject import ClientSelectableObject
from helpers.CallbackDelayer import CallbackDelayer, TimeDeltaMeter
from AvatarInputHandler import cameras, mathUtils
from gui.shared.utils.HangarSpace import g_hangarSpace
from gui.shared import event_dispatcher as shared_events
from gui.Scaleform.Waiting import Waiting
import SoundGroups

class CameraMovementStates:
    ON_OBJECT = 0
    MOVING_TO_OBJECT = 1
    FROM_OBJECT = 2


def normalizeAngle(angle):
    return angle if angle >= 0 else angle + 2 * math.pi


class ClientSelectableCameraObject(ClientSelectableObject, CallbackDelayer, TimeDeltaMeter):
    allCameraObjects = list()
    UPDATE_CAMERA_DS = 0.01
    UPDATE_CAMERA_MULTIPLIER = 5.0
    ON_CAMERA_MOVEMENT_SOUND_NAME = 'hangar_h15_whoosh'
    ON_SELECT_SOUND_NAME = ''
    ON_DESELECT_SOUND_NAME = 'hangar_h15_sabaton_music_pause'

    def __init__(self):
        ClientSelectableObject.__init__(self)
        CallbackDelayer.__init__(self)
        TimeDeltaMeter.__init__(self)
        self.__state = CameraMovementStates.FROM_OBJECT
        self.isRoot = False
        self.__camera = cameras.FreeCamera()
        self.__cameraDoneCallback = None
        self.goalPosition = Math.Vector3(0.0, 0.0, 0.0)
        self.cameraPitch = mathUtils.clamp(-math.pi / 2.0 * 0.99, math.pi / 2.0 * 0.99, -1.0 * self.cameraPitch)
        self.cameraYaw = normalizeAngle(self.cameraYaw)
        self.cameraPivot = Math.Vector3(self.cameraPivotX, self.cameraPivotY, self.cameraPivotZ)
        self.goalDistance = Math.Vector2(0.0, 0.0)
        self.goalTarget = Math.Vector3(0.0, 0.0, 0.0)
        self.yawLimits = Math.Vector2(self.yawLimitMin, self.yawLimitMax)
        self.pitchLimits = Math.Vector2(math.degrees(self.pitchLimitMin), math.degrees(self.pitchLimitMax))
        self.__sounds = dict()
        self.__wasPreviousUpdateSkipped = False
        self.enable(True)
        return

    def onEnterWorld(self, prereqs):
        ClientSelectableObject.onEnterWorld(self, prereqs)
        ClientSelectableCameraObject.allCameraObjects.append(self)
        self.__initSounds()

    def __initSounds(self):
        if self.ON_CAMERA_MOVEMENT_SOUND_NAME:
            self.__sounds[CameraMovementStates.MOVING_TO_OBJECT] = SoundGroups.g_instance.getSound2D(self.ON_CAMERA_MOVEMENT_SOUND_NAME)
        if self.ON_SELECT_SOUND_NAME:
            self.__sounds[CameraMovementStates.ON_OBJECT] = SoundGroups.g_instance.getSound2D(self.ON_SELECT_SOUND_NAME)
        if self.ON_DESELECT_SOUND_NAME:
            self.__sounds[CameraMovementStates.FROM_OBJECT] = SoundGroups.g_instance.getSound2D(self.ON_DESELECT_SOUND_NAME)

    def onLeaveWorld(self):
        ClientSelectableCameraObject.allCameraObjects.remove(self)
        self.stopCallback(self.__update)
        if self.__camera == BigWorld.camera():
            BigWorld.camera(None)
            BigWorld.worldDrawEnabled(False)
        self.__camera.destroy()
        self.__camera = None
        for sound in self.__sounds.itervalues():
            sound.stop()

        self.__sounds.clear()
        ClientSelectableObject.onLeaveWorld(self)
        CallbackDelayer.destroy(self)
        return

    def _setState(self, state):
        if self.__state != state:
            self.__playSoundForState(state)
            self.enable(state == CameraMovementStates.FROM_OBJECT)
            self.__state = state

    def __playSoundForState(self, state):
        if state in self.__sounds:
            sound = self.__sounds[state]
            if not sound.isPlaying:
                sound.play()

    @property
    def state(self):
        return self.__state

    def onReleased(self):
        ClientSelectableCameraObject.switchCamera(self)

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
            for cameraObject in ClientSelectableCameraObject.allCameraObjects:
                if cameraObject.state != CameraMovementStates.FROM_OBJECT:
                    cameraObject.onDeselect()

            clickedObject.onSelect(callback)
            return

    def onSelect(self, callback=None):
        self._setState(CameraMovementStates.MOVING_TO_OBJECT)
        self._callOnSelectEvent()
        self.__startCameraMovement()
        self.__cameraDoneCallback = callback
        self.measureDeltaTime()
        self.delayCallback(0.0, self.__update)

    def onDeselect(self):
        self._setState(CameraMovementStates.FROM_OBJECT)
        self.stopCallback(self.__update)
        self.__cameraDoneCallback = None
        self.enable(True)
        return

    def _callOnSelectEvent(self):
        shared_events.showSabatonVehiclePreview()

    def setStartValues(self):
        size = self.model.height / (2.0 * self.cameraObjectAspect)
        self.goalDistance[0] = size / math.tan(BigWorld.projection().fov / 2.0)
        self.goalDistance[1] = self.cameraMaxDistance
        self.goalTarget = Math.Matrix(self.model.matrix).translation

    def __startCameraMovement(self):
        self.setStartValues()
        startMatrix = Math.Matrix(BigWorld.camera().matrix)
        self.__teleportHangarSpaceCamera()
        self.__camera.enable(startMatrix)
        self.__wasPreviousUpdateSkipped = False

    def __teleportHangarSpaceCamera(self):
        clientSpace = g_hangarSpace.space
        constr = clientSpace.getCameraLocation()['camConstraints']
        constr.pitchLimits = self.pitchLimits
        constr.yawLimits = self.yawLimits
        yaw = self.cameraYaw
        pitch = -1.0 * self.cameraPitch
        clientSpace.setCameraLocation(self.goalTarget, self.cameraPivot, yaw, pitch, (self.goalDistance[0] + self.goalDistance[1]) * 0.5, constr, True)
        hangarCamera = clientSpace.getCamera()
        hangarCamera.forceUpdate()
        self.goalPosition = hangarCamera.position
        self.setCursorCameraDistance()

    def __update(self):
        isUpdateSkipped = Waiting.isVisible()
        if isUpdateSkipped or self.__wasPreviousUpdateSkipped:
            self.__wasPreviousUpdateSkipped = isUpdateSkipped
            self.measureDeltaTime()
            return 0.0
        self.__updateCameraLocation()
        isCameraDone = (self.goalPosition - BigWorld.camera().position).length < self.UPDATE_CAMERA_DS
        if isCameraDone:
            self.stopCallback(self.__update)
            self.__finishCameraMovement()
        else:
            return 0.0

    def __updateCameraLocation(self):
        dt = self.measureDeltaTime()
        position = self.__interpolateValue(self.__camera.getWorldMatrix().translation, self.goalPosition, dt)
        yaw = self.__interpolateValue(normalizeAngle(self.__camera.getWorldMatrix().yaw), self.cameraYaw, dt)
        pitch = self.__interpolateValue(self.__camera.getWorldMatrix().pitch, self.cameraPitch, dt)
        mat = mathUtils.createRTMatrix(Math.Vector3(yaw, pitch, 0.0), position)
        self.__camera.setWorldMatrix(mat)

    def __interpolateValue(self, currentValue, goalValue, dt):
        delta = goalValue - currentValue
        return currentValue + delta * self.UPDATE_CAMERA_MULTIPLIER * dt

    def __finishCameraMovement(self):
        self._setState(CameraMovementStates.ON_OBJECT)
        self.__camera.disable()
        BigWorld.camera(g_hangarSpace.space.getCamera())
        if self.__cameraDoneCallback is not None:
            self.__cameraDoneCallback()
            self.__cameraDoneCallback = None
        return

    def setCursorCameraDistance(self):
        g_hangarSpace.space.setCameraDistance(self.goalDistance[0], self.goalDistance[1])
