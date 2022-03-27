# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/DynamicCameras/main_tank_commander_camera.py
import time
import typing
import weakref
from functools import wraps
import math
import Keys
import BigWorld
import Math
import GUI
import math_utils
from AvatarInputHandler.cameras import ICamera, readFloat, readBool
from Math import Vector3
from constants import CollisionFlags
from gui.Scaleform.managers.cursor_mgr import CursorManager
from gui.battle_control.controllers.commander.common import MappedKeys
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer, TimeDeltaMeter
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.commander.proxies.vehicle import _ProxyVehicle
_TWO_PI = 2.0 * math.pi
_OFF_SCREEN_MOVE_COEF_OFFSET = 0.95
_DEFAULT_COLLISION_EVADE_LIMIT = 150
EXCLUDE_UI_ELEMENTS = ('fragCorrelationBar', 'debugPanel', 'battleTimer')

def angleToRadian(angle):
    return angle * math.pi / 180.0


FLOAT_DECIMAL_PLACE = 5
ANGLE_ACCURACY = angleToRadian(2)
ART_STATE_PITCH = angleToRadian(-89)
ART_STATE_YAW = 0

def getCameraAsSettingsHolder(settingsDataSec):
    return CommanderCamera(settingsDataSec)


class CommanderCameraState(object):

    def __init__(self, commanderCamera):
        self.activeControllers = []
        self.commanderCamera = commanderCamera

    def start(self):
        pass

    def stop(self):
        pass

    def update(self, dt):
        for controller in self.activeControllers:
            controller.update(dt)

    def handleKeyEvent(self, isDown, key, mods, event=None):
        res = False
        for controller in self.activeControllers:
            res |= controller.handleKeyEvent(isDown, key, mods, event)

        return res

    def handleMouseEvent(self, dx, dy, dz):
        res = False
        for controller in self.activeControllers:
            res |= controller.handleMouseEvent(dx, dy, dz)

        return res

    def handleMouseWheel(self, delta):
        res = False
        for controller in self.activeControllers:
            res |= controller.handleMouseWheel(delta)

        return res

    def transitionEnded(self, target, yaw, pitch):
        pass


class CommanderCameraStateNormal(CommanderCameraState):

    def __init__(self, commanderCamera):
        super(CommanderCameraStateNormal, self).__init__(commanderCamera)
        self.activeControllers = [commanderCamera.horizontalMoveController, commanderCamera.rotationController, commanderCamera.zoomController]

    def transitionEnded(self, target, yaw, pitch):
        self.commanderCamera.rotationController.setYaw(yaw, False)
        self.commanderCamera.rotationController.setPitch(pitch, False)
        self.commanderCamera.zoomController.currentHeight = target.y
        self.commanderCamera.zoomController.desiredHeight = self.commanderCamera.zoomController.currentHeight


class CommanderCameraStateTransition(CommanderCameraState):

    def __init__(self, commanderCamera):
        super(CommanderCameraStateTransition, self).__init__(commanderCamera)
        self.activeControllers = [commanderCamera.transitionController]


class CommanderCameraStateArt(CommanderCameraState):
    appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, commanderCamera):
        super(CommanderCameraStateArt, self).__init__(commanderCamera)
        self.activeControllers = [commanderCamera.horizontalMoveController]

    def update(self, dt):
        super(CommanderCameraStateArt, self).update(dt)
        if self.appLoader.getApp().cursorMgr and not GUI.mcursor().visible:
            self.appLoader.getApp().cursorMgr.attachCursor()


