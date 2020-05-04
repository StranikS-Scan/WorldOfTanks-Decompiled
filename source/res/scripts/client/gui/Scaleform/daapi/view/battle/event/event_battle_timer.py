# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/event_battle_timer.py
import math
from enum import IntEnum
import BattleReplay
import SoundGroups
import BigWorld
from constants import ScenarioGoalType, ScenarioGoalFinishedState
from gui.Scaleform.locale.EVENT import EVENT
from helpers import dependency
from PlayerEvents import g_playerEvents
from game_event_getter import GameEventGetterMixin
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.Scaleform.daapi.view.meta.EventTimerMeta import EventTimerMeta
from gui.shared.formatters.time_formatters import getBattleTimerString
from gui.battle_control.avatar_getter import getSoundNotifications
from gui import makeHtmlString
from helpers.i18n import makeString as _ms
from shared_utils import first
from wotdecorators import condition
_BATTLE_TIMER_ID = 'event_battle_timer'
_UPDATE_INTERVAL = 1.0
_INVALID_TIME = 0
_ADDITIONAL_FAKE_TIME = 1
_GOAL_BACKGROUND_DURATION = 3
_ALWAYS_BIG_MESSAGE_TIME = 60
_SPECIAL_TIMER_SHOW_TIME = 120
_LAST_SECONDS_TIME = 10
_TIMER_SIZE_SMALL = 0
_TIMER_SIZE_BIG = 1
_HUNDRED_PERCENT = 100.0

class TimerStates(IntEnum):
    NONE = 0
    SPECIAL = 1
    NORMAL = 2
    BIG = 3
    LAST_SECONDS = 4
    FINISHED = 5


class SimpleGoalFormatter(object):

    @classmethod
    def formatTitle(cls, goalInfo):
        finishReason = goalInfo['finishReason']
        if finishReason != ScenarioGoalFinishedState.NONE:
            return cls._formatFinishReason(goalInfo)
        goalID = goalInfo['uid']
        message = _ms(EVENT.getGoalTitle(goalID))
        return makeHtmlString('html_templates:eventGoals', 'title', {'message': message})

    @classmethod
    def formatDescription(cls, goalInfo):
        goalID = goalInfo['uid']
        if not goalID:
            return ''
        finishReason = goalInfo['finishReason']
        return cls._formatDescription(goalInfo) if finishReason == ScenarioGoalFinishedState.NONE else ''

    @classmethod
    def formatProgress(cls, goalInfo):
        goalID = goalInfo['uid']
        if not goalID:
            return ''
        finishReason = goalInfo['finishReason']
        return cls._formatProgress(goalInfo) if finishReason == ScenarioGoalFinishedState.NONE else ''

    @classmethod
    def _formatFinishReason(cls, goalInfo):
        finishReason = goalInfo['finishReason']
        goalID = goalInfo['uid']
        if finishReason == ScenarioGoalFinishedState.SUCCESS:
            if not EVENT.hasGoalWin(goalID):
                return ''
            message = _ms(EVENT.getGoalWin(goalID))
            return makeHtmlString('html_templates:eventGoals', 'win', {'message': message})
        elif not EVENT.hasGoalLose(goalID):
            return ''
        else:
            message = _ms(EVENT.getGoalLose(goalID))
            return makeHtmlString('html_templates:eventGoals', 'lose', {'message': message})

    @classmethod
    def _formatDescription(cls, goalInfo):
        goalID = goalInfo['uid']
        if not EVENT.hasGoalDescription(goalID):
            return ''
        kwargs = first(goalInfo['winCondition'].values(), {})
        kwargs['left'] = kwargs.get('needed', 0) - kwargs.get('current', 0)
        message = _ms(EVENT.getGoalDescription(goalID), **kwargs)
        return makeHtmlString('html_templates:eventGoals', 'description', {'message': message})

    @classmethod
    def _formatProgress(cls, goalInfo):
        goalID = goalInfo['uid']
        if not EVENT.hasGoalProgress(goalID):
            return ''
        kwargs = first(goalInfo['winCondition'].values(), {})
        kwargs['left'] = kwargs.get('needed', 0) - kwargs.get('current', 0)
        message = _ms(EVENT.getGoalProgress(goalID), **kwargs)
        return makeHtmlString('html_templates:eventGoals', 'progress', {'message': message})


