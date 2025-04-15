# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/sounds/sound_battle_controller.py
import typing
import math
import BigWorld
import SoundGroups
import WWISE
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from items.utils import isclose
from PlayerEvents import g_playerEvents
from ArenaPhasesComponent import ArenaPhasesComponent
from HBGoalComponent import HBGoalComponent
from HBBattleFeedbackComponent import HBBattleFeedbackComponent
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control import avatar_getter
from HBAvatarComponent import HBAvatarComponent
from HBTeamInfoComponent import HBTeamInfoComponent
from historical_battles.gui.sounds.sound_constants import HBBattleStates, HBGameplayVoiceovers, HBNotificationEvents, HBTimerEvents, HBUISound
from historical_battles.gui.sounds.sound_helpers import getArenaPhasesComponent
from historical_battles_common.hb_constants import GoalState, GoalBossId, HB_GAME_PARAMS_KEY
from historical_battles_common.hb_constants_extension import BATTLE_EVENT_TYPE
from historical_battles_common.hb_constants_extension import ARENA_BONUS_TYPE
from gui.battle_control.controllers.sound_ctrls.common import SoundPlayersBattleController
from shared_utils import nextTick
from functools import partial
if typing.TYPE_CHECKING:
    from typing import Optional
    from gui.battle_control.controllers.sound_ctrls.common import SoundPlayer
_FINISH_TIME_CORRECTION = 1
_UPDATE_TIMER_INTERVAL = 1
_TIME_IS_RUNNING_OUT = 10
_ONE_MINUTE_LEFT = 60
_TWO_MINUTES_LEFT = 120

class HBBattleSoundRemappingController(SoundPlayersBattleController):

    def startControl(self, *args):
        WWISE.activateRemapping(HB_GAME_PARAMS_KEY)
        super(HBBattleSoundRemappingController, self).startControl()

    def stopControl(self):
        super(HBBattleSoundRemappingController, self).stopControl()
        nextTick(partial(WWISE.deactivateRemapping, HB_GAME_PARAMS_KEY))()

    def _initializeSoundPlayers(self):
        pass


