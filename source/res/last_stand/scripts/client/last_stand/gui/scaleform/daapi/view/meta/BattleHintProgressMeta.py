# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/meta/BattleHintProgressMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BattleHintProgressMeta(BaseDAAPIComponent):

    def as_updateProgressS(self, value, progressValue):
        return self.flashObject.as_updateProgress(value, progressValue) if self._isDAAPIInited() else None
