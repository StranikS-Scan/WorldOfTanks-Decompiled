# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/rts_vehicle_change_ctrl.py
import logging
import typing
import BigWorld
import Math
import Keys
import aih_constants
import BattleReplay
import constants
from AvatarInputHandler.AimingSystems import getShotPosition, getVehicleGunMarkerPosition, getMultiGunCurrentShotPosition
from BattleReplay import CallbackDataNames
from Event import Event
import TriggersManager
from gui.battle_control.arena_info.interfaces import IRTSVehicleChangeController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.controllers.commander.rts_commander_ctrl import MappedKeys
from helpers import dependency
from shared_utils import first
from skeletons.gui.battle_session import IBattleSessionProvider
from Math import Vector3, Matrix
_logger = logging.getLogger(__name__)

class _RTSVehicleChangeController(IRTSVehicleChangeController):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _DEFAULT_ARCADE_CAMERA_DISTANCE = 15

    def __init__(self, setup):
        super(_RTSVehicleChangeController, self).__init__()
        self.onStartVehicleControl = Event()
        self.onStopVehicleControl = Event()
        self.__avatar = setup.avatar
        self.__nextVehicleID = None
        self.__commanderVehicleID = None
        self.__isEnabled = True
        self.__leavingVehicleID = None
        return

    def startControl(self, *args):
        pass

    def stopControl(self):
        pass

    def getControllerID(self):
        return BATTLE_CTRL_ID.VEHICLE_CHANGE_CTRL

    @property
    def isEnabled(self):
        return self.__isEnabled and self.__avatar.isAICommander

    def setEnabled(self, enabled):
        self.__isEnabled = enabled

    @property
    def currentVehicleID(self):
        currentVehicleID = self.__nextVehicleID
        if currentVehicleID is None:
            currentVehicleID = self.__avatar.playerVehicleID
        return currentVehicleID

    @property
    def isVehicleChanging(self):
        return self.__nextVehicleID is not None

    def canChangeVehicle(self, vehicle):
        return not self.isEnabled or vehicle is None or self.__isCommanderVehicle(vehicle.id) or vehicle.isAlive()

    def handleKeyEvent(self, isDown, key, mods):
        if not self.isEnabled:
            return False
        if constants.HAS_DEV_RESOURCES and BigWorld.isKeyDown(Keys.KEY_CAPSLOCK):
            return False
        isCommanderVehicle = self.__isCommanderVehicle(self.__avatar.playerVehicleID)
        rtsCommander = self.__sessionProvider.dynamic.rtsCommander
        if not isCommanderVehicle and rtsCommander and MappedKeys.isMappedTo(key, MappedKeys.KEY_CONTROL_VEHICLE):
            rtsCommander.onRTSKeyEvent(isDown, key)
        if not (isDown and MappedKeys.isMappedTo(key, MappedKeys.KEY_CONTROL_VEHICLE)):
            return False
        if isCommanderVehicle:
            self.changeToCandidateVehicle()
        else:
            self.resetVehicle()
        return True

    def changeVehicle(self, vehicleID):
        if not self.isEnabled:
            return False
        else:
            vehicleID = vehicleID or self.__getCommanderVehicleID()
            if vehicleID is None or vehicleID == self.currentVehicleID or self.isVehicleChanging or not self.__avatar.isOnArena:
                return False
            newVehicle = BigWorld.entity(vehicleID)
            if newVehicle is None:
                return False
            self._setCurrentVehicleID(vehicleID)
            if not self.__isCommanderVehicle(vehicleID):
                self.__onStartVehicleControlAttempt(vehicleID)
            else:
                self.__onStopVehicleControlAttempt()
            return True

    def changeToCandidateVehicle(self):
        vehicleID = self.getCandidateVehicleID()
        if vehicleID is not None:
            self.changeVehicle(vehicleID)
        return

    def resetVehicle(self):
        return self.changeVehicle(None)

    def stopVehicleControl(self):
        if not self.resetVehicle():
            self.__avatar.stopVehicleControlAttempt()

    def onVehicleChangeFailed(self):
        if not self.isEnabled:
            return
        else:
            vehicleID = self.currentVehicleID
            if not self.__isCommanderVehicle(vehicleID):
                self.__onStartVehicleControlFailed(vehicleID)
            else:
                self.__onStopVehicleControlFailed()
            self._setCurrentVehicleID(None)
            self.resetVehicle()
            return

    def onVehicleChanged(self, vehicleID):
        if not self.isEnabled or not self.isVehicleChanging or vehicleID != self.currentVehicleID:
            return
        else:
            newVehicle = BigWorld.entity(vehicleID)
            if newVehicle is None:
                return
            isCommanderVehicle = self.__isCommanderVehicle(vehicleID)
            if isCommanderVehicle:
                oldVehicle = BigWorld.entity(self.__avatar.playerVehicleID)
                if oldVehicle is not None:
                    self.__sessionProvider.startVehicleVisual(oldVehicle, True)
            self.__avatar.setPlayerVehicle(vehicleID)
            gunRotator = self.__avatar.gunRotator
            if gunRotator is not None:
                gunRotator.clientMode = not isCommanderVehicle
                gunRotator.stop()
                gunRotator.reset()
                if not isCommanderVehicle:
                    gunRotator.start()
            self.__avatar.enableServerAim(not isCommanderVehicle)
            if self.__avatar.inputHandler is not None:
                self.__avatar.inputHandler.setKillerVehicleID(None)
            self.__sessionProvider.switchVehicle(vehicleID)
            if not isCommanderVehicle:
                self.__sessionProvider.stopVehicleVisual(vehicleID, False)
            self.__avatar.updateObservedVehicleData()
            self._setCurrentVehicleID(None)
            if not isCommanderVehicle:
                self.__onStartVehicleControlSuccess(vehicleID)
            else:
                self.__onStopVehicleControlSuccess()
            return

    def getCandidateVehicleID(self):
        return first(self.__sessionProvider.dynamic.rtsCommander.vehicles.iterkeys(lambda v: v.isSelected))

    def _changeControlMode(self, ctrlModeName, **kwargs):
        if self.__avatar.inputHandler is not None:
            self.__avatar.inputHandler.onCameraChanged += self.__onCameraChanged
            self.__avatar.inputHandler.onControlModeChanged(ctrlModeName, **kwargs)
            self.__avatar.inputHandler.refreshGunMarkers()
        return

    def _setCurrentVehicleID(self, vehicleID):
        self.__nextVehicleID = vehicleID

    def __onStartVehicleControlAttempt(self, vehicleID):
        self.__avatar.startVehicleControlAttempt(vehicleID)

    def __onStartVehicleControlSuccess(self, vehicleID):
        self._changeControlMode(aih_constants.CTRL_MODE_NAME.ARCADE, preferredPos=self.__getVehicleGunMarkerPosition(vehicleID))
        self.__sessionProvider.dynamic.rtsCommander.onStartVehicleControl(vehicleID)
        vehicle = BigWorld.entity(vehicleID)
        if vehicle is None:
            return
        else:
            vehicle.resetProperties()
            if not BattleReplay.g_replayCtrl.isPlaying:
                TriggersManager.g_manager.activateTrigger(TriggersManager.TRIGGER_TYPE.TANKMAN_MODE)
            self.onStartVehicleControl(vehicleID)
            return

    def __onStartVehicleControlFailed(self, vehicleID):
        pass

    def __onCameraChanged(self, eMode, _):
        if eMode == aih_constants.CTRL_MODE_NAME.ARCADE:
            self.__avatar.inputHandler.ctrl.camera.setCameraDistance(self._DEFAULT_ARCADE_CAMERA_DISTANCE)
            self.__avatar.inputHandler.onCameraChanged -= self.__onCameraChanged

    def __onStopVehicleControlAttempt(self):
        self.__avatar.setCruiseCtrlMode(0)
        self.__avatar.moveVehicle(self.__avatar.makeVehicleMovementCommandByKeys(), False)
        self.__leavingVehicleID = self.__avatar.playerVehicleID
        if self.__avatar.inputHandler:
            aih = self.__avatar.inputHandler
            cam = aih.ctrl.camera
            yaw, _ = self.__getCameraYawPitch()
            aih.setAutorotation(True)
            cam.disable()
            cameraLocation = Math.Matrix(cam.aimingSystem.matrix).translation
            leavingVehicle = BigWorld.entity(self.__leavingVehicleID)
            targetPos = leavingVehicle.position if leavingVehicle else cameraLocation
            self._changeControlMode(aih_constants.CTRL_MODE_NAME.COMMANDER, startingPos=cameraLocation, targetPos=targetPos, targetYaw=yaw if yaw != 0 else self.__getLookAtYPR(cameraLocation, targetPos))
        self.__avatar.stopVehicleControlAttempt()

    def __onStopVehicleControlSuccess(self):
        if not BattleReplay.g_replayCtrl.isPlaying:
            TriggersManager.g_manager.deactivateTrigger(TriggersManager.TRIGGER_TYPE.TANKMAN_MODE)
        leavingVehicle = None
        if self.__leavingVehicleID:
            leavingVehicle = BigWorld.entity(self.__leavingVehicleID)
        if leavingVehicle:
            if leavingVehicle.appearance is not None:
                leavingVehicle.appearance.disableExternalTracksScroll()
            leavingVehicle.resetProperties()
        self.__sessionProvider.dynamic.rtsCommander.onStopVehicleControl(self.__leavingVehicleID)
        self.onStopVehicleControl(self.__leavingVehicleID)
        self.__leavingVehicleID = None
        return

    def __onStopVehicleControlFailed(self):
        _logger.warning('Cases of unsuccessful vehicle control')
        vehicleID = self.__avatar.playerVehicleID
        if not self.__isCommanderVehicle(vehicleID):
            self._changeControlMode(aih_constants.CTRL_MODE_NAME.ARCADE, preferredPos=self.__getVehicleGunMarkerPosition(vehicleID))

    def __getLookAtYPR(self, lookAtPosition, currentPosition):
        lookDir = lookAtPosition - currentPosition
        camMat = Matrix()
        camMat.lookAt(currentPosition, lookDir, Vector3(0, 1, 0))
        camMat.invert()
        return camMat.yaw

    def __getCameraYawPitch(self):
        cameraMatrix = Math.Matrix(self.__avatar.inputHandler.ctrl.camera.camera.matrix)
        return (-cameraMatrix.yaw, -cameraMatrix.pitch)

    def __getVehicleGunMarkerPosition(self, vehicleID, yaw=None, pitch=None):
        vehicle = self.__sessionProvider.dynamic.rtsCommander.vehicles.get(vehicleID)
        if vehicle is None or not vehicle.initialized:
            _logger.error('Could not get vehicle proxy with id = %r', vehicleID)
            return
        else:
            turretYaw, gunPitch = vehicle.serverGunAngles
            if yaw is not None:
                turretYaw = yaw - vehicle.yaw
            if pitch is not None:
                gunPitch = pitch - vehicle.pitch
            shotPosition, shotDirection = getShotPosition(Math.Matrix(vehicle.matrix), vehicle.typeDescriptor, turretYaw, gunPitch, gunOffset=getMultiGunCurrentShotPosition(vehicle))
            return getVehicleGunMarkerPosition(vehicleID, shotPosition, shotDirection, self.__avatar)[0]

    def __isCommanderVehicle(self, vehicleID):
        return vehicleID == self.__getCommanderVehicleID()

    def __getCommanderVehicleID(self):
        if self.__commanderVehicleID is None:
            self.__commanderVehicleID = self.__avatar.commanderVehicleID()
        return self.__commanderVehicleID


