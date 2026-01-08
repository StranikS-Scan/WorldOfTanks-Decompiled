# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/spotting_indicators_ctrl.py
import logging
import typing
from enum import Enum
from functools import partial
import BigWorld
from Event import Event
from PlayerEvents import g_playerEvents
from ReplayEvents import g_replayEvents
from Vehicle import Vehicle
from constants import DIRECT_DETECTION_TYPE
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.controllers.interfaces import IBattleController
from helpers.dependency import instance
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from typing import Dict, List, Optional, Tuple
    from gui.battle_control import BattleSessionSetup
    from gui.battle_control.controllers.vehicle_state_ctrl import VehicleStateController
_logger = logging.getLogger(__name__)

class ISpottingIndicator(object):
    __slots__ = ()
    ToggleType = typing.Callable[[bool, bool], None]
    EnabledType = typing.Callable[[], bool]

    def getIndicatorTogglesByType(self):
        raise NotImplementedError


class ISpottingIndicatorsController(IBattleController):
    __slots__ = ()
    onSpottingIndicatorAction = None

    def getControllerID(self):
        return BATTLE_CTRL_ID.SPOTTING_INDICATORS_CTRL

    def bindSpottingIndicator(self, indicator):
        raise NotImplementedError

    def unbindSpottingIndicator(self, indicator):
        raise NotImplementedError


class IndicatorAction(Enum):
    SHOW = 'show'
    HIDE = 'hide'
    PASS = 'pass'


_TYPE = DIRECT_DETECTION_TYPE
SPOTTING_INDICATORS_PRIORITY = ((_TYPE.UNSPOTTED,), (_TYPE.RAYTRACE,
  _TYPE.RECON,
  _TYPE.FORCED,
  _TYPE.STEALTH_RADAR), (_TYPE.SPECIAL_RECON,))
_PRIORITY_BY_DETECTION_TYPE = {detectionType:priority for priority, detectionTypes in enumerate(SPOTTING_INDICATORS_PRIORITY) for detectionType in detectionTypes}

def bindSpottingIndicator(indicator):
    spot = instance(IBattleSessionProvider).shared.spottingIndicatorsCtrl
    if spot is not None:
        spot.bindSpottingIndicator(indicator)
    else:
        _logger.error('Tryng to bind this indicator: %s, when controller is None', indicator)
    return


def unbindSpottingIndicator(indicator):
    spot = instance(IBattleSessionProvider).shared.spottingIndicatorsCtrl
    if spot is not None:
        spot.unbindSpottingIndicator(indicator)
    return


class SpottingIndicatorsController(ISpottingIndicatorsController):
    __slots__ = ('onSpottingIndicatorAction', '_vehicleState', '__detectionType', '__visToggleByType', '_durationByType', '__showTimerID', '__prevControllingVehID', '__enabledByType', '__weakref__')

    def __init__(self, vehicleState):
        self._vehicleState = vehicleState
        self.onSpottingIndicatorAction = Event()
        self.__detectionType = None
        self.__visToggleByType = {}
        self._durationByType = {}
        self.__enabledByType = {}
        self.__showTimerID = None
        self.__prevControllingVehID = 0
        return

    def startControl(self):
        state = self._vehicleState
        state.onVehicleControlling += self._onVehicleControlling
        state.onPostMortemSwitched += self.__onPostMortemSwitched
        g_playerEvents.onObservedByEnemy += self._onObservedByEnemy

    def bindSpottingIndicator(self, indicator):
        for detectionType, toggle, duration, isEnabled in indicator.getIndicatorTogglesByType():
            self.__visToggleByType[detectionType] = toggle
            self._durationByType[detectionType] = duration
            self.__enabledByType[detectionType] = isEnabled

    def unbindSpottingIndicator(self, indicator):
        for detectionType, toggle, duration, isEnabled in indicator.getIndicatorTogglesByType():
            if detectionType in self.__visToggleByType:
                self._hideSpottingIndicator(detectionType, force=True)
                del self.__visToggleByType[detectionType]
                del self._durationByType[detectionType]
                del self.__enabledByType[detectionType]

    def stopControl(self):
        self._hideSpottingIndicator(force=True)
        state = self._vehicleState
        state.onVehicleControlling -= self._onVehicleControlling
        state.onPostMortemSwitched -= self.__onPostMortemSwitched
        self._vehicleState = None
        g_playerEvents.onObservedByEnemy -= self._onObservedByEnemy
        self.onSpottingIndicatorAction.clear()
        self.__visToggleByType.clear()
        self._durationByType.clear()
        self.__enabledByType.clear()
        return

    def _getIndicatorAction(self, newDetectionType, isObserved):
        if newDetectionType not in self.__visToggleByType:
            return IndicatorAction.PASS
        else:
            oldDetectionType = self.__detectionType
            enabled = self.__enabledByType[newDetectionType]()
            if not enabled and oldDetectionType == newDetectionType:
                return IndicatorAction.HIDE
            if not isObserved:
                if oldDetectionType == newDetectionType:
                    return IndicatorAction.HIDE
                return IndicatorAction.PASS
            hasIndicator = oldDetectionType is not None
            if hasIndicator and oldDetectionType == newDetectionType:
                return IndicatorAction.PASS
            if not hasIndicator:
                return IndicatorAction.SHOW
            oldPriority = _PRIORITY_BY_DETECTION_TYPE[oldDetectionType]
            newPriority = _PRIORITY_BY_DETECTION_TYPE[newDetectionType]
            return IndicatorAction.PASS if oldPriority >= newPriority else IndicatorAction.SHOW

    def _onObservedByEnemy(self, detectionType, isObserved):
        action = self._getIndicatorAction(detectionType, isObserved)
        if action == IndicatorAction.SHOW:
            self._showSpottingIndicator(detectionType)
        elif action == IndicatorAction.HIDE:
            self._hideSpottingIndicator(detectionType)

    def _showSpottingIndicator(self, detectionType):
        self._hideSpottingIndicator()
        toggle = self.__visToggleByType[detectionType]
        toggle(True, False)
        self.__detectionType = detectionType
        self._startShowTimer(detectionType)
        self._callOnSpottingIndicatorAction(detectionType, True)

    def _startShowTimer(self, detectionType, duration=None):
        if duration is None:
            duration = self._durationByType[detectionType]
        if duration:
            self.__showTimerID = BigWorld.callback(duration, partial(self.__onShowTimerCB, detectionType))
        return

    def _hideSpottingIndicator(self, detectionType=None, force=False):
        if self.__detectionType is None:
            return
        elif detectionType is not None and self.__detectionType != detectionType:
            return
        else:
            detectionType = self.__detectionType
            toggle = self.__visToggleByType[detectionType]
            toggle(False, force)
            self._cancelShowTimer()
            self.__detectionType = None
            self._callOnSpottingIndicatorAction(detectionType, False)
            return

    def _callOnSpottingIndicatorAction(self, detectionType, isVisible):
        self.onSpottingIndicatorAction(detectionType, isVisible)

    def _onVehicleControlling(self, vehicle):
        if self.__prevControllingVehID != vehicle.id:
            self.__prevControllingVehID = vehicle.id
            self._hideSpottingIndicator(force=True)

    def __onPostMortemSwitched(self, _, __):
        self._hideSpottingIndicator(force=True)

    def __onShowTimerCB(self, detectionType):
        self.__showTimerID = None
        self._hideSpottingIndicator(detectionType)
        return

    def _cancelShowTimer(self):
        if self.__showTimerID is not None:
            BigWorld.cancelCallback(self.__showTimerID)
            self.__showTimerID = None
        return


