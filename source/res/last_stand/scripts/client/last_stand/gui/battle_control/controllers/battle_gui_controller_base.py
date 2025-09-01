# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/battle_control/controllers/battle_gui_controller_base.py
import BattleReplay
import BigWorld
import logging
from Event import EventManager, Event
from PlayerEvents import g_playerEvents
from last_stand.gui.ls_gui_constants import BATTLE_CTRL_ID
from helpers import dependency, isPlayerAvatar
from skeletons.gui.battle_session import IBattleSessionProvider
from LSArenaPhasesComponent import LSArenaPhasesComponent
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from helpers.CallbackDelayer import CallbackDelayer
_logger = logging.getLogger(__name__)

class EventBattleGoal(object):
    UNKNOWN = None


class LSBattleGUIControllerBase(IArenaVehiclesController):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    _TIME_TO_END_NOTIFY = 10
    _UPDATE_PERIOD = 0.5
    _BATTLE_GOALS_WITHOUT_TIMER = []

    def __init__(self):
        super(LSBattleGUIControllerBase, self).__init__()
        self._eManager = EventManager()
        self.onBattleGoalChanged = Event(self._eManager)
        self.onVehicleBuffIconAdded = Event(self._eManager)
        self.onVehicleBuffIconRemoved = Event(self._eManager)
        self.onPhaseChanged = Event(self._eManager)
        self.onHandleEquipmentPressed = Event(self._eManager)
        self.onSoulsContainerReady = Event(self._eManager)
        self.onPhaseTimeChanged = Event(self._eManager)
        self.onInvulnerableStateChanged = Event(self._eManager)
        self.onVehicleInvulnerabilityChanged = Event(self._eManager)
        self._callbackDelayer = CallbackDelayer()
        self._currentGoal = EventBattleGoal.UNKNOWN
        self._vehicleMarkerIcons = {}
        self._hiddenVehicleIDs = set()
        self._invulnerableVehiclesIDs = set()
        self._pendingHint = None
        self.isEventTimerEnabled = True
        return

    @property
    def currentGoal(self):
        return self._currentGoal

    @property
    def vehicleMarkerIcons(self):
        return self._vehicleMarkerIcons

    @property
    def battleHintsCtrl(self):
        return self.guiSessionProvider.dynamic.battleHints

    def getControllerID(self):
        return BATTLE_CTRL_ID.LS_BATTLE_GUI_CTRL

    def startControl(self, battleCtx, arenaVisitor):
        super(LSBattleGUIControllerBase, self).startControl(battleCtx, arenaVisitor)
        self._callbackDelayer.delayCallback(self._UPDATE_PERIOD, self._update)
        LSArenaPhasesComponent.onPhaseChanged += self._onPhaseChanged
        LSArenaPhasesComponent.onPhaseTimeChanged += self._onPhaseTimeChanged
        g_playerEvents.onHideBattleHint += self._onHideBattleHint

    def stopControl(self):
        LSArenaPhasesComponent.onPhaseChanged -= self._onPhaseChanged
        LSArenaPhasesComponent.onPhaseTimeChanged -= self._onPhaseTimeChanged
        g_playerEvents.onHideBattleHint -= self._onHideBattleHint
        self._callbackDelayer.clearCallbacks()
        self._eManager.clear()
        self._vehicleMarkerIcons.clear()
        self._hiddenVehicleIDs.clear()
        self._invulnerableVehiclesIDs.clear()
        self._pendingHint = None
        super(LSBattleGUIControllerBase, self).stopControl()
        return

    def setVehicleHidden(self, vehicleID, isHidden):
        if isHidden:
            self.guiSessionProvider.shared.feedback.onVehicleMarkerRemoved(vehicleID)
            self._hiddenVehicleIDs.add(vehicleID)
        else:
            self._hiddenVehicleIDs.discard(vehicleID)

    def setVehicleInvulnerable(self, vehicleID, isInvulnerable):
        if isInvulnerable:
            self._invulnerableVehiclesIDs.add(vehicleID)
        else:
            self._invulnerableVehiclesIDs.discard(vehicleID)
        self.onVehicleInvulnerabilityChanged(vehicleID, isInvulnerable)

    def isVehicleHidden(self, vehicleID):
        return vehicleID in self._hiddenVehicleIDs

    def isVehicleInvulnerable(self, vehicleID):
        return vehicleID in self._invulnerableVehiclesIDs

    def addVehicleMarkerIcon(self, vehicleID, iconName):
        self._vehicleMarkerIcons.setdefault(vehicleID, set()).add(iconName)
        self.onVehicleBuffIconAdded(vehicleID, iconName)

    def removeVehicleMarkerIcon(self, vehicleID, iconName):
        self._vehicleMarkerIcons.get(vehicleID, set()).discard(iconName)
        self.onVehicleBuffIconRemoved(vehicleID, iconName)

    def _onPhaseChanged(self, arenaPhases):
        self.onPhaseChanged()

    def _onPhaseTimeChanged(self, timeLeft, prev, lastPhase, isTimerAlarmEnabled):
        self.onPhaseTimeChanged(timeLeft, prev, lastPhase, isTimerAlarmEnabled)

    def _update(self):
        if not isPlayerAvatar():
            return self._UPDATE_PERIOD
        else:
            relevantGoal = self._getRelevantGoal()
            if relevantGoal != self._currentGoal:
                self.onBattleGoalChanged(relevantGoal)
                self._removeBattleCommunicationMarkers(relevantGoal)
                self._pendingHint = (self._currentGoal, relevantGoal)
                self._currentGoal = relevantGoal
                if self._currentGoal in self._BATTLE_GOALS_WITHOUT_TIMER:
                    self.isEventTimerEnabled = BattleReplay.g_replayCtrl.isPlaying
            if self._pendingHint is not None and self._showRelevantBattleHint(*self._pendingHint):
                self._pendingHint = None
            return self._UPDATE_PERIOD

    def _getRelevantGoal(self):
        return EventBattleGoal.UNKNOWN

    def _getAliveAllyVehicles(self):
        arenaDP = self.guiSessionProvider.getArenaDP()
        return [ vInfo.vehicleID for vInfo in arenaDP.getVehiclesInfoIterator() if arenaDP.isAllyTeam(vInfo.team) and vInfo.isAlive() ]

    def _showRelevantBattleHint(self, prevGoal, newGoal):
        if self.battleHintsCtrl is None:
            _logger.warning('BattleHintsController is not loaded. Battle hint (%s) will not be displayed.', newGoal)
            return False
        else:
            if prevGoal is not None:
                self.battleHintsCtrl.removeHint(prevGoal, hide=True)
            if newGoal is None:
                return True
            self.battleHintsCtrl.showHint(newGoal, params=self._getHintParams())
            success = self.battleHintsCtrl.checkHintInQueue(newGoal)
            if not success and not BattleReplay.g_replayCtrl.isPlaying:
                _logger.warning('Hint (%s) will not be displayed. Will retry on the next update.', newGoal)
            return success

    def _isPlayerVehicle(self, vehicleID):
        player = BigWorld.player()
        return False if not player else vehicleID == player.playerVehicleID

    def _getHintParams(self):
        return None

    def _onHideBattleHint(self, battleHint):
        if battleHint.uniqueName in self._BATTLE_GOALS_WITHOUT_TIMER:
            self.isEventTimerEnabled = True

    def _removeBattleCommunicationMarkers(self, goal):
        pass
