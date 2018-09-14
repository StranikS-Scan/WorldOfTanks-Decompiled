# Embedded file name: scripts/client/AvatarPositionControl.py
import BigWorld
import constants
import weakref
import BattleReplay
from debug_utils import *
import time
from AvatarInputHandler.CallbackDelayer import CallbackDelayer

class AvatarPositionControl(CallbackDelayer):
    FOLLOW_CAMERA_MAX_DEVIATION = 7.0

    def __init__(self, avatar):
        CallbackDelayer.__init__(self)
        self.__avatar = weakref.proxy(avatar)
        self.__bFollowCamera = False

    def destroy(self):
        self.__avatar = None
        CallbackDelayer.destroy(self)
        return

    def bindToVehicle(self, bValue = True, vehicleID = None):
        if bValue:
            if vehicleID is None:
                vehicleID = self.__avatar.playerVehicleID
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
