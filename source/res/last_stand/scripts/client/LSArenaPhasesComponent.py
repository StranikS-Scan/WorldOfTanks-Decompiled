# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/LSArenaPhasesComponent.py
import BigWorld
from helpers import isPlayerAvatar
from script_component.DynamicScriptComponent import DynamicScriptComponent
import Event
import logging
from helpers.CallbackDelayer import CallbackDelayer
from helpers.EffectsList import effectsFromSection, EffectsListPlayer
from helpers import newFakeModel
from ls_dyn_object_cache import LSEffects, getEffectSection
from last_stand_common.last_stand_constants import INVALID_PHASE
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
_logger = logging.getLogger(__name__)

class LSEnvironmentSwitcher(object):

    def __init__(self, spaceID):
        self._isSwitchInProcess = False
        self._callbackDelayer = CallbackDelayer()
        self._fakeModel = None
        self._effectsPlayer = None
        self._spaceID = spaceID
        section = getEffectSection(LSEffects.PHASE_SWITCH)
        self._effects = effectsFromSection(section)
        self._envSwitchDelay = section['envSwitchDelay'].asFloat
        return

    def onDestroy(self):
        self._effects = None
        self._callbackDelayer.destroy()
        self._cancelOngoingSwitcher()
        return

    def setupEnvironment(self, envName, isInstantSwitch=False):
        self._cancelOngoingSwitcher()
        if isInstantSwitch or self._effects is None:
            self._switchEnvironment(envName)
            return
        else:
            self._fakeModel = newFakeModel()
            BigWorld.player().addModel(self._fakeModel)
            self._effectsPlayer = EffectsListPlayer(self._effects.effectsList, self._effects.keyPoints, debugParent=self)
            self._effectsPlayer.play(self._fakeModel, callbackFunc=self._cancelOngoingSwitcher)
            self._callbackDelayer.delayCallback(self._envSwitchDelay, self._switchEnvironment, envName)
            return

    def _cancelOngoingSwitcher(self):
        self._callbackDelayer.clearCallbacks()
        if self._effectsPlayer:
            self._effectsPlayer.stop()
            self._effectsPlayer = None
        if self._fakeModel:
            BigWorld.player().delModel(self._fakeModel)
            self._fakeModel = None
        return

    def _switchEnvironment(self, envName):
        BigWorld.spaces[self._spaceID].setEnvironment(envName)


class LSArenaPhasesComponent(DynamicScriptComponent):
    onPhaseChanged = Event.Event()
    onPhaseTimeChanged = Event.Event()
    onHideVehicleOnMinimap = Event.Event()

    def __init__(self):
        super(LSArenaPhasesComponent, self).__init__()
        self.envSwitcher = LSEnvironmentSwitcher(self.entity.spaceID)
        g_eventBus.addListener(GameEvent.BATTLE_LOADING, self._onBattleLoading, scope=EVENT_BUS_SCOPE.BATTLE)

    def onDestroy(self):
        if self.envSwitcher:
            self.envSwitcher.onDestroy()
            self.envSwitcher = None
        self.onPhaseChanged.clear()
        self.onPhaseTimeChanged.clear()
        g_eventBus.removeListener(GameEvent.BATTLE_LOADING, self._onBattleLoading, scope=EVENT_BUS_SCOPE.BATTLE)
        super(LSArenaPhasesComponent, self).onDestroy()
        return

    def _onAvatarReady(self):
        if self.phasesCount:
            self.onPhaseChanged(self)
            lastPhase = self.activePhase == self.phasesCount
            self.onPhaseTimeChanged(self.timeLeft, self.timeLeft, lastPhase, self.isTimerAlarmEnabled)
        self._setupEnvironment(True)

    def set_activePhase(self, prev):
        _logger.info('LSArenaPhasesComponent set activePhase=%s', self.activePhase)
        if prev != self.activePhase:
            self.onPhaseChanged(self)

    def set_timeLeft(self, prev):
        lastPhase = self.activePhase == self.phasesCount
        self.onPhaseTimeChanged(self.timeLeft, prev, lastPhase, self.isTimerAlarmEnabled)

    def set_activeEnvironment(self, prev):
        if not self._isAvatarReady:
            return
        self._setupEnvironment()

    def _setupEnvironment(self, isInstant=False):
        if self.envSwitcher is None or not self.activeEnvironment:
            return
        else:
            self.envSwitcher.setupEnvironment(self.activeEnvironment, isInstant)
            return

    def hideVehicleOnMinimap(self, vehicleID):
        self.onHideVehicleOnMinimap(vehicleID)

    def isLastPhase(self):
        return self.activePhase == self.phasesCount and self.activePhase != INVALID_PHASE

    @staticmethod
    def getInstance():
        if not isPlayerAvatar():
            return None
        else:
            player = BigWorld.player()
            if not player:
                return None
            return None if not player.arena or not player.arena.arenaInfo else getattr(player.arena.arenaInfo, 'LSArenaPhasesComponent', None)

    def _onBattleLoading(self, event):
        if event.ctx.get('isShown'):
            self._setupEnvironment(True)