class _RTSVehicleChangeControllerRecorder(_RTSVehicleChangeController):

    def _setCurrentVehicleID(self, vehicleID):
        if vehicleID is not None:
            BattleReplay.g_replayCtrl.serializeCallbackData(CallbackDataNames.SET_CONTROL_VEHICLE_ID, (vehicleID,))
        super(_RTSVehicleChangeControllerRecorder, self)._setCurrentVehicleID(vehicleID)
        return


class _RTSVehicleChangeControllerPlayer(_RTSVehicleChangeController):

    def startControl(self):
        BattleReplay.g_replayCtrl.setDataCallback(CallbackDataNames.SET_CONTROL_VEHICLE_ID, self._setCurrentVehicleID)

    def stopControl(self):
        BattleReplay.g_replayCtrl.delDataCallback(CallbackDataNames.SET_CONTROL_VEHICLE_ID, self._setCurrentVehicleID)
        super(_RTSVehicleChangeControllerPlayer, self).stopControl()

    def _changeControlMode(self, ctrlModeName, **kwargs):
        if not BattleReplay.isPlaying:
            super(_RTSVehicleChangeControllerPlayer, self)._changeControlMode(ctrlModeName, **kwargs)

    def handleKeyEvent(self, isDown, key, mods):
        pass


def createVehicleChangeCtrl(setup):
    replayCtrl = BattleReplay.g_replayCtrl
    if replayCtrl.isPlaying:
        vehicleChangeCls = _RTSVehicleChangeControllerPlayer
    elif replayCtrl.isRecording:
        vehicleChangeCls = _RTSVehicleChangeControllerRecorder
    else:
        vehicleChangeCls = _RTSVehicleChangeController
    return vehicleChangeCls(setup)
