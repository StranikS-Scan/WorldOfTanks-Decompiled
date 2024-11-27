# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/DynamicCameras/arcade_camera_helper.py
from enum import Enum
from collections import namedtuple
import math
import time
import math_utils
from AvatarInputHandler.cameras import readFloat, readVec2, readInt, readString
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
LINEAR_EASING = math_utils.Easing.linearEasing
SQUARE_EASING = math_utils.Easing.squareEasing
EXPONENTIAL_EASING = math_utils.Easing.exponentialEasing
EASING_FUNCTION_MAP = {1: LINEAR_EASING,
 2: SQUARE_EASING,
 3: EXPONENTIAL_EASING}
MinMax = namedtuple('MinMax', ('min', 'max'))
ZoomState = namedtuple('ZoomState', ('distRange', 'scrollSensitivity', 'sensitivity', 'angleRangeOnMinDist', 'angleRangeOnMaxDist', 'transitionDurationIn', 'transitionDurationOut', 'transitionEasingIn', 'transitionEasingOut', 'focusRadiusOnMinMaxDist', 'heightAboveBaseOnMinMaxDist', 'overScrollProtectOnMax', 'overScrollProtectOnMin', 'minLODBiasForTanks', 'settingsKey'))

def readAngle(dataSec, name, minVal, maxVal, defaultVal):
    angle = readVec2(dataSec, name, minVal, maxVal, defaultVal)
    angle[0] = math.radians(angle[0]) - math.pi * 0.5
    angle[1] = math.radians(angle[1]) - math.pi * 0.5
    return angle


def readEasing(dataSec, name, minVal, maxVal, defaultVal):
    easing = readInt(dataSec, name, minVal, maxVal, defaultVal)
    return EASING_FUNCTION_MAP[easing]


def readZoomState(dataSec):
    if dataSec is None:
        return
    else:
        distRangeVec = readVec2(dataSec, 'distRange', (1, 1), (180, 180), (25, 45))
        distRange = MinMax(distRangeVec.x, distRangeVec.y)
        scrollSensitivity = readFloat(dataSec, 'scrollSensitivity', 0, 50, 10)
        sensitivity = readFloat(dataSec, 'sensitivity', 0, 5, 0.002)
        overScrollProtectOnMax = readFloat(dataSec, 'overScrollProtectOnMax', 0, 10, 0)
        overScrollProtectOnMin = readFloat(dataSec, 'overScrollProtectOnMin', 0, 10, 0)
        angleRangeOnMinDist = readAngle(dataSec, 'angleRangeOnMinDist', (1, 1), (180, 180), (10, 110))
        angleRangeOnMaxDist = readAngle(dataSec, 'angleRangeOnMaxDist', (1, 1), (180, 180), (10, 110))
        transitionDurationIn = readFloat(dataSec, 'transitionDurationIn', 0, 5, 0.5)
        transitionDurationOut = readFloat(dataSec, 'transitionDurationOut', 0, 5, 0.5)
        transitionEasingIn = readEasing(dataSec, 'transitionEasingIn', 1, 3, 3)
        transitionEasingOut = readEasing(dataSec, 'transitionEasingOut', 1, 3, 3)
        focusRadiusOnMinMaxDistVec = readVec2(dataSec, 'focusRadiusOnMinMaxDist', (-100, -100), (100, 100), (3, 3))
        focusRadiusOnMinMaxDist = MinMax(focusRadiusOnMinMaxDistVec.x, focusRadiusOnMinMaxDistVec.y)
        heightAboveBaseOnMinMaxDistVec = readVec2(dataSec, 'heightAboveBaseOnMinMaxDist', (1, 1), (180, 180), (3, 3))
        heightAboveBaseOnMinMaxDist = MinMax(heightAboveBaseOnMinMaxDistVec.x, heightAboveBaseOnMinMaxDistVec.y)
        minLODBiasForTanks = readFloat(dataSec, 'minLODBiasForTanks', 0, 5, 0.0)
        settingsKey = readString(dataSec, 'settingsKey', '')
        return ZoomState(distRange=distRange, scrollSensitivity=scrollSensitivity, sensitivity=sensitivity, angleRangeOnMinDist=angleRangeOnMinDist, angleRangeOnMaxDist=angleRangeOnMaxDist, transitionDurationIn=transitionDurationIn, transitionDurationOut=transitionDurationOut, focusRadiusOnMinMaxDist=focusRadiusOnMinMaxDist, heightAboveBaseOnMinMaxDist=heightAboveBaseOnMinMaxDist, overScrollProtectOnMax=overScrollProtectOnMax, overScrollProtectOnMin=overScrollProtectOnMin, transitionEasingIn=transitionEasingIn, transitionEasingOut=transitionEasingOut, minLODBiasForTanks=minLODBiasForTanks, settingsKey=settingsKey)


