# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/maps_training/ribbon_panel.py
from gui.Scaleform.daapi.view.battle.shared.ribbons_panel import BattleRibbonsPanel
from gui.Scaleform.genConsts.BATTLE_EFFICIENCY_TYPES import BATTLE_EFFICIENCY_TYPES as _BET
_PROHIB_BATTLE_EFFICIENCY_TYPES = (_BET.CAPTURE, _BET.DEFENCE, _BET.BASE_CAPTURE_BLOCKED)

class MapsTrainingRibbonPanel(BattleRibbonsPanel):

    def _shouldShowRibbon(self, ribbon):
        return False if ribbon.getType() in _PROHIB_BATTLE_EFFICIENCY_TYPES else super(MapsTrainingRibbonPanel, self)._shouldShowRibbon(ribbon)
