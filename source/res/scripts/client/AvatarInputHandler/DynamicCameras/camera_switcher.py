# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/DynamicCameras/camera_switcher.py
import time
import typing
from enum import Enum
import BigWorld
import math_utils

class SWITCH_TYPES(Enum):
    FROM_MAX_DIST = 0
    FROM_MIN_DIST = 1


class CameraSwitcher(object):
    _TIMEOUT_TIME = 0.35
    _INTERVAL_TO_SWITCH = 0.2
    __slots__ = ('__switchType', '__switchToName', '__switchToPos', '__lastDist', '__intervalToSwitch', '__lastScrollTime', '__hasTimeout', '__timeoutCallback', '__timeoutTime')

    def __init__(self, switchType, switchToName, switchToPos, intervalToSwitch=_INTERVAL_TO_SWITCH, timeoutTime=_TIMEOUT_TIME):
        self.__switchType = switchType
        self.__switchToName = switchToName
        self.__switchToPos = switchToPos
        self.__lastDist = None
        self.__hasTimeout = None
        self.__timeoutCallback = None
        self.__timeoutTime = timeoutTime
        self.__intervalToSwitch = intervalToSwitch
        self.__lastScrollTime = 0
        return

    def clear(self):
        self.__lastDist = None
        self.__clearTimeout()
        return

    def getSwitchParams(self):
        return (self.__switchToName, self.__switchToPos)

    def needToSwitch(self, zValue, dist, minValue, maxValue):
        if self.__switchType == SWITCH_TYPES.FROM_MAX_DIST:
            result = self.__switchFromDist(zValue, dist, maxValue)
        else:
            result = self.__switchFromDist(zValue, dist, minValue)
        self.__lastDist = dist
        return result

    def __clearTimeout(self):
        if self.__timeoutCallback is not None:
            BigWorld.cancelCallback(self.__timeoutCallback)
            self.__timeoutCallback = None
        self.__hasTimeout = None
        return

    def __setTimeout(self):
        self.__hasTimeout = False
        self.__timeoutCallback = None
        return

    def __switchFromDist(self, zValue, dist, value):
        currentScrollInterval = None
        if zValue != 0:
            currentTime = time.time()
            currentScrollInterval = currentTime - self.__lastScrollTime
            self.__lastScrollTime = currentTime
        if self.__lastDist == dist:
            isEqual = math_utils.almostZero(value - dist)
            if isEqual and self.__hasTimeout is None and self.__timeoutTime:
                self.__hasTimeout = True
                self.__timeoutCallback = BigWorld.callback(self.__timeoutTime, self.__setTimeout)
            if isEqual and currentScrollInterval is not None:
                return not self.__hasTimeout or currentScrollInterval > self.__intervalToSwitch
        else:
            self.__clearTimeout()
        return False


class CameraSwitcherCollection(object):

    def __init__(self, cameraSwitchers, isEnabled=True):
        self.__cameraSwitchers = cameraSwitchers
        self.__isEnabled = isEnabled
        self.__switchParams = None
        return

    def clear(self):
        for switcher in self.__cameraSwitchers:
            switcher.clear()

    def setIsEnabled(self, isEnabled):
        self.__isEnabled = isEnabled

    def getSwitchParams(self):
        return self.__switchParams

    def needToSwitch(self, zValue, dist, minValue, maxValue):
        if not self.__isEnabled:
            return False
        for switcher in self.__cameraSwitchers:
            if switcher.needToSwitch(zValue, dist, minValue, maxValue):
                self.__switchParams = switcher.getSwitchParams()
                return True

        return False
