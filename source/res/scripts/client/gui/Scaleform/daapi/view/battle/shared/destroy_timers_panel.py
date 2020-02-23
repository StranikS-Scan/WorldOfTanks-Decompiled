# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/destroy_timers_panel.py
import weakref
import math
from collections import defaultdict
import BigWorld
import BattleReplay
from AvatarInputHandler import AvatarInputHandler
from ReplayEvents import g_replayEvents
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.view.battle.shared import destroy_times_mapping as _mapping
from gui.Scaleform.daapi.view.battle.shared.timers_common import TimerComponent, PythonTimer
from gui.Scaleform.daapi.view.meta.DestroyTimersPanelMeta import DestroyTimersPanelMeta
from gui.Scaleform.genConsts.BATTLE_DESTROY_TIMER_STATES import BATTLE_DESTROY_TIMER_STATES as _TIMER_STATES
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, CROSSHAIR_VIEW_ID
from gui.battle_control import event_dispatcher as gui_event_dispatcher
from gui.shared.items_parameters import isAutoReloadGun
from helpers import dependency, i18n
from items import vehicles
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.lobby_context import ILobbyContext
_TIMERS_PRIORITY = {(_TIMER_STATES.STUN, _TIMER_STATES.WARNING_VIEW): 1,
 (_TIMER_STATES.CAPTURE_BLOCK, _TIMER_STATES.WARNING_VIEW): 1,
 (_TIMER_STATES.OVERTURNED, _TIMER_STATES.CRITICAL_VIEW): 1,
 (_TIMER_STATES.DROWN, _TIMER_STATES.CRITICAL_VIEW): 1,
 (_TIMER_STATES.DEATH_ZONE, _TIMER_STATES.CRITICAL_VIEW): 1,
 (_TIMER_STATES.FIRE, _TIMER_STATES.WARNING_VIEW): 2,
 (_TIMER_STATES.DROWN, _TIMER_STATES.WARNING_VIEW): 3,
 (_TIMER_STATES.OVERTURNED, _TIMER_STATES.WARNING_VIEW): 4,
 (_TIMER_STATES.UNDER_FIRE, _TIMER_STATES.WARNING_VIEW): 3,
 (_TIMER_STATES.RECOVERY, _TIMER_STATES.CRITICAL_VIEW): 1,
 (_TIMER_STATES.SECTOR_AIRSTRIKE, _TIMER_STATES.CRITICAL_VIEW): 1,
 (_TIMER_STATES.SECTOR_AIRSTRIKE, _TIMER_STATES.WARNING_VIEW): 1,
 (_TIMER_STATES.SMOKE, _TIMER_STATES.WARNING_VIEW): 4,
 (_TIMER_STATES.INSPIRE, _TIMER_STATES.WARNING_VIEW): 3,
 (_TIMER_STATES.INSPIRE_CD, _TIMER_STATES.WARNING_VIEW): 3}
_SECONDARY_TIMERS = (_TIMER_STATES.STUN,
 _TIMER_STATES.CAPTURE_BLOCK,
 _TIMER_STATES.SMOKE,
 _TIMER_STATES.INSPIRE,
 _TIMER_STATES.INSPIRE_CD)
_MAX_DISPLAYED_SECONDARY_STATUS_TIMERS = 2
_VERTICAL_SHIFT_WITH_AUTOLOADER_IN_SNIPER_MODE = 42

def _showTimerView(typeID, viewID, view, totalTime, isBubble, currentTime=0, secondInRow=False):
    if typeID in _SECONDARY_TIMERS:
        view.as_showSecondaryTimerS(typeID, totalTime, currentTime, secondInRow)
    else:
        view.as_showS(typeID, viewID, isBubble)
    gui_event_dispatcher.destroyTimersPanelShown(shown=True)


def _hideTimerView(typeID, view):
    if typeID in _SECONDARY_TIMERS:
        view.as_hideSecondaryTimerS(typeID)
    else:
        view.as_hideS(typeID)
    gui_event_dispatcher.destroyTimersPanelShown(shown=False)


class _ActionScriptTimer(TimerComponent):

    def _startTick(self):
        if self._totalTime > 0 and self._typeID not in _SECONDARY_TIMERS:
            self._viewObject.as_setTimeInSecondsS(self._typeID, self._totalTime, BigWorld.serverTime() - self._startTime)

    def _stopTick(self):
        pass

    def _showView(self, isBubble):
        _showTimerView(self._typeID, self._viewID, self._viewObject, self._totalTime, isBubble, BigWorld.serverTime() - self._startTime, secondInRow=self._secondInRow)

    def _hideView(self):
        _hideTimerView(self._typeID, self._viewObject)


