# Embedded file name: scripts/client/Vibroeffects/Controllers/TrackBreakingController.py
import BigWorld
import Math
from Math import Matrix
from debug_utils import *
import math
import copy
from Vibroeffects.Controllers.OnceController import OnceController

class TrackBreakingController:
    __MIN_MOVEMENT_SPEED = 1
    __wasLeftTrackBroken = None
    __wasRightTrackBroken = None
    __ANGLES_VIBRATIONS = [[math.pi / 4, 'crit_track_front_right_veff'],
     [math.pi / 2 + math.pi / 4, 'crit_track_front_left_veff'],
     [math.pi + math.pi / 4, 'crit_track_rear_left_veff'],
     [math.pi * 3 / 2 + math.pi / 4, 'crit_track_rear_right_veff']]

    def __break(self, vehicleSpeed):
        if vehicleSpeed < TrackBreakingController.__MIN_MOVEMENT_SPEED:
            OnceController('crit_track_veff')
        else:
            OnceController('move_track_veff')

    def __breakWithDirection(self, vehicle, isLeftTrackBroken):
        cameraDirection = Math.Vector3(BigWorld.camera().direction)
        cameraDirection.y = 0
        vehicleMatrix = Math.Matrix(vehicle.matrix)
        vehicleMatrix.setElement(3, 0, 0)
        vehicleMatrix.setElement(3, 1, 0)
        vehicleMatrix.setElement(3, 2, 0)
        vehicleMatrix.invert()
        cameraDirection = vehicleMatrix.applyVector(cameraDirection)
        brokenTrackAngle = 0
        if isLeftTrackBroken:
            brokenTrackAngle = math.pi
        dirAngleRelative = math.atan2(cameraDirection.z, cameraDirection.x)
        minDirDelta = math.pi * 2
        vibrationToPlay = ''
        for angleVibration in TrackBreakingController.__ANGLES_VIBRATIONS:
            curAngle = angleVibration[0]
            curAngle += dirAngleRelative
            if curAngle > math.pi * 2:
                curAngle -= math.pi * 2
            if curAngle < 0:
                curAngle += math.pi * 2
            curDirDelta = abs(curAngle - brokenTrackAngle)
            if curDirDelta > math.pi:
                curDirDelta = math.pi * 2 - curDirDelta
            if curDirDelta < minDirDelta:
                minDirDelta = curDirDelta
                vibrationToPlay = angleVibration[1]

        OnceController(vibrationToPlay)

    def update(self, vehicle, isLeftTrackBroken, isRightTrackBroken):
        if self.__wasLeftTrackBroken == False and isLeftTrackBroken:
            self.__breakWithDirection(vehicle, True)
        elif self.__wasRightTrackBroken == False and isRightTrackBroken:
            self.__breakWithDirection(vehicle, False)
        self.__wasLeftTrackBroken = isLeftTrackBroken
        self.__wasRightTrackBroken = isRightTrackBroken
