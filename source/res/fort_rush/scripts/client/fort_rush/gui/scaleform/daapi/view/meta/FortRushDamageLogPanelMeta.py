# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/scaleform/daapi/view/meta/FortRushDamageLogPanelMeta.py
from gui.Scaleform.daapi.view.battle.shared.damage_log_panel import DamageLogPanel

class FortRushDamageLogPanelMeta(DamageLogPanel):

    def as_updateSummaryFortRushValueS(self, value):
        return self.flashObject.as_updateSummaryFortRushValue(value) if self._isDAAPIInited() else None
