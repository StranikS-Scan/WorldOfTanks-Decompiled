# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/epic_battle_death_mode.py
import GUI
import BigWorld
import constants
import CommandMapping
import Math
import Keys
import SoundGroups
import ResMgr
from ClientArena import CollisionResult
from aih_constants import CTRL_MODE_NAME
from control_modes import VideoCameraControlMode, PostMortemControlMode
from VideoCamera import VideoCamera, _Inertia, KeySensor
from PostmortemDelay import PostmortemDelay
from supply_shared import Supply
from helpers import isPlayerAvatar
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control.controllers.epic_spectator_ctrl import SPECTATOR_MODE

class EpicVideoCamera(VideoCamera):

    def __init__(self, configDataSec):
        super(EpicVideoCamera, self).__init__(configDataSec)
        self.__selectedTargetID = None
        return

    def enable(self, **args):
        super(EpicVideoCamera, self).enable(**args)
        self._alignerToLand.enableWithFixedHeight(self.__heightAboveTerrain)
        if isPlayerAvatar():
            BigWorld.player().positionControl.moveTo(self._cam.position)
            BigWorld.player().positionControl.followCamera(True)

    def setHeight(self, height):
        self._alignerToLand.enableWithFixedHeight(height)

    def handleKeyEvent(self, key, isDown):
        return False if key is None else self._movementSensor.handleKeyEvent(key, isDown) or self._rotationSensor.handleKeyEvent(key, isDown)

    def handleMouseEvent(self, dx, dy, dz):
        relativeSenseGrowth = self._rotationSensor.sensitivity / self._rotationSensor.defaultSensitivity
        self._rotationSensor.addVelocity(Math.Vector3(dx, dy, 0) * self._mouseSensitivity * relativeSenseGrowth)
        GUI.mcursor().position = Math.Vector2(0, 0)

    def reload(self):
        if not constants.IS_DEVELOPMENT:
            return
        ResMgr.purge('gui/avatar_input_handler.xml')
        cameraSec = ResMgr.openSection('gui/avatar_input_handler.xml/epicVideoMode/camera/')
        self._readCfg(cameraSec)

    def _readCfg(self, configDataSec):
        self._readMovementSettings(configDataSec)
        self._mouseSensitivity = configDataSec.readFloat('sensitivity', 1.0)
        self._scrollSensitivity = configDataSec.readFloat('scrollSensitivity', 1.0)
        self._inertiaEnabled = configDataSec.readBool('inertiaEnabled', True)
        self._movementInertia = _Inertia(configDataSec.readFloat('linearFriction', 0.1))
        self._rotationInertia = _Inertia(configDataSec.readFloat('rotationFriction', 0.1))
        self._readRotationSettings(configDataSec, {})
        self._readZoomSettings(configDataSec, {})
        self.__heightAboveTerrain = configDataSec.readFloat('heightAboveTerrain', 50.0)
        self.setHeight(self.__heightAboveTerrain)

    def _readMovementSettings(self, configDataSec):
        movementMappings = dict()
        movementMappings[getattr(Keys, configDataSec.readString('keyMoveLeft', 'KEY_A'))] = Math.Vector3(-1, 0, 0)
        movementMappings[getattr(Keys, configDataSec.readString('keyMoveRight', 'KEY_D'))] = Math.Vector3(1, 0, 0)
        movementMappings[getattr(Keys, configDataSec.readString('keyMoveForward', 'KEY_W'))] = Math.Vector3(0, 0, 1)
        movementMappings[getattr(Keys, configDataSec.readString('keyMoveBackward', 'KEY_S'))] = Math.Vector3(0, 0, -1)
        linearSensitivity = configDataSec.readFloat('linearVelocity', 40.0)
        self._movementSensor = KeySensor(movementMappings, linearSensitivity)
        self._verticalMovementSensor = KeySensor({}, linearSensitivity)
        self._movementSensor.currentVelocity = Math.Vector3()

    def _readRotationSettings(self, configDataSec, rotationMappings):
        rotationSensitivity = configDataSec.readFloat('angularVelocity', 0.7)
        self._rotationSensor = KeySensor(rotationMappings, rotationSensitivity)
        self._rotationSensor.currentVelocity = Math.Vector3()

    def _checkSpaceBounds(self, startPos, endPos):
        if not isPlayerAvatar():
            return endPos
        moveDir = endPos - startPos
        moveDir.normalise()
        collisionResult, _ = BigWorld.player().arena.collideWithArenaBB(startPos, endPos)
        if collisionResult == CollisionResult.INTERSECTION:
            return BigWorld.player().arena.getClosestPointOnArenaBB(endPos)
        if collisionResult == CollisionResult.OUTSIDE:
            onBorder = BigWorld.player().arena.getClosestPointOnArenaBB(endPos)
            offset = onBorder - endPos
            offset.normalise()
            return onBorder + offset
        return endPos

    def _update(self):
        player = BigWorld.player()
        target = player.target
        specCtrl = self.guiSessionProvider.dynamic.spectator

        def resetTarget():
            self.__selectedTargetID = None
            specCtrl.spectatedVehicleChanged(None)
            return

        def shouldReset():
            if target is None:
                return True
            elif target.__class__.__name__ != 'Vehicle':
                return True
            elif target.id == self.__selectedTargetID:
                return True
            vehicleDesc = player.arena.vehicles.get(target.id)
            if not vehicleDesc or not vehicleDesc['isAlive'] or vehicleDesc['team'] != player.team:
                return True
            elif Supply.isSupply(vehicleDesc['vehicleType'].type.tags):
                resetTarget()
                return True
            else:
                return False

        if shouldReset():
            if target is None and self.__selectedTargetID is not None:
                resetTarget()
            return VideoCamera._update(self)
        else:
            self.__selectedTargetID = target.id
            if self.__selectedTargetID != specCtrl.spectatedVehicle:
                specCtrl.spectatedVehicleChanged(self.__selectedTargetID)
            return VideoCamera._update(self)


