# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/battle_timers.py
from gui.Scaleform.daapi.view.battle.shared.battle_timers import BattleTimer
from gui.battle_control.battle_constants import COUNTDOWN_STATE

class EventBattleTimer(BattleTimer):

    def setState(self, state):
        super(EventBattleTimer, self).setState(state)
        self.as_showBattleTimerS(state not in COUNTDOWN_STATE.VISIBLE)
