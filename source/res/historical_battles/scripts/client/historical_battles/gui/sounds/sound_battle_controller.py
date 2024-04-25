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
from VehicleLivesComponent import VehicleLivesComponent
from HBBattleFeedbackComponent import HBBattleFeedbackComponent
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control import avatar_getter
from historical_battles.gui.sounds.sound_constants import HBBattleStates, HBGameplayVoiceovers, HBNotificationEvents, HBTimerEvents, HBUISound
from historical_battles.gui.sounds.sound_helpers import getArenaPhasesComponent, getPlayerVehicleLivesComponent
from historical_battles_common.hb_constants import GoalState, GoalBossId
from historical_battles_common.hb_constants_extension import BATTLE_EVENT_TYPE
if typing.TYPE_CHECKING:
    from Vehicle import Vehicle
    from typing import Optional
_FINISH_TIME_CORRECTION = 1
_UPDATE_TIMER_INTERVAL = 1
_TIME_IS_RUNNING_OUT = 10
_ONE_MINUTE_LEFT = 60
_TWO_MINUTES_LEFT = 120

class SoundBattleController(CallbackDelayer):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(SoundBattleController, self).__init__()
        self.__goalID = None
        self.__lastGoalFinishedID = None
        self.__hurryUpTimerSoundIsPlaying = False
        self.__isWin = False
        self.__isEndOfBattle = False
        return

    def start(self):
        HBGoalComponent.onGoalsUpdated += self.__onGoalsUpdated
        ArenaPhasesComponent.onPhasesUpdate += self.__onPhaseChanged
        VehicleLivesComponent.onIncreasedLives += self.__onIncreasedLives
        VehicleLivesComponent.onLivesExhausted += self.__onLivesExhausted
        VehicleLivesComponent.onVehicleDestroyed += self.__onVehicleDestroyed
        HBBattleFeedbackComponent.onVehicleHeal += self.__onVehicleHeal
        g_playerEvents.onRoundFinished += self.__onRoundFinished

    def finalize(self):
        HBGoalComponent.onGoalsUpdated -= self.__onGoalsUpdated
        ArenaPhasesComponent.onPhasesUpdate -= self.__onPhaseChanged
        VehicleLivesComponent.onIncreasedLives -= self.__onIncreasedLives
        VehicleLivesComponent.onLivesExhausted -= self.__onLivesExhausted
        VehicleLivesComponent.onVehicleDestroyed -= self.__onVehicleDestroyed
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

    def __onVehicleDestroyed(self, vehicle, lives):
        if avatar_getter.getPlayerVehicleID() == vehicle.id:
            self.__playVoiceForDestroyedPlayerVehicle(lives)

    def __playVoiceForDestroyedPlayerVehicle(self, lives):
        if lives < 0:
            return
        if lives != 0:
            avatar_getter.getSoundNotifications().play(HBGameplayVoiceovers.PLAYER_VEHICLE_DESTROYED)
        else:
            arenaPhasesComponent = getArenaPhasesComponent()
            if not arenaPhasesComponent:
                return
            if arenaPhasesComponent.currentPhase == arenaPhasesComponent.phasesCount:
                avatar_getter.getSoundNotifications().play(HBGameplayVoiceovers.PLAYER_VEHICLE_DESTROYED_LAST_TIME)
            else:
                self.__playVoiceForDestroyedPlayerVehicleOnRegularPhase()

    def __playVoiceForDestroyedPlayerVehicleOnRegularPhase(self):
        aliveAllies = self.__isAliveTeammatesPresent()
        if aliveAllies:
            avatar_getter.getSoundNotifications().play(HBGameplayVoiceovers.ADDITIONAL_LIFE_EXPECTATION)
        else:
            avatar_getter.getSoundNotifications().play(HBGameplayVoiceovers.PLAYER_VEHICLE_DESTROYED_LAST_TIME)

    def __onGoalsUpdated(self, goalsInfo):
        if not goalsInfo:
            return
        lastGoal = goalsInfo[-1]
        goalID = lastGoal['id']
        goalFinished = lastGoal['state'] != GoalState.ACTIVE
        isLastTask = goalID == 'ATT_goal_final' or goalID == GoalBossId.FEW.value or goalID == GoalBossId.ONE.value
        self.__isEndOfBattle = goalFinished and isLastTask
        self.__isWin = lastGoal['state'] == GoalState.WIN and isLastTask
        if self.__isEndOfBattle:
            return
        if self.__lastGoalFinishedID != goalID and goalFinished:
            self.__lastGoalFinishedID = goalID
            SoundGroups.g_instance.playSound2D(HBNotificationEvents.TASK_DONE)
        if goalID != self.__goalID:
            SoundGroups.g_instance.playSound2D(HBNotificationEvents.GENERAL)
            if goalID == 'ATT_goal_counter_attack':
                avatar_getter.getSoundNotifications().play(HBGameplayVoiceovers.REPEL_COUNTER_ATTACK)
            if isLastTask:
                avatar_getter.getSoundNotifications().play(HBGameplayVoiceovers.BOSS_TASK)
            if self._sessionProvider.isReplayPlaying:
                self.__finishTime = lastGoal['time'] + BigWorld.serverTime() - _FINISH_TIME_CORRECTION
            else:
                self.__finishTime = lastGoal['finishTime']
            self.__updateTimer()
            self.__goalID = goalID

    def __updateTimer(self):
        if self.__isEndOfBattle:
            return
        else:
            timeLeft = math.ceil(self.__finishTime - BigWorld.serverTime())
            arenaPhasesComponent = getArenaPhasesComponent()
            if arenaPhasesComponent:
                soundEvent = None
                currentPhase = arenaPhasesComponent.currentPhase
                phasesCount = arenaPhasesComponent.phasesCount
                if isclose(_ONE_MINUTE_LEFT, timeLeft) and currentPhase != phasesCount:
                    soundEvent = HBGameplayVoiceovers.ONE_MINUTE_LEFT
                elif isclose(_TWO_MINUTES_LEFT, timeLeft) and currentPhase == phasesCount:
                    soundEvent = HBGameplayVoiceovers.TWO_MINUTES_LEFT
                if soundEvent:
                    SoundGroups.g_instance.playSound2D(HBNotificationEvents.TIME_EMERGENCE)
                    self.__playTimeLeftVoiceover(soundEvent)
            if isclose(0, timeLeft) and self.__hurryUpTimerSoundIsPlaying:
                self.__hurryUpTimerSoundIsPlaying = False
                SoundGroups.g_instance.playSound2D(HBTimerEvents.STOP)
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

    def __onPhaseChanged(self, arenaPhases):
        if not arenaPhases:
            return
        currentArenaPhase = arenaPhases.currentPhase
        if currentArenaPhase == 1:
            WWISE.WW_setState(HBBattleStates.GROUP, HBBattleStates.SILENCE)
        elif currentArenaPhase == 2:
            WWISE.WW_setState(HBBattleStates.GROUP, HBBattleStates.RELAXED)
        elif currentArenaPhase == 3:
            WWISE.WW_setState(HBBattleStates.GROUP, HBBattleStates.SILENCE)
            avatar_getter.getSoundNotifications().play(HBGameplayVoiceovers.PLAYER_ATTACK)
        elif currentArenaPhase == 4:
            WWISE.WW_setState(HBBattleStates.GROUP, HBBattleStates.INTENSIVE)
        elif currentArenaPhase == 5:
            WWISE.WW_setState(HBBattleStates.GROUP, HBBattleStates.BOSS_FIGHT)

    def __onIncreasedLives(self, vehicle):
        arenaPhasesComponent = getArenaPhasesComponent()
        if not arenaPhasesComponent:
            return
        if vehicle and vehicle.id == avatar_getter.getPlayerVehicleID() and arenaPhasesComponent.currentPhase > 1:
            avatar_getter.getSoundNotifications().play(HBGameplayVoiceovers.LIFE_ADDED)

    def __onRoundFinished(self, winnerTeam, reason, extraData):
        if self.__isWin:
            avatar_getter.getSoundNotifications().play(HBGameplayVoiceovers.WIN)
        else:
            avatar_getter.getSoundNotifications().play(HBGameplayVoiceovers.DEFEAT)

    def __onLivesExhausted(self, vehicle):
        playerVehicleID = avatar_getter.getPlayerVehicleID()
        playerVeh = BigWorld.entity(playerVehicleID)
        if not playerVeh:
            return
        if not playerVeh.isAlive():
            return
        if vehicle.id == playerVehicleID:
            return
        isAliveTeammatesPresent = self.__isAliveTeammatesPresent()
        if not isAliveTeammatesPresent:
            avatar_getter.getSoundNotifications().play(HBGameplayVoiceovers.PLAYER_ALONE_IN_BATTLE)

    def __isAliveTeammatesPresent(self):
        playerVehicleID = avatar_getter.getPlayerVehicleID()
        arenaDP = self._sessionProvider.getArenaDP()
        allyTeams = arenaDP.getAllyTeams()
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
            livesComponent = vehicle.dynamicComponents.get('VehicleLivesComponent', None)
            if livesComponent and livesComponent.lives > 0:
                return True

        return False

    def __isPlayerVehicleAlive(self):
        playerVehicleID = avatar_getter.getPlayerVehicleID()
        vehicle = BigWorld.entity(playerVehicleID)
        if not vehicle:
            return False
        return True if vehicle.isAlive() else False

    def __playerVehicleHasLives(self):
        livesComponent = getPlayerVehicleLivesComponent()
        if not livesComponent:
            return False
        return True if livesComponent.lives > 0 else False

    def __playTimeLeftVoiceover(self, soundEvent):
        if self.__isPlayerVehicleAlive():
            avatar_getter.getSoundNotifications().play(soundEvent)
        elif self.__playerVehicleHasLives():
            avatar_getter.getSoundNotifications().play(soundEvent)
