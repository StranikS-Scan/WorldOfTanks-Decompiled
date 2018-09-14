# Embedded file name: scripts/client/AvatarInputHandler/ArtyHitMarker.py
from helpers.CallbackDelayer import CallbackDelayer
from AvatarInputHandler.control_modes import _SuperGunMarker, _SPGFlashGunMarker
import BattleReplay
import BigWorld
import Math
from Math import Vector3, Matrix
import math
from AvatarInputHandler import mathUtils
from ProjectileMover import getCollidableEntities

class ArtyHitMarker(_SPGFlashGunMarker, CallbackDelayer):

    def __init__(self, curShotInfoFunc, dispersionUpdateFunc, desiredShotInfoFunc):
        _SPGFlashGunMarker.__init__(self, curShotInfoFunc, dispersionUpdateFunc, _SuperGunMarker.GUN_MARKER_CLIENT)
        CallbackDelayer.__init__(self)
        self.__updateInterval = 0.0 if BattleReplay.g_replayCtrl.isPlaying else 0.1
        self.__desiredShotInfoFunc = desiredShotInfoFunc
        self.__trajectoryDrawer = BigWorld.wg_trajectory_drawer()

    def create(self):
        _SPGFlashGunMarker.create(self)
        self.__trajectoryDrawer.setColors(Math.Vector4(0, 255, 0, 255), Math.Vector4(255, 0, 0, 255), Math.Vector4(128, 128, 128, 255))
        self.__trajectoryDrawer.setGetDynamicCollidersCallback(lambda start, end: [ e.collideSegment for e in getCollidableEntities((BigWorld.player().playerVehicleID,), start, end) ])

    def setupShotParams(self, shotDescr, offset = (0, 0)):
        self.__trajectoryDrawer.setParams(shotDescr['maxDistance'], Math.Vector3(0, -shotDescr['gravity'], 0), offset)

    def destroy(self):
        _SPGFlashGunMarker.destroy(self)
        CallbackDelayer.destroy(self)
        self.__desiredShotInfoFunc = None
        self.__trajectoryDrawer.visible = False
        self.__trajectoryDrawer = None
        return

    def enable(self, state):
        _SPGFlashGunMarker.enable(self, state)
        self.delayCallback(self.__updateInterval, self.__tick)

    def disable(self):
        _SPGFlashGunMarker.disable(self)
        self.stopCallback(self.__tick)

    def setGUIVisible(self, isVisible, valueUpdate = False):
        _SPGFlashGunMarker.show(self, isVisible)
        self.__trajectoryDrawer.visible = isVisible

    def __tick(self):
        desiredPos, startPos, startVelocity = self.__desiredShotInfoFunc()
        self.__trajectoryDrawer.update(desiredPos, startPos, startVelocity, self.__updateInterval)
        return self.__updateInterval
