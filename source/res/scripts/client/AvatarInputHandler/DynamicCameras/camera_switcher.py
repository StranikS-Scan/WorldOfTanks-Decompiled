# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/DynamicCameras/camera_switcher.py
import time
import typing
from enum import Enum
import BigWorld
import math_utils

class SwitchTypes(Enum):
    FROM_MAX_DIST = 0
    FROM_MIN_DIST = 1
    FROM_TRANSITION_DIST_AS_MAX = 2
    FROM_TRANSITION_DIST_AS_MIN = 3


class SwitchToPlaces(Enum):
    TO_RELATIVE_POS = 0
    TO_TRANSITION_DIST = 1
    TO_NEAR_POS = 2


TRANSITION_DIST_HYSTERESIS = 0.01

class CameraSwitcher(object):
    _TIMEOUT_TIME = 0.35
    _INTERVAL_TO_SWITCH = 0.2
    __slots__ = ('__switchType', '__switchToName', '__switchToPos', '__lastDist', '__intervalToSwitch', '__lastScrollTime', '__hasTimeout', '__timeoutCallback', '__timeoutTime', '__transitionValue', '__switchToPlaceType')

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
        if self.__switchType in (SwitchTypes.FROM_TRANSITION_DIST_AS_MAX, SwitchTypes.FROM_TRANSITION_DIST_AS_MIN):
            self.__switchToPlaceType = SwitchToPlaces.TO_TRANSITION_DIST
        else:
            self.__switchToPlaceType = SwitchToPlaces.TO_RELATIVE_POS
        return

    def clear(self):
        self.__lastDist = None
        self.__clearTimeout()
        return

    def getSwitchParams(self):
        return (self.__switchToName, self.__switchToPos, self.__switchToPlaceType)

    def needToSwitch(self, zValue, dist, minValue, maxValue, transitionValue=None):
        if transitionValue is not None:
            transMin, transMax = self.getDistLimitationForSwitch(minValue, maxValue, transitionValue)
        else:
            transMin = minValue
            transMax = maxValue
        if self.__switchType == SwitchTypes.FROM_MAX_DIST:
            result = self.__switchFromDist(zValue, dist, maxValue)
        elif self.__switchType == SwitchTypes.FROM_TRANSITION_DIST_AS_MAX:
            result = self.__switchFromDist(zValue, dist, transMax)
        elif self.__switchType == SwitchTypes.FROM_TRANSITION_DIST_AS_MIN:
            result = self.__switchFromDist(zValue, dist, transMin)
        else:
            result = self.__switchFromDist(zValue, dist, minValue)
        self.__lastDist = dist
        return result

    def getDistLimitationForSwitch(self, minValue, maxValue, transitionValue):
        resultMin = minValue
        resultMax = maxValue
        if self.__switchType == SwitchTypes.FROM_TRANSITION_DIST_AS_MIN:
            resultMin = max(transitionValue, minValue)
        elif self.__switchType == SwitchTypes.FROM_TRANSITION_DIST_AS_MAX:
            resultMax = min(maxValue, transitionValue)
        return (resultMin, resultMax)

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

    def isEnabled(self):
        return self.__isEnabled

    def needToSwitch(self, zValue, dist, minValue, maxValue, transitionValue=None):
        if not self.__isEnabled:
            return False
        for switcher in self.__cameraSwitchers:
            if switcher.needToSwitch(zValue, dist, minValue, maxValue, transitionValue):
                self.__switchParams = switcher.getSwitchParams()
                return True

        return False

    def getDistLimitationForSwitch(self, minValue, maxValue, transitionValue):
        if not self.__isEnabled:
            return (minValue, maxValue)
        resMinValue = minValue
        resMaxValue = maxValue
        for switcher in self.__cameraSwitchers:
            curMinValue, curMaxValue = switcher.getDistLimitationForSwitch(minValue, maxValue, transitionValue)
            resMinValue = max(curMinValue, resMinValue)
            resMaxValue = min(curMaxValue, resMaxValue)

        return (resMinValue, resMaxValue)
