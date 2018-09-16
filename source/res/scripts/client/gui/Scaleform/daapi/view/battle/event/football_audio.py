# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/football_audio.py
import Ball
import BigWorld
import Goal
import WWISE
import ArenaType
import SoundGroups
import Vehicle
from constants import ARENA_PERIOD
from gui.battle_control import avatar_getter
from gui.battle_control.controllers.football_ctrl import IFootballEntitiesView
from gui.battle_control.controllers.football_ctrl import IFootballView, IFootballPeriodListener
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
_DELTA_TIME = 0.25
_TRIGGER_CLOSE_TO_GOAL_TIME = 5
_CRITICAL_DISTANCE_TO_OWN_GOAL = 70
_CRITICAL_DISTANCE_TO_ENEMY_GOAL = 70
_TIME_2_MINUTES_PASSED = 4
_TIME_3_MINUTES_PASSED = 3
_TIME_4_MINUTES_PASSED = 2
BALL_SIDE_TIMER_OFFSET = 5.0
_BALL_SIDE_SOUNDS = ('vo_fb_our_part_of_field', 'vo_fb_enemy_part_of_field')
_RTPC_FOOTBALL_BALL_SIDE = 'RTPC_ext_ev_football_side_ball'
_RTPC_FOOTBALL_PLAYER_SIDE = 'RTPC_ext_ev_football_side_player'

class GoalProximitySoundPlayer(IFootballView, IFootballEntitiesView):

    def __init__(self):
        super(GoalProximitySoundPlayer, self).__init__()
        self.__team = avatar_getter.getPlayerTeam()
        self.__ownGoalPosition = None
        self.__enemyGoalPosition = None
        self.__tickCallbackID = None
        self.__distanceToOwnGoal = 100
        self.__distanceToEnemyGoal = 100
        self.__timeSpentCloseToGoal = 0
        self.__timeSpentCloseToOwnGoal = 0
        self.__ballEntityID = None
        self.__ownGoalEntityID = None
        self.__enemyGoalEntityID = None
        self.__isInitialized = False
        self.__isCloseToOwnGoalTriggered = False
        self.__isCloseToGoalTriggered = False
        return

    def clear(self):
        self.__stopTicking()
        self.__ownGoalPosition = None
        self.__enemyGoalPosition = None
        super(GoalProximitySoundPlayer, self).clear()
        return

    def onEntityRegistered(self, entityID):
        entity = BigWorld.entities.get(entityID)
        if isinstance(entity, Ball.Ball):
            self.__ballEntityID = entityID
        elif isinstance(entity, Goal.Goal):
            if entity.team == self.__team:
                self.__ownGoalEntityID = entityID
                self.__ownGoalPosition = entity.position
            else:
                self.__enemyGoalEntityID = entityID
                self.__enemyGoalPosition = entity.position
        oldInitVal = self.__isInitialized
        self.__isInitialized = self.__ballEntityID is not None and self.__ownGoalEntityID is not None and self.__enemyGoalEntityID is not None
        if oldInitVal != self.__isInitialized:
            self.__startTicking()
        return

    def onEntityUnregistered(self, entityID):
        super(GoalProximitySoundPlayer, self).onEntityUnregistered(entityID)
        if entityID == self.__ballEntityID:
            self.__ballEntityID = None
            self.__isInitialized = False
        elif entityID == self.__enemyGoalEntityID:
            self.__enemyGoalEntityID = None
            self.__isInitialized = False
        elif entityID == self.__ownGoalEntityID:
            self.__ownGoalEntityID = None
            self.__isInitialized = False
        if not self.__isInitialized:
            self.__stopTicking()
        return

    def updateScore(self, teamScore, scoreInfo):
        self.__stopTicking()
        self.__timeSpentCloseToGoal = 0
        self.__timeSpentCloseToOwnGoal = 0
        self.__isCloseToOwnGoalTriggered = False
        self.__isCloseToGoalTriggered = False

    def onReturnToPlay(self, data):
        self.__startTicking()

    def onWinnerDeclared(self, winner, delay):
        self.__stopTicking()

    def __startTicking(self):
        if self.__isInitialized and self.__tickCallbackID is None:
            self.__tickCallbackID = BigWorld.callback(_DELTA_TIME, self.__tick)
        return

    def __stopTicking(self):
        if self.__tickCallbackID:
            BigWorld.cancelCallback(self.__tickCallbackID)
            self.__tickCallbackID = None
        return

    def __tick(self):
        self.__updateSoundParams()
        self.__tickCallbackID = BigWorld.callback(_DELTA_TIME, self.__tick)

    def __updateSoundParams(self):
        ball = BigWorld.entities.get(self.__ballEntityID)
        if ball:
            self.__distanceToOwnGoal = (ball.position - self.__ownGoalPosition).length
            self.__distanceToEnemyGoal = (ball.position - self.__enemyGoalPosition).length
            WWISE.WW_setRTCPGlobal('RTPC_ext_ev_football_distance_from_the_ball_gate_PC', self.__distanceToOwnGoal)
            WWISE.WW_setRTCPGlobal('RTPC_ext_ev_football_distance_from_the_ball_gate_NPC', self.__distanceToEnemyGoal)
            if self.__distanceToOwnGoal < _CRITICAL_DISTANCE_TO_OWN_GOAL:
                if not self.__isCloseToOwnGoalTriggered:
                    self.__timeSpentCloseToGoal += _DELTA_TIME
                    if self.__timeSpentCloseToGoal > _TRIGGER_CLOSE_TO_GOAL_TIME:
                        self.__timeSpentCloseToGoal = 0
                        self.__isCloseToOwnGoalTriggered = True
                        SoundGroups.g_instance.playSound2D('vo_fb_close_to_our_gates')
                        return
            else:
                self.__timeSpentCloseToGoal = 0
                self.__isCloseToOwnGoalTriggered = False
            if self.__distanceToEnemyGoal < _CRITICAL_DISTANCE_TO_ENEMY_GOAL:
                if not self.__isCloseToGoalTriggered:
                    self.__timeSpentCloseToOwnGoal += _DELTA_TIME
                    if self.__timeSpentCloseToOwnGoal > _TRIGGER_CLOSE_TO_GOAL_TIME:
                        self.__timeSpentCloseToOwnGoal = 0
                        self.__isCloseToGoalTriggered = True
                        SoundGroups.g_instance.playSound2D('vo_fb_close_to_enemy_gates')
            else:
                self.__timeSpentCloseToOwnGoal = 0
                self.__isCloseToGoalTriggered = False


