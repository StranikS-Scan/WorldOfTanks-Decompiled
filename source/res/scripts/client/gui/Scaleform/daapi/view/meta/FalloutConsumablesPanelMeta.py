# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FalloutConsumablesPanelMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel

class FalloutConsumablesPanelMeta(ConsumablesPanel):

    def as_initializeRageProgressS(self, show, barProps):
        return self.flashObject.as_initializeRageProgress(show, barProps) if self._isDAAPIInited() else None

    def as_updateProgressBarValueByDeltaS(self, delta):
        return self.flashObject.as_updateProgressBarValueByDelta(delta) if self._isDAAPIInited() else None

    def as_updateProgressBarValueS(self, value):
        return self.flashObject.as_updateProgressBarValue(value) if self._isDAAPIInited() else None
