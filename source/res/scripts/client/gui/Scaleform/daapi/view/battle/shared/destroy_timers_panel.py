# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/destroy_timers_panel.py
import math
import weakref
from collections import defaultdict
import BattleReplay
import BigWorld
from ReplayEvents import g_replayEvents
from debug_utils import LOG_DEBUG
from AvatarInputHandler import AvatarInputHandler
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform.daapi.view.battle.shared import destroy_times_mapping as _mapping
from gui.Scaleform.daapi.view.battle.shared.timers_common import TimerComponent, PythonTimer
from gui.Scaleform.daapi.view.meta.DestroyTimersPanelMeta import DestroyTimersPanelMeta
from gui.Scaleform.genConsts.BATTLE_DESTROY_TIMER_STATES import BATTLE_DESTROY_TIMER_STATES
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_TIMER_STATES = BATTLE_DESTROY_TIMER_STATES
_TIMERS_PRIORITY = {(_TIMER_STATES.STUN, _TIMER_STATES.WARNING_VIEW): 0,
 (_TIMER_STATES.OVERTURNED, _TIMER_STATES.CRITICAL_VIEW): 1,
 (_TIMER_STATES.DROWN, _TIMER_STATES.CRITICAL_VIEW): 1,
 (_TIMER_STATES.DEATH_ZONE, _TIMER_STATES.CRITICAL_VIEW): 1,
 (_TIMER_STATES.GAS_ATTACK, _TIMER_STATES.CRITICAL_VIEW): 1,
 (_TIMER_STATES.FIRE, _TIMER_STATES.WARNING_VIEW): 2,
 (_TIMER_STATES.DROWN, _TIMER_STATES.WARNING_VIEW): 3,
 (_TIMER_STATES.OVERTURNED, _TIMER_STATES.WARNING_VIEW): 4}

def _showTimerView(typeID, viewID, view, totalTime, isBubble):
    if typeID != _TIMER_STATES.STUN:
        view.as_showS(typeID, viewID, isBubble)
    else:
        view.as_showStunS(totalTime, 0)


def _hideTimerView(typeID, view):
    if typeID != _TIMER_STATES.STUN:
        view.as_hideS(typeID)
    else:
        view.as_hideStunS()


class _ActionScriptTimer(TimerComponent):

    def _startTick(self):
        if self._totalTime > 0 and self._typeID != _TIMER_STATES.STUN:
            self._panel.as_setTimeInSecondsS(self._typeID, self._totalTime, BigWorld.serverTime() - self._startTime)

    def _stopTick(self):
        pass

    def _showView(self, isBubble):
        _showTimerView(self._typeID, self._viewID, self._panel, self._totalTime, isBubble)

    def _hideView(self):
        _hideTimerView(self._typeID, self._panel)


class _PythonTimer(PythonTimer):

    def _showView(self, isBubble):
        _showTimerView(self._typeID, self._viewID, self._panel, self._totalTime, isBubble)

    def _hideView(self):
        _hideTimerView(self._typeID, self._panel)

    def _setViewSnapshot(self, timeLeft):
        totalTime = math.ceil(self._totalTime)
        if self._typeID != _TIMER_STATES.STUN:
            self._panel.as_setTimeSnapshotS(self._typeID, totalTime, totalTime - math.ceil(timeLeft))
        else:
            self._panel.as_setStunTimeSnapshotS(totalTime, totalTime - math.ceil(timeLeft))


class _BaseTimersCollection(object):
    __slots__ = ('_timers', '_panel', '_clazz')

    def __init__(self, panel, clazz):
        self._timers = {}
        self._panel = panel
        self._clazz = clazz

    def clear(self):
        pass

    def addTimer(self, typeID, viewID, totalTime):
        pass

    def removeTimer(self, typeID):
        pass

    def removeTimers(self):
        pass


class _TimersCollection(_BaseTimersCollection):

    def __init__(self, panel, clazz):
        super(_TimersCollection, self).__init__(panel, clazz)

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
            timer.clear()


