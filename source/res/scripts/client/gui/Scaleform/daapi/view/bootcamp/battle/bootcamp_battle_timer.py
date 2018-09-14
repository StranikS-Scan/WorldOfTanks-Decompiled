# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/battle/bootcamp_battle_timer.py
from gui.Scaleform.daapi.view.battle.shared.battle_timers import BattleTimer, _WWISE_EVENTS

class BootcampBattleTimer(BattleTimer):

    def __init__(self):
        super(BootcampBattleTimer, self).__init__()

    def _callWWISE(self, wwiseEventName):
        if wwiseEventName == _WWISE_EVENTS.BATTLE_END:
            self.sessionProvider.dynamic.finishSound.setFinishSound(_WWISE_EVENTS.BATTLE_END)
        else:
            super(BootcampBattleTimer, self)._callWWISE(wwiseEventName)