class _TimerSoundNotifications(object):
    _GOAL_FINISH_SUCCESS_NOTIFICATIONS = {'capture_A': 'se20_enemy_retreats',
     'capture_B': 'se20_enemy_retreats',
     'capture_C': 'se20_enemy_retreats'}
    _GOAL_VOICEOVER_PATTERN = 'se20_goal_{}'
    _TIME_1_MIN = 60
    _LEFT_1_MIN_NOTIFICATION = 'se20_gameplay_time_running_out'
    _TIME_2_MIN = 120
    _LEFT_2_MIN_NOTIFICATION = 'se20_gameplay_active_gameplay_required'
    _LAST_SECONDS_COUNTDOWN_SOUND = 'ev_2020_secret_event_hangar_ui_time_countdown'
    ifEnabled = condition('_enabled')

    def __init__(self):
        self._enabled = False
        self.__soundNotifications = None
        self.__lastHandledGoalUpdate = None
        self.__lastSecondsSound = SoundGroups.g_instance.getSound2D(self._LAST_SECONDS_COUNTDOWN_SOUND)
        self.__lastNotifiedTime = None
        return

    def enable(self):
        self._enabled = True
        self.__soundNotifications = getSoundNotifications()

    @ifEnabled
    def notifyGoalUpdate(self, goalId, isGoalFinished, finishReason):
        if self.__lastHandledGoalUpdate == (goalId, isGoalFinished, finishReason):
            return
        else:
            self.__lastHandledGoalUpdate = (goalId, isGoalFinished, finishReason)
            if isGoalFinished and finishReason == ScenarioGoalFinishedState.SUCCESS:
                goalNotification = self._GOAL_FINISH_SUCCESS_NOTIFICATIONS.get(goalId)
                if goalNotification is not None:
                    self.__soundNotifications.play(goalNotification)
            return

    @ifEnabled
    def notifyGoalChange(self, newGoalId, isGoalFinished):
        if not isGoalFinished:
            self.__soundNotifications.play(self._GOAL_VOICEOVER_PATTERN.format(newGoalId))

    @ifEnabled
    def notifyTimeLeft(self, timeLeft):
        if self.__lastNotifiedTime is not None and timeLeft < self.__lastNotifiedTime:
            if timeLeft <= self._TIME_2_MIN < self.__lastNotifiedTime:
                self.__soundNotifications.play(self._LEFT_2_MIN_NOTIFICATION)
                self.__lastNotifiedTime = timeLeft
            elif timeLeft <= self._TIME_1_MIN < self.__lastNotifiedTime:
                self.__soundNotifications.play(self._LEFT_1_MIN_NOTIFICATION)
                self.__lastNotifiedTime = timeLeft
        else:
            self.__lastNotifiedTime = timeLeft
        return

    @ifEnabled
    def notifyLastSecondsStart(self):
        self.__lastSecondsSound.play()

    @ifEnabled
    def notifyLastSecondsStop(self):
        if self.__lastSecondsSound.isPlaying:
            self.__lastSecondsSound.stop()


_GOAL_FORMATTER_BY_TYPE = {ScenarioGoalType.SIMPLE_GOAL: SimpleGoalFormatter}

