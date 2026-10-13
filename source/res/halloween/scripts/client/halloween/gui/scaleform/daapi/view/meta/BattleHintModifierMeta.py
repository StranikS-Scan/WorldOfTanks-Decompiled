# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/meta/BattleHintModifierMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BattleHintModifierMeta(BaseDAAPIComponent):

    def as_updateHintS(self, data):
        return self.flashObject.as_updateHint(data) if self._isDAAPIInited() else None