class SoundBattleController(CallbackDelayer):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _DEFENCE_SOUND_STATE = {1: HBBattleStates.RELAXED,
     2: HBBattleStates.BOSS_FIGHT}
    _OFFENCE_SOUND_STATE = {1: HBBattleStates.SILENCE,
     2: HBBattleStates.RELAXED,
     3: HBBattleStates.SILENCE,
     4: HBBattleStates.INTENSIVE,
     5: HBBattleStates.BOSS_FIGHT}

    def __init__(self):
        super(SoundBattleController, self).__init__()
        self.__goalID = None
        self.__lastGoalFinishedID = None
        self.__hurryUpTimerSoundIsPlaying = False
        self.__isWin = False
        self.__isEndOfBattle = False
        self.__isAloneInBattle = False
        self.__bonusType = BigWorld.player().arena.bonusType
        return

    def start(self):
        HBGoalComponent.onGoalsUpdated += self.__onGoalsUpdated
        ArenaPhasesComponent.onWavesUpdate += self.__onPhaseChanged
        HBAvatarComponent.onDeath += self.__onDeath
        HBTeamInfoComponent.onAllyInfoUpdated += self.__onAlliesUpdated
        HBBattleFeedbackComponent.onVehicleHeal += self.__onVehicleHeal
        g_playerEvents.onRoundFinished += self.__onRoundFinished

    def finalize(self):
        HBGoalComponent.onGoalsUpdated -= self.__onGoalsUpdated
        ArenaPhasesComponent.onWavesUpdate -= self.__onPhaseChanged
        HBAvatarComponent.onDeath -= self.__onDeath
        HBTeamInfoComponent.onAllyInfoUpdated -= self.__onAlliesUpdated
        HBBattleFeedbackComponent.onVehicleHeal -= self.__onVehicleHeal
        g_playerEvents.onRoundFinished -= self.__onRoundFinished
        if self.__hurryUpTimerSoundIsPlaying:
            SoundGroups.g_instance.playSound2D(HBTimerEvents.STOP)
            self.__hurryUpTimerSoundIsPlaying = False
        CallbackDelayer.destroy(self)

    def __onVehicleHeal(self, eventID):
        if eventID == BATTLE_EVENT_TYPE.HEAL_VEHICLE_APPLIED_ACTION:
            SoundGroups.g_instance.playSound2D(HBUISound.HEAL_POINT_NPC)
            avatar_getter.getSoundNotifications().play(HBGameplayVoiceovers.HEAL_POINT_NPC)

    def __onDeath(self, *_):
        avatarComponent = BigWorld.player().HBAvatarComponent
        lives = avatarComponent.getAliveVehicleCount()
        self.__playVoiceForDestroyedPlayerVehicle(lives)

    def __playVoiceForDestroyedPlayerVehicle(self, lives):
        if lives != 0:
            avatar_getter.getSoundNotifications().play(HBGameplayVoiceovers.PLAYER_VEHICLE_DESTROYED)
        else:
            avatar_getter.getSoundNotifications().play(HBGameplayVoiceovers.PLAYER_VEHICLE_DESTROYED_LAST_TIME)

    def __onGoalsUpdated(self, goalsInfo):
        if not goalsInfo:
            return
        lastGoal = goalsInfo[-1]
        goalID = lastGoal['id']
        goalFinished = lastGoal['state'] != GoalState.ACTIVE
        isLastTask = goalID == 'ATT_goal_final' or goalID == GoalBossId.FEW.value or goalID == GoalBossId.ONE.value or goalID == 'def_counter_attack'
        self.__isEndOfBattle = goalFinished and isLastTask
        self.__isWin = lastGoal['state'] == GoalState.WIN and isLastTask
        if self.__lastGoalFinishedID != goalID and goalFinished:
            self.__lastGoalFinishedID = goalID
            SoundGroups.g_instance.playSound2D(HBNotificationEvents.TASK_DONE)
        if self.__isEndOfBattle:
            return
        if goalID != self.__goalID:
            SoundGroups.g_instance.playSound2D(HBNotificationEvents.GENERAL)
            phasesComponent = getArenaPhasesComponent()
            currentPhase = phasesComponent.currentPhase
            if goalID == 'ATT_goal_counter_attack':
                avatar_getter.getSoundNotifications().play(HBGameplayVoiceovers.REPEL_COUNTER_ATTACK)
            elif goalID == 'ATT_goal_main' and currentPhase != 1:
                avatar_getter.getSoundNotifications().play(HBGameplayVoiceovers.PLAYER_ATTACK)
            if isLastTask and self.__bonusType == ARENA_BONUS_TYPE.HB_OFFENCE:
                avatar_getter.getSoundNotifications().play(HBGameplayVoiceovers.BOSS_TASK)
            elif isLastTask and self.__bonusType == ARENA_BONUS_TYPE.HB_DEFENCE:
                avatar_getter.getSoundNotifications().play(HBGameplayVoiceovers.DEFENCE_COUNTER_ATTACK)
            if self._sessionProvider.isReplayPlaying:
                self.__finishTime = lastGoal['time'] + BigWorld.serverTime() - _FINISH_TIME_CORRECTION
            else:
                self.__finishTime = lastGoal['finishTime']
            self.__updateTimer()
            self.__goalID = goalID

    def __updateTimer(self):
        timeLeft = max(math.ceil(self.__finishTime - BigWorld.serverTime()), 0)
        if self.__isEndOfBattle:
            self.__handleTimoutSound(timeLeft)
            return
        else:
            arenaPhasesComponent = getArenaPhasesComponent()
            if arenaPhasesComponent:
                soundEvent = None
                isTimeEmergence = False
                currentPhase = arenaPhasesComponent.currentPhase
                phasesCount = arenaPhasesComponent.phasesCount
                isOffence = self.__bonusType == ARENA_BONUS_TYPE.HB_OFFENCE
                isDefence = self.__bonusType == ARENA_BONUS_TYPE.HB_DEFENCE
                if isclose(_ONE_MINUTE_LEFT, timeLeft):
                    if isOffence and currentPhase != phasesCount:
                        soundEvent = HBGameplayVoiceovers.ONE_MINUTE_LEFT
                        isTimeEmergence = True
                    elif isDefence:
                        if currentPhase == phasesCount:
                            soundEvent = HBGameplayVoiceovers.ONE_MINUTE_LEFT
                        else:
                            SoundGroups.g_instance.setState(HBBattleStates.GROUP, HBBattleStates.INTENSIVE)
                elif isclose(_TWO_MINUTES_LEFT, timeLeft):
                    isTimeEmergence = True
                    if isOffence and currentPhase == phasesCount:
                        soundEvent = HBGameplayVoiceovers.TWO_MINUTES_LEFT
                if isTimeEmergence:
                    SoundGroups.g_instance.playSound2D(HBNotificationEvents.TIME_EMERGENCE)
                if soundEvent:
                    self.__playTimeLeftVoiceover(soundEvent)
            self.__handleTimoutSound(timeLeft)
            if timeLeft > 0:
                if timeLeft <= _TIME_IS_RUNNING_OUT and not self.__hurryUpTimerSoundIsPlaying:
                    self.__hurryUpTimerSoundIsPlaying = True
                    SoundGroups.g_instance.playSound2D(HBTimerEvents.START)
                    SoundGroups.g_instance.playSound2D(HBNotificationEvents.GENERAL)
                if timeLeft > _TIME_IS_RUNNING_OUT and self.__hurryUpTimerSoundIsPlaying:
                    self.__hurryUpTimerSoundIsPlaying = False
                    SoundGroups.g_instance.playSound2D(HBTimerEvents.STOP)
                self.delayCallback(_UPDATE_TIMER_INTERVAL, self.__updateTimer)
            return

    def __handleTimoutSound(self, timeLeft):
        if isclose(0, timeLeft) and self.__hurryUpTimerSoundIsPlaying:
            self.__hurryUpTimerSoundIsPlaying = False
            SoundGroups.g_instance.playSound2D(HBTimerEvents.STOP)

    def __onPhaseChanged(self, arenaPhases):
        if not arenaPhases or not arenaPhases.canShow():
            return
        currentPhase = arenaPhases.currentPhase
        currentWave = arenaPhases.currentWave
        if not currentWave > 0:
            return
        soundStateMap = self._DEFENCE_SOUND_STATE
        if self.__bonusType == ARENA_BONUS_TYPE.HB_OFFENCE:
            soundStateMap = self._OFFENCE_SOUND_STATE
        soundState = soundStateMap[currentPhase]
        if self.__bonusType == ARENA_BONUS_TYPE.HB_DEFENCE and currentPhase == 1:
            voiceOver = HBGameplayVoiceovers.DEFENCE_WAVES
            if currentWave == 1:
                soundState = HBBattleStates.SILENCE
                voiceOver = HBGameplayVoiceovers.DEFENCE_FIRST_WAVE
            elif currentWave == 6:
                soundState = HBBattleStates.INTENSIVE
                voiceOver = HBGameplayVoiceovers.DEFENCE_LAST_WAVE
            avatar_getter.getSoundNotifications().play(voiceOver)
        SoundGroups.g_instance.setState(HBBattleStates.GROUP, soundState)

    def __onRoundFinished(self, winnerTeam, reason, extraData):
        voiceOversMap = {ARENA_BONUS_TYPE.HB_OFFENCE: {1: HBGameplayVoiceovers.OFFENCE_WIN,
                                       2: HBGameplayVoiceovers.OFFENCE_DEFEAT},
         ARENA_BONUS_TYPE.HB_DEFENCE: {1: HBGameplayVoiceovers.DEFENCE_WIN,
                                       2: HBGameplayVoiceovers.DEFENCE_DEFEAT,
                                       0: HBGameplayVoiceovers.DEFENCE_DRAW}}
        if self.__isWin:
            battleState = HBBattleStates.VICTORY
        else:
            battleState = HBBattleStates.DEFEAT
        SoundGroups.g_instance.setState(HBBattleStates.GROUP, battleState)
        avatar_getter.getSoundNotifications().play(voiceOversMap[self.__bonusType][winnerTeam])

    def __onAlliesUpdated(self):
        if self.__isAloneInBattle:
            return
        playerVehicleID = avatar_getter.getPlayerVehicleID()
        playerVeh = BigWorld.entity(playerVehicleID)
        if not playerVeh:
            return
        if not playerVeh.isAlive():
            return
        isAliveTeammatesPresent = self.__isAliveTeammatesPresent()
        if not isAliveTeammatesPresent:
            self.__isAloneInBattle = True
            avatar_getter.getSoundNotifications().play(HBGameplayVoiceovers.PLAYER_ALONE_IN_BATTLE)

    def __isAliveTeammatesPresent(self):
        playerVehicleID = avatar_getter.getPlayerVehicleID()
        arenaDP = self._sessionProvider.getArenaDP()
        allyTeams = arenaDP.getAllyTeams()
        arena = BigWorld.player().arena
        teamInfo = arena.teamInfo.dynamicComponents.get('hbTeamInfoComponent')
        for vehInfo in arenaDP.getVehiclesInfoIterator():
            if vehInfo.team not in allyTeams:
                continue
            if vehInfo.vehicleID == playerVehicleID:
                continue
            vehicle = BigWorld.entity(vehInfo.vehicleID)
            if not vehicle:
                continue
            if vehicle.isAlive():
                return True
            livesCount = teamInfo.getAliveVehicleCount(vehInfo.vehicleID)
            if livesCount > 0:
                return True

        return False

    def __playTimeLeftVoiceover(self, soundEvent):
        avatar_getter.getSoundNotifications().play(soundEvent)