class CommanderCamera(ICamera, CallbackDelayer, TimeDeltaMeter):
    appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, dataSec):
        CallbackDelayer.__init__(self)
        TimeDeltaMeter.__init__(self, time.clock)
        self.__cam = BigWorld.CursorCamera()
        self.transitionController = None
        self.horizontalMoveController = None
        self.rotationController = None
        self.zoomController = None
        self.__checkAngleTimerID = None
        self._translationMatrix = None
        self._initialRotation = Math.Vector3()
        self._moveUpOffset = 0
        self._moveUpHeight = 0
        self._moveUpPitch = 0
        self._stopVehicleControlOffset = 0
        self._stopVehicleControlHeight = 0
        self._stopVehicleControlPitch = 0
        self._focusOnPointOffset = 0
        self._focusOnPointHeight = 0
        self._focusOnPointPitch = 0
        self._flyTime = 0
        self._maxCameraHeight = 0
        self.__artStateHeight = 0
        self._maxAngleToCenterBehindSpace = 0
        self._moveToCenterPause = 0
        self._cfg = dict()
        self.__readCfg(dataSec)
        self._curState = None
        self._stateAfterTransition = None
        return

    def __del__(self):
        if self.__checkAngleTimerID is not None:
            BigWorld.cancelCallback(self.__checkAngleTimerID)
        return

    @property
    def camera(self):
        return self.__cam

    @property
    def config(self):
        return self._cfg

    @property
    def translationMatrix(self):
        return self._translationMatrix

    @translationMatrix.setter
    def translationMatrix(self, value):
        self.camera.target = value

    @property
    def rotationMatrix(self):
        return self.camera.source

    @rotationMatrix.setter
    def rotationMatrix(self, value):
        self.__cam.source = value

    def enableHorizontalMovement(self, enable):
        if self.horizontalMoveController:
            self.horizontalMoveController.setEnabled(enable)

    def setDefault(self):
        self.rotationController.setYaw(self._initialRotation.z, smoothly=True)
        self.rotationController.update(0, True)

    def setArtMode(self):
        self.moveToArtState()

    def isArtState(self):
        res = isinstance(self._curState, CommanderCameraStateArt)
        return res

    def isTransitionState(self):
        res = isinstance(self._curState, CommanderCameraStateTransition)
        return res

    def setNormalMode(self):
        self._setState(CommanderCameraStateNormal(self))

    def transitionEnded(self, target, yaw, pitch):
        if self._stateAfterTransition:
            self._stateAfterTransition.transitionEnded(target, yaw, pitch)
            self._setState(self._stateAfterTransition)
            self._stateAfterTransition = None
        else:
            state = CommanderCameraStateNormal(self)
            state.transitionEnded(target, yaw, pitch)
            self._setState(state)
        return

    def destroy(self):
        CallbackDelayer.destroy(self)
        self.disable()
        self.__cam = None
        return

    def enable(self, targetPos, initialRotation):
        self.measureDeltaTime()
        self._setupCamera(Vector3(targetPos.x, targetPos.y, targetPos.z), rotation=initialRotation)
        self._setupControllers()
        self._setState(CommanderCameraStateNormal(self))
        self.__cameraUpdate()
        self.delayCallback(0.0, self.__cameraUpdate)

    def disable(self):
        cursorMgr = CommanderCamera.appLoader.getApp().cursorMgr
        if cursorMgr is not None:
            cursorMgr.setCursorForced(CursorManager.ARROW)
        self.stopCallback(self.__cameraUpdate)
        self.translationMatrix = None
        self.rotationMatrix = None
        if self.__checkAngleTimerID is not None:
            BigWorld.cancelCallback(self.__checkAngleTimerID)
            self.__checkAngleTimerID = None
        BigWorld.camera(None)
        self._setState(None)
        self.horizontalMoveController = None
        self.rotationController = None
        self.zoomController = None
        self.transitionController = None
        return

    def handleKeyEvent(self, isDown, key, mods, event=None):
        return self._curState.handleKeyEvent(isDown, key, mods, event)

    def handleMouseEvent(self, dx, dy, dz):
        return self._curState.handleMouseEvent(dx, dy, dz)

    def handleMouseWheel(self, delta):
        return self._curState.handleMouseWheel(delta)

    def teleport(self, pos):
        self.horizontalMoveController.resetMovement(True)
        camPos = self.translationMatrix.translation
        if camPos.y > pos.y:
            pos.y = camPos.y
        targetTerrainHeight = getTerrainHeightAt(pos)
        if targetTerrainHeight >= pos.y:
            camTerrainHeight = getTerrainHeightAt(camPos)
            pos.y = min(targetTerrainHeight + camPos.y - camTerrainHeight, self._maxCameraHeight)
        self.moveTo(pos, self.__cam.source.yaw, self.__cam.source.pitch, self._flyTime)

    def teleportWithFocusOnPoint(self, pos):
        self.moveToPosWithParams(pos, self.__cam.source.yaw, self._focusOnPointPitch, self._focusOnPointOffset, self._focusOnPointHeight)

    def moveTo(self, pos, yaw, pitch, duration):
        self.horizontalMoveController.resetMovement(True)
        self.zoomController.reset()
        self.transitionController.start(pos, yaw, pitch, duration)
        self._setState(CommanderCameraStateTransition(self))

    def moveToPos(self, pos, yaw):
        self.moveToPosWithParams(pos, yaw, self._stopVehicleControlPitch, self._stopVehicleControlOffset, self._stopVehicleControlHeight)

    def moveToPosWithParams(self, pos, yaw, pitch, offset, height):
        if self.isTransitionState():
            return
        if self.isArtState():
            camPos = Math.Vector3(pos.x, self.__artStateHeight, pos.z)
            self._stateAfterTransition = CommanderCameraStateArt(self)
            self.moveTo(camPos, ART_STATE_YAW, ART_STATE_PITCH, self._flyTime)
        else:
            lookDirection = Math.Vector3(math.sin(yaw), 0.0, math.cos(yaw))
            camPos = pos - lookDirection * offset
            camPos.y = min(height + pos.y, self._maxCameraHeight)
            self.moveTo(camPos, yaw, pitch, self._flyTime)

    def moveToVehicle(self, vehicle):
        if vehicle is None or not vehicle.isAlive or self.isTransitionState():
            return
        else:
            turretYaw, _ = vehicle.aimParams
            gunYaw = vehicle.yaw + turretYaw
            self.moveToPos(vehicle.position, gunYaw)
            return

    def moveUp(self):
        lookDirection = Math.Vector3(math.sin(self.__cam.source.yaw), 0.0, math.cos(self.__cam.source.yaw))
        camPos = self.__cam.target.translation - lookDirection * self._moveUpOffset
        camPos.y = min(camPos.y + self._moveUpHeight, self._maxCameraHeight)
        self._stateAfterTransition = None
        self.moveTo(camPos, self.__cam.source.yaw, self._moveUpPitch, self._flyTime)
        return

    def moveToArtState(self):
        camPos = self.__cam.target.translation
        camPos.y = self.__artStateHeight
        self._stateAfterTransition = CommanderCameraStateArt(self)
        self.moveTo(camPos, ART_STATE_YAW, ART_STATE_PITCH, self._flyTime)

    def liftUnder(self, targetPos, targetYaw):
        lookDirection = Math.Vector3(math.sin(targetYaw), 0.0, math.cos(targetYaw))
        camPos = targetPos - lookDirection * self._stopVehicleControlOffset
        camPos.y = min(self._stopVehicleControlHeight + targetPos.y, self._maxCameraHeight)
        self.zoomController.currentHeight = self._stopVehicleControlHeight
        self.zoomController.desiredHeight = self._stopVehicleControlHeight
        self.translationMatrix.setTranslate(camPos)
        self.rotationController.setYaw(targetYaw, False)
        self.rotationController.setPitch(self._stopVehicleControlPitch, False)

    def liftUnderArtMode(self, targetPos, targetYaw):
        self.horizontalMoveController.resetMovement(True)
        camPos = Math.Vector3(targetPos.x, self.__artStateHeight, targetPos.z)
        self.translationMatrix.setTranslate(camPos)
        self.rotationMatrix.setRotateYPR(Vector3(ART_STATE_YAW, ART_STATE_PITCH, 0))
        self._setState(CommanderCameraStateArt(self))

    def reload(self, cameraSec):
        self.__readCfg(cameraSec)
        self.horizontalMoveController.init()
        self.rotationController.init(self._initialRotation)
        self.zoomController.init()

    def _setupCamera(self, position, rotation):
        self._initialRotation = rotation
        self.__cam.source = math_utils.createRotationMatrix(rotation)
        self.__cam.target = math_utils.createTranslationMatrix(position)
        boundingBoxExtension = BigWorld.player().arena.arenaType.boundingBoxExtension
        if boundingBoxExtension is None:
            boundingBoxExtension = 0
        self._levelBoundingBox = BigWorld.player().arena.arenaType.boundingBox
        extendedBoundingBox = (self._levelBoundingBox[0] - Math.Vector2(boundingBoxExtension, boundingBoxExtension), self._levelBoundingBox[1] + Math.Vector2(boundingBoxExtension, boundingBoxExtension))
        self._translationMatrix = MatrixWithTranslationBBRestriction(self.camera.target, extendedBoundingBox)
        self.__cam.pivotMaxDist = 0.0
        self.__cam.maxDistHalfLife = 0.01
        self.__cam.movementHalfLife = 0.0
        self.__cam.turningHalfLife = -1
        self.__cam.pivotPosition = Math.Vector3(0.0, 0.0, 0.0)
        BigWorld.camera(self.__cam)
        return

    def _setupControllers(self):
        self.horizontalMoveController = HorizontalMoveController(self._cfg, self.camera, self._translationMatrix)
        self.horizontalMoveController.init()
        self.horizontalMoveController.setMovementUpdateCallback(self.__movementUpdatedCallback)
        self.rotationController = RotationController(self._cfg, self.camera, self._translationMatrix)
        self.rotationController.init(self._initialRotation)
        self.rotationController.setMovementUpdateCallback(self.__movementUpdatedCallback)
        self.zoomController = ZoomController(self._cfg, self.camera, self._translationMatrix)
        self.zoomController.init()
        self.zoomController.setMovementUpdateCallback(self.__movementUpdatedCallback)
        self.transitionController = TransitionController(self._cfg, self.camera, self._translationMatrix)
        self.transitionController.setMovementUpdateCallback(self.__movementUpdatedCallback)
        self.transitionController.setEndTransitionCallback(self.transitionEnded)

    def _setState(self, state):
        if self._curState is not None:
            self._curState.stop()
        self._curState = state
        if self._curState is not None:
            self._curState.start()
        return

    def __movementUpdatedCallback(self):
        if self.__checkAngleTimerID is not None:
            BigWorld.cancelCallback(self.__checkAngleTimerID)
        self.__checkAngleTimerID = BigWorld.callback(self._moveToCenterPause, self.__checkAngle)
        return

    def __checkAngle(self):
        self.__checkAngleTimerID = None
        if self.__cam is None:
            return
        elif self.isArtState():
            return
        else:
            camPos = self.__cam.target.translation
            if camPos.x > self._levelBoundingBox[0].x and camPos.x < self._levelBoundingBox[1].x and camPos.z > self._levelBoundingBox[0].y and camPos.z < self._levelBoundingBox[1].y:
                return
            lookDirection = Math.Vector3(math.sin(self.__cam.source.yaw), 0.0, math.cos(self.__cam.source.yaw))
            lookDirection.normalise()
            dirToCenter = -self.__cam.target.translation
            dirToCenter.normalise()
            dot = lookDirection.dot(dirToCenter)
            dot = math_utils.clamp(-0.999999999999, 0.999999999999, dot)
            yawDist = math.acos(dot)
            yawDiff = yawDist - self._maxAngleToCenterBehindSpace
            if yawDiff > 0 and yawDiff > ANGLE_ACCURACY:
                if lookDirection.cross2D(dirToCenter) > 0:
                    yawDiff = -yawDiff
                self.moveTo(self.__cam.target.translation, self.__cam.source.yaw + round(yawDiff, FLOAT_DECIMAL_PLACE), self.__cam.source.pitch, self._flyTime)
            return

    def __cameraUpdate(self):
        delta = self.measureDeltaTime()
        if delta > 1.0:
            delta = 0.0
        self._curState.update(delta)

    def __readCfg(self, dataSec):
        self._cfg.clear()
        self._cfg['horizontal_speed_low'] = readFloat(dataSec, 'horizontal_speed_low', 0, 1000, 40)
        self._cfg['horizontal_speed_height'] = readFloat(dataSec, 'horizontal_speed_height', 0, 1000, 200)
        self._cfg['horizontal_acceleration_speed_low'] = readFloat(dataSec, 'horizontal_acceleration_speed_low', 0, 1000, 40)
        self._cfg['horizontal_acceleration_speed_height'] = readFloat(dataSec, 'horizontal_acceleration_speed_height', 0, 1000, 40)
        self._cfg['horizontal_deacceleration_speed_low'] = readFloat(dataSec, 'horizontal_deacceleration_speed_low', 0, 1000, 40)
        self._cfg['horizontal_deacceleration_speed_height'] = readFloat(dataSec, 'horizontal_deacceleration_speed_height', 0, 1000, 40)
        self._cfg['min_camera_height'] = readFloat(dataSec, 'min_camera_height', 0, 1000, 20)
        self._cfg['max_camera_height'] = readFloat(dataSec, 'max_camera_height', 0, 1000, 150)
        self._cfg['camera_start_offset'] = readFloat(dataSec, '', minVal=0, maxVal=1000, defaultVal=20)
        self._cfg['max_collision_evade_limit'] = readFloat(dataSec, 'max_collision_evade_limit', 10, 1000, _DEFAULT_COLLISION_EVADE_LIMIT)
        self._cfg['top_down_mode_height'] = readFloat(dataSec, 'top_down_mode_height', 0, 1000, 150)
        self._cfg['tank_commander_mode_enter_animation'] = readBool(dataSec, 'tank_commander_mode_enter_animation', True)
        rtsMinMaxCameraHeightOffset = BigWorld.player().arena.arenaType.rtsMinMaxCameraHeightOffset
        if rtsMinMaxCameraHeightOffset is not None:
            self._cfg['min_camera_height'] += rtsMinMaxCameraHeightOffset
            self._cfg['max_camera_height'] += rtsMinMaxCameraHeightOffset
            self._cfg['top_down_mode_height'] += rtsMinMaxCameraHeightOffset
        self._cfg['rotation_mouse_angle_speed'] = readFloat(dataSec, 'rotation_mouse_angle_speed', 0, 1000, 100)
        self._cfg['rotation_half_life'] = readFloat(dataSec, 'rotation_half_life', 0, 1000, 100)
        self._cfg['scroll_sensitivity'] = readFloat(dataSec, 'scroll_sensitivity', 0, 100, 40)
        self._cfg['scroll_stop_time'] = readFloat(dataSec, 'scroll_stop_time', 0, 10, 0.6)
        self._cfg['max_camera_pitch'] = readFloat(dataSec, 'max_camera_pitch', -1000, 1000, -65)
        self._cfg['min_camera_pitch'] = readFloat(dataSec, 'min_camera_pitch', -1000, 1000, 0)
        self._cfg['max_mouse_camera_pitch'] = readFloat(dataSec, 'max_mouse_camera_pitch', -1000, 1000, 100)
        self._cfg['min_mouse_camera_pitch'] = readFloat(dataSec, 'min_mouse_camera_pitch', -1000, 1000, 100)
        self._cfg['edge_pen_screen_coef'] = readFloat(dataSec, 'edge_pen_screen_coef', 0, 1, 0.99)
        self._cfg['disable_enge_pen_on_gui_elements'] = readBool(dataSec, 'disable_enge_pen_on_gui_elements', False)
        self._cfg['max_angle_to_center_behind_space'] = readFloat(dataSec, 'max_angle_to_center_behind_space', 0, 180, 20)
        self._cfg['move_to_center_pause'] = readFloat(dataSec, 'move_to_center_pause', 0, 60, 3)
        self._cfg['move_up_offset'] = readFloat(dataSec, 'move_up_offset', 0, 1000, 150)
        self._cfg['move_up_height'] = readFloat(dataSec, 'move_up_height', 0, 1000, 150)
        self._cfg['move_up_pitch'] = readFloat(dataSec, 'move_up_pitch', -170, -1, -55)
        self._cfg['stop_vehicle_control_offset'] = readFloat(dataSec, 'stop_vehicle_control_offset', 0, 1000, 150)
        self._cfg['stop_vehicle_control_height'] = readFloat(dataSec, 'stop_vehicle_control_height', 0, 1000, 150)
        self._cfg['stop_vehicle_control_pitch'] = readFloat(dataSec, 'stop_vehicle_control_pitch', -170, -1, -55)
        self._cfg['focus_on_point_offset'] = readFloat(dataSec, 'focus_on_point_offset', 0, 1000, 150)
        self._cfg['focus_on_point_height'] = readFloat(dataSec, 'focus_on_point_height', 0, 1000, 150)
        self._cfg['focus_on_point_pitch'] = readFloat(dataSec, 'focus_on_point_pitch', -170, -1, -89)
        self._cfg['fly_time'] = readFloat(dataSec, 'fly_time', 0, 100, 1)
        self._moveUpOffset = self._cfg['move_up_offset']
        self._moveUpHeight = min(self._cfg['move_up_height'], self._cfg['max_camera_height'])
        self._moveUpPitch = math_utils.clamp(self._cfg['min_camera_pitch'], self._cfg['max_camera_pitch'], self._cfg['move_up_pitch'])
        self._moveUpPitch = angleToRadian(self._moveUpPitch)
        self._stopVehicleControlOffset = self._cfg['stop_vehicle_control_offset']
        self._stopVehicleControlHeight = min(self._cfg['stop_vehicle_control_height'], self._cfg['max_camera_height'])
        self._stopVehicleControlPitch = math_utils.clamp(self._cfg['min_camera_pitch'], self._cfg['max_camera_pitch'], self._cfg['stop_vehicle_control_pitch'])
        self._stopVehicleControlPitch = angleToRadian(self._stopVehicleControlPitch)
        self._focusOnPointOffset = self._cfg['focus_on_point_offset']
        self._focusOnPointHeight = min(self._cfg['focus_on_point_height'], self._cfg['max_camera_height'])
        self._focusOnPointPitch = math_utils.clamp(self._cfg['min_camera_pitch'], self._cfg['max_camera_pitch'], self._cfg['focus_on_point_pitch'])
        self._focusOnPointPitch = angleToRadian(self._focusOnPointPitch)
        self._flyTime = self._cfg['fly_time']
        self._maxCameraHeight = self._cfg['max_camera_height']
        self.__artStateHeight = self._cfg['top_down_mode_height']
        self._maxAngleToCenterBehindSpace = angleToRadian(self._cfg['max_angle_to_center_behind_space'])
        self._moveToCenterPause = self._cfg['move_to_center_pause']
        return


