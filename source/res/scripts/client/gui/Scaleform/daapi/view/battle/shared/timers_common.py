# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/timers_common.py
import BigWorld
from gui.shared.utils.TimeInterval import TimeInterval

class TimerComponent(object):
    __slots__ = ('_viewObject', '_typeID', '_viewID', '_totalTime', '_startTime', '_finishTime', '_secondInRow')

    def __init__(self, viewObject, typeID, viewID, totalTime, finishTime, startTime=None, secondInRow=False, **kwargs):
        super(TimerComponent, self).__init__(**kwargs)
        self._viewObject = viewObject
        self._typeID = typeID
        self._viewID = viewID
        self._totalTime = totalTime
        self._secondInRow = secondInRow
        if finishTime:
            self._startTime = finishTime - totalTime
            self._finishTime = finishTime
        else:
            self._startTime = BigWorld.serverTime()
            self._finishTime = self._startTime + totalTime if totalTime > 0 else self._startTime

    def __repr__(self):
        return 'TimerComponent(typeID = {}, viewID = {}, totalTime = {})'.format(self._typeID, self._viewID, self._totalTime)

    def clear(self):
        self._viewObject = None
        return

    def show(self, isBubble=True):
        self._showView(isBubble)
        self._startTick()

    def hide(self):
        self._stopTick()
        self._hideView()

    @property
    def typeID(self):
        return self._typeID

    @property
    def viewID(self):
        return self._viewID

    @property
    def finishTime(self):
        return self._finishTime

    @property
    def totalTime(self):
        return self._totalTime

    def _startTick(self):
        raise NotImplementedError

    def _stopTick(self):
        raise NotImplementedError

    def _hideView(self):
        raise NotImplementedError

    def _showView(self, isBubble):
        raise NotImplementedError


class PythonTimer(TimerComponent):
    __slots__ = ('_timeInterval', '__weakref__')

    def __init__(self, viewObject, typeID, viewID, totalTime, finishTime, startTime=None, interval=1.0, secondInRow=False, **kwargs):
        super(PythonTimer, self).__init__(viewObject, typeID, viewID, totalTime, finishTime, startTime, secondInRow=secondInRow, **kwargs)
        self._timeInterval = TimeInterval(interval, self, '_tick')

    def clear(self):
        self._timeInterval.stop()
        super(PythonTimer, self).clear()

    def _startTick(self):
        if self._totalTime:
            timeLeft = max(0, self._finishTime - BigWorld.serverTime())
            if timeLeft:
                self._setViewSnapshot(timeLeft)
                self._timeInterval.restart()

    def _stopTick(self):
        self._timeInterval.stop()

    def _tick(self):
        timeLeft = self._finishTime - BigWorld.serverTime()
        if timeLeft >= 0:
            self._setViewSnapshot(timeLeft)
        else:
            self.hide()

    def _setViewSnapshot(self, timeLeft):
        raise NotImplementedError


class PrecisePythonTimer(PythonTimer):
    __slots__ = ('__short1stPeriodCbId', '__interval', '_timeInterval', '_startTime')

    def __init__(self, viewObject, typeID, viewID, totalTime, finishTime, startTime=None, interval=1.0, secondInRow=False, **kwargs):
        super(PrecisePythonTimer, self).__init__(viewObject, typeID, viewID, totalTime, finishTime, startTime, interval, secondInRow, **kwargs)
        if startTime is not None:
            self._startTime = startTime
        self.__interval = interval
        self.__short1stPeriodCbId = None
        return

    def _startTick(self):
        if self._totalTime:
            timeLeft = max(0, self._finishTime - BigWorld.serverTime())
            if timeLeft:
                self._setViewSnapshot(timeLeft)
                self._timeInterval = TimeInterval(self.__interval, self, '_tick')
                firstShortPeriod = float(self._totalTime) % self.__interval
                if round(firstShortPeriod, 4) > 0.0:
                    self.__short1stPeriodCbId = BigWorld.callback(firstShortPeriod, self.__onShort1stPeriodFinished)
                else:
                    self._timeInterval.restart()

    def clear(self):
        self.__clearShort1stPeriodCb()
        super(PrecisePythonTimer, self).clear()

    def _stopTick(self):
        self.__clearShort1stPeriodCb()
        super(PrecisePythonTimer, self)._stopTick()

    def _setViewSnapshot(self, timeLeft):
        raise NotImplementedError

    def __clearShort1stPeriodCb(self):
        if self.__short1stPeriodCbId is not None:
            BigWorld.cancelCallback(self.__short1stPeriodCbId)
        self.__short1stPeriodCbId = None
        return

    def __onShort1stPeriodFinished(self):
        self.__short1stPeriodCbId = None
        self._tick()
        timeLeft = self._finishTime - BigWorld.serverTime()
        if timeLeft > 0:
            self._timeInterval.restart()
        else:
            self.hide()
        return
