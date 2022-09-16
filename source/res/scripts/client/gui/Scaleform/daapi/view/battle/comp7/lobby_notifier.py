# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/comp7/lobby_notifier.py
import BigWorld
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from constants import ARENA_PERIOD
_NOTIFICATION_TIME = 30.0

class LobbyNotifier(IAbstractPeriodView):

    def __init__(self):
        super(LobbyNotifier, self).__init__()
        self.__isNotified = False

    def setCountdown(self, state, timeLeft):
        if state == ARENA_PERIOD.PREBATTLE and timeLeft <= _NOTIFICATION_TIME:
            self.__doNotify()

    def __doNotify(self):
        if not self.__isNotified:
            BigWorld.WGWindowsNotifier.onBattleBeginning()
            self.__isNotified = True