class BaseMoveController(object):
    appLoader = dependency.descriptor(IAppLoader)
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, cfg, camera, translationMatrix):
        super(BaseMoveController, self).__init__()
        self._camera = camera
        self._translationMatrix = translationMatrix
        self._cfg = cfg
        self._movementUpdatedCallback = None
        self._maxCollisionEvadeLimit = _DEFAULT_COLLISION_EVADE_LIMIT
        return

    def setMovementUpdateCallback(self, callback):
        self._movementUpdatedCallback = callback

    def movementUpdated(self):
        if self._movementUpdatedCallback:
            self._movementUpdatedCallback()
            rtsCommander = self._sessionProvider.dynamic.rtsCommander
            rtsCommander.onCameraPositionChanged(self._translationMatrix.translation)

    @property
    def config(self):
        return self._cfg

    @property
    def camera(self):
        return self._camera

    @property
    def translationMatrix(self):
        return self._translationMatrix

    @property
    def rotationMatrix(self):
        return self.camera.source

    def resetMovement(self, immediately=False):
        pass

    def handleKeyEvent(self, isDown, key, mods, event=None):
        return False

    def handleMouseEvent(self, dx, dy, dz):
        return False

    def handleMouseWheel(self, delta):
        return False

    def update(self, deltaTime):
        pass

    def init(self):
        pass


