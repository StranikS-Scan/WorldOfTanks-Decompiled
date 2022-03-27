# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/commander/proxies/camera.py
import BigWorld
import Keys
import Math
from gui.battle_control.controllers.commander.common import center, MappedKeys
from helpers import dependency
from shared_utils import first
from skeletons.gui.battle_session import IBattleSessionProvider
from CommanderStartCamera import CommanderStartCamera
_COMMANDER_CAMERA_START_OFFSET_PATH = 'camera_start_offset'
_COMMANDER_CAMERA_ENTER_MODE_ANIMATION_ENABLED = 'tank_commander_mode_enter_animation'

class CameraProxy(object):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, commanderCamera):
        self.__cam = commanderCamera
        self.__startCamera = None
        self.__isArtMode = False
        self.__isCameraAdjustmentEnabled = True
        return

    @property
    def config(self):
        return self.__cam.config

    @property
    def position(self):
        return None if self.__cam.translationMatrix is None else self.__cam.translationMatrix.translation

    def enable(self, *_, **kwargs):
        self.__startCamera = first((o for o in BigWorld.userDataObjects.values() if isinstance(o, CommanderStartCamera) and o.team == BigWorld.player().team))
        targetPosition = kwargs.get('targetPos')
        startingPosition = kwargs.get('startingPos')
        targetYaw = kwargs.get('targetYaw')
        if self.__isArtMode:
            self.__liftArtMode(targetPosition, targetYaw)
        else:
            self.__place(startingPosition, targetPosition, targetYaw)

    def disable(self):
        pass

    def reset(self, commanderCamera):
        self.__cam = commanderCamera
        self.__isArtMode = False

    def moveToVehicle(self, vehicle):
        self.__cam.moveToVehicle(vehicle)

    def moveToPos(self, pos, yaw=0):
        self.__cam.moveToPos(pos, yaw)

    def moveToPosKeepRotation(self, pos):
        self.__cam.moveToPos(pos, self.__cam.rotationMatrix.yaw)

    def teleportWithFocusOnPoint(self, point):
        self.__cam.teleportWithFocusOnPoint(point)

    def teleport(self, worldPos, useOffset=False):
        self.__cam.teleport(self.__getPositionWithOffset(worldPos) if useOffset else worldPos)

    def handleMouseEvent(self, dx, dy, dz):
        return self.__cam.handleMouseEvent(dx, dy, dz)

    def handleMouseWheel(self, delta):
        return self.__cam.handleMouseWheel(delta)

    def handleKeyEvent(self, isDown, key, mods, event):
        if self.__isCameraAdjustmentEnabled:
            if key == Keys.KEY_ADD and isDown:
                self.handleMouseEvent(0, 0, 120)
                return True
            if key == Keys.KEY_NUMPADMINUS and isDown:
                self.handleMouseEvent(0, 0, -120)
                return True
            if MappedKeys.isKey(event, MappedKeys.KEY_MOVE_UP):
                self.__isArtMode = False
                self.__cam.moveUp()
                return True
            if MappedKeys.isKey(event, MappedKeys.KEY_DEFAULT_CAMERA):
                self.__cam.setDefault()
                return True
            if MappedKeys.isKey(event, MappedKeys.KEY_GOTO_CONTACT):
                if self.__isArtMode:
                    self.__isArtMode = False
                    self.__cam.moveUp()
                else:
                    self.__isArtMode = True
                    self.__cam.setArtMode()
            if MappedKeys.isKey(event, MappedKeys.KEY_FOCUS_CAMERA):
                self.__focusCamera(self.__sessionProvider.dynamic.rtsCommander.vehicles.values(lambda v: v.isSelected))
                return True
        return self.__cam.handleKeyEvent(isDown, key, mods, event)

    def enablePlayerCameraAdjustment(self, enable):
        self.__isCameraAdjustmentEnabled = enable

    def enableHorizontalCameraMovement(self, enable):
        self.__cam.enableHorizontalMovement(enable)

    def __place(self, startingPosition, targetPos, targetYaw):
        if startingPosition is None:
            startingPosition = self.__getInitialPosition()
        targetRotation = self.__getInitialRotation()
        if targetYaw is not None:
            targetRotation.z = targetYaw
        self.__cam.enable(startingPosition, targetRotation)
        if targetPos is not None:
            if self.config[_COMMANDER_CAMERA_ENTER_MODE_ANIMATION_ENABLED]:
                self.__cam.moveToPos(targetPos, targetYaw)
            else:
                self.__cam.liftUnder(targetPos, targetYaw)
        return

    def __liftArtMode(self, targetPos, targetYaw):
        self.__cam.enable(targetPos, initialRotation=self.__getInitialRotation())
        self.__cam.liftUnderArtMode(targetPos, targetYaw)

    def __focusCamera(self, vehicles):
        targetPosition = None
        if vehicles:
            positions = tuple((vehicle.position for vehicle in vehicles))
            if positions:
                targetPosition = center([ vehicle.position for vehicle in vehicles ])
        if targetPosition is None:
            targetPosition = self.__getInitialPosition()
        targetPosition = self.__getPositionWithOffset(targetPosition)
        self.__cam.teleport(targetPosition)
        return

    def __getInitialRotation(self):
        if self.__startCamera is None:
            return Math.Vector3()
        else:
            direction = Math.Vector3(self.__startCamera.direction)
            direction.y = -direction.y
            return direction

    def __getInitialPosition(self):
        return Math.Vector3() if self.__startCamera is None else self.__startCamera.position

    def __getPositionWithOffset(self, position):
        lookDirection = Math.Vector3(self.__cam.camera.direction.x, 0.0, self.__cam.camera.direction.z)
        lookDirection.normalise()
        return position - lookDirection * self.config[_COMMANDER_CAMERA_START_OFFSET_PATH]


def _sign(val):
    if val > 0:
        return 1.0
    return -1.0 if val < 0 else 0.0