class DeathFreeCamMode(VideoCameraControlMode):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, dataSection, avatarInputHandler):
        super(DeathFreeCamMode, self).__init__(dataSection, avatarInputHandler)
        self.__forcedGuiControlEnabled = False

    def _createCamera(self, cameraDataSection):
        self._cam = EpicVideoCamera(cameraDataSection)

    def enable(self, **args):
        VideoCameraControlMode.enable(self, **args)
        specCtrl = self.guiSessionProvider.dynamic.spectator
        specCtrl.spectatorViewModeChanged(SPECTATOR_MODE.FREECAM)
        specCtrl.spectatedVehicleChanged(None)
        ctrl = self.guiSessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onRespawnInfoUpdated += self.__onRespawnInfoUpdated
            if ctrl.respawnInfo is not None:
                self.__onRespawnInfoUpdated(ctrl.respawnInfo)
        self.__forcedGuiControlEnabled = BigWorld.player().isForcedGuiControlMode()
        return

    def disable(self):
        VideoCameraControlMode.disable(self)
        ctrl = self.guiSessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onRespawnInfoUpdated -= self.__onRespawnInfoUpdated
        return

    def handleKeyEvent(self, isDown, key, mods, event=None):
        VideoCameraControlMode.handleKeyEvent(self, isDown, key, mods, event)
        cmdMap = CommandMapping.g_instance
        if not self.__forcedGuiControlEnabled and cmdMap.isFired(CommandMapping.CMD_CM_POSTMORTEM_NEXT_VEHICLE, key) and isDown and BigWorld.player().target is not None and BigWorld.player().target.__class__.__name__ == 'Vehicle':
            vehicleDesc = BigWorld.player().arena.vehicles.get(BigWorld.player().target.id)
            if vehicleDesc['isAlive'] and vehicleDesc['team'] == BigWorld.player().team:
                self.__switchToVehicle(BigWorld.player().target.id)
                return True
        return False

    def selectPlayer(self, vehID):
        self.__switchToVehicle(vehID)

    def alwaysReceiveKeyEvents(self, isDown=True):
        return True

    def setForcedGuiControlMode(self, enable):
        self.__forcedGuiControlEnabled = enable

    def isSelfVehicle(self):
        return False

    def __switchToVehicle(self, toId=None):
        player = BigWorld.player()
        vehicles = player.arena.vehicles
        vehicleDesc = vehicles.get(toId)
        if vehicleDesc is None:
            return
        elif not vehicleDesc['isAlive'] or vehicleDesc['team'] != player.team or Supply.isSupply(vehicleDesc['vehicleType'].type.tags):
            return
        else:
            targetMode = CTRL_MODE_NAME.POSTMORTEM
            player.inputHandler.onControlModeChanged(targetMode, postmortemParams=None, newVehicleID=toId, bPostmortemDelay=False, respawn=True, camMatrix=BigWorld.camera().matrix, transitionDuration=self._cameraTransitionDurations[targetMode])
            player.inputHandler.onCameraChanged(targetMode, toId)
            if toId is None:
                self.guiSessionProvider.switchToPostmortem(False)
            return

    def __onRespawnInfoUpdated(self, respawnInfo):
        if respawnInfo is not None:
            self.selectPlayer(None)
            BigWorld.player().inputHandler.onControlModeChanged(CTRL_MODE_NAME.RESPAWN_DEATH, prevModeName=CTRL_MODE_NAME.POSTMORTEM, camMatrix=BigWorld.camera().matrix, curVehicleID=self.curVehicleID, transitionDuration=self._cameraTransitionDurations[CTRL_MODE_NAME.RESPAWN_DEATH])
        return

    def overridePose(self, pos, rot):
        transform = Math.Matrix()
        transform.setRotateYPR(rot)
        transform.translation = self._cam._checkSpaceBounds(BigWorld.camera().position, pos)
        self._cam.setViewMatrix(transform)