class TransitionController(BaseMoveController):

    def __init__(self, cfg, camera, translationMatrix):
        super(TransitionController, self).__init__(cfg, camera, translationMatrix)
        self._isTransition = False
        self._startTarget = None
        self._endTarget = None
        self._startYaw = 0
        self._endYaw = 0
        self._startPitch = 0
        self._endPitch = 0
        self._duration = 0
        self._curTime = 0
        self._height = 80
        self._callBackEndTransition = None
        return

    def isTransition(self):
        return self._isTransition

    def setEndTransitionCallback(self, callback=None):
        self._callBackEndTransition = callback

    def start(self, target, endYaw, endPitch, duration):
        self._startTarget = self.translationMatrix.translation
        self._endTarget = target
        self._startYaw = self.rotationMatrix.yaw
        self._endYaw = endYaw
        startVec = Math.Vector2(math.cos(self._startYaw), math.sin(self._startYaw))
        endVec = Math.Vector2(math.cos(self._endYaw), math.sin(self._endYaw))
        dot = startVec.dot(endVec)
        dot = math_utils.clamp(-0.999999999999, 0.999999999999, dot)
        self._yawDist = math.acos(dot)
        if startVec.cross2D(endVec) < 0:
            self._yawDist = -self._yawDist
        self._startPitch = self.rotationMatrix.pitch
        self._endPitch = endPitch
        self._height = self._startTarget.distTo(self._endTarget) / 10
        self._duration = duration
        self._isTransition = True
        self._curTime = 0
        self._extremumCoefficient = 0.5

    def update(self, deltaTime):
        if self._isTransition is True and self._camera is not None:
            self._curTime += deltaTime
            ratio = min(self._curTime / self._duration, 1)
            easeInRatio = math_utils.easeInQuad(ratio, 1.0, 1.0)
            ratio = math_utils.easeOutQuad(ratio, 1.0, 1.0)
            target = self._startTarget + ratio * (self._endTarget - self._startTarget)
            target.y = self._startTarget.y + easeInRatio * (self._endTarget.y - self._startTarget.y)
            yaw = self._startYaw + ratio * self._yawDist
            pitch = self._startPitch + ratio * (self._endPitch - self._startPitch)
            target = self.translationMatrix.getCorrectTranslation(target)
            terrainHeight = getTerrainHeightAt(target)
            target.y = max(terrainHeight, target.y)
            self.translationMatrix.translation = target
            self.rotationMatrix.setRotateYPR(Vector3(getNormilizedAngle(yaw), pitch, 0))
            self.movementUpdated()
            if ratio >= 1:
                self._isTransition = False
                if self._callBackEndTransition is not None:
                    self._callBackEndTransition(target, getNormilizedAngle(yaw), pitch)
        return


