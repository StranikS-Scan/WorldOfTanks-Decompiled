# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWArenaSoundComponent.py
from __future__ import absolute_import
import logging
import WWISE
import BigWorld
from constants import ARENA_PERIOD
from PlayerEvents import g_playerEvents
from halloween.gui.sounds.voiceovers import Voiceover
from script_component.DynamicScriptComponent import DynamicScriptComponent
from HWArenaPhasesComponent import HWArenaPhasesComponent
from halloween_common.halloween_constants import INVALID_PHASE, ARENA_BONUS_TYPE
from halloween.gui.sounds.sound_constants import BATTLE_START, ACTIVE_PHASE_RTPC, BATTLE_FINISH, PHASE_CHANGED, ARENA_PHASE_END_WARNING_EVENT_PREFIX, ActivePhaseState, DifficultyState, PhaseStartedVoiceover
from halloween.gui.sounds.arena_components import HWStaticDeathZoneSounds, HWPostMortemSounds, HWArenaLootSounds, HWBossBattleMusic, HWHexapodBossBattleMusic, HWEquipmentPanelSounds, HWBuffsPanelSounds, HWPersonalDeathZoneSounds, HWVoiceovers, HWTeamFightVoiceovers, HWPhaseStateUpdateSounds, HWVehicleDetectorSounds, HWBotSpawnSounds
from halloween.gui.sounds import playSound, ComponentsHolder
_logger = logging.getLogger(__name__)
_ARENA_SOUND_COMPONENTS = [HWStaticDeathZoneSounds,
 HWPostMortemSounds,
 HWEquipmentPanelSounds,
 HWBuffsPanelSounds,
 HWPersonalDeathZoneSounds,
 HWVoiceovers,
 HWTeamFightVoiceovers,
 HWPhaseStateUpdateSounds,
 HWVehicleDetectorSounds,
 HWBotSpawnSounds,
 HWArenaLootSounds]
_ARENA_SOUND_COMPONENTS_CONDITIONAL = [(HWBossBattleMusic, lambda parent: parent.arena.bonusType in (ARENA_BONUS_TYPE.HALLOWEEN,)), (HWHexapodBossBattleMusic, lambda parent: parent.arena.bonusType in (ARENA_BONUS_TYPE.HALLOWEEN_MEDIUM, ARENA_BONUS_TYPE.HALLOWEEN_HARD))]
_SUPPORTED_END_WARNING_PHASE_IDS = (1, 2, 3)
_PHASE_END_WARNING_TIME_OFFSET = 62

class HWArenaSoundComponent(DynamicScriptComponent):

    def __init__(self):
        super(HWArenaSoundComponent, self).__init__()
        self._components = ComponentsHolder(_ARENA_SOUND_COMPONENTS, self)
        self._shouldTriggerPhaseEndWarningEvent = False
        self._bossAuraIntersectionsCounter = 0
        self._ongoingSoundsPlayed = False

    def onDestroy(self):
        HWArenaPhasesComponent.onPhaseChanged -= self._onPhaseChanged
        HWArenaPhasesComponent.onPhaseTimeChanged -= self._onPhaseTimeChanged
        g_playerEvents.onArenaPeriodChange -= self._onArenaPeriodChaned
        if BigWorld.player().arena.period == ARENA_PERIOD.BATTLE:
            playSound(BATTLE_FINISH)
        self._components.onDestroy()
        super(HWArenaSoundComponent, self).onDestroy()

    def _onAvatarReady(self):
        self._components.extend([ component for component, condition in _ARENA_SOUND_COMPONENTS_CONDITIONAL if condition(self) ], self)
        HWArenaPhasesComponent.onPhaseChanged += self._onPhaseChanged
        HWArenaPhasesComponent.onPhaseTimeChanged += self._onPhaseTimeChanged
        g_playerEvents.onArenaPeriodChange += self._onArenaPeriodChaned
        arena = BigWorld.player().arena
        if arena.period == ARENA_PERIOD.BATTLE:
            playSound(BATTLE_START)
        self._setPhaseStates(HWArenaPhasesComponent.getInstance().activePhase)
        self._components.onAvatarReady()
        WWISE.WW_setState(DifficultyState.GROUP, DifficultyState.VALUE(arena.bonusType))
        for event in self.ongoingSoundEvents:
            playSound(event)

        self._ongoingSoundsPlayed = True

    def onBotCreated(self, vehicleType, position):
        self._components.call('onBotCreated', vehicleType, position)

    def onPlaySoundEvent(self, event):
        if self._ongoingSoundsPlayed:
            playSound(event)

    def onPlayVoiceover(self, voiceover, exposition, aliveOnly):
        if self._isAvatarReady:
            Voiceover(voiceover, exposition, aliveOnly=aliveOnly).play()

    def onShotAtBoss(self, attackerID, attackReason, damage):
        self._components.call('onShotAtBoss', attackerID, attackReason, damage)

    def onBossEnterWorld(self, bossEntity):
        self._components.call('onBossEnterWorld', bossEntity)

    @property
    def arena(self):
        player = BigWorld.player()
        return None if not player else player.arena

    def _onPhaseChanged(self, arenaPhases):
        activePhase = arenaPhases.activePhase
        self._setPhaseStates(activePhase)
        PhaseStartedVoiceover.get(activePhase).play()
        if activePhase > 1:
            playSound(PHASE_CHANGED)

    def _setPhaseStates(self, activePhase):
        if activePhase == INVALID_PHASE:
            return
        self._shouldTriggerPhaseEndWarningEvent = activePhase in _SUPPORTED_END_WARNING_PHASE_IDS
        WWISE.WW_setRTCPGlobal(ACTIVE_PHASE_RTPC, activePhase)
        WWISE.WW_setState(ActivePhaseState.GROUP, ActivePhaseState.getStateByPhase(activePhase))

    def _onPhaseTimeChanged(self, timeLeft, _, lastPhase):
        if not lastPhase and self._shouldTriggerPhaseEndWarningEvent:
            self._shouldTriggerPhaseEndWarningEvent = 0 < timeLeft <= _PHASE_END_WARNING_TIME_OFFSET and False
            playSound(ARENA_PHASE_END_WARNING_EVENT_PREFIX.format(phase=HWArenaPhasesComponent.getInstance().activePhase))

    def _onArenaPeriodChaned(self, period, *_):
        if period == ARENA_PERIOD.BATTLE:
            playSound(BATTLE_START)
        elif period == ARENA_PERIOD.AFTERBATTLE:
            playSound(BATTLE_FINISH)

    def onBossAuraIntersect(self, vehicleId, entered):
        player = BigWorld.player()
        if not player or player.playerVehicleID != vehicleId:
            return
        if entered:
            if self._bossAuraIntersectionsCounter == 0:
                self._components.call('onBossAuraIntersectEvent', vehicleId, True)
            self._bossAuraIntersectionsCounter += 1
        else:
            self._bossAuraIntersectionsCounter -= 1
            if self._bossAuraIntersectionsCounter == 0:
                self._components.call('onBossAuraIntersectEvent', vehicleId, False)