class _PythonTimer(PythonTimer):

    def _showView(self, isBubble):
        _showTimerView(self._typeID, self._viewID, self._viewObject, self._totalTime, isBubble, BigWorld.serverTime() - self._startTime, secondInRow=self._secondInRow)

    def _hideView(self):
        _hideTimerView(self._typeID, self._viewObject)

    def _setViewSnapshot(self, timeLeft):
        totalTime = math.ceil(self._totalTime)
        if self._typeID in _SECONDARY_TIMERS:
            self._viewObject.as_setSecondaryTimeSnapshotS(self._typeID, totalTime, totalTime - timeLeft)
        else:
            self._viewObject.as_setTimeSnapshotS(self._typeID, totalTime, totalTime - math.ceil(timeLeft))


class _BaseTimersCollection(object):
    __slots__ = ('_timers', '_panel', '_clazz')

    def __init__(self, panel, clazz):
        self._timers = {}
        self._panel = panel
        self._clazz = clazz

    def clear(self):
        pass

    def addTimer(self, typeID, viewID, totalTime, finishTime, startTimer=None):
        pass

    def addSecondaryTimer(self, typeID, viewID, totalTime, finishTime, startTime=None):
        pass

    def removeTimer(self, typeID):
        pass

    def removeSecondaryTimer(self, typeID):
        pass

    def removeTimers(self):
        pass


