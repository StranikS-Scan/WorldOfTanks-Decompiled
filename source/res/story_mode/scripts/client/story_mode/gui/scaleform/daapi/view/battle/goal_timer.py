# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/battle/goal_timer.py
from functools import partial
import BigWorld
import SoundGroups
from PlayerEvents import g_playerEvents
from constants import ARENA_PERIOD
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from helpers.time_utils import ONE_MINUTE
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from story_mode.gui.app_loader.observers import getStoryModeBattle
from story_mode.gui.scaleform.daapi.view.meta.StoryModeTimerMeta import StoryModeTimerMeta

class Times(object):
    SHOW_BEFORE_END = 300
    NOTIFY_BEFORE_END = 120
    BIG_STATE_DURATION = 4


class TimerState(object):
    SMALL = 0
    BIG = 1


class FxColor(object):
    WHITE = 'white'
    RED = 'red'


class TimerSound(object):
    BATTLE_ENDING_SOON = 'time_buzzer_02'
    COUNTDOWN_TICKING = 'time_countdown'
    STOP_TICKING = 'time_countdown_stop'


class StoryModeTimer(StoryModeTimerMeta, IAbstractPeriodView):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(StoryModeTimer, self).__init__()
        self.__lastTime = None
        self.__isActive = False
        self.__periodBattle = False
        self.__stateChangeCallback = None
        self.__sounds = dict()
        return

    def setTotalTime(self, timeLeft):
        if not self.__periodBattle or not self._isDAAPIInited() or self.__lastTime == timeLeft:
            return
        if timeLeft <= Times.SHOW_BEFORE_END < self.__lastTime:
            self.__activateTimer(False, FxColor.WHITE)
        elif timeLeft <= Times.NOTIFY_BEFORE_END < self.__lastTime:
            self.__activateTimer(True, FxColor.RED)
        self.__lastTime = timeLeft
        if self.__isActive:
            self.__updateTimer(timeLeft)

    def _populate(self):
        super(StoryModeTimer, self)._populate()
        self.__periodBattle = self.sessionProvider.shared.arenaPeriod.getPeriod() == ARENA_PERIOD.BATTLE
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange

    def _dispose(self):
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        if self.__stateChangeCallback is not None:
            BigWorld.cancelCallback(self.__stateChangeCallback)
            self.__stateChangeCallback = None
        for sound in self.__sounds.values():
            sound.stop()

        self.__sounds.clear()
        super(StoryModeTimer, self)._dispose()
        return

    def __activateTimer(self, notify, color):
        if notify:
            self.__callWWISE(TimerSound.BATTLE_ENDING_SOON)
        self.__isActive = True
        battlePage = getStoryModeBattle()
        if battlePage and battlePage.isGuiVisible():
            self.as_playFxS(True, False, color)
            self.as_setTimerStateS(TimerState.BIG)
        else:
            self.as_setTimerStateS(TimerState.SMALL)
        self.as_setHintStateS(True)
        self.as_setTimerBackgroundS(True)
        self.__stateChangeCallback = BigWorld.callback(Times.BIG_STATE_DURATION, partial(self.__setSmall, notify))

    def __setSmall(self, notify):
        if notify:
            self.__callWWISE(TimerSound.COUNTDOWN_TICKING)
        self.as_setTimerStateS(TimerState.SMALL)
        self.as_setTimerBackgroundS(False)
        self.__stateChangeCallback = None
        return

    def __onArenaPeriodChange(self, period, *args):
        self.__periodBattle = period == ARENA_PERIOD.BATTLE
        if period == ARENA_PERIOD.AFTERBATTLE:
            self.__callWWISE(TimerSound.STOP_TICKING)
            self.__isActive = False
            self.as_updateTimeS('')
            self.as_setTimerBackgroundS(False)

    def __updateTimer(self, timeLeft):
        minutes, seconds = divmod(int(timeLeft), ONE_MINUTE)
        self.as_updateTimeS('{:02d}:{:02d}'.format(minutes, seconds))

    def __callWWISE(self, wwiseEventName):
        sound = SoundGroups.g_instance.getSound2D(wwiseEventName)
        if sound is not None:
            sound.play()
            self.__sounds[wwiseEventName] = sound
        return
