# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_cameras/hangar_camera_yaw_filter.py
import math
import math_utils
_EPS = 0.001

class HangarCameraYawFilter(object):

    def __init__(self, start, length, camSens):
        self.__offset = start
        self.__length = length
        self.__cycled = self.__length > 2.0 * math.pi - _EPS
        self.__camSens = camSens
        self.__prevDirection = 0.0

    def toLimit(self, inAngle):
        inAngle = math_utils.reduceToPI(inAngle)
        inAngle = self.__normalize(inAngle)
        if not self.__cycled and inAngle > self.__length:
            if inAngle - self.__length < 2.0 * math.pi - inAngle:
                return self.__refresh(self.__length)
            return self.__refresh(0.0)
        return self.__refresh(inAngle)

    def getNextYaw(self, currentYaw, targetYaw, delta):
        if delta == 0.0:
            return targetYaw
        if self.__prevDirection * delta < 0.0:
            targetYaw = currentYaw
        self.__prevDirection = delta
        nextYaw = targetYaw + delta * self.__camSens
        if delta > 0.0:
            if nextYaw >= currentYaw:
                deltaYaw = nextYaw - currentYaw
            else:
                deltaYaw = 2.0 * math.pi + nextYaw - currentYaw
            if deltaYaw > math.pi:
                nextYaw = currentYaw + math.pi * 0.9
        else:
            if nextYaw <= currentYaw:
                deltaYaw = currentYaw - nextYaw
            else:
                deltaYaw = 2.0 * math.pi - nextYaw + currentYaw
            if deltaYaw > math.pi:
                nextYaw = currentYaw - math.pi * 0.9
        nextYaw = math_utils.reduceToPI(nextYaw)
        nextYaw = self.__normalize(nextYaw)
        currentYaw = self.__normalize(currentYaw)
        if not self.__cycled:
            if delta > 0.0 and (nextYaw > self.__length or nextYaw < currentYaw):
                return self.__refresh(self.__length)
            if delta < 0.0 and (nextYaw > self.__length or nextYaw > currentYaw):
                return self.__refresh(0.0)
        return self.__refresh(nextYaw)

    def __normalize(self, angle):
        angle -= self.__offset
        if angle < -_EPS:
            angle += 2.0 * math.pi
        elif angle > 2.0 * math.pi + _EPS:
            angle -= 2.0 * math.pi
        return angle

    def __refresh(self, angle):
        angle += self.__offset
        return math_utils.reduceToPI(angle)
