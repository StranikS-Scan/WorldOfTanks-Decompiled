# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventBattleTimerMeta.py
from gui.Scaleform.daapi.view.meta.BattleTimerMeta import BattleTimerMeta

class EventBattleTimerMeta(BattleTimerMeta):

    def as_showAddExtraTimeS(self, value, isRed=False):
        return self.flashObject.as_showAddExtraTime(value, isRed) if self._isDAAPIInited() else None

    def as_setIsEnlargedS(self, value=False):
        return self.flashObject.as_setIsEnlarged(value) if self._isDAAPIInited() else None
