# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/legacy/TimersBar.py
import SoundGroups
from debug_utils import LOG_DEBUG
from helpers.i18n import makeString as _ms
from gui.battle_control import g_sessionProvider
from gui.battle_control.battle_constants import COUNTDOWN_STATE
from gui.battle_control.controllers.period_ctrl import ITimersBar

class _SOUNDS:
    BATTLE_ENDING_SOON = 'time_buzzer_02'
    COUNTDOWN_TICKING = 'time_countdown'
    BATTLE_END = 'time_over'
    STOP_TICKING = 'time_countdown_stop'


_BATTLE_END_SOUND_TIME = 2
_FALLOUT_ENDING_SOON_TIME = 120
_STATE_TO_MESSAGE = {COUNTDOWN_STATE.WAIT: _ms('#ingame_gui:timer/waiting'),
 COUNTDOWN_STATE.START: _ms('#ingame_gui:timer/starting'),
 COUNTDOWN_STATE.STOP: _ms('#ingame_gui:timer/started')}

class TimersBar(ITimersBar):

    def __init__(self, ui=None, isEvent=False):
        super(TimersBar, self).__init__()
        self.__ui = ui
        self.__isTicking = False
        self.__state = COUNTDOWN_STATE.STOP
        visitor = g_sessionProvider.arenaVisitor
        self.__roundLength = visitor.type.getRoundLength()
        if visitor.gui.isFalloutBattle():
            self.__endingSoonTime = _FALLOUT_ENDING_SOON_TIME
        else:
            self.__endingSoonTime = visitor.type.getBattleEndingSoonTime()
        self.__endWarningIsEnabled = self.__checkEndWarningStatus(visitor)
        if isEvent or self.__endWarningIsEnabled:
            timerPath = 'eventBattleTimer.swf'
            SoundGroups.g_instance.playSound2D(_SOUNDS.STOP_TICKING)
        else:
            timerPath = 'BattleTimer.swf'
        self.__ui.movie.loadTimer(timerPath)

    def __del__(self):
        LOG_DEBUG('TimersBar is deleted')

    def destroy(self):
        self.__ui = None
        return

    def setTotalTime(self, totalTime):
        minutes, seconds = divmod(int(totalTime), 60)
        if self.__endWarningIsEnabled and self.__state == COUNTDOWN_STATE.STOP:
            if _BATTLE_END_SOUND_TIME < totalTime <= self.__endingSoonTime:
                if not self.__isTicking:
                    self.__startTicking()
                if totalTime == self.__endingSoonTime:
                    _g_sound.playSound2D(_SOUNDS.BATTLE_ENDING_SOON)
            elif self.__isTicking:
                self.__stopTicking()
                if totalTime == _BATTLE_END_SOUND_TIME:
                    _g_sound.playSound2D(_SOUNDS.BATTLE_END)
        self.__call('timerBar.setTotalTime', [int(self.__isTicking), '{:02d}'.format(minutes), '{:02d}'.format(seconds)])

    def hideTotalTime(self):
        self.__call('showBattleTimer', [False])

    def setCountdown(self, state, timeLeft):
        self.__state = state
        self.__call('timerBig.setTimer', [_STATE_TO_MESSAGE[state], timeLeft])

    def hideCountdown(self, state, speed):
        self.__state = state
        self.__call('timerBig.setTimer', [_STATE_TO_MESSAGE[state]])
        self.__call('timerBig.hide', [speed])

    def setWinConditionText(self, text):
        pass

    def setState(self, state):
        pass

    def __startTicking(self):
        _g_sound.playSound2D(_SOUNDS.COUNTDOWN_TICKING)
        self.__isTicking = True

    def __stopTicking(self):
        _g_sound.playSound2D(_SOUNDS.STOP_TICKING)
        self.__isTicking = False

    def __call(self, funcName, args=None):
        if self.__ui:
            self.__ui.call('battle.{0}'.format(funcName), args)

    def __validateEndingSoonTime(self):
        return 0 < self.__endingSoonTime < self.__roundLength

    def __checkEndWarningStatus(self, visitor):
        endingSoonTimeIsValid = self.__validateEndingSoonTime()
        return visitor.isBattleEndWarningEnabled() and endingSoonTimeIsValid
