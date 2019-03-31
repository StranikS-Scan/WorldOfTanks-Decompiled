# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarPositionControl.py
# Compiled at: 2011-02-21 20:06:04
import BigWorld
import constants
import weakref
from debug_utils import *
import time

class AvatarPositionControl:
    FOLLOW_CAMERA_MAX_DEVIATION = 10.0

    def __init__(self, avatar):
        self.__avatar = weakref.proxy(avatar)
        self.__bFollowCamera = False

    def destroy(self):
        self.__avatar = None
        return

    def bindToVehicle(self, bValue=True, vehicleID=None):
        if bValue:
            if vehicleID is None:
                vehicleID = self.__avatar.playerVehicleID
            self.__doBind(vehicleID)
        else:
            self.__doUnbind()
        return

    def followCamera(self, bValue=True):
        self.__bFollowCamera = bValue
        if bValue:
            self.onFollowCameraTick()

    def moveTo(self, pos):
        self.__avatar.cell.moveTo(pos)

    def getFollowCamera(self):
        return self.__bFollowCamera

    def onFollowCameraTick(self):
        if not self.__bFollowCamera:
            return
        else:
            cam = BigWorld.camera()
            if cam is None:
                return
            if BigWorld.camera().position.flatDistTo(self.__avatar.position) >= self.FOLLOW_CAMERA_MAX_DEVIATION:
                self.moveTo(BigWorld.camera().position)
            return

    def __doBind(self, vehicleID):
        pos = self.__avatar.arena.positions.get(vehicleID)
        if pos is None and vehicleID == self.__avatar.playerVehicleID:
            pos = self.__avatar.getOwnVehiclePosition()
        if pos is None:
            pos = self.__avatar.position
        self.__avatar.cell.bindToVehicle(vehicleID, pos)
        return

    def __doUnbind(self):
        self.__avatar.cell.bindToVehicle(0, self.__avatar.position)