class _Replay(SpottingIndicatorsController):
    __slots__ = ()
    __stateTransitionEvents = []

    def startControl(self):
        super(_Replay, self).startControl()
        g_replayEvents.onTimeWarpStart += self.__onTimeWarpStart
        g_replayEvents.onTimeWarpFinish += self.__onTimeWarpFinish

    def stopControl(self):
        g_replayEvents.onTimeWarpFinish -= self.__onTimeWarpFinish
        g_replayEvents.onTimeWarpStart -= self.__onTimeWarpStart
        super(_Replay, self).stopControl()

    def _getIndicatorAction(self, newDetectionType, isObserved):
        isTimeWarp = g_replayEvents.isTimeWarp
        if isTimeWarp and g_replayEvents.isLastWarpRewind:
            return IndicatorAction.PASS
        action = super(_Replay, self)._getIndicatorAction(newDetectionType, isObserved)
        if not isTimeWarp:
            return action
        if action == IndicatorAction.SHOW:
            self.__recordEvent(newDetectionType, True)
        elif action == IndicatorAction.HIDE:
            self.__recordEvent(newDetectionType, False)
        return IndicatorAction.PASS

    def _startShowTimer(self, detectionType, duration=None):
        timeLeft = self.__getLastEventTimeLeft() if g_replayEvents.isTimeWarp else None
        super(_Replay, self)._startShowTimer(detectionType, timeLeft)
        return

    def _onVehicleControlling(self, vehicle):
        pass

    def _callOnSpottingIndicatorAction(self, detectionType, isVisible):
        if g_replayEvents.isTimeWarp:
            return
        self.__recordEvent(detectionType, isVisible)
        super(_Replay, self)._callOnSpottingIndicatorAction(detectionType, isVisible)

    def __onTimeWarpStart(self):
        self._cancelShowTimer()

    def __onTimeWarpFinish(self):
        self._hideSpottingIndicator(force=True)
        events = self.__stateTransitionEvents
        if not events:
            return
        if g_replayEvents.isLastWarpRewind:
            now = BigWorld.time()
            while events:
                if events[-1][0] < now:
                    break
                del events[-1]
            else:
                self._hideSpottingIndicator(force=True)
                return

        _, detectionType, isVisible = events[-1]
        timeLeft = self.__getLastEventTimeLeft()
        if isVisible and (timeLeft or not self._durationByType[detectionType]):
            self._showSpottingIndicator(detectionType)

    def __getLastEventTimeLeft(self):
        events = self.__stateTransitionEvents
        if not events:
            return 0.0
        startTime, detectionType, isVisible = events[-1]
        if not isVisible:
            return 0.0
        now = BigWorld.time()
        elapsed = now - startTime
        duration = self._durationByType[detectionType]
        timeLeft = max(0.0, duration - elapsed)
        return timeLeft

    def __recordEvent(self, detectionType, isVisible):
        self.__stateTransitionEvents.append((BigWorld.time(), detectionType, isVisible))

    def __repr__(self):
        pass


def createCtrl(setup, state):
    return _Replay(state) if setup.isReplayPlaying else SpottingIndicatorsController(state)
