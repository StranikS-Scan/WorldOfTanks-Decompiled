# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/siege_component.py
import BigWorld
from gui.shared.utils.TimeInterval import TimeInterval
from constants import VEHICLE_SIEGE_STATE

class _ComponentUpdater(object):
    __slots__ = ('_parentObj', '_totalTime', '_timeLeft', '_siegeState', '_engineState', '_isSmooth')

    def __init__(self, parentObj, totalTime, timeLeft, siegeState, engineState, isSmooth):
        super(_ComponentUpdater, self).__init__()
        self._parentObj = parentObj
        self._totalTime = totalTime
        self._timeLeft = timeLeft
        self._siegeState = siegeState
        self._engineState = engineState
        self._isSmooth = isSmooth

    def __repr__(self):
        return '_UpdaterComponent(totalTime = {}, timeLeft = {}, siegeState = {}, engineState = {})'.format(self._totalTime, self._timeLeft, self._siegeState, self._engineState)

    def clear(self):
        self._stopTick()
        self._parentObj = None
        return

    def show(self):
        self._startTick()

    def _startTick(self):
        raise NotImplementedError

    def _stopTick(self):
        raise NotImplementedError


class _ActionScriptUpdater(_ComponentUpdater):
    __slots__ = ()

    def _startTick(self):
        self._parentObj.as_switchSiegeStateS(self._totalTime, self._timeLeft, self._siegeState, self._engineState, self._isSmooth)

    def _stopTick(self):
        pass


class _PythonUpdater(_ComponentUpdater):
    __slots__ = ('_timeInterval', '_startTime', '_finishTime', '__weakref__')

    def __init__(self, parentObj, totalTime, timeLeft, siegeState, engineState, isSmooth):
        super(_PythonUpdater, self).__init__(parentObj, totalTime, timeLeft, siegeState, engineState, isSmooth)
        self._timeInterval = TimeInterval(0.05, self, '_tick')
        self._startTime = BigWorld.serverTime()
        self._finishTime = self._startTime + timeLeft

    def clear(self):
        self._timeInterval.stop()
        super(_PythonUpdater, self).clear()

    def _startTick(self):
        if self._siegeState in VEHICLE_SIEGE_STATE.SWITCHING:
            timeLeft = max(0, self._finishTime - BigWorld.serverTime())
            if timeLeft:
                self._updateSnapshot(timeLeft)
                self._timeInterval.start()
        else:
            self._updateSnapshot(self._timeLeft)
        self._isSmooth = False

    def _stopTick(self):
        self._timeInterval.stop()

    def _tick(self):
        timeLeft = self._finishTime - BigWorld.serverTime()
        if timeLeft >= 0 and self._engineState != 'destroyed':
            self._updateSnapshot(timeLeft)

    def _updateSnapshot(self, timeLeft):
        self._parentObj.as_switchSiegeStateSnapshotS(self._totalTime, timeLeft, self._siegeState, self._engineState, self._isSmooth)


class _SiegeComponent(object):
    __slots__ = ('_componentUpdater', '_parentObj', '_clazz')

    def __init__(self, parentObj, clazz):
        super(_SiegeComponent, self).__init__()
        self._componentUpdater = None
        self._parentObj = parentObj
        self._clazz = clazz
        return

    def invalidate(self, totalTime, timeLeft, siegeState, engineState, isSmooth):
        self._clearUpdater()
        self._componentUpdater = self._clazz(self._parentObj, totalTime, timeLeft, siegeState, engineState, isSmooth)
        self._componentUpdater.show()

    def clear(self):
        self._parentObj = None
        self._clearUpdater()
        return

    def _clearUpdater(self):
        if self._componentUpdater is not None:
            self._componentUpdater.clear()
        return


class _DefaultSiegeComponent(_SiegeComponent):
    __slots__ = ()

    def __init__(self, parentObj):
        super(_DefaultSiegeComponent, self).__init__(parentObj, _ActionScriptUpdater)


class _ReplaySiegeComponent(_SiegeComponent):
    __slots__ = ()

    def __init__(self, parentObj):
        super(_ReplaySiegeComponent, self).__init__(parentObj, _PythonUpdater)


def createSiegeComponent(siegeModeIndicator, isReplayPlaying):
    if isReplayPlaying:
        component = _ReplaySiegeComponent(siegeModeIndicator)
    else:
        component = _DefaultSiegeComponent(siegeModeIndicator)
    return component