class _TimersCollection(_BaseTimersCollection):

    def clear(self):
        while self._timers:
            _, timer = self._timers.popitem()
            timer.clear()

    def addTimer(self, typeID, viewID, totalTime, finishTime, startTimer=None):
        if typeID in self._timers:
            timer = self._timers.pop(typeID)
            timer.clear()
        timer = self._clazz(self._panel, typeID, viewID, totalTime, finishTime)
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
    __slots__ = ('_currentTimer', '_currentSecondaryTimers', '_priorityMap', '_prioritySecondaryMap')

    def __init__(self, panel, clazz):
        super(_StackTimersCollection, self).__init__(panel, clazz)
        self._currentTimer = None
        self._currentSecondaryTimers = []
        self._priorityMap = defaultdict(set)
        self._prioritySecondaryMap = defaultdict(set)
        return

    def clear(self):
        self._currentTimer = None
        self._priorityMap.clear()
        while self._timers:
            _, timer = self._timers.popitem()
            timer.clear()

        return

    def addTimer(self, typeID, viewID, totalTime, finishTime, startTime=None):
        if typeID in self._timers:
            oldTimer = self._timers.pop(typeID)
            if self._currentTimer and self._currentTimer.typeID == typeID:
                self._currentTimer = None
            for timersSet in self._priorityMap.itervalues():
                timersSet.discard(typeID)

        else:
            oldTimer = None
        timer = self._clazz(self._panel, typeID, viewID, totalTime, finishTime, startTime)
        LOG_DEBUG('Adds destroy timer', timer)
        self._timers[typeID] = timer
        timerPriority = _TIMERS_PRIORITY[timer.typeID, timer.viewID]
        self._priorityMap[timerPriority].add(timer.typeID)
        if timerPriority == 0:
            timer.show()
        elif self._currentTimer is None:
            npTimer = self.__findNextPriorityByPriorityMap()
            if oldTimer and (npTimer is None or oldTimer.typeID != npTimer.typeID):
                oldTimer.hide()
            self._currentTimer = npTimer
            if self._currentTimer is not None:
                self._currentTimer.show(npTimer.typeID == timer.typeID)
        else:
            cmpResult = cmp(timerPriority, _TIMERS_PRIORITY[self._currentTimer.typeID, self._currentTimer.viewID])
            if cmpResult == -1 or cmpResult == 0 and self._currentTimer.finishTime >= timer.finishTime:
                self._currentTimer.hide()
                self._currentTimer = timer
                self._currentTimer.show(True)
        return

    def addSecondaryTimer(self, typeID, viewID, totalTime, finishTime, startTime=None):
        secondInRow = self.hasActiveSecondaryTimer(typeID)
        self.removeSecondaryTimer(typeID)
        timer = self._clazz(self._panel, typeID, viewID, totalTime, finishTime, startTime, secondInRow=secondInRow)
        LOG_DEBUG('Adds secondary timer', timer)
        self._timers[typeID] = timer
        timerPriority = _TIMERS_PRIORITY[timer.typeID, timer.viewID]
        self._prioritySecondaryMap[timerPriority].add(timer.typeID)
        if not self._currentSecondaryTimers:
            self._currentSecondaryTimers.append(timer)
            timer.show()
        else:
            if timer not in self._currentSecondaryTimers:
                self._currentSecondaryTimers.append(timer)
            if len(self._currentSecondaryTimers) >= _MAX_DISPLAYED_SECONDARY_STATUS_TIMERS:
                self.__evaluateMultipleStatusStates()
            else:
                timer.show()

    def hasActiveSecondaryTimer(self, typeID):
        for timer in self._currentSecondaryTimers:
            if timer.typeID == typeID:
                return True

        return False

    def removeTimer(self, typeID):
        if typeID in self._timers:
            timer = self._timers.pop(typeID)
            self._priorityMap[_TIMERS_PRIORITY[typeID, timer.viewID]].discard(typeID)
            if self._currentTimer and self._currentTimer.typeID == typeID:
                timer.hide()
                self._currentTimer = None
        self._currentTimer = self.__findNextPriorityByPriorityMap()
        if self._currentTimer and self._currentTimer.typeID != typeID:
            self._currentTimer.show(False)
        return

    def removeSecondaryTimer(self, typeID):
        if typeID in self._timers and typeID in _SECONDARY_TIMERS:
            timer = self._timers.pop(typeID)
            self._prioritySecondaryMap[_TIMERS_PRIORITY[typeID, timer.viewID]].discard(typeID)
            if timer in self._currentSecondaryTimers:
                timer.hide()
                self._currentSecondaryTimers.remove(timer)
            self.__evaluateMultipleStatusStates(False)

    def removeTimers(self):
        if self._currentTimer:
            self._currentTimer.hide()
        for timer in self._timers.itervalues():
            timer.hide()

        self._currentSecondaryTimers = []
        self._currentTimer = None
        self._timers.clear()
        self._priorityMap.clear()
        return

    def __evaluateMultipleStatusStates(self, bubble=True):
        activeTimers = self.__getActiveSecondaryTimers()
        if not activeTimers or not self._currentSecondaryTimers:
            return
        for currTimer in self._currentSecondaryTimers:
            if currTimer.typeID in activeTimers and activeTimers.index(currTimer.typeID) > 1:
                currTimer.hide()
            currTimer.show(bubble)

    def __getActiveSecondaryTimers(self):
        if not self._timers:
            return
        activeTimers = []
        now = BigWorld.serverTime()
        timerIDs = set((key for key, value in self._timers.iteritems() if now < value.finishTime or value.totalTime == 0))
        for priority, timersSet in sorted(self._prioritySecondaryMap.items(), key=lambda x: x[0]):
            timers = timersSet & timerIDs
            if timers and priority != 0:
                finishTimeSortedTimers = sorted(timers, key=lambda x: self._timers[x].finishTime)
                for activeTimerID in finishTimeSortedTimers:
                    activeTimers.append(activeTimerID)

        return activeTimers

    def __findNextPriorityByPriorityMap(self):
        if not self._timers:
            return None
        else:
            now = BigWorld.serverTime()
            timerIDs = set((key for key, value in self._timers.iteritems() if now < value.finishTime or value.totalTime == 0))
            for priority, timersSet in sorted(self._priorityMap.items(), key=lambda x: x[0]):
                timers = timersSet & timerIDs
                if timers and priority != 0:
                    typeID = min(timers, key=lambda x: self._timers[x].finishTime)
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
    lobbyContext = dependency.instance(ILobbyContext)
    isReplayPlaying = sessionProvider.isReplayPlaying
    if lobbyContext.getServerSettings().spgRedesignFeatures.isStunEnabled():
        TimersCollection = _ReplayStackTimersCollection if isReplayPlaying else _RegularStackTimersCollection
    else:
        TimersCollection = _ReplayTimersCollection if isReplayPlaying else _RegularTimersCollection
    return TimersCollection(weakref.proxy(panel))