class _StackTimersCollection(_BaseTimersCollection):
    __slots__ = ('_currentTimer', '_priorityMap')

    def __init__(self, panel, clazz):
        super(_StackTimersCollection, self).__init__(panel, clazz)
        self._currentTimer = None
        self._priorityMap = defaultdict(set)
        return

    def clear(self):
        self._currentTimer = None
        self._priorityMap.clear()
        while self._timers:
            _, timer = self._timers.popitem()
            timer.clear()

        return

    def addTimer(self, typeID, viewID, totalTime):
        if typeID in self._timers:
            oldTimer = self._timers.pop(typeID)
            if self._currentTimer and self._currentTimer.typeID == typeID:
                self._currentTimer = None
            for timersSet in self._priorityMap.itervalues():
                timersSet.discard(typeID)

        else:
            oldTimer = None
        timer = self._clazz(self._panel, typeID, viewID, totalTime)
        LOG_DEBUG('Adds destroy timer', timer)
        self._timers[typeID] = timer
        timerPriority = _TIMERS_PRIORITY[timer.typeID, timer.viewID]
        self._priorityMap[timerPriority].add(timer.typeID)
        if timerPriority == 0:
            timer.show()
        elif self._currentTimer is None:
            npTimer = self.__findNextPriorityTimer()
            if oldTimer and oldTimer.typeID != npTimer.typeID:
                oldTimer.hide()
            self._currentTimer = npTimer
            self._currentTimer.show(npTimer.typeID == timer.typeID)
        else:
            cmpResult = cmp(timerPriority, _TIMERS_PRIORITY[self._currentTimer.typeID, self._currentTimer.viewID])
            if cmpResult == -1 or cmpResult == 0 and self._currentTimer.finishTime >= timer.finishTime:
                self._currentTimer.hide()
                self._currentTimer = timer
                self._currentTimer.show(True)
        return

    def removeTimer(self, typeID):
        if typeID in self._timers:
            LOG_DEBUG('Removes timer', typeID)
            timer = self._timers.pop(typeID)
            self._priorityMap[_TIMERS_PRIORITY[typeID, timer.viewID]].discard(typeID)
            if typeID == _TIMER_STATES.STUN:
                timer.hide()
            elif self._currentTimer and self._currentTimer.typeID == typeID:
                timer.hide()
                self._currentTimer = None
        self._currentTimer = self.__findNextPriorityTimer()
        if self._currentTimer and self._currentTimer.typeID != typeID:
            self._currentTimer.show(False)
        return

    def removeTimers(self):
        if self._currentTimer:
            self._currentTimer.hide()
        for timer in self._timers.itervalues():
            timer.hide()

        self._currentTimer = None
        self._timers.clear()
        self._priorityMap.clear()
        return

    def __findNextPriorityTimer(self):
        if self._timers:
            now = BigWorld.serverTime()
            timerIDs = set((key for key, value in self._timers.iteritems() if now < value.finishTime or value.totalTime == 0))
            for priority, timersSet in sorted(self._priorityMap.items(), key=lambda x: x[0]):
                timers = timersSet & timerIDs
                if timers and priority != 0:
                    typeID = min(timers, key=lambda x: self._timers[x].finishTime)
                    LOG_DEBUG('Found next priority destroy timer', self._timers[typeID])
                    return self._timers[typeID]

        return None


class _ActionScriptTimerMixin(_BaseTimersCollection):

    def __init__(self, panel):
        super(_ActionScriptTimerMixin, self).__init__(panel, _ActionScriptTimer)


class _PythonTimerMixin(_BaseTimersCollection):

    def __init__(self, panel):
        super(_PythonTimerMixin, self).__init__(panel, _PythonTimer)
        g_replayEvents.onPause += self.__onReplayPaused

    def clear(self):
        g_replayEvents.onPause -= self.__onReplayPaused
        super(_PythonTimerMixin, self).clear()

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


class _ReplayStackTimersCollection(_PythonTimerMixin, _StackTimersCollection):
    pass


class _ReplayTimersCollection(_PythonTimerMixin, _TimersCollection):
    pass


class _RegularStackTimersCollection(_ActionScriptTimerMixin, _StackTimersCollection):
    pass


class _RegularTimersCollection(_ActionScriptTimerMixin, _TimersCollection):
    pass


def _createTimersCollection(panel):
    sessionProvider = dependency.instance(IBattleSessionProvider)
    isReplayPlaying = sessionProvider.isReplayPlaying
    if g_lobbyContext.getServerSettings().spgRedesignFeatures.isStunEnabled():
        TimersCollection = _ReplayStackTimersCollection if isReplayPlaying else _RegularStackTimersCollection
    else:
        TimersCollection = _ReplayTimersCollection if isReplayPlaying else _RegularTimersCollection
    return TimersCollection(weakref.proxy(panel))


class DestroyTimersPanel(DestroyTimersPanelMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, mapping=None):
        super(DestroyTimersPanel, self).__init__()
        self.as_turnOnStackViewS(g_lobbyContext.getServerSettings().spgRedesignFeatures.isStunEnabled())
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
        handler = avatar_getter.getInputHandler()
        if handler is not None:
            if isinstance(handler, AvatarInputHandler):
                handler.onCameraChanged += self.__onCameraChanged
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
            ctrl.onVehicleControlling += self.__onVehicleControlling
            vehicle = ctrl.getControllingVehicle()
            if vehicle is not None:
                self.__onVehicleControlling(vehicle)
        return

    def _dispose(self):
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
            ctrl.onVehicleControlling -= self.__onVehicleControlling
        handler = avatar_getter.getInputHandler()
        if handler is not None:
            if isinstance(handler, AvatarInputHandler):
                handler.onCameraChanged -= self.__onCameraChanged
        self.__hideAll()
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

            self.__timers.removeTimer(_TIMER_STATES.FIRE)
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

    def __showStunTimer(self, value):
        if value:
            self.__timers.addTimer(_TIMER_STATES.STUN, _TIMER_STATES.WARNING_VIEW, value)
        else:
            self.__hideTimer(_TIMER_STATES.STUN)

    def __onVehicleControlling(self, vehicle):
        ctrl = self.sessionProvider.shared.vehicleState
        checkStatesIDs = (VEHICLE_VIEW_STATE.FIRE,
         VEHICLE_VIEW_STATE.SHOW_DESTROY_TIMER,
         VEHICLE_VIEW_STATE.SHOW_DEATHZONE_TIMER,
         VEHICLE_VIEW_STATE.STUN)
        for stateID in checkStatesIDs:
            stateValue = ctrl.getStateValue(stateID)
            if stateValue:
                self.__onVehicleStateUpdated(stateID, stateValue)

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
        elif state == VEHICLE_VIEW_STATE.STUN:
            self.__showStunTimer(value)
        elif state in (VEHICLE_VIEW_STATE.DESTROYED, VEHICLE_VIEW_STATE.CREW_DEACTIVATED):
            self.__hideAll()

    def __onCameraChanged(self, ctrlMode, vehicleID=None):
        if ctrlMode == 'video':
            self.__hideAll()
