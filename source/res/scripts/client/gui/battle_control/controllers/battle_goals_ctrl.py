# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/battle_goals_ctrl.py
import time
import logging
import BigWorld
from Event import Event
from helpers import dependency
from constants import ECP_SWITCHES
from gui.battle_control.battle_constants import BATTLE_CTRL_ID, VEHICLE_VIEW_STATE, EventBattleGoal, SoulCollectorDestroyTimerState
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.battle_control.arena_info.settings import VEHICLE_STATUS
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.Scaleform.daapi.view.battle.event.game_event_getter import GameEventGetterMixin
from helpers.CallbackDelayer import CallbackDelayer, TimeDeltaMeter
_logger = logging.getLogger(__name__)

class BattleGoalsController(IArenaVehiclesController, GameEventGetterMixin):

    class Events(object):

        def __init__(self):
            super(BattleGoalsController.Events, self).__init__()
            self.onTimerUpdated = Event()
            self.onUpdatePointerMessage = Event()
            self.onGoalChanged = Event()

    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _UPDATE_PERIOD = 0.25
    _DEFAULT_TIME = 300
    _ALARM_TIME = 10
    _COLLECT_MATTER = 'collectMatter'
    _DELIVER_MATTER = 'deliverMatter'
    _GET_TO_POINT = 'getToPoint'
    _GOAL_HINTS = {EventBattleGoal.UNKNOWN: None,
     EventBattleGoal.COLLECT_MATTER: _COLLECT_MATTER,
     EventBattleGoal.DELIVER_MATTER: _DELIVER_MATTER,
     EventBattleGoal.GET_TO_COLLECTOR: _GET_TO_POINT}
    _DESTROY_TIMER_RETENTION_TIME = {SoulCollectorDestroyTimerState.COLLECTOR_PROGRESS: 2.0}

    def __init__(self):
        GameEventGetterMixin.__init__(self)
        self._events = self.Events()
        self._callbackDelayer = CallbackDelayer()
        self._deltaMeter = TimeDeltaMeter(time.clock)
        self._currentGoal = EventBattleGoal.UNKNOWN
        self._currentHint = None
        self._currentCollectorID = None
        self._time = self._DEFAULT_TIME
        self._isTimerVisible = False
        self._destroyTimerState = SoulCollectorDestroyTimerState.NO_TIMER
        self._destroyTimerRetentionTime = 0.0
        return

    @property
    def events(self):
        return self._events

    @property
    def isAlarm(self):
        return self._time <= self._ALARM_TIME

    @property
    def currentGoal(self):
        return self._currentGoal

    @property
    def currentCollectorID(self):
        return self._currentCollectorID

    @property
    def destroyTimerState(self):
        return self._destroyTimerState

    @property
    def currentTime(self):
        return self._time

    def isVehicleNearCollector(self, vehicle):
        if not self._currentCollectorID or not vehicle:
            return False
        collector = BigWorld.entities.get(self._currentCollectorID)
        if not collector:
            return False
        pos = collector.position
        distance = (pos - vehicle.position).length
        return distance < collector.radius

    def startControl(self, battleCtx, arenaVisitor):
        self._callbackDelayer.delayCallback(self._UPDATE_PERIOD, self._update)
        self._deltaMeter.measureDeltaTime()
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onUpdateScenarioTimer += self._onUpdateScenarioTimer
        g_eventBus.addListener(events.BattleHintEvent.ON_HIDE, self._handleHintOnHide, scope=EVENT_BUS_SCOPE.BATTLE)
        self.environmentData.onEnvironmentEventIDUpdate += self.__onEnvironmentEventIDUpdate
        return

    def stopControl(self):
        self._callbackDelayer.clearCallbacks()
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onUpdateScenarioTimer -= self._onUpdateScenarioTimer
        g_eventBus.removeListener(events.BattleHintEvent.ON_HIDE, self._handleHintOnHide, scope=EVENT_BUS_SCOPE.BATTLE)
        self.environmentData.onEnvironmentEventIDUpdate -= self.__onEnvironmentEventIDUpdate
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.BATTLE_GOALS

    def getCurrentCollectorSoulsInfo(self):
        if not self.soulCollector or not self._currentCollectorID:
            return (0, 0)
        else:
            soulCollectorsData = self.soulCollector.getSoulCollectorData()
            if soulCollectorsData:
                collector = soulCollectorsData.get(self._currentCollectorID, None)
                if collector:
                    return (float(collector[0]), float(collector[1]))
            return (0, 0)

    def _update(self):
        self._currentCollectorID = self._findCurrentCollector()
        soulsCollected, collectorCapacity = self.getCurrentCollectorSoulsInfo()
        self._updateDestroyTimer(soulsCollected, collectorCapacity)
        return self._UPDATE_PERIOD

    def _onUpdateScenarioTimer(self, waitTime, alarmTime, isVisible):
        self._time = waitTime
        self._isTimerVisible = isVisible
        self.events.onTimerUpdated(self._time, isVisible, self.isAlarm)
        soulsCollected, collectorCapacity = self.getCurrentCollectorSoulsInfo()
        relevantGoal = self._getRelevantGoal(soulsCollected, collectorCapacity)
        goalChanged = relevantGoal != self._currentGoal
        if goalChanged:
            self._currentGoal = relevantGoal
            self.events.onGoalChanged(collectorID=self._currentCollectorID, relevantGoal=relevantGoal)
            if isVisible:
                self._showRelevantBattleHint()
        if not isVisible and self._currentHint is not None:
            self._hideBattleHint()
        self._updateDestroyTimer(soulsCollected, collectorCapacity, goalChanged)
        return

    def _handleHintOnHide(self, event):
        if event.ctx['hint'] != self._currentHint:
            return
        else:
            self._currentHint = None
            self.events.onUpdatePointerMessage(self._currentGoal)
            return

    def _showRelevantBattleHint(self):
        self.events.onUpdatePointerMessage(None)
        battleHints = self.sessionProvider.dynamic.battleHints
        if battleHints is None:
            return
        else:
            oldHint = self._currentHint
            self._currentHint = self._GOAL_HINTS[self._currentGoal]
            if oldHint is not None:
                battleHints.removeHintFromQueue(oldHint)
                battleHints.hideHint(oldHint)
            if self._currentHint is None:
                return
            battleHints.showHint(self._currentHint)
            return

    def _hideBattleHint(self):
        self.events.onUpdatePointerMessage(None)
        battleHints = self.sessionProvider.dynamic.battleHints
        if battleHints is None:
            return
        else:
            battleHints.removeHintFromQueue(self._currentHint)
            battleHints.hideHint(self._currentHint)
            self._currentHint = None
            return

    def _updateDestroyTimer(self, soulsCollected, collectorCapacity, forceInvalidate=False):
        self._destroyTimerRetentionTime -= self._deltaMeter.measureDeltaTime()
        relevantDestroyTimerState = self._getRelevantDestroyTimerState()
        needInvalidateTimer = forceInvalidate
        if self._destroyTimerState != relevantDestroyTimerState:
            if self._destroyTimerRetentionTime <= 0.0 or self._isDestroyTimerSuppressed():
                self._destroyTimerState = relevantDestroyTimerState
                self._destroyTimerRetentionTime = self._DESTROY_TIMER_RETENTION_TIME.get(self._destroyTimerState, 0.0)
                needInvalidateTimer = True
        else:
            self._destroyTimerRetentionTime = self._DESTROY_TIMER_RETENTION_TIME.get(self._destroyTimerState, 0.0)
        if self._destroyTimerState == SoulCollectorDestroyTimerState.COLLECTOR_PROGRESS:
            needInvalidateTimer = self._currentCollectorID is not None
        if needInvalidateTimer:
            data = self._buildDestroyTimerStateData(self._destroyTimerState, soulsCollected, collectorCapacity)
            self.sessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.COLLECTOR_STATUS, data)
        return

    def _getRelevantDestroyTimerState(self):
        vehicle = BigWorld.player().vehicle
        if self._isDestroyTimerSuppressed():
            return SoulCollectorDestroyTimerState.NO_TIMER
        isNear = self.isVehicleNearCollector(vehicle)
        if isNear and self._currentGoal == EventBattleGoal.GET_TO_COLLECTOR:
            return SoulCollectorDestroyTimerState.WAIT_ALLIES
        if isNear and self._getVehicleSouls(vehicle.id):
            return SoulCollectorDestroyTimerState.COLLECTOR_PROGRESS
        return SoulCollectorDestroyTimerState.ALARM_TIMER if self.isAlarm else SoulCollectorDestroyTimerState.NO_TIMER

    def _buildDestroyTimerStateData(self, state, soulsCollected, collectorCapacity):
        result = {'state': state}
        if state == SoulCollectorDestroyTimerState.COLLECTOR_PROGRESS:
            result['soulsCollected'] = soulsCollected
            result['collectorCapacity'] = collectorCapacity
            result['isActive'] = self._currentGoal in (EventBattleGoal.DELIVER_MATTER, EventBattleGoal.GET_TO_COLLECTOR)
        elif state == SoulCollectorDestroyTimerState.ALARM_TIMER:
            result['timeLeft'] = self._time
            result['alarmTime'] = self._ALARM_TIME
            result['showMessage'] = self._currentGoal in (EventBattleGoal.DELIVER_MATTER, EventBattleGoal.GET_TO_COLLECTOR)
        return result

    def _getRelevantGoal(self, soulsCollected, collectorCapacity):
        if collectorCapacity <= 0 or self._currentCollectorID is None:
            return EventBattleGoal.UNKNOWN
        else:
            aliveVehiclesSouls = self._getAliveAllyVehiclesSouls()
            if not aliveVehiclesSouls:
                return EventBattleGoal.UNKNOWN
            if soulsCollected >= collectorCapacity:
                return EventBattleGoal.GET_TO_COLLECTOR
            playersSoulsCount = sum(aliveVehiclesSouls, 0)
            return EventBattleGoal.DELIVER_MATTER if soulsCollected + playersSoulsCount >= collectorCapacity else EventBattleGoal.COLLECT_MATTER

    def _findCurrentCollector(self):
        ecpStates = self.ecpState.getStates()
        if ecpStates is None:
            return
        else:
            for ecpID, ecp in ecpStates.iteritems():
                if ecp[0][5] == ECP_SWITCHES.on and ecp[1][5] > 0:
                    return ecpID

            return

    def _getAliveAllyVehiclesSouls(self):
        arenaDP = self.sessionProvider.getArenaDP()
        return [ self._getVehicleSouls(vInfo.vehicleID) for vInfo in arenaDP.getVehiclesInfoIterator() if arenaDP.isAllyTeam(vInfo.team) and vInfo.vehicleStatus & VEHICLE_STATUS.IS_ALIVE ]

    def _getVehicleSouls(self, vehID):
        return 0 if self.souls is None else self.souls.getSouls(vehID)

    def _isDestroyTimerSuppressed(self):
        player = BigWorld.player()
        vehicle = player.vehicle
        ownVeh = BigWorld.entity(player.playerVehicleID)
        return vehicle is None or ownVeh is None or not ownVeh.isAlive() or not self._isTimerVisible or self._currentCollectorID is None

    def __onEnvironmentEventIDUpdate(self, _):
        self._currentCollectorID = None
        self._currentGoal = EventBattleGoal.UNKNOWN
        return
