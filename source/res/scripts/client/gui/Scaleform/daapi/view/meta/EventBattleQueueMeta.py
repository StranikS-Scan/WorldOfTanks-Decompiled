# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventBattleQueueMeta.py
from gui.Scaleform.daapi.view.meta.BaseBattleQueueMeta import BaseBattleQueueMeta

class EventBattleQueueMeta(BaseBattleQueueMeta):

    def as_setDifficultyS(self, value):
        return self.flashObject.as_setDifficulty(value) if self._isDAAPIInited() else None