class _FootaballVOCategory(object):
    SCORE = 0
    TIME = 1
    ALL = (SCORE, TIME)


class _PendingPlayerMixin(object):

    def __init__(self):
        super(_PendingPlayerMixin, self).__init__()
        self.__pendingSounds = [None] * len(_FootaballVOCategory.ALL)
        self.__arenaLoaded = False
        self.__playingSound = None
        return

    def __del__(self):
        self.__pendingSounds = None
        self.__playingSound = None
        return

    def onArenaLoaded(self):
        self.__arenaLoaded = True
        self.__playPendingSound()

    def _playVoiceOver(self, soundId, category):
        if not self.__arenaLoaded:
            self.__pendingSounds[category] = soundId
        else:
            self.__pendingSounds[category] = None
            SoundGroups.g_instance.playSound2D(soundId)
        return

    def __playPendingSound(self):
        for category in _FootaballVOCategory.ALL:
            soundId = self.__pendingSounds[category]
            if soundId is not None:
                self.__playingSound = SoundGroups.g_instance.getSound2D(soundId)
                self.__playingSound.setCallback(self.__onSoundEnd)
                self.__playingSound.play()
                self.__pendingSounds[category] = None
                break

        return

    def __onSoundEnd(self, _):
        self.__playingSound = None
        self.__playPendingSound()
        return