class DestroyTimersPanel(DestroyTimersPanelMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, mapping=None):
        super(DestroyTimersPanel, self).__init__()
        self.as_turnOnStackViewS(self.lobbyContext.getServerSettings().spgRedesignFeatures.isStunEnabled())
        if mapping is not None:
            self._mapping = mapping
        else:
            self._mapping = _mapping.FrontendMapping()
        self._timers = _createTimersCollection(self)
        self.__sound = None
        self.__vehicleID = None
        self.__viewID = CROSSHAIR_VIEW_ID.UNDEFINED
        return

    def _populate(self):
        super(DestroyTimersPanel, self)._populate()
        handler = avatar_getter.getInputHandler()
        if handler is not None:
            if isinstance(handler, AvatarInputHandler):
                handler.onCameraChanged += self.__onCameraChanged
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated += self._onVehicleStateUpdated
            ctrl.onVehicleControlling += self.__onVehicleControlling
            vehicle = ctrl.getControllingVehicle()
            if vehicle is not None:
                self.__onVehicleControlling(vehicle)
        crosshairCtrl = self.sessionProvider.shared.crosshair
        if crosshairCtrl is not None:
            crosshairCtrl.onCrosshairViewChanged += self.__onCrosshairViewChanged
        return

    def _dispose(self):
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self._onVehicleStateUpdated
            ctrl.onVehicleControlling -= self.__onVehicleControlling
        crosshairCtrl = self.sessionProvider.shared.crosshair
        if crosshairCtrl is not None:
            crosshairCtrl.onCrosshairViewChanged -= self.__onCrosshairViewChanged
        handler = avatar_getter.getInputHandler()
        if handler is not None:
            if isinstance(handler, AvatarInputHandler):
                handler.onCameraChanged -= self.__onCameraChanged
        self.__hideAll()
        self._timers.clear()
        self._mapping.clear()
        self.__stopSound()
        self._mapping = None
        self._timers = None
        super(DestroyTimersPanel, self)._dispose()
        return

    def __hideAll(self):
        self._timers.removeTimers()

    def __setFireInVehicle(self, isInFire):
        if isInFire:
            self._timers.addTimer(_TIMER_STATES.FIRE, _TIMER_STATES.WARNING_VIEW, 0, None)
        else:
            self._hideTimer(_TIMER_STATES.FIRE)
        return

    def _showTimer(self, typeID, totalTime, level, finishTime, startTime=None):
        if typeID is not None:
            if typeID in _SECONDARY_TIMERS:
                self._timers.addSecondaryTimer(typeID, level, totalTime, finishTime, startTime)
            else:
                self._timers.addTimer(typeID, _mapping.getTimerViewTypeID(level), totalTime, finishTime, startTime)
        return

    def _hideTimer(self, typeID):
        if typeID is not None:
            if typeID in _SECONDARY_TIMERS:
                self._timers.removeSecondaryTimer(typeID)
            else:
                self._timers.removeTimer(typeID)
        return

    def __showDestroyTimer(self, value):
        if value.needToCloseAll():
            for typeID in self._mapping.getDestroyTimersTypesIDs():
                self._hideTimer(typeID)

            self._timers.removeTimer(_TIMER_STATES.FIRE)
        elif value.needToCloseTimer():
            self._hideTimer(self._mapping.getTimerTypeIDByMiscCode(value.code))
        else:
            self._showTimer(self._mapping.getTimerTypeIDByMiscCode(value.code), value.totalTime, value.level, None, value.startTime)
        return

    def _showDeathZoneTimer(self, value):
        if value.needToCloseAll():
            for typeID in self._mapping.getDeathZoneTimersTypesIDs():
                self._hideTimer(typeID)

        elif value.needToCloseTimer():
            self._hideTimer(self._mapping.getTimerTypeIDByDeathZoneCode(value.zoneID))
        else:
            self.__playDeathZoneSound(value.zoneID, value.level)
            self._showTimer(self._mapping.getTimerTypeIDByDeathZoneCode(value.zoneID), value.totalTime, value.level, value.finishTime)

    def __stopSound(self):
        if self.__sound is not None:
            self.__sound.stop()
            self.__sound = None
        return

    def __playDeathZoneSound(self, code, level):
        self.__stopSound()
        sound = self._mapping.getSoundByDeathZone(code, level)
        if sound is not None:
            self.__sound = sound
            self.__sound.play()
        return

    def __showStunTimer(self, value):
        if value.duration > 0.0:
            self._showTimer(_TIMER_STATES.STUN, value.totalTime, _TIMER_STATES.WARNING_VIEW, value.endTime, value.startTime)
        else:
            self._hideTimer(_TIMER_STATES.STUN)

    def __showCaptureBlockTimer(self, value):
        if value:
            self._showTimer(_TIMER_STATES.CAPTURE_BLOCK, value, _TIMER_STATES.WARNING_VIEW, None)
        else:
            self._hideTimer(_TIMER_STATES.CAPTURE_BLOCK)
        return

    def __updateSmokeTimer(self, smokesInfo):
        if smokesInfo:
            maxEndTime, eqID = max(((smokeInfo['endTime'], smokeInfo['equipmentID']) for smokeInfo in smokesInfo))
            duration = vehicles.g_cache.equipments()[eqID].totalDuration
            self._showTimer(_TIMER_STATES.SMOKE, duration, _TIMER_STATES.WARNING_VIEW, maxEndTime)
        else:
            self._hideTimer(_TIMER_STATES.SMOKE)

    def __updateInspireTimer(self, isSourceVehicle, isInactivation, endTime, duration):
        LOG_DEBUG('[INSPIRE] {} __updateInspireTimer: isSourceVehicle: {}, isInactivation: {}, endTime: {}, duration: {}'.format(*(str(x) for x in (BigWorld.player().id,
         isSourceVehicle,
         isInactivation,
         endTime,
         duration))))
        if isInactivation is not None:
            self._hideTimer(_TIMER_STATES.INSPIRE)
            self._hideTimer(_TIMER_STATES.INSPIRE_CD)
            if isInactivation:
                self._showTimer(_TIMER_STATES.INSPIRE_CD, duration, _TIMER_STATES.WARNING_VIEW, endTime)
                self.as_setSecondaryTimerTextS(_TIMER_STATES.INSPIRE_CD, i18n.makeString(EPIC_BATTLE.INSPIRE_INSPIRED))
            else:
                self._showTimer(_TIMER_STATES.INSPIRE, duration, _TIMER_STATES.WARNING_VIEW, endTime)
                text = i18n.makeString(EPIC_BATTLE.INSPIRE_INSPIRING) if isSourceVehicle else i18n.makeString(EPIC_BATTLE.INSPIRE_INSPIRED)
                self.as_setSecondaryTimerTextS(_TIMER_STATES.INSPIRE, text)
        else:
            self._hideTimer(_TIMER_STATES.INSPIRE)
            self._hideTimer(_TIMER_STATES.INSPIRE_CD)
        return

    def __onVehicleControlling(self, vehicle):
        ctrl = self.sessionProvider.shared.vehicleState
        checkStatesIDs = (VEHICLE_VIEW_STATE.FIRE,
         VEHICLE_VIEW_STATE.DESTROY_TIMER,
         VEHICLE_VIEW_STATE.DEATHZONE_TIMER,
         VEHICLE_VIEW_STATE.STUN,
         VEHICLE_VIEW_STATE.CAPTURE_BLOCKED,
         VEHICLE_VIEW_STATE.SMOKE,
         VEHICLE_VIEW_STATE.INSPIRE)
        for stateID in checkStatesIDs:
            stateValue = ctrl.getStateValue(stateID)
            if stateValue:
                self._onVehicleStateUpdated(stateID, stateValue)

        vehicle.updateStunInfo()
        self.__vehicleID = vehicle.id
        self.__updatePanelPosition()

    def __onCrosshairViewChanged(self, viewID):
        self.__viewID = viewID
        self.__updatePanelPosition()

    def __updatePanelPosition(self):
        vehicle = BigWorld.entity(self.__vehicleID) if self.__vehicleID is not None else None
        if vehicle is None or vehicle.typeDescriptor is None:
            self.as_setVerticalOffsetS(0)
            return
        else:
            verticalOffset = 0
            vTypeDescr = vehicle.typeDescriptor
            hasAutoloaderInterface = vTypeDescr.isDualgunVehicle or isAutoReloadGun(vTypeDescr.gun)
            if self.__viewID is CROSSHAIR_VIEW_ID.SNIPER and hasAutoloaderInterface:
                verticalOffset = _VERTICAL_SHIFT_WITH_AUTOLOADER_IN_SNIPER_MODE
            self.as_setVerticalOffsetS(verticalOffset)
            return

    def _onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.SWITCHING:
            self.__hideAll()
        elif state == VEHICLE_VIEW_STATE.FIRE:
            self.__setFireInVehicle(value)
        elif state == VEHICLE_VIEW_STATE.DESTROY_TIMER:
            self.__showDestroyTimer(value)
        elif state == VEHICLE_VIEW_STATE.DEATHZONE_TIMER:
            self._showDeathZoneTimer(value)
        elif state == VEHICLE_VIEW_STATE.STUN:
            self.__showStunTimer(value)
        elif state == VEHICLE_VIEW_STATE.CAPTURE_BLOCKED:
            self.__showCaptureBlockTimer(value)
        elif state == VEHICLE_VIEW_STATE.SMOKE:
            self.__updateSmokeTimer(value)
        elif state == VEHICLE_VIEW_STATE.INSPIRE:
            self.__updateInspireTimer(**value)
        elif state in (VEHICLE_VIEW_STATE.DESTROYED, VEHICLE_VIEW_STATE.CREW_DEACTIVATED):
            self.__hideAll()

    def __onCameraChanged(self, ctrlMode, vehicleID=None):
        if ctrlMode == 'video':
            self.__hideAll()
