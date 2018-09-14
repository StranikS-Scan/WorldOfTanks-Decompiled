# Embedded file name: scripts/client/AvatarPositionControl.py
from AvatarInputHandler import mathUtils
import BigWorld
import Math
from Event import Event
import constants
import weakref
import BattleReplay
from debug_utils import *
import time
from helpers.CallbackDelayer import CallbackDelayer

def logFunc(func):

    def wrapped(*args, **kwargs):
        LOG_DEBUG('|||||||||||||||||| %s(%s, %s) |||||||||||' % (func.func_name, args, kwargs))
        func(*args, **kwargs)

    return wrapped


class ConsistentMatrices(object):
    attachedVehicleMatrix = property(lambda self: self.__attachedVehicleMatrix)
    ownVehicleMatrix = property(lambda self: self.__ownVehicleMProv)

    def __init__(self):
        self.__attachedVehicleMatrix = Math.WGAdaptiveMatrixProvider()
        self.__attachedVehicleMatrix.target = mathUtils.createIdentityMatrix()
        self.__ownVehicleMProv = Math.WGAdaptiveMatrixProvider()
        self.__ownVehicleMProv.target = mathUtils.createIdentityMatrix()
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

    def notifyPreBind(self, avatar, targetVehicleID = None):
        bindMatrix = Math.Matrix(self.attachedVehicleMatrix)
        useStatic = True
        if avatar.vehicle is not None and avatar.vehicle.id == targetVehicleID:
            bindMatrix = avatar.vehicle.matrix
            useStatic = False
        self.__setTarget(bindMatrix, useStatic)
        return

    def notifyVehicleChanged(self, avatar):
        if avatar.vehicle is None or not avatar.vehicle.isStarted:
            self.__attachedVehicleMatrix.target = None
            self.onVehicleMatrixBindingChanged(True)
            return
        else:
            if avatar.vehicle.id == avatar.playerVehicleID:
                self.__linkOwnVehicle(avatar.vehicle)
            self.__setTarget(avatar.vehicle.matrix, False)
            return

    def notifyViewPointChanged(self, avatar, staticPosition = None):
        if staticPosition is not None:
            self.__setTarget(mathUtils.createTranslationMatrix(staticPosition))
        return

    def __setTarget(self, matrix, asStatic = True):
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
        else:
            self.__ownVehicleMProv.target = vehicle.matrix


class AvatarPositionControl(CallbackDelayer):
    FOLLOW_CAMERA_MAX_DEVIATION = 7.0
    onAvatarVehicleChanged = property(lambda self: self.__onAvatarVehicleChanged)

    def __init__(self, avatar):
        CallbackDelayer.__init__(self)
        self.__avatar = weakref.proxy(avatar)
        self.__bFollowCamera = False

    def destroy(self):
        self.__avatar = None
        CallbackDelayer.destroy(self)
        return

    def bindToVehicle(self, bValue = True, vehicleID = None):
        if vehicleID is None:
            vehicleID = self.__avatar.playerVehicleID
        BigWorld.player().consistentMatrices.notifyPreBind(BigWorld.player(), vehicleID)
        if bValue:
            self.__doBind(vehicleID)
        else:
            self.__doUnbind()
        return

    def followCamera(self, bValue = True):
        self.__bFollowCamera = bValue
        if bValue:
            self.delayCallback(constants.SERVER_TICK_LENGTH, self.__followCameraTick)
        else:
            self.stopCallback(self.__followCameraTick)

    def switchViewpoint(self, toPrevious):
        BigWorld.player().consistentMatrices.notifyPreBind(BigWorld.player())
        self.__avatar.cell.switchViewpoint(toPrevious)

    def moveTo(self, pos):
        self.__avatar.cell.moveTo(pos)

    def getFollowCamera(self):
        return self.__bFollowCamera

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
        self.__avatar.cell.bindToVehicle(vehicleID)

    def __doUnbind(self):
        self.__avatar.cell.bindToVehicle(0)
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isRecording:
            replayCtrl.setPlayerVehicleID(0)
