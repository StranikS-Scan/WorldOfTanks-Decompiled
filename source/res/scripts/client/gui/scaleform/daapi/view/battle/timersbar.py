# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/TimersBar.py
import math
from debug_utils import LOG_DEBUG
from gui.battle_control.battle_constants import COUNTDOWN_STATE
from gui.battle_control.battle_period_ctrl import ITimersBar
from helpers import i18n
_STATE_TO_MESSAGE = {COUNTDOWN_STATE.WAIT: i18n.makeString('#ingame_gui:timer/waiting'),
 COUNTDOWN_STATE.START: i18n.makeString('#ingame_gui:timer/starting'),
 COUNTDOWN_STATE.STOP: i18n.makeString('#ingame_gui:timer/started')}

class TimersBar(ITimersBar):

    def __init__(self, ui = None, isEvent = False):
        super(TimersBar, self).__init__()
        self.__ui = ui
        timerPath = 'eventBattleTimer.swf' if isEvent else 'BattleTimer.swf'
        self.__ui.movie.loadTimer(timerPath)

    def __del__(self):
        LOG_DEBUG('TimersBar is deleted')

    def destroy(self):
        self.__ui = None
        return

    def setTotalTime(self, level, totalTime):
        secondsStr = str(totalTime % 60)
        minutesStr = str(totalTime / 60)
        if len(secondsStr) < 2:
            secondsStr = '0' + secondsStr
        if len(minutesStr) < 2:
            minutesStr = '0' + minutesStr
        self.__call('timerBar.setTotalTime', [level, minutesStr, secondsStr])

    def hideTotalTime(self):
        self.__call('showBattleTimer', [False])

    def setCountdown(self, state, _, timeLeft):
        self.__call('timerBig.setTimer', [_STATE_TO_MESSAGE[state], timeLeft])

    def hideCountdown(self, state, speed):
        self.__call('timerBig.setTimer', [_STATE_TO_MESSAGE[state]])
        self.__call('timerBig.hide', [speed])

    def __call(self, funcName, args = None):
        if self.__ui:
            self.__ui.call('battle.{0}'.format(funcName), args)
