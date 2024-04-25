# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/HBBattleHintMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class HBBattleHintMeta(BaseDAAPIComponent):

    def as_showHintS(self, data):
        return self.flashObject.as_showHint(data) if self._isDAAPIInited() else None

    def as_hideHintS(self):
        return self.flashObject.as_hideHint() if self._isDAAPIInited() else None

    def as_closeHintS(self):
        return self.flashObject.as_closeHint() if self._isDAAPIInited() else None
