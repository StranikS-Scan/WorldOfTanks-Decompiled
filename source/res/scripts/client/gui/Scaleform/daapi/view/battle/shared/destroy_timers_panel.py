# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/destroy_timers_panel.py
import weakref
import BattleReplay
import BigWorld
from ReplayEvents import g_replayEvents
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.view.battle.shared import destroy_times_mapping as _mapping
from gui.Scaleform.daapi.view.meta.DestroyTimersPanelMeta import DestroyTimersPanelMeta
from gui.Scaleform.genConsts.BATTLE_DESTROY_TIMER_STATES import BATTLE_DESTROY_TIMER_STATES
from gui.battle_control import g_sessionProvider, avatar_getter
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.shared.utils.TimeInterval import TimeInterval
_TIMER_STATES = BATTLE_DESTROY_TIMER_STATES

class _TimerComponent(object):
    __slots__ = ('_panel', '_typeID', '_viewID', '_totalTime')

    def __init__(self, panel, typeID, viewID, totalTime):
        super(_TimerComponent, self).__init__()
        self._panel = panel
        self._typeID = typeID
        self._viewID = viewID
        self._totalTime = totalTime

    def __repr__(self):
        return '_TimerComponent(typeID = {}, viewID = {}, totalTime = {})'.format(self._typeID, self._viewID, self._totalTime)

    def clear(self):
        self._panel = None
        return

    def show(self):
        self._panel.as_showS(self._typeID, self._viewID)
        self._startTick()

    def hide(self):
        self._stopTick()
        self._panel.as_hideS(self._typeID)

    def _startTick(self):
        raise NotImplementedError

    def _stopTick(self):
        raise NotImplementedError


class _ActionScriptTimer(_TimerComponent):

    def _startTick(self):
        if self._totalTime > 0:
            self._panel.as_setTimeInSecondsS(self._typeID, self._totalTime, 0)

    def _stopTick(self):
        pass


class _PythonTimer(_TimerComponent):
    __slots__ = ('_timeInterval', '_startTime', '_finishTime', '__weakref__')

    def __init__(self, panel, typeID, viewID, totalTime):
        super(_PythonTimer, self).__init__(panel, typeID, viewID, totalTime)
        self._timeInterval = TimeInterval(1.0, self, '_tick')
        self._startTime = BigWorld.serverTime()
        if totalTime:
            self._finishTime = self._startTime + totalTime
        else:
            self._finishTime = 0

    def clear(self):
        self._timeInterval.stop()
        super(_PythonTimer, self).clear()

    def _startTick(self):
        if self._totalTime:
            timeLeft = max(0, self._finishTime - BigWorld.serverTime())
            if timeLeft:
                self._panel.as_setTimeSnapshotS(self._typeID, self._totalTime, timeLeft)
                self._timeInterval.start()

    def _stopTick(self):
        self._timeInterval.stop()

    def _tick(self):
        timeLeft = self._finishTime - BigWorld.serverTime()
        if timeLeft >= 0:
            self._panel.as_setTimeSnapshotS(self._typeID, self._totalTime, timeLeft)
        else:
            self.hide()


class _TimersCollection(object):
    __slots__ = ('_timers', '_panel', '_clazz')

    def __init__(self, panel, clazz):
        super(_TimersCollection, self).__init__()
        self._timers = {}
        self._panel = panel
        self._clazz = clazz

    def getIterator(self):
        for typeID, timer in self._timers.iteritems():
            yield (typeID, timer)

    def clear(self):
        while self._timers:
            _, timer = self._timers.popitem()
            timer.clear()

    def addTimer(self, typeID, viewID, totalTime):
        if typeID in self._timers:
            timer = self._timers.pop(typeID)
            timer.clear()
        timer = self._clazz(self._panel, typeID, viewID, totalTime)
        LOG_DEBUG('Adds destroy timer', timer)
        self._timers[typeID] = timer
        timer.show()

    def removeTimer(self, typeID):
        if typeID in self._timers:
            LOG_DEBUG('Removes timer', typeID)
            timer = self._timers.pop(typeID)
            timer.hide()

    def removeTimers(self):
        while self._timers:
            _, timer = self._timers.popitem()
            timer.hide()


class _DefaultCollection(_TimersCollection):

    def __init__(self, panel):
        super(_DefaultCollection, self).__init__(panel, _ActionScriptTimer)


class _ReplayCollection(_TimersCollection):

    def __init__(self, panel):
        super(_ReplayCollection, self).__init__(panel, _PythonTimer)
        g_replayEvents.onPause += self.__onReplayPaused

    def clear(self):
        g_replayEvents.onPause -= self.__onReplayPaused
        super(_ReplayCollection, self).clear()

    def __onReplayPaused(self, isPaused):
        panel = self._panel
        if panel is None:
            return
        else:
            if isPaused:
                panel.as_setSpeedS(0)
            else:
                panel.as_setSpeedS(BattleReplay.g_replayCtrl.playbackSpeed)
            return