class HorizontalMoveController(BaseMoveController):

    def __init__(self, cfg, camera, translationMatrix):
        super(HorizontalMoveController, self).__init__(cfg, camera, translationMatrix)
        self._moveLeft = 0
        self._moveRight = 0
        self._moveForward = 0
        self._moveBackward = 0
        self._battlePage = None
        self._velocity = None
        self._isEnabled = True
        return

    def setEnabled(self, enabled):
        self._isEnabled = enabled

    @property
    def battlePage(self):
        if self._battlePage is None:
            app = self.appLoader.getApp()
            if app:
                viewsContainer = app.containerManager.getContainer(WindowLayer.VIEW)
                if viewsContainer:
                    searchCriteria = {POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.CLASSIC_BATTLE_PAGE}
                    self._battlePage = viewsContainer.getView(criteria=searchCriteria)
        return self._battlePage

    def init(self):
        super(HorizontalMoveController, self).init()
        maxSpeed = self.__dynamicLerpFunction(self.config['horizontal_speed_low'], self.config['horizontal_speed_height'])
        acceleration = self.__dynamicLerpFunction(self.config['horizontal_acceleration_speed_low'], self.config['horizontal_acceleration_speed_height'])
        deacceleration = self.__dynamicLerpFunction(self.config['horizontal_deacceleration_speed_low'], self.config['horizontal_deacceleration_speed_height'])
        self._velocity = InertialValueVector2(InertialValueWithDynamicValues(maxSpeed, acceleration, deacceleration), InertialValueWithDynamicValues(maxSpeed, acceleration, deacceleration))
        self._maxCollisionEvadeLimit = self.config['max_collision_evade_limit']

    def moveLeft(self, value):
        self._moveLeft = int(value)
        self._updateVelocityX()

    def moveRight(self, value):
        self._moveRight = -int(value)
        self._updateVelocityX()

    def moveForward(self, value):
        self._moveForward = int(value)
        self._updateVelocityY()

    def moveBackward(self, value):
        self._moveBackward = -int(value)
        self._updateVelocityY()

    def resetMovement(self, immediately=False):
        self.moveLeft(False)
        self.moveRight(False)
        self.moveForward(False)
        self.moveBackward(False)
        if immediately:
            for velocity in self._velocity:
                velocity.curValue = 0.0

    def handleKeyEvent(self, isDown, key, mods, event=None):
        self._updateMoveDirection()
        return super(HorizontalMoveController, self).handleKeyEvent(isDown, key, mods, event)

    def handleMouseEvent(self, dx, dy, dz):
        if not BigWorld.isKeyDown(Keys.KEY_MIDDLEMOUSE) and (dx or dy):
            self._updateMoveDirection()
        return super(HorizontalMoveController, self).handleMouseEvent(dx, dy, dz)

    def update(self, deltaTime):
        prevCameraPos = self.translationMatrix.translation
        self._updateVelocity(deltaTime)
        if self._isNeedUpdate():
            self._update(deltaTime)
        terrainHeight = getTerrainHeightAt(self.translationMatrix.translation)
        if terrainHeight > self._maxCollisionEvadeLimit:
            self.resetMovement(immediately=True)
            self.translationMatrix.translation = prevCameraPos
        super(HorizontalMoveController, self).update(deltaTime)

    def _updateMoveDirection(self):
        if not self._isEnabled:
            self.resetMovement(True)
            return
        isCtrlDown = BigWorld.isKeyDown(Keys.KEY_LCONTROL)
        moveLeft = not isCtrlDown and isAnyKeysDown(Keys.KEY_LEFTARROW, MappedKeys.getKey(MappedKeys.KEY_CAM_LEFT))
        moveRight = not isCtrlDown and isAnyKeysDown(Keys.KEY_RIGHTARROW, MappedKeys.getKey(MappedKeys.KEY_CAM_RIGHT))
        moveForward = not isCtrlDown and isAnyKeysDown(Keys.KEY_UPARROW, MappedKeys.getKey(MappedKeys.KEY_CAM_FORWARD))
        moveBackward = not isCtrlDown and isAnyKeysDown(Keys.KEY_DOWNARROW, MappedKeys.getKey(MappedKeys.KEY_CAM_BACK))
        mcursor = GUI.mcursor()
        if not (moveLeft or moveRight or moveForward or moveBackward) and not self._isCursorOnSomething() and mcursor.inWindow and mcursor.inFocus:
            x, y = mcursor.position
            edgeCoef = self.config['edge_pen_screen_coef'] * _OFF_SCREEN_MOVE_COEF_OFFSET
            moveLeft, moveRight = x < -edgeCoef, x > edgeCoef
            moveForward, moveBackward = y > edgeCoef, y < -edgeCoef
        self.moveLeft(moveLeft)
        self.moveRight(moveRight)
        self.moveForward(moveForward)
        self.moveBackward(moveBackward)

    def _isCursorOnSomething(self):
        if self.config['disable_enge_pen_on_gui_elements'] and self.battlePage:
            result = self.battlePage.as_isObjectUnderCursorS()
            return result is not None and result not in EXCLUDE_UI_ELEMENTS
        else:
            return False

    def _update(self, deltaTime):
        if self._sessionProvider.dynamic.rtsBWCtrl.isMouseOverUIMinimap() and not isAnyKeysDown(Keys.KEY_LEFTARROW, MappedKeys.getKey(MappedKeys.KEY_CAM_LEFT)) and not isAnyKeysDown(Keys.KEY_RIGHTARROW, MappedKeys.getKey(MappedKeys.KEY_CAM_RIGHT)) and not isAnyKeysDown(Keys.KEY_UPARROW, MappedKeys.getKey(MappedKeys.KEY_CAM_FORWARD)):
            if not isAnyKeysDown(Keys.KEY_DOWNARROW, MappedKeys.getKey(MappedKeys.KEY_CAM_BACK)):
                self._velocity.x.moveDirection = 0
                self._velocity.y.moveDirection = 0
                return
        forwardVector = Vector3(self._camera.direction.x, 0, self._camera.direction.z)
        forwardVector.normalise()
        rightVector = forwardVector * Vector3(0, 1, 0)
        rightVector.normalise()
        deltaMove = (forwardVector * self._velocity.y() + rightVector * self._velocity.x()) * deltaTime
        self.translationMatrix.translation += deltaMove
        self.movementUpdated()

    def _isNeedUpdate(self):
        return any((velocity.curValue for velocity in self._velocity))

    def _updateVelocity(self, deltaTime):
        for velocity in self._velocity:
            velocity.update(deltaTime)

    def _updateVelocityX(self):
        self._velocity.x.moveDirection = self._moveLeft + self._moveRight

    def _updateVelocityY(self):
        self._velocity.y.moveDirection = self._moveForward + self._moveBackward

    def getLerpValue(self):
        minCameraHeight = self.config['min_camera_height']
        maxCameraHeight = self.config['max_camera_height']
        heightRange = maxCameraHeight - minCameraHeight
        return (self.translationMatrix.translation.y - minCameraHeight) / heightRange

    @staticmethod
    def __divideWrapper(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            res = func(*args, **kwargs)
            return res / 2 if isAnyKeysDown(Keys.KEY_LSHIFT, Keys.KEY_RSHIFT, Keys.MODIFIER_SHIFT) else res

        return wrapper

    def __dynamicLerpFunction(self, minValue, maxValue):

        @self.__divideWrapper
        def wrapper(s=weakref.proxy(self)):
            return math_utils.lerp(minValue, maxValue, s.getLerpValue())

        return wrapper


class ZoomController(BaseMoveController):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, cfg, camera, translationMatrix):
        super(ZoomController, self).__init__(cfg, camera, translationMatrix)
        self._maxHeight = 150
        self._minHeight = 20
        self._currentHeight = translationMatrix.translation.y
        self._desiredHeight = self._currentHeight
        self._previousWheelDirection = 0.0
        self._offsetChangeByWheelScroll = 0.05
        self._mouseWheelDeltaFactor = 40.0
        self._wheelTimeToEnd = 0.6
        self._curWheelTimeLeft = 0.0
        self._initialScrollValue = 0.0
        self._scrollOffset = 35

    @property
    def currentHeight(self):
        return self._currentHeight

    @currentHeight.setter
    def currentHeight(self, value):
        self._currentHeight = math_utils.clamp(self._minHeight, self._maxHeight, value)

    @property
    def desiredHeight(self):
        return self._desiredHeight

    @desiredHeight.setter
    def desiredHeight(self, value):
        self._desiredHeight = math_utils.clamp(self._minHeight, self._maxHeight, value)

    @property
    def maxHeight(self):
        return self._maxHeight

    def handleMouseWheel(self, delta):
        if abs(delta) > 0:
            self.__mouseScroll(delta * self._mouseWheelDeltaFactor)
        return super(ZoomController, self).handleMouseWheel(delta)

    def handleMouseEvent(self, dx, dy, dz):
        if abs(dz) > 0:
            self.__mouseScroll(dz)
        return super(ZoomController, self).handleMouseEvent(dx, dy, dz)

    def __mouseScroll(self, dz):
        info = self.__sessionProvider.dynamic.rtsBWCtrl.getMouseInfo()
        if not info.mouseScrollEnabled:
            return
        currentWheelValue = -dz * self._offsetChangeByWheelScroll
        if currentWheelValue:
            terrainHeight = getTerrainHeightAt(self.camera.position)
            if terrainHeight > self.currentHeight:
                self.currentHeight = terrainHeight
                self.desiredHeight = terrainHeight
            currentWheelDirection = dz / abs(dz)
            if currentWheelDirection * self._previousWheelDirection <= 0.0:
                self.desiredHeight = self.currentHeight + currentWheelValue
            else:
                self.desiredHeight += currentWheelValue
            self._initialScrollValue = self.currentHeight
            self._curWheelTimeLeft = self._wheelTimeToEnd
            self._previousWheelDirection = currentWheelDirection

    def init(self):
        super(ZoomController, self).init()
        self._maxHeight = self.config['max_camera_height']
        self._minHeight = self.config['min_camera_height']
        self._currentHeight = math_utils.clamp(self._minHeight, self._maxHeight, self._translationMatrix.translation.y)
        self._desiredHeight = self._currentHeight
        self._previousWheelDirection = 0.0
        self._offsetChangeByWheelScroll = 0.05
        self._mouseWheelDeltaFactor = self.config['scroll_sensitivity']
        self._wheelTimeToEnd = self.config['scroll_stop_time']
        self._curWheelTimeLeft = 0.0
        self._initialScrollValue = 0.0
        self._scrollOffset = 35
        self._undergroundHeightWasUsed = False
        self._maxCollisionEvadeLimit = self.config['max_collision_evade_limit']
        self.update(0, True)

    def reset(self):
        self._curWheelTimeLeft = -1

    def update(self, deltaTime, force=False):
        if force or self._isNeedUpdate():
            self._update(deltaTime)
        self._updatePosUnderGround()

    def _update(self, deltaTime):
        self._undergroundHeightWasUsed = False
        oldOffset = self.currentHeight
        self._curWheelTimeLeft -= deltaTime
        if self._curWheelTimeLeft <= 0.0:
            self.currentHeight = self.desiredHeight
            self._curWheelTimeLeft = 0.0
        else:
            self.currentHeight = self._initialScrollValue + (self.desiredHeight - self._initialScrollValue) * math.sin((self._wheelTimeToEnd - self._curWheelTimeLeft) / self._wheelTimeToEnd * math.pi / 2.0)
        deltaOffset = (oldOffset - self.currentHeight) / (self._maxHeight - self._minHeight) * self._scrollOffset
        forwardVector = Vector3(self._camera.direction.x, 0, self._camera.direction.z)
        forwardVector.normalise()
        self.translationMatrix.setTranslate(Vector3(self.translationMatrix.translation.x + forwardVector.x * deltaOffset, max(getTerrainHeightAt(self.camera.position), self.currentHeight), self.translationMatrix.translation.z + forwardVector.z * deltaOffset))
        self.movementUpdated()

    def _isNeedUpdate(self):
        return self._curWheelTimeLeft >= 0.0 and not (self._curWheelTimeLeft == 0 and self.currentHeight == self.desiredHeight) or self._undergroundHeightWasUsed

    def _updatePosUnderGround(self):
        terrainHeight = getTerrainHeightAt(self.camera.position)
        if self._maxCollisionEvadeLimit > terrainHeight > self.currentHeight:
            self._undergroundHeightWasUsed = True
            self.translationMatrix.setTranslate(Vector3(self.translationMatrix.translation.x, terrainHeight, self.translationMatrix.translation.z))