class FootballEventsSound(IAbstractPeriodView, _PendingPlayerMixin, IFootballView, IFootballPeriodListener):

    def __init__(self):
        super(FootballEventsSound, self).__init__()
        self.__team = avatar_getter.getPlayerTeam()
        self.__minutes = 0
        self.__score = (0, 0)
        self.__period = ARENA_PERIOD.IDLE
        self.__gameStarted = False
        self.__endGamePlayed = False
        self.__playWhistle = True
        self.__isOvertime = False
        self.__timeSounds = {_TIME_2_MINUTES_PASSED: ('vo_fb_time_2_minutes_passed', lambda team, score: sum(score) == 0),
         _TIME_3_MINUTES_PASSED: ('vo_fb_time_4_minutes', lambda team, score: True),
         _TIME_4_MINUTES_PASSED: ('vo_fb_time_3_minutes', lambda team, score: score[team - 1] < score[2 - team])}

    def onPrepareFootballOvertime(self):
        self.__playWhistle = True
        SoundGroups.g_instance.playSound2D('ev_football_overtime_countdown')

    def onStartFootballOvertime(self):
        self.__isOvertime = True
        SoundGroups.g_instance.playSound2D('vo_fb_overtime_starts')

    def onWinnerDeclared(self, winner, delay):
        if self.__team == winner:
            SoundGroups.g_instance.playSound2D('vo_fb_win')
        else:
            SoundGroups.g_instance.playSound2D('vo_fb_defeat')

    def setTotalTime(self, totalTime):
        minutes = int(totalTime) / 60
        if self.__minutes != minutes and minutes > 1:
            self.__minutes = minutes
            if minutes in self.__timeSounds:
                soundId, condition = self.__timeSounds.pop(minutes)
                if condition(self.__team, self.__score):
                    self._playVoiceOver(soundId, _FootaballVOCategory.TIME)
        if self.__period == ARENA_PERIOD.BATTLE and int(totalTime) == 0:
            if not self.__isOvertime and self.__score[0] == self.__score[1]:
                self.__isOvertime = True
                SoundGroups.g_instance.playSound2D('ev_football_end_main_time')

    def setPeriod(self, period):
        if period == ARENA_PERIOD.BATTLE:
            if self.__period == ARENA_PERIOD.PREBATTLE:
                if self.__playWhistle:
                    SoundGroups.g_instance.playSound2D('ev_football_whistle')
                if not self.__gameStarted:
                    SoundGroups.g_instance.playSound2D('vo_fb_match_start')
            self.__gameStarted = True
            self.__playWhistle = False
        self.__period = period
        if self.__period == ARENA_PERIOD.AFTERBATTLE and not self.__endGamePlayed:
            self.__endGamePlayed = True
            SoundGroups.g_instance.playSound2D('ev_football_end_game')

    def updateScore(self, teamScore, scoreInfo=None):
        if teamScore:
            self.__score = teamScore
            self.__playScoreSounds(scoreInfo)

    def onReturnToPlay(self, _):
        if sum(self.__score) == 0:
            return
        team = avatar_getter.getPlayerTeam()
        soundID = 'vo_fb_score_{}_{}'.format(self.__score[team - 1], self.__score[2 - team])
        self._playVoiceOver(soundID, _FootaballVOCategory.SCORE)

    def __playScoreSounds(self, scoreInfo):
        WWISE.WW_setRTCPGlobal('RTPC_ext_football_score_ally', self.__score[self.__team - 1])
        WWISE.WW_setRTCPGlobal('RTPC_ext_football_score_enemy', self.__score[2 - self.__team])
        if scoreInfo is not None:
            ownGoal, scoringTeam = scoreInfo
            if self.__team == scoringTeam:
                SoundGroups.g_instance.playSound2D('ev_football_goal_in_enemy_gate')
                SoundGroups.g_instance.playSound2D('vo_fb_goal_scored')
            else:
                SoundGroups.g_instance.playSound2D('ev_football_goal_in_our_gate')
                SoundGroups.g_instance.playSound2D('vo_fb_own_goal' if ownGoal else 'vo_fb_goal_received')
        return


