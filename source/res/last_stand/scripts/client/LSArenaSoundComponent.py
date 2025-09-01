# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/LSArenaSoundComponent.py
import WWISE
import BigWorld
import SoundGroups
from constants import ARENA_PERIOD
from PlayerEvents import g_playerEvents
from script_component.DynamicScriptComponent import DynamicScriptComponent
from LSArenaPhasesComponent import LSArenaPhasesComponent
from last_stand_common.last_stand_constants import INVALID_PHASE
from last_stand.gui.ls_gui_constants import BATTLE_CTRL_ID
from last_stand.gui.sounds.sound_constants import BOTS_SPAWN, BATTLE_START, BATTLE_FINISH, DifficultyState
from last_stand.gui.sounds.arena_components import LSStaticDeathZoneSounds, LSPostMortemSounds, LSEquipmentPanelSounds, LSPersonalDeathZoneSounds, LSVoiceovers, LSTeamFightVoiceovers, LSBattleMusic, LSConvoySounds
from last_stand.gui.sounds import playSound, ComponentsHolder
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_ARENA_SOUND_COMPONENTS = [LSStaticDeathZoneSounds,
 LSPostMortemSounds,
 LSEquipmentPanelSounds,
 LSPersonalDeathZoneSounds,
 LSVoiceovers,
 LSTeamFightVoiceovers,
 LSBattleMusic,
 LSConvoySounds]
_PHASE_END_WARNING_TIME_OFFSET = 62
_PHASE_END_WARNING_TIME_OFFSET_DELTA = 2
_LS_MODE_WORLD = 1

class LSArenaSoundComponent(DynamicScriptComponent):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(LSArenaSoundComponent, self).__init__()
        self._components = ComponentsHolder(_ARENA_SOUND_COMPONENTS, self)
        self._shouldTriggerPhaseEndWarningEvent = False

    @property
    def lsBattleGuiCtrl(self):
        return self._sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.LS_BATTLE_GUI_CTRL)

    def onDestroy(self):
        LSArenaPhasesComponent.onPhaseChanged -= self._onPhaseChanged
        if self.lsBattleGuiCtrl is not None:
            self.lsBattleGuiCtrl.onPhaseTimeChanged -= self._onPhaseTimeChanged
        g_playerEvents.onArenaPeriodChange -= self._onArenaPeriodChaned
        if BigWorld.player().arena.period == ARENA_PERIOD.BATTLE:
            playSound(BATTLE_FINISH)
        self._components.onDestroy()
        super(LSArenaSoundComponent, self).onDestroy()
        return

    def _onAvatarReady(self):
        LSArenaPhasesComponent.onPhaseChanged += self._onPhaseChanged
        if self.lsBattleGuiCtrl is not None:
            self.lsBattleGuiCtrl.onPhaseTimeChanged += self._onPhaseTimeChanged
        g_playerEvents.onArenaPeriodChange += self._onArenaPeriodChaned
        arena = BigWorld.player().arena
        if arena.period == ARENA_PERIOD.BATTLE:
            playSound(BATTLE_START)
        self._setPhaseStates(LSArenaPhasesComponent.getInstance().activePhase)
        self._components.onAvatarReady()
        WWISE.WW_setState(DifficultyState.GROUP, DifficultyState.VALUE(arena.bonusType))
        return

    def onBotCreated(self, vehicleType, position):
        spawnEvent = BOTS_SPAWN.get(vehicleType)
        if spawnEvent is not None:
            SoundGroups.g_instance.playSoundPos(spawnEvent, position)
        return

    def _onPhaseChanged(self, arenaPhases):
        activePhase = arenaPhases.activePhase
        self._setPhaseStates(activePhase)
        self._components.call('onPhaseChanged', activePhase)

    def _setPhaseStates(self, activePhase):
        if activePhase == INVALID_PHASE:
            return
        self._shouldTriggerPhaseEndWarningEvent = True

    def _onPhaseTimeChanged(self, timeLeft, _, lastPhase, isTimerAlarmEnabled):
        if isTimerAlarmEnabled and self._shouldTriggerPhaseEndWarningEvent:
            self._shouldTriggerPhaseEndWarningEvent = 0 < timeLeft <= _PHASE_END_WARNING_TIME_OFFSET and False
            isInDelta = _PHASE_END_WARNING_TIME_OFFSET - timeLeft < _PHASE_END_WARNING_TIME_OFFSET_DELTA
            self._components.call('oneMinuteLeft', lastPhase, isInDelta)

    def _onArenaPeriodChaned(self, period, *_):
        if period == ARENA_PERIOD.BATTLE:
            playSound(BATTLE_START)
        elif period == ARENA_PERIOD.AFTERBATTLE:
            playSound(BATTLE_FINISH)
