# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/Scaleform/daapi/view/battle/portal_battle_timers.py
import BigWorld
from gui.Scaleform.daapi.view.battle.shared.battle_timers import BattleTimer, PreBattleTimer
from PortalBattleStateComponent import PortalBattleStateComponent

class PortalBattleTimer(BattleTimer):

    def __init__(self):
        super(PortalBattleTimer, self).__init__()
        self.__battleFinishTime = None
        return

    def _populate(self):
        super(PortalBattleTimer, self)._populate()
        PortalBattleStateComponent.onBattleFinishTimeChanged += self.__onBattleFinishTimeChanged
        self.__updateData()

    def __updateData(self):
        battleState = BigWorld.player().arena.arenaInfo.portalBattleStateComponent
        if not battleState:
            return
        self.__onBattleFinishTimeChanged(battleState.battleFinishTime)

    def _dispose(self):
        PortalBattleStateComponent.onBattleFinishTimeChanged -= self.__onBattleFinishTimeChanged
        super(PortalBattleTimer, self)._dispose()

    def setTotalTime(self, totalTime):
        timeLeft = totalTime
        if self.__battleFinishTime:
            timeLeft = max(self.__battleFinishTime - BigWorld.serverTime(), 0)
        super(PortalBattleTimer, self).setTotalTime(timeLeft)

    def __onBattleFinishTimeChanged(self, battleFinishTime):
        self.__battleFinishTime = battleFinishTime
        self.setTotalTime(0)


class PortalPreBattleTimer(PreBattleTimer):

    def hideCountdown(self, state, speed):
        self._clearTimeShiftCallback()
        self.as_hideAllS(False)
