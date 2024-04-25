# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/timer.py
import math
from enum import IntEnum
import BigWorld
from gui import makeHtmlString
from gui.Scaleform.daapi.view.meta.HBTimerMeta import HBTimerMeta
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters.time_formatters import getBattleTimerString
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from PlayerEvents import g_playerEvents
from helpers.CallbackDelayer import CallbackDelayer
from HBGoalComponent import HBGoalComponent
from historical_battles_common.hb_constants import GoalState, GoalBossId

class TimerStates(IntEnum):
    NONE = 0
    NORMAL = 1
    BIG = 2
    LAST_SECONDS = 3
    FINISHED = 4


class TimerSize(IntEnum):
    SMALL = 0
    BIG = 1


_HUNDRED_PERCENT = 100.0
_UPDATE_INTERVAL = 1
_INVALID_TIME = 0
_ALWAYS_BIG_MESSAGE_TIME = 60
_LAST_SECONDS_TIME = 10
_GOAL_HIGHLIGHT_DURATION = 4
_TWO_MINUTES_TIME = 120
_FINISH_TIME_CORRECTION = 1

class SimpleGoalFormatter(object):

    @classmethod
    def formatTitle(cls, goalsInfo):
        state = goalsInfo['state']
        subState = goalsInfo['subState']
        if state != GoalState.ACTIVE:
            return cls._formatFinishReason(goalsInfo)
        goalID = goalsInfo['id']
        message = R.strings.hb_battle.goals.title.dyn(goalID)
        if message and subState:
            message = message.dyn(subState)
        return '' if not message else makeHtmlString('html_templates:hbEventGoals', 'title', {'message': backport.text(message())})

    @classmethod
    def formatDescription(cls, goalsInfo):
        goalID = goalsInfo['id']
        if not goalID:
            return ''
        state = goalsInfo['state']
        return cls._formatDescription(goalsInfo) if state == GoalState.ACTIVE else ''

    @classmethod
    def formatProgress(cls, goalsInfo):
        goalID = goalsInfo['id']
        if not goalID:
            return ''
        state = goalsInfo['state']
        return cls._formatProgress(goalsInfo) if state == GoalState.ACTIVE else ''

    @classmethod
    def _formatFinishReason(cls, goalsInfo):
        state = goalsInfo['state']
        goalID = goalsInfo['id']
        subState = goalsInfo['subState']
        if state == GoalState.WIN:
            message = R.strings.hb_battle.goals.win.dyn(goalID)
            if message and subState:
                message = message.dyn(subState)
            key = 'win'
        else:
            message = R.strings.hb_battle.goals.lose.dyn(goalID)
            if message and subState:
                message = message.dyn(subState)
            key = 'lose'
        return '' if not message else makeHtmlString('html_templates:hbEventGoals', key, {'message': backport.text(message())})

    @classmethod
    def _formatDescription(cls, goalsInfo):
        goalID = goalsInfo['id']
        subState = goalsInfo['subState']
        description = R.strings.hb_battle.goals.description.dyn(goalID)
        if not description:
            return ''
        if description and subState:
            description = description.dyn(subState)
        kwargs = {'current': goalsInfo['progress'],
         'needed': goalsInfo['progressTotal'],
         'left': goalsInfo['progressTotal'] - goalsInfo['progress']}
        message = backport.text(description(), **kwargs)
        return makeHtmlString('html_templates:hbEventGoals', 'description', {'message': message})

    @classmethod
    def _formatProgress(cls, goalsInfo):
        goalID = goalsInfo['id']
        subState = goalsInfo['subState']
        progress = R.strings.hb_battle.goals.progress.dyn(goalID)
        if not progress:
            return ''
        if progress and subState:
            subProgress = progress.dyn(subState)
            if subProgress:
                progress = subProgress
        kwargs = {'current': goalsInfo['progress'],
         'needed': goalsInfo['progressTotal'],
         'left': goalsInfo['progressTotal'] - goalsInfo['progress']}
        message = backport.text(progress(), **kwargs)
        return makeHtmlString('html_templates:hbEventGoals', 'progress', {'message': message})


