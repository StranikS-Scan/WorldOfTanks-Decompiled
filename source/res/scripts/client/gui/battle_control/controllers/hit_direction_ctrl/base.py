# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/hit_direction_ctrl/base.py
from enum import Enum
import BigWorld

class HitType(Enum):
    HIT_DAMAGE = 0
    ARTY_HIT_PREDICTION = 1


class IHitIndicator(object):

    def getHitType(self):
        raise NotImplementedError

    def destroy(self):
        raise NotImplementedError

    def getDuration(self):
        raise NotImplementedError

    def getBeginAnimationDuration(self):
        raise NotImplementedError

    def setVisible(self, flag):
        raise NotImplementedError

    def showHitDirection(self, idx, hitData, timeLeft):
        raise NotImplementedError

    def invalidateSettings(self, diff=None):
        pass

    def hideHitDirection(self, idx):
        raise NotImplementedError


class HitDirection(object):
    __slots__ = ('__idx', '__hitData', '__startTime', '__isShown', '__indicator')

    def __init__(self, idx):
        super(HitDirection, self).__init__()
        self.__idx = idx
        self.__hitData = None
        self.__startTime = 0
        self.__isShown = False
        self.__indicator = None
        return

    def __repr__(self):
        return '_HitDirection(idx={0}, hitData={1}, startTime={2}, isShown={3}, hasUI={4})'.format(self.__idx, self.__hitData, self.__startTime, self.__isShown, self.__indicator is not None)

    def clear(self):
        self.__hitData = None
        self.__startTime = 0
        self.__isShown = False
        self.__indicator = None
        return

    def getIndex(self):
        return self.__idx

    def getHitData(self):
        return self.__hitData

    def isShown(self):
        return self.__isShown

    def getIndicator(self):
        return self.__indicator

    def getTimeLeft(self):
        if self.__isShown:
            timeLeft = BigWorld.time() - self.__startTime
        else:
            timeLeft = 0
        return timeLeft

    def getStartTime(self):
        return self.__startTime

    def setIndicator(self, indicator):
        self.__indicator = indicator
        return self.redraw()

    def redraw(self):
        duration = 0
        if self.__isShown and self.__hitData is not None and self.__indicator is not None:
            timeLeft = BigWorld.time() - self.__startTime
            duration = self.__indicator.getDuration()
            if timeLeft < duration:
                self.__indicator.showHitDirection(self.__idx, self.__hitData, timeLeft)
            else:
                duration = 0
        return duration

    def show(self, hitData, extend=False):
        self.__isShown = True
        self.__startTime = BigWorld.time()
        extend = extend and self.__hitData is not None
        if extend:
            self.__hitData.extend(hitData)
        else:
            self.__hitData = hitData
        if self.__indicator:
            duration = self.__indicator.getDuration()
            timeLeft = self.__indicator.getBeginAnimationDuration() if extend else 0
            self.__indicator.showHitDirection(self.__idx, self.__hitData, timeLeft)
        else:
            duration = 0
        return duration

    def hide(self):
        if not self.__isShown:
            return
        self.__isShown = False
        if self.__indicator:
            self.__indicator.hideHitDirection(self.__idx)
