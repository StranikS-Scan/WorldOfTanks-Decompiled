# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event_mark1/battle_end_warning_panel.py
from gui.shared.lock import Lock
from gui.battle_control.battle_constants import BATTLE_SYNC_LOCKS
from gui.Scaleform.daapi.view.battle.classic import battle_end_warning_panel

class Mark1BattleEndWarningPanel(battle_end_warning_panel.BattleEndWarningPanel):

    def __init__(self):
        super(Mark1BattleEndWarningPanel, self).__init__()
        self.__viewLock = Lock(BATTLE_SYNC_LOCKS.MARK1_EVENT_NOTIFICATIONS)

    def _dispose(self):
        self.__viewLock.dispose()
        super(Mark1BattleEndWarningPanel, self)._dispose()

    def _setVisible(self, isVisible):
        if isVisible:
            if self.__viewLock.tryLock():
                super(Mark1BattleEndWarningPanel, self)._setVisible(isVisible)
        else:
            self.__viewLock.unlock()
            super(Mark1BattleEndWarningPanel, self)._setVisible(isVisible)