class HistoricalBattlesTimer(HBTimerMeta, CallbackDelayer):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _COLOR = '#ffffff'
    _ONE_MINUTE_SECONDS = 60

    def __init__(self):
        HBTimerMeta.__init__(self)
        CallbackDelayer.__init__(self)
        self.__goalID = None
        self.__subState = None
        self._visible = False
        self._currentHint = None
        self.__timerState = TimerStates.NONE
        self.__prevTimeLeft = 0
        self.__finishTime = _INVALID_TIME
        return

    def _populate(self):
        super(HistoricalBattlesTimer, self)._populate()
        self.as_updateProgressBarS(0, False)
        self.as_setTimerStateS(int(TimerSize.BIG))
        arena = BigWorld.player().arena
        geometryName = arena.arenaType.geometryName
        if geometryName:
            goalsInfo = arena.arenaInfo.goalComponent.goalsInfo
            self.__onGoalsUpdated(goalsInfo)
        g_playerEvents.onRoundFinished += self.__onRoundFinished
        HBGoalComponent.onGoalsUpdated += self.__onGoalsUpdated

    def _dispose(self):
        self._visible = False
        CallbackDelayer.destroy(self)
        g_playerEvents.onRoundFinished -= self.__onRoundFinished
        HBGoalComponent.onGoalsUpdated -= self.__onGoalsUpdated
        super(HistoricalBattlesTimer, self)._dispose()

    def __update(self):
        timeLeft = math.ceil(self.__finishTime - BigWorld.serverTime())
        timerState = self.__timerState
        if timeLeft <= 0:
            self.__resetTimer()
            return
        if timerState == TimerStates.NORMAL:
            self.as_updateTimeS(getBattleTimerString(timeLeft))
            if timeLeft <= _TWO_MINUTES_TIME < self.__prevTimeLeft:
                self.__highlightMessage(True)
                self.as_playFxS(True, False)
            if timeLeft <= _ALWAYS_BIG_MESSAGE_TIME:
                self.__highlightMessage(False, True)
                self.as_playFxS(True, False)
                timerState = TimerStates.BIG
        if timerState == TimerStates.BIG:
            self.as_updateTimeS(getBattleTimerString(timeLeft))
            if timeLeft <= _LAST_SECONDS_TIME:
                self.as_playFxS(True, True)
                timerState = TimerStates.LAST_SECONDS
        if timerState == TimerStates.LAST_SECONDS:
            self.as_updateTimeS(getBattleTimerString(timeLeft))
        self.__prevTimeLeft = timeLeft
        self.__timerState = timerState
        self.delayCallback(_UPDATE_INTERVAL, self.__update)

    def __onGoalsUpdated(self, goalsInfo):
        if not goalsInfo:
            return
        lastGoal = goalsInfo[-1]
        goalID = lastGoal['id']
        subState = lastGoal['subState']
        if goalID != self.__goalID:
            self.__changeGoal(lastGoal)
            if self.sessionProvider.isReplayPlaying:
                self.__finishTime = lastGoal['time'] + BigWorld.serverTime() - _FINISH_TIME_CORRECTION
            else:
                self.__finishTime = lastGoal['finishTime']
            self.__update()
        elif subState != self.__subState:
            self.__highlightMessage(True)
            self.__subState = subState
        goalFinished = lastGoal['state'] != GoalState.ACTIVE
        currentProgress = lastGoal['progress']
        totalProgress = lastGoal['progressTotal']
        showProgress = totalProgress != 0 and not goalFinished and goalID != GoalBossId.ONE.value and goalID != GoalBossId.FEW.value
        progress = float(currentProgress) / totalProgress * _HUNDRED_PERCENT if showProgress else 0
        self.as_updateProgressBarS(progress, showProgress)
        formatter = SimpleGoalFormatter
        self.as_updateTitleS(formatter.formatTitle(lastGoal))
        self.as_updateObjectiveBigS(formatter.formatDescription(lastGoal))
        self.as_updateObjectiveS(formatter.formatProgress(lastGoal))
        if goalFinished and self.__timerState != TimerStates.FINISHED:
            self.as_updateTimeS('')
            self.__highlightMessage(True)
            self.__timerState = TimerStates.FINISHED
            self.as_playFxS(False, False)
            self.stopCallback(self.__update)
            return

    def __resetTimer(self):
        self.as_setTimerStateS(int(TimerSize.SMALL))
        self.as_updateTimeS('')
        self.as_playFxS(False, False)
        self.as_updateProgressBarS(0, False)
        self.stopCallback(self.__update)

    def __highlightMessage(self, withTitle=False, permanent=False):
        self.stopCallback(self.__hideBigTimer)
        self.as_setTimerStateS(int(TimerSize.BIG))
        if withTitle:
            self.as_setHintStateS(True)
        if not permanent:
            self.delayCallback(_GOAL_HIGHLIGHT_DURATION, self.__hideBigTimer)

    def __hideBigTimer(self):
        self.as_setTimerStateS(int(TimerSize.SMALL))
        self.as_setHintStateS(False)

    def __onRoundFinished(self, winnerTeam, reason, extraData):
        self.as_updateTitleS('')
        self.as_updateObjectiveBigS('')
        self.as_updateObjectiveS('')
        self.__resetTimer()

    def __changeGoal(self, lastGoalInfo):
        self.__resetTimer()
        self.__timerState = TimerStates.NORMAL
        self.__goalID = lastGoalInfo['id']
        self.__subState = lastGoalInfo['subState']
        self.__highlightMessage(True)
