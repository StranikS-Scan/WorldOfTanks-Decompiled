# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/Scaleform/daapi/view/battle/battle_timers.py
from constants import ARENA_PERIOD
from gui.Scaleform.daapi.view.battle.shared.battle_timers import PreBattleTimer, BattleTimer

class FallTanksPreBattleTimer(PreBattleTimer):

    def _onHideAll(self, speed):
        super(FallTanksPreBattleTimer, self)._onHideAll(speed)
        self.as_setWinConditionTextS('')
        self.as_setMessageS('')


class FallTanksBattleTimer(BattleTimer):

    def __init__(self):
        super(FallTanksBattleTimer, self).__init__()
        self.__period = ARENA_PERIOD.IDLE

    def setPeriod(self, period):
        self.__period = period

    def hideTotalTime(self):
        pass

    def _sendTime(self, totalTime):
        if self.__period == ARENA_PERIOD.BATTLE:
            totalTime = self.getRoundLength() - totalTime
        super(FallTanksBattleTimer, self)._sendTime(totalTime)