class EventBattleTimer(EventTimerMeta, GameEventGetterMixin, CallbackDelayer):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        EventTimerMeta.__init__(self)
        GameEventGetterMixin.__init__(self)
        CallbackDelayer.__init__(self)
        self.__isMainTimer = False
        self.__finishTime = _INVALID_TIME
        self.__timerState = TimerStates.NONE
        self.__sounds = _TimerSoundNotifications()
        self.__goalId = None
        self.__goalFinished = False
        return

    def allowAnimation(self):
        self.__isMainTimer = True
        self.__sounds.enable()
        self.as_setTimerStateS(_TIMER_SIZE_SMALL)

    def _populate(self):
        super(EventBattleTimer, self)._populate()
        self.scenarioGoals.onScenarioGoalsChanged += self.__onGoalUpdate
        self.activeTimers.onActiveTimersUpdated += self.__onTimerUpdate
        g_playerEvents.onRoundFinished += self.__onRoundFinished
        self.as_setTimerStateS(_TIMER_SIZE_SMALL if self.__isMainTimer else _TIMER_SIZE_BIG)
        self.as_updateProgressBarS(0, False)
        self.__onGoalUpdate()

    def _dispose(self):
        self.scenarioGoals.onScenarioGoalsChanged -= self.__onGoalUpdate
        self.activeTimers.onActiveTimersUpdated -= self.__onTimerUpdate
        g_playerEvents.onRoundFinished -= self.__onRoundFinished
        CallbackDelayer.destroy(self)
        super(EventBattleTimer, self)._dispose()

    def __onGoalUpdate(self):
        info = self.scenarioGoals.getLastGoal()
        if not info:
            return
        goalId = info['uid']
        finishReason = info['finishReason']
        self.__goalFinished = goalFinished = finishReason != ScenarioGoalFinishedState.NONE
        if goalId != self.__goalId:
            self.__changeGoal(info)
            self.__sounds.notifyGoalChange(goalId, goalFinished)
        current, needed = self.__getGoalProgress(info)
        progressVisible = not goalFinished and needed != 0
        progress = float(current) / needed * _HUNDRED_PERCENT if progressVisible else 0
        self.as_updateProgressBarS(int(progress), progressVisible)
        currentGoal, totalGoals = self.scenarioGoals.getGoalsInfo()
        self.as_updateProgressPhaseS(currentGoal, totalGoals)
        self.__sounds.notifyGoalUpdate(goalId, goalFinished, finishReason)
        formatter = self.__getGoalFormatter(info['goalTypeID'])
        self.as_updateTitleS(formatter.formatTitle(info))
        self.as_updateObjectiveBigS(formatter.formatDescription(info))
        self.as_updateObjectiveS(formatter.formatProgress(info))
        if goalFinished and self.__timerState != TimerStates.FINISHED:
            permanentBackground = currentGoal == totalGoals or finishReason == ScenarioGoalFinishedState.FAILED
            self.__showBackground(permanentBackground)
            self.__timerState = TimerStates.FINISHED
            self.__resetTimer()
            return
        self.__updateTimer(info)

    def __onTimerUpdate(self, diff):
        info = self.scenarioGoals.getLastGoal()
        if info is None:
            return
        else:
            goalId = info['uid']
            notFinished = info['finishReason'] == ScenarioGoalFinishedState.NONE
            if goalId == self.__goalId:
                finishTime = self.__getFinishTime(goalId)
                if finishTime != self.__finishTime and notFinished:
                    deltaTime = getBattleTimerString(finishTime - self.__finishTime)
                    self.__showAddTimeMessage(deltaTime)
            self.__updateTimer(info)
            return

    def __updateTimer(self, goalInfo):
        if BattleReplay.g_replayCtrl.isPlaying:
            return
        goalId = goalInfo['uid']
        self.__finishTime = self.__getFinishTime(goalId)
        if self.__finishTime:
            self.__update()

    def __update(self):
        timeLeft = math.ceil(self.__finishTime - BigWorld.serverTime())
        timerState = self.__timerState
        if timeLeft <= 0:
            self.__resetTimer()
            return
        self.__sounds.notifyTimeLeft(timeLeft)
        if timerState == TimerStates.SPECIAL:
            self.as_updateTimeS('')
            if timeLeft <= _SPECIAL_TIMER_SHOW_TIME:
                self.__showBackground()
                self.as_playFxS(True, False)
                timerState = TimerStates.NORMAL
        if timerState == TimerStates.NORMAL:
            self.as_updateTimeS(getBattleTimerString(timeLeft))
            if timeLeft <= _ALWAYS_BIG_MESSAGE_TIME:
                self.__changeTimerSize(_TIMER_SIZE_BIG)
                timerState = TimerStates.BIG
        if timerState == TimerStates.BIG:
            self.as_updateTimeS(getBattleTimerString(timeLeft))
            if timeLeft <= _LAST_SECONDS_TIME:
                self.__sounds.notifyLastSecondsStart()
                self.as_playFxS(True, True)
                timerState = TimerStates.LAST_SECONDS
        if timerState == TimerStates.LAST_SECONDS:
            self.as_updateTimeS(getBattleTimerString(timeLeft))
        self.__timerState = timerState
        self.delayCallback(_UPDATE_INTERVAL, self.__update)

    def __resetTimer(self):
        self.__changeTimerSize(_TIMER_SIZE_SMALL)
        self.as_updateTimeS('')
        self.as_playFxS(False, False)
        self.__sounds.notifyLastSecondsStop()
        self.as_updateProgressBarS(0, False)
        self.stopCallback(self.__update)

    def __changeGoal(self, goalInfo):
        specialTimer = goalInfo['specialTimer']
        self.__resetTimer()
        self.__timerState = TimerStates.SPECIAL if specialTimer else TimerStates.NORMAL
        self.__sounds.notifyLastSecondsStop()
        goalId = goalInfo['uid']
        self.__goalId = goalId
        if goalId:
            self.__showBackground()

    def __showBackground(self, permanent=False):
        self.stopCallback(self.__hideBackground)
        self.__changeTimerSize(_TIMER_SIZE_BIG)
        self.as_setTimerBackgroundS(True)
        if not permanent:
            self.delayCallback(_GOAL_BACKGROUND_DURATION, self.__hideBackground)

    def __hideBackground(self):
        self.__changeTimerSize(_TIMER_SIZE_SMALL)
        self.as_setTimerBackgroundS(False)

    def __showAddTimeMessage(self, deltaTime):
        if not self.__isMainTimer:
            return
        if BattleReplay.g_replayCtrl.isPlaying:
            return
        self.as_showMessageS(deltaTime)
        self.delayCallback(_GOAL_BACKGROUND_DURATION, self.__hideAddTimeMessage)

    def __hideAddTimeMessage(self):
        self.as_hideMessageS()

    def __changeTimerSize(self, size):
        correctSize = size if self.__isMainTimer else _TIMER_SIZE_BIG
        self.as_setTimerStateS(correctSize)

    def __getGoalFormatter(self, goalType):
        return _GOAL_FORMATTER_BY_TYPE.get(goalType, SimpleGoalFormatter)

    def __getFinishTime(self, goalId):
        if self.__goalFinished:
            return 0
        goalTime = self.activeTimers.getTimerData(goalId)
        return goalTime['finishTime'] - _ADDITIONAL_FAKE_TIME if goalTime else 0

    def __getGoalProgress(self, goalInfo):
        kwargs = first(goalInfo['winCondition'].values(), {})
        return (kwargs.get('current', 0), kwargs.get('needed', 0))

    def __onRoundFinished(self, winnerTeam, reason):
        self.__resetTimer()
        self.as_updateTitleS('')
        self.as_updateObjectiveBigS('')
        self.as_updateObjectiveS('')
