# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventBattleTimerMeta.py
from gui.Scaleform.daapi.view.battle.shared.battle_timers import BattleTimer

class EventBattleTimerMeta(BattleTimer):

    def as_setPlayerTypeS(self, isBoss):
        return self.flashObject.as_setPlayerType(isBoss) if self._isDAAPIInited() else None

    def as_showAdditionalTimeS(self, time):
        return self.flashObject.as_showAdditionalTime(time) if self._isDAAPIInited() else None

    def as_showMessageS(self, message, isOverTime=False):
        return self.flashObject.as_showMessage(message, isOverTime) if self._isDAAPIInited() else None

    def as_hideMessageS(self):
        return self.flashObject.as_hideMessage() if self._isDAAPIInited() else None