class RotationController(BaseMoveController):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, cfg, camera, translationMatrix):
        super(RotationController, self).__init__(cfg, camera, translationMatrix)
        self._startRotationMousePos = None
        self._yaw = 0
        self.desiredYaw = self._yaw
        self.rotatingMouseCoef = 0.00016
        self.halfRotationTime = 0.1
        self._maxHeight = self.config['max_camera_height']
        self._minHeight = self.config['min_camera_height']
        self._minPitch = angleToRadian(160)
        self._maxPitch = angleToRadian(90)
        self._maxMousePitch = self._minPitch
        self._minMousePitch = self._maxPitch
        self._pitch = self._minPitch
        self._desiredPitch = self._pitch
        return

    @property
    def yaw(self):
        return self._yaw

    @property
    def currentHeight(self):
        return self.translationMatrix.translation.y

    def init(self, initialRotation):
        super(RotationController, self).init()
        self.rotatingMouseCoef = self.config['rotation_mouse_angle_speed']
        self.halfRotationTime = self.config['rotation_half_life']
        self._maxHeight = self.config['max_camera_height']
        self._minHeight = self.config['min_camera_height']
        self._maxPitch = angleToRadian(self.config['max_camera_pitch'])
        self._minPitch = angleToRadian(self.config['min_camera_pitch'])
        restrictions = (angleToRadian(self.config['max_mouse_camera_pitch']), angleToRadian(self.config['min_mouse_camera_pitch']))
        self._maxMousePitch = max(*restrictions)
        self._minMousePitch = min(*restrictions)
        self._desiredPitch = initialRotation.y
        self._pitch = self._desiredPitch
        self.setYaw(initialRotation.z, smoothly=False)

    def update(self, deltaTime, force=False):
        if force or round(self.desiredYaw, FLOAT_DECIMAL_PLACE) != round(self._yaw, FLOAT_DECIMAL_PLACE) or round(self._desiredPitch, FLOAT_DECIMAL_PLACE) != round(self._pitch, FLOAT_DECIMAL_PLACE):
            self._yaw = angleDecay(self._yaw, self.desiredYaw, self.halfRotationTime, deltaTime)
            self._pitch = angleDecay(self._pitch, self._desiredPitch, self.halfRotationTime, deltaTime)
            self.rotationMatrix.setRotateYPR(Vector3(getNormilizedAngle(self._yaw), self._pitch, 0))
            self.movementUpdated()
        if self.appLoader.getApp().cursorMgr:
            if not self.isRotating() and not GUI.mcursor().visible:
                self.appLoader.getApp().cursorMgr.attachCursor()
        super(RotationController, self).update(deltaTime)

    def handleKeyEvent(self, isDown, key, mods, event=None):
        info = self.__sessionProvider.dynamic.rtsBWCtrl.getMouseInfo()
        if BigWorld.isKeyDown(MappedKeys.getKey(MappedKeys.KEY_CAM_ZOOM)) and info.mouseWheelEnabled:
            if not self.isRotating():
                self._startRotationMousePos = GUI.mcursor().position
                self._yaw = getNormilizedAngle(self._yaw)
                self.desiredYaw = self._yaw
                self._desiredPitch = self._pitch
                if self.appLoader.getApp().cursorMgr:
                    self.appLoader.getApp().cursorMgr.detachCursor()
        elif self.isRotating():
            self.__restoreMousePosition()
            self._startRotationMousePos = None
            if self.appLoader.getApp().cursorMgr:
                self.appLoader.getApp().cursorMgr.attachCursor()
        return super(RotationController, self).handleKeyEvent(isDown, key, mods, event)

    def handleMouseEvent(self, dx, dy, dz):
        if self.isRotating() and (dx or dy):
            self.desiredYaw += dx * self.rotatingMouseCoef
            deltaY = -dy * self.rotatingMouseCoef
            self._desiredPitch = math_utils.clamp(self._minMousePitch, self._maxMousePitch, self._desiredPitch + deltaY)
            self.__restoreMousePosition()
        return super(RotationController, self).handleMouseEvent(dx, dy, dz)

    def isRotating(self):
        return self._startRotationMousePos is not None

    def setYaw(self, yaw, smoothly=True):
        self.desiredYaw = yaw
        if not smoothly:
            self._yaw = self.desiredYaw
            self.update(0, True)

    def setPitch(self, pitch, smoothly=True):
        self._desiredPitch = math_utils.clamp(self._minMousePitch, self._maxMousePitch, pitch)
        if not smoothly:
            self._pitch = self._desiredPitch
            self.update(0, True)

    def __restoreMousePosition(self):
        GUI.mcursor().position = self._startRotationMousePos