class DeathTankFollowMode(PostMortemControlMode):

    def handleKeyEvent(self, isDown, key, mods, event=None):
        cmdMap = CommandMapping.g_instance
        if cmdMap.isFired(CommandMapping.CMD_CM_POSTMORTEM_SELF_VEHICLE, key) and isDown and self.curPostmortemDelay is None:
            self.selectPlayer(None)
            self._switchToCtrlMode(CTRL_MODE_NAME.DEATH_FREE_CAM)
            return True
        else:
            if cmdMap.isFired(CommandMapping.CMD_CM_POSTMORTEM_NEXT_VEHICLE, key) and isDown and self.curPostmortemDelay is None and BigWorld.player().target is not None and BigWorld.player().target.__class__.__name__ == 'Vehicle':
                vehicleDesc = BigWorld.player().arena.vehicles.get(BigWorld.player().target.id)
                if vehicleDesc['isAlive'] and vehicleDesc['team'] == BigWorld.player().team:
                    self.selectPlayer(BigWorld.player().target.id)
                    return True
            if cmdMap.isFiredList((CommandMapping.CMD_CM_CAMERA_ROTATE_LEFT,
             CommandMapping.CMD_CM_CAMERA_ROTATE_RIGHT,
             CommandMapping.CMD_CM_CAMERA_ROTATE_UP,
             CommandMapping.CMD_CM_CAMERA_ROTATE_DOWN,
             CommandMapping.CMD_CM_INCREASE_ZOOM,
             CommandMapping.CMD_CM_DECREASE_ZOOM), key):
                dx = dy = dz = 0.0
                if cmdMap.isActive(CommandMapping.CMD_CM_CAMERA_ROTATE_LEFT):
                    dx = -1.0
                if cmdMap.isActive(CommandMapping.CMD_CM_CAMERA_ROTATE_RIGHT):
                    dx = 1.0
                if cmdMap.isActive(CommandMapping.CMD_CM_CAMERA_ROTATE_UP):
                    dy = -1.0
                if cmdMap.isActive(CommandMapping.CMD_CM_CAMERA_ROTATE_DOWN):
                    dy = 1.0
                if cmdMap.isActive(CommandMapping.CMD_CM_INCREASE_ZOOM):
                    dz = 1.0
                if cmdMap.isActive(CommandMapping.CMD_CM_DECREASE_ZOOM):
                    dz = -1.0
                self.camera.update(dx, dy, dz, True, True, False if dx == dy == dz == 0.0 else True)
                return True
            return False

    @classmethod
    def _getPostmortemDelay(cls, *args, **kwargs):
        return EpicPostmortemCamera(*args, **kwargs)

    def _onMatrixBound(self, isStatic):
        super(DeathTankFollowMode, self)._onMatrixBound(isStatic)
        cameraTransitionDuration = self._cameraTransitionDurations.get(CTRL_MODE_NAME.POSTMORTEM, -1)
        if cameraTransitionDuration > 0:
            self.camera.restartCameraTransition(cameraTransitionDuration)

    def enable(self, **args):
        self.altTargetMode = CTRL_MODE_NAME.DEATH_FREE_CAM
        super(DeathTankFollowMode, self).enable(**args)
        SoundGroups.g_instance.changePlayMode(0)
        specCtrl = self.guiSessionProvider.dynamic.spectator
        if specCtrl is not None:
            specCtrl.spectatedVehicleChanged(None)
            specCtrl.spectatorViewModeChanged(SPECTATOR_MODE.FOLLOW if self.curPostmortemDelay is None else SPECTATOR_MODE.DEATHCAM)
        vehicleID = args.get('newVehicleID')
        if vehicleID is not None:
            self.selectPlayer(vehicleID)
        return


class EpicPostmortemCamera(PostmortemDelay):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _startKillerVision(self):
        vInfo = self.__guiSessionProvider.getArenaDP().getVehicleInfo(self._killerVehicleID)
        if Supply.isAirShip(vInfo.vehicleType.tags):
            player = BigWorld.player()
            self._killerVehicleID = player.playerVehicleID
        super(EpicPostmortemCamera, self)._startKillerVision()