class EScrollDir(Enum):
    IN = 0
    OUT = 1

    @staticmethod
    def convertDZ(dz):
        if dz == 0:
            return None
        else:
            return EScrollDir.IN if dz > 0 else EScrollDir.OUT


class OverScrollProtector(object):
    __slots__ = ('__lastScrollTime', '__interval', '__eScrollDirection')

    def __init__(self):
        self.__interval = None
        self.__lastScrollTime = None
        self.__eScrollDirection = None
        return

    def start(self, interval, eScrollDirection):
        if interval > 0 and eScrollDirection in (EScrollDir.IN, EScrollDir.OUT):
            self.__interval = interval
            self.__eScrollDirection = eScrollDirection
            self.__lastScrollTime = time.time()
        else:
            self.reset()

    def updateOnScroll(self, eScrollDirection):
        if not self.isProtecting():
            return
        if eScrollDirection != self.__eScrollDirection:
            self.reset()
            return
        currentTime = time.time()
        currentScrollInterval = currentTime - self.__lastScrollTime
        if currentScrollInterval < self.__interval:
            self.__lastScrollTime = currentTime
        else:
            self.reset()

    def isProtecting(self):
        return bool(self.__lastScrollTime)

    def reset(self):
        self.__interval = None
        self.__lastScrollTime = None
        self.__eScrollDirection = None
        return


class ZoomStateSwitcher(object):
    __slots__ = ('__zoomStates', '__index', '__currentZoomState')
    __settings = dependency.descriptor(ISettingsCore)
    _NONE_INDEX = -1

    def __init__(self):
        self.__zoomStates = []
        self.__index = self._NONE_INDEX
        self.__currentZoomState = None
        return

    def __iter__(self):
        return iter(self.__zoomStates)

    def loadConfig(self, dataSection):
        self.__zoomStates = []
        self.reset()
        self.__currentZoomState = None
        if dataSection:
            for data in dataSection.values():
                state = readZoomState(data)
                if state:
                    self.__zoomStates.append(state)

        return

    def isEmpty(self):
        return not self.__zoomStates

    def reset(self):
        self.__index = self._NONE_INDEX

    def switchToState(self, stateName):
        for index, state in enumerate(self.__zoomStates):
            if state.settingsKey == stateName:
                self.setCurrentState(state)
                self.__index = index
                return

        self.reset()
        self.setCurrentState(None)
        return

    def getNextState(self):
        return self.__getState(lambda i: i + 1, self.__index)

    def getPrevState(self):
        return self.__getState(lambda i: i - 1, self.__index)

    def setCurrentState(self, zoomState):
        self.__currentZoomState = zoomState

    def getCurrentState(self):
        return self.__currentZoomState

    def __getState(self, func, startIndex):
        index = func(startIndex)
        if self.__isIndexValid(index):
            if not self.__isEnabledBySettings(index):
                return self.__getState(func, index)
            self.__index = index
            return self.__zoomStates[index]
        else:
            return None

    def __isIndexValid(self, index):
        return self.__zoomStates and 0 <= index < len(self.__zoomStates)

    def __isEnabledBySettings(self, index):
        if self.__isIndexValid(index):
            state = self.__zoomStates[index]
            if state.settingsKey and self.__settings.isReady:
                return bool(self.__settings.options.getSetting(state.settingsKey).get())
            return True
        return False


class CollideAnimatorEasing(object):

    def __init__(self):
        self.__easing = None
        return

    def start(self, distance, interval):
        if self.__easing is None:
            self.__easing = SQUARE_EASING(0.0, distance, interval)
        return

    def update(self, deltaTime):
        if self.__easing:
            self.__easing.update(deltaTime)
            result = self.__easing.value
            if result > self.__easing.b / 2:
                result = self.__easing.b - result
            if self.__easing.stopped:
                self.stop()
            return result

    def stop(self):
        self.__easing = None
        return