class MatrixWithTranslationBBRestriction(object):

    def __init__(self, matrix, boundingBox):
        super(MatrixWithTranslationBBRestriction, self).__init__()
        self._matrix = matrix
        self._boundingBox = boundingBox

    def __getattr__(self, name):
        return getattr(self._matrix, name)

    @property
    def translation(self):
        return self._matrix.translation

    @translation.setter
    def translation(self, value):
        self.setTranslate(value)

    def setTranslate(self, pos):
        self._matrix.setTranslate(self.getCorrectTranslation(pos))

    def getCorrectTranslation(self, translation):
        return Vector3(math_utils.clamp(self._boundingBox[0].x, self._boundingBox[1].x, translation.x), translation.y, math_utils.clamp(self._boundingBox[0].y, self._boundingBox[1].y, translation.z))


class InertialValue(object):

    def __init__(self, maxValue, accelerationSpeed, deaccelerationSpeed):
        super(InertialValue, self).__init__()
        self._curValue = 0.0
        self._maxValue = maxValue
        self._accelerationSpeed = accelerationSpeed
        self._deaccelerationSpeed = deaccelerationSpeed
        self._moveDirection = 0

    def __call__(self, *args, **kwargs):
        return self.curValue

    @property
    def curValue(self):
        return self._curValue

    @curValue.setter
    def curValue(self, value):
        self._curValue = value

    @property
    def maxValue(self):
        return self._maxValue

    @property
    def accelerationSpeed(self):
        return self._accelerationSpeed

    @property
    def deaccelerationSpeed(self):
        return self._deaccelerationSpeed

    @property
    def moveDirection(self):
        return self._moveDirection

    @moveDirection.setter
    def moveDirection(self, value):
        self._moveDirection = value

    def update(self, delta):
        if not (self.curValue == 0.0 and self.moveDirection == 0):
            newValue = self.curValue
            if self.moveDirection == 0:
                newValue -= newValue / abs(newValue) * self.deaccelerationSpeed * delta
                if newValue * self.curValue <= 0:
                    newValue = 0
            else:
                accelerationSpeed = self.accelerationSpeed
                if self.curValue * self.moveDirection < 0:
                    accelerationSpeed = self.accelerationSpeed + self.deaccelerationSpeed
                if abs(newValue) > self.maxValue and newValue * self.moveDirection >= 0:
                    newValue -= self.moveDirection * accelerationSpeed * delta
                    if abs(newValue) < self.maxValue:
                        newValue = self.moveDirection * self.maxValue
                else:
                    newValue += self.moveDirection * accelerationSpeed * delta
                    if abs(newValue) > self.maxValue:
                        newValue = self.moveDirection * self.maxValue
            self._curValue = newValue


