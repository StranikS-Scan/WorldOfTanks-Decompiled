# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarPositionControl.py
import weakref
import logging
import math_utils
import BigWorld
import Math
from Event import Event
import constants
import BattleReplay
from helpers.CallbackDelayer import CallbackDelayer
_logger = logging.getLogger(__name__)

class ConsistentMatrices(object):
    attachedVehicleMatrix = property(lambda self: self.__attachedVehicleMatrix)
    ownVehicleMatrix = property(lambda self: self.__ownVehicleMProv)
    ownVehicleTurretMProv = property(lambda self: self.__ownVehicleTurretMProv)

    def __init__(self):
        self.__attachedVehicleMatrix = Math.WGAdaptiveMatrixProvider()
        self.__attachedVehicleMatrix.target = math_utils.createIdentityMatrix()
        self.__ownVehicleMProv = Math.WGAdaptiveMatrixProvider()
        self.__ownVehicleMProv.target = math_utils.createIdentityMatrix()
        self.__ownVehicleTurretMProv = Math.WGAdaptiveMatrixProvider()
        self.__ownVehicleTurretMProv.target = math_utils.createIdentityMatrix()
        self.onVehicleMatrixBindingChanged = Event()

    def notifyEnterWorld(self, avatar):
        self.notifyVehicleChanged(avatar)

    def notifyLeaveWorld(self, avatar):
        self.__setTarget(avatar.matrix)

    def notifyVehicleLoaded(self, avatar, vehicle):
        if vehicle == avatar.vehicle:
            self.notifyVehicleChanged(avatar)
        elif vehicle.id == avatar.playerVehicleID:
            self.__linkOwnVehicle(vehicle)
            self.__setTarget(vehicle.matrix, False)

    def notifyPreBind(self, avatar):
        vehicle = avatar.getVehicleAttached()
        if vehicle is None or avatar.isObserver():
            bindMatrix = self.attachedVehicleMatrix
            useStatic = True
        else:
            bindMatrix = vehicle.matrix
            useStatic = False
        self.__setTarget(bindMatrix, useStatic)
        return

    def notifyVehicleChanged(self, avatar, updateStopped=False):
        if avatar.vehicle is None or not updateStopped and not avatar.vehicle.isStarted:
            self.__attachedVehicleMatrix.target = None
            self.onVehicleMatrixBindingChanged(True)
            return
        else:
            if avatar.vehicle.id == avatar.playerVehicleID:
                self.__linkOwnVehicle(avatar.vehicle)
            self.__setTarget(avatar.vehicle.matrix, False)
            return

    def notifyViewPointChanged(self, avatar, staticPosition=None):
        if staticPosition is not None:
            self.__setTarget(math_utils.createTranslationMatrix(staticPosition))
        return

    def __setTarget(self, matrix, asStatic=True):
        if asStatic:
            self.__attachedVehicleMatrix.setStaticTransform(Math.Matrix(matrix))
            self.__attachedVehicleMatrix.target = None
        else:
            self.__attachedVehicleMatrix.target = matrix
        self.onVehicleMatrixBindingChanged(asStatic)
        return

    def __linkOwnVehicle(self, vehicle):
        if isinstance(vehicle.filter, BigWorld.WGVehicleFilter):
            self.__ownVehicleMProv.target = vehicle.filter.bodyMatrix
            self.__ownVehicleTurretMProv.target = vehicle.filter.turretMatrix
        else:
            self.__ownVehicleMProv.target = vehicle.matrix
            if vehicle.appearance:
                self.__ownVehicleTurretMProv.target = vehicle.appearance.turretMatrix


class AvatarPositionControl(CallbackDelayer):
    FOLLOW_CAMERA_MAX_DEVIATION = 7.0
    onAvatarVehicleChanged = property(lambda self: self.__onAvatarVehicleChanged)
    isSwitching = property(lambda self: self.__isSwitching)

    def __init__(self, avatar):
        CallbackDelayer.__init__(self)
        self.__avatar = weakref.proxy(avatar)
        self.__bFollowCamera = False
        self.__isSwitching = False

    def destroy(self):
        self.__avatar = None
        CallbackDelayer.destroy(self)
        return

    def bindToVehicle(self, bValue=True, vehicleID=None):
        if vehicleID is None:
            vehicleID = self.__avatar.playerVehicleID
        BigWorld.player().consistentMatrices.notifyPreBind(BigWorld.player())
        if bValue:
            self.__doBind(vehicleID)
        else:
            self.__doUnbind(vehicleID)
        return

    def followCamera(self, bValue=True):
        self.__bFollowCamera = bValue
        if bValue:
            self.delayCallback(constants.SERVER_TICK_LENGTH, self.__followCameraTick)
        else:
            self.stopCallback(self.__followCameraTick)

    def switchViewpoint(self, isViewpoint, vehOrPointId):
        if self.__isSwitching:
            self.stopCallback(self.__resetSwitching)
            _logger.warning('switchViewpoint happened during switching cooldown! isSwitching check missed!')
        self.__isSwitching = True
        if BattleReplay.isServerSideReplay():
            BattleReplay.g_replayCtrl.bindToVehicleForServerSideReplay(vehOrPointId)
            self.__resetSwitching()
        else:
            self.__avatar.cell.switchViewPointOrBindToVehicle(isViewpoint, vehOrPointId)
            self.delayCallback(0.5, self.__resetSwitching)

    def moveTo(self, pos):
        self.__avatar.cell.moveTo(pos)

    def getFollowCamera(self):
        return self.__bFollowCamera

    def __resetSwitching(self):
        self.__isSwitching = False

    def __followCameraTick(self):
        if not self.__bFollowCamera:
            return
        else:
            cam = BigWorld.camera()
            if cam is None:
                return
            if cam.position.flatDistTo(self.__avatar.position) >= self.FOLLOW_CAMERA_MAX_DEVIATION:
                self.moveTo(cam.position)
            return constants.SERVER_TICK_LENGTH

    def __doBind(self, vehicleID):
        if BattleReplay.isServerSideReplay():
            BattleReplay.g_replayCtrl.bindToVehicleForServerSideReplay(vehicleID)
        else:
            self.__avatar.cell.bindToVehicle(vehicleID)

    def __doUnbind(self, vehicleID=None):
        if vehicleID is None:
            vehicleID = 0
        if BattleReplay.isServerSideReplay():
            BattleReplay.g_replayCtrl.bindToVehicleForServerSideReplay(vehicleID)
        else:
            self.__avatar.cell.bindToVehicle(vehicleID)
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isRecording:
            replayCtrl.setPlayerVehicleID(0)
        return