def _createTimersCollection(panel):
    if BattleReplay.g_replayCtrl.isPlaying:
        collection = _ReplayCollection(weakref.proxy(panel))
    else:
        collection = _DefaultCollection(weakref.proxy(panel))
    return collection


class DestroyTimersPanel(DestroyTimersPanelMeta):

    def __init__(self, mapping=None):
        super(DestroyTimersPanel, self).__init__()
        if mapping is not None:
            assert isinstance(mapping, _mapping.FrontendMapping)
            self.__mapping = mapping
        else:
            self.__mapping = _mapping.FrontendMapping()
        self.__timers = _createTimersCollection(self)
        self.__sound = None
        return

    def _populate(self):
        super(DestroyTimersPanel, self)._populate()
        ctrl = g_sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
            checkStatesIDs = (VEHICLE_VIEW_STATE.FIRE, VEHICLE_VIEW_STATE.SHOW_DESTROY_TIMER, VEHICLE_VIEW_STATE.SHOW_DEATHZONE_TIMER)
            for stateID in checkStatesIDs:
                stateValue = ctrl.getStateValue(stateID)
                if stateValue:
                    self.__onVehicleStateUpdated(stateID, stateValue)

        handler = avatar_getter.getInputHandler()
        if handler is not None:
            handler.onCameraChanged += self.__onCameraChanged
        return

    def _dispose(self):
        ctrl = g_sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        handler = avatar_getter.getInputHandler()
        if handler is not None:
            handler.onCameraChanged -= self.__onCameraChanged
        self.__timers.clear()
        self.__mapping.clear()
        self.__stopSound()
        super(DestroyTimersPanel, self)._dispose()
        return

    def __hideAll(self):
        self.__timers.removeTimers()

    def __setFireInVehicle(self, isInFire):
        if isInFire:
            self.__timers.addTimer(_TIMER_STATES.FIRE, _TIMER_STATES.WARNING_VIEW, 0)
        else:
            self.__hideTimer(_TIMER_STATES.FIRE)

    def __showTimer(self, typeID, totalTime, level):
        if typeID is not None:
            self.__timers.addTimer(typeID, _mapping.getTimerViewTypeID(level), totalTime)
        return

    def __hideTimer(self, typeID):
        if typeID is not None:
            self.__timers.removeTimer(typeID)
        return

    def __showDestroyTimer(self, value):
        code, totalTime, level = value
        self.__showTimer(self.__mapping.getTimerTypeIDByMiscCode(code), totalTime, level)

    def __hideDestroyTimer(self, value):
        if value is not None:
            self.__hideTimer(self.__mapping.getTimerTypeIDByMiscCode(value))
        else:
            for typeID in self.__mapping.getDestroyTimersTypesIDs():
                self.__hideTimer(typeID)

            self.as_hideS(_TIMER_STATES.FIRE)
        return

    def __showDeathZoneTimer(self, value):
        code, totalTime, level = value
        self.__playDeathZoneSound(code, level)
        self.__showTimer(self.__mapping.getTimerTypeIDByDeathZoneCode(code), totalTime, level)

    def __hideDeathZoneTimer(self, value):
        if value is not None:
            self.__hideTimer(self.__mapping.getTimerTypeIDByDeathZoneCode(value))
        else:
            for typeID in self.__mapping.getDeathZoneTimersTypesIDs():
                self.__hideTimer(typeID)

        return

    def __stopSound(self):
        if self.__sound is not None:
            self.__sound.stop()
            self.__sound = None
        return

    def __playDeathZoneSound(self, code, level):
        self.__stopSound()
        sound = self.__mapping.getSoundByDeathZone(code, level)
        if sound is not None:
            self.__sound = sound
            self.__sound.play()
        return

    def __onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.SWITCHING:
            self.__hideAll()
        elif state == VEHICLE_VIEW_STATE.FIRE:
            self.__setFireInVehicle(value)
        elif state == VEHICLE_VIEW_STATE.SHOW_DESTROY_TIMER:
            self.__showDestroyTimer(value)
        elif state == VEHICLE_VIEW_STATE.HIDE_DESTROY_TIMER:
            self.__hideDestroyTimer(value)
        elif state == VEHICLE_VIEW_STATE.SHOW_DEATHZONE_TIMER:
            self.__showDeathZoneTimer(value)
        elif state == VEHICLE_VIEW_STATE.HIDE_DEATHZONE_TIMER:
            self.__hideDeathZoneTimer(value)

    def __onCameraChanged(self, ctrlMode, vehicleID=None):
        if ctrlMode == 'video':
            self.__hideAll()
