# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ThermalVisionIndicatorMeta.py
from gui.Scaleform.daapi.view.battle.shared.indicator_items.base import BaseIndicator

class ThermalVisionIndicatorMeta(BaseIndicator):

    def as_setEnemyIndicatorS(self, isVisible):
        return self.flashObject.as_setEnemyIndicator(isVisible) if self._isDAAPIInited() else None
