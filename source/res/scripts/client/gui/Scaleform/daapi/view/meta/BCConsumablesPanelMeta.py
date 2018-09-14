# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BCConsumablesPanelMeta.py
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel

class BCConsumablesPanelMeta(ConsumablesPanel):

    def as_setBigSizeS(self, value):
        return self.flashObject.as_setBigSize(value) if self._isDAAPIInited() else None
