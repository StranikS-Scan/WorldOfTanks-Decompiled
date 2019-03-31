# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/PostmortemDelay.py
# Compiled at: 2011-01-05 17:09:23
import BigWorld
import Math
import cameras
import constants
from PlayerEvents import g_playerEvents
from constants import ARENA_PERIOD
from debug_utils import *
import math

class PostmortemDelay:
    FADE_DELAY_TIME = 2.0
    KILLER_VISION_TIME = 5.0
    KILLER_VEHICLE_CAMERA_DISTANCE = 15.0
    KILLER_VEHICLE_CAMERA_PIVOT_POSITION = Math.Vector3(0.0, 1.5, 3.0)
    KILLER_VEHICLE_PITCH_OFFSET = -0.3

    def __init__(self, arcadeCamera, onStop):
        assert isinstance(arcadeCamera, cameras.ArcadeCamera)
        self.__killerVehicleID = None
        self.__bActive = False
        self.__bChoiceWindowActive = False
        self.__bFadeScreenActive = False
        self.__bKillerVisionActive = False
        self.__savedPivotPosition = None
        self.__savedCameraDistance = None
        self.__savedYawPitch = None
        self.__arcadeCamera = arcadeCamera
        self.__onStop = onStop
        self.__cbIDWait = None
        BigWorld.player().onVehicleLeaveWorld += self.__onVehicleLeaveWorld
        g_playerEvents.onArenaPeriodChange += self.__onRoundFinished
        return

    def destroy(self):
        self.stop()
        self.__arcadeCamera = None
        self.__onStop = None
        BigWorld.player().onVehicleLeaveWorld -= self.__onVehicleLeaveWorld
        g_playerEvents.onArenaPeriodChange -= self.__onRoundFinished
        return

    def start(self):
        if self.__bActive:
            return
        self.__bActive = True
        self.__fadeScreen()
        self.__moveCameraTo(BigWorld.player().playerVehicleID)
        self.__cbIDWait = BigWorld.callback(self.FADE_DELAY_TIME, self.__onFadeDelay)

    def stop(self):
        if not self.__bActive:
            return
        else:
            self.__cancelWait()
            self.__showChoiceWindow(False)
            self.__fadeScreen(bFade=False)
            self.__bKillerVisionActive = False
            self.__moveCameraTo(BigWorld.player().playerVehicleID)
            self.__killerVehicleID = None
            self.__savedPivotPosition = None
            self.__savedCameraDistance = None
            self.__savedYawPitch = None
            self.__bActive = False
            try:
                self.__onStop()
            except:
                LOG_CURRENT_EXCEPTION()

            return

    def __fadeScreen(self, bFade=True):
        if self.__bFadeScreenActive == bFade:
            return
        self.__bFadeScreenActive = bFade
        if bFade:
            pass

    def __showChoiceWindow(self, bShow=True):
        if self.__bChoiceWindowActive == bShow:
            return
        self.__bChoiceWindowActive = bShow
        if bShow:
            self.__onContinueBattle()

    def __moveCameraTo(self, vehicleID, sourceVehicleID=None):
        vehicle = BigWorld.entity(vehicleID)
        if vehicle is None:
            if vehicleID == BigWorld.player().playerVehicleID:
                self.__setCameraSettings(targetMP=BigWorld.player().getOwnVehicleMatrix(), pivotPosition=self.__savedPivotPosition, cameraDistance=self.__savedCameraDistance, yawPitch=self.__savedYawPitch)
                return True
            return False
        else:
            self.__setCameraSettings(targetMP=vehicle.matrix, pivotPosition=self.__savedPivotPosition, cameraDistance=self.__savedCameraDistance, yawPitch=self.__savedYawPitch)
            if sourceVehicleID is not None:
                sourceVehicle = BigWorld.entity(sourceVehicleID)
                if sourceVehicle is not None:
                    self.__savedPivotPosition = self.__arcadeCamera.getPivotPosition()
                    self.__savedCameraDistance = self.__arcadeCamera.getCameraDistance()
                    self.__savedYawPitch = self.__arcadeCamera.getYawPitch()
                    dir = Math.Matrix(vehicle.matrix).translation - Math.Matrix(sourceVehicle.matrix).translation
                    yaw = dir.yaw
                    pitch = dir.pitch + self.KILLER_VEHICLE_PITCH_OFFSET
                    if pitch > math.pi * 0.5:
                        pitch = math.pi * 0.5
                    if pitch < -math.pi * 0.5:
                        pitch = -math.pi * 0.5
                    self.__setCameraSettings(pivotPosition=Math.Vector3(self.KILLER_VEHICLE_CAMERA_PIVOT_POSITION), cameraDistance=self.KILLER_VEHICLE_CAMERA_DISTANCE, yawPitch=(yaw, pitch))
            return True

    def __setCameraSettings(self, targetMP=None, pivotPosition=None, cameraDistance=None, yawPitch=None):
        if targetMP is not None:
            self.__arcadeCamera.camera.target = targetMP
        if pivotPosition is not None:
            self.__arcadeCamera.setPivotPosition(pivotPosition)
        if cameraDistance is not None:
            self.__arcadeCamera.setCameraDistance(cameraDistance)
        if yawPitch is not None:
            self.__arcadeCamera.setYawPitch(yawPitch[0], yawPitch[1])
        return

    def __onFadeDelay(self):
        self.__cbIDWait = None
        if self.__killerVehicleID is None:
            self.__killerVehicleID = BigWorld.player().inputHandler.getKillerVehicleID()
        if self.__killerVehicleID is None:
            self.stop()
            return
        else:
            self.__startKillerVision()
            return

    def __startKillerVision(self):
        if not self.__moveCameraTo(self.__killerVehicleID, BigWorld.player().playerVehicleID):
            LOG_DEBUG("<PostmortemDelay>: can't move camera to killer vehicle")
            self.__showChoiceWindow()
            return
        self.__bKillerVisionActive = True
        self.__cbIDWait = BigWorld.callback(self.KILLER_VISION_TIME, self.__onKillerVisionFinished)

    def __onKillerVisionFinished(self):
        self.__cbIDWait = None
        self.__bKillerVisionActive = False
        self.__moveCameraTo(BigWorld.player().playerVehicleID)
        self.__showChoiceWindow()
        return

    def __onContinueBattle(self):
        self.stop()

    def __onVehicleLeaveWorld(self, vehicle):
        if not self.__bActive:
            return
        if vehicle.id == self.__killerVehicleID:
            if self.__bKillerVisionActive:
                self.__arcadeCamera.camera.target = Math.Matrix(self.__arcadeCamera.camera.target)

    def __onRoundFinished(self, period, *args):
        if period != ARENA_PERIOD.AFTERBATTLE:
            return
        self.stop()

    def __cancelWait(self):
        if self.__cbIDWait is not None:
            BigWorld.cancelCallback(self.__cbIDWait)
            self.__cbIDWait = None
        return
