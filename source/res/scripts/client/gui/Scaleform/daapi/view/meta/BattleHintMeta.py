# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleHintMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BattleHintMeta(BaseDAAPIComponent):

    def as_showHintS(self, type, data):
        return self.flashObject.as_showHint(type, data) if self._isDAAPIInited() else None

    def as_hideHintS(self):
        return self.flashObject.as_hideHint() if self._isDAAPIInited() else None

    def as_closeHintS(self):
        return self.flashObject.as_closeHint() if self._isDAAPIInited() else None
