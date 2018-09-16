# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/football_pre_battle_timer.py
from gui.Scaleform.daapi.view.battle.shared.battle_timers import PreBattleTimer
from gui.battle_control.controllers.football_ctrl import IFootballPeriodListener
from gui.battle_control.battle_constants import COUNTDOWN_STATE
from gui.Scaleform.locale.FOOTBALL2018 import FOOTBALL2018
from helpers.i18n import makeString

class FootballPreBattleTimer(PreBattleTimer, IFootballPeriodListener):

    def __init__(self):
        super(FootballPreBattleTimer, self).__init__()
        self.__hidden = False
        self.__hideView = False

    def updateBattleCtx(self, battleCtx):
        if not self.__hidden:
            super(FootballPreBattleTimer, self).updateBattleCtx(battleCtx)

    def onPrepareFootballOvertime(self):
        if not self.__hidden:
            self.__hidden = True
            self.as_hideAllS(speed=0)

    def onBallDrop(self):
        if not self.__hidden:
            self.__hidden = True
            self.as_hideAllS(speed=0)

    def hideCountdown(self, state, speed):
        if not self.__hidden:
            if self.__hideView:
                self.__hidden = True
                super(FootballPreBattleTimer, self).hideCountdown(state, speed)

    def setCountdown(self, state, timeLeft):
        if not self.__hidden:
            self.as_setMessageS(makeString(FOOTBALL2018.MESSAGES_FOOTBALL_TIMER_STARTING))
            if state == COUNTDOWN_STATE.WAIT:
                self.as_hideTimerS()
            else:
                self.as_setTimerS(timeLeft)
            if not self.__hideView:
                self.__hideView = True