class InertialValueWithDynamicValues(InertialValue):

    @property
    def maxValue(self):
        return self._maxValue()

    @property
    def accelerationSpeed(self):
        return self._accelerationSpeed()

    @property
    def deaccelerationSpeed(self):
        return self._deaccelerationSpeed()


class InertialValueVector2(list):

    def __init__(self, x, y):
        super(InertialValueVector2, self).__init__()
        self.append(x)
        self.append(y)

    @property
    def x(self):
        return self[0]

    @property
    def y(self):
        return self[1]


def decay(src, dst, halfLife, dTime, minSpeed=0.0):
    if halfLife <= 0.0:
        return dst
    res = dst + pow(0.5, dTime / halfLife) * (src - dst)
    if minSpeed:
        dir_ = 1 if dst - src >= 0 else -1
        res = src + dir_ * max(abs(src - res), minSpeed)
        if (dst - res) * dir_ <= 0:
            return dst
    return res


def angleDecay(src, dst, halfLife, dTime, minSpeed=0.0):
    return decay(src, getSameSignAngle(src, dst), halfLife, dTime, minSpeed)


def getSameSignAngle(angle, closest):
    if closest > angle + math.pi:
        return closest - _TWO_PI
    return closest + _TWO_PI if closest < angle - math.pi else closest


def getNormilizedAngle(angle):
    if angle > _TWO_PI:
        return angle % _TWO_PI
    return _TWO_PI - abs(angle) % _TWO_PI if angle < 0 else angle


def isAnyKeysDown(*keys):
    return any((BigWorld.isKeyDown(key) for key in keys))


def getTerrainHeightAt(pos):
    offset = 3
    x = pos.x
    z = pos.z
    result = BigWorld.wg_collideDynamicStatic(BigWorld.player().spaceID, Math.Vector3(x, 1000.0, z), Math.Vector3(x, -1000.0, z), CollisionFlags.TRIANGLE_CAMERANOCOLLIDE, 0, -1)
    terrainHeight = result[0][1] if result else 0
    return terrainHeight + offset