class FieldPositionVOSoundPlayer(IFootballEntitiesView):

    def __init__(self):
        super(FieldPositionVOSoundPlayer, self).__init__()
        self.__team = avatar_getter.getPlayerTeam()
        self.__vehEntityID = None
        self.__footballCenterField = ArenaType.g_cache[BigWorld.player().arenaTypeID].football.getFieldPosition[0]
        self.__vehicleFieldSide = 0
        self.__tickCallbackID = None
        self.__ballEntityID = None
        self.__ballFieldSideTimer = 0
        self.__ballFieldSide = 0
        self.__isInitialized = False
        self.__ballSFXID = None
        return

    def onEntityRegistered(self, entityID):
        entity = BigWorld.entities.get(entityID)
        if isinstance(entity, Ball.Ball):
            self.__ballEntityID = entityID
        if isinstance(entity, Vehicle.Vehicle) and avatar_getter.getPlayerVehicleID() == entityID:
            self.__vehEntityID = entityID
        oldInitVal = self.__isInitialized
        self.__isInitialized = self.__vehEntityID is not None and self.__ballEntityID is not None
        if oldInitVal != self.__isInitialized:
            self.__startTicking()
        return

    def onEntityUnregistered(self, entityID):
        super(FieldPositionVOSoundPlayer, self).onEntityUnregistered(entityID)
        if entityID == self.__vehEntityID:
            self.__vehEntityID = None
            self.__isInitialized = False
        elif entityID == self.__ballEntityID:
            self.__ballEntityID = None
            self.__isInitialized = False
        if not self.__isInitialized:
            self.__stopTicking()
        return

    def clear(self):
        self.__stopTicking()
        self.__team = None
        self.__vehEntityID = None
        self.__footballCenterField = None
        self.__vehicleFieldSide = 0
        self.__tickCallbackID = None
        self.__ballEntityID = None
        self.__ballFieldSideTimer = 0
        self.__ballFieldSide = 0
        self.__isInitialized = False
        self.__ballSFXID = None
        super(FieldPositionVOSoundPlayer, self).clear()
        return

    def __startTicking(self):
        if self.__isInitialized and self.__tickCallbackID is None:
            self.__tickCallbackID = BigWorld.callback(_DELTA_TIME, self.__tick)
        return

    def __stopTicking(self):
        if self.__tickCallbackID:
            BigWorld.cancelCallback(self.__tickCallbackID)
            self.__tickCallbackID = None
        return

    def __tick(self):
        self.__updateBallPosition()
        self.__updateTankPosition()
        self.__tickCallbackID = BigWorld.callback(_DELTA_TIME, self.__tick)

    def __updateBallPosition(self):
        ball = BigWorld.entities.get(self.__ballEntityID)
        if ball:
            ballFieldSide = self.__getFieldSide(ball.position)
            if self.__ballFieldSide != ballFieldSide:
                self.__ballFieldSide = ballFieldSide
                self.__onBallSwitchedSides(self.__ballFieldSide)
                return
            if self.__ballFieldSideTimer is not 0 and self.__ballFieldSideTimer <= BigWorld.time():
                self.__ballFieldSideTimer = 0
                SoundGroups.g_instance.playSound2D(_BALL_SIDE_SOUNDS[self.__ballSFXID])

    def __updateTankPosition(self):
        vehicle = BigWorld.entities.get(self.__vehEntityID)
        if vehicle:
            vehicleFieldSide = self.__getFieldSide(vehicle.position)
            if self.__vehicleFieldSide != vehicleFieldSide:
                self.__vehicleFieldSide = vehicleFieldSide
                WWISE.WW_setRTCPGlobal(_RTPC_FOOTBALL_PLAYER_SIDE, self.__determineRTPCFieldSide(self.__vehicleFieldSide))

    def __determineRTPCFieldSide(self, fieldSide):
        if self.__team == 1:
            if fieldSide == 1:
                return 0
            return 1
        return 1 if fieldSide == 1 else 0

    def __getFieldSide(self, currentPos):
        x = currentPos[0]
        if abs(x - self.__footballCenterField) < 1.0:
            return 0
        return 1 if x < self.__footballCenterField else 2

    def __onBallSwitchedSides(self, fieldSide):
        if fieldSide is not 0:
            self.__ballFieldSideTimer = BigWorld.time() + BALL_SIDE_TIMER_OFFSET
            self.__ballSFXID = self.__determineRTPCFieldSide(fieldSide)
            WWISE.WW_setRTCPGlobal(_RTPC_FOOTBALL_BALL_SIDE, self.__ballSFXID)
        else:
            self.__ballFieldSideTimer = 0
