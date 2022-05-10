# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleRoyaleTechParametersComponent.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BattleRoyaleTechParametersComponent(BaseDAAPIComponent):

    def as_updateHeightS(self, value):
        return self.flashObject.as_updateHeight(value) if self._isDAAPIInited() else None
