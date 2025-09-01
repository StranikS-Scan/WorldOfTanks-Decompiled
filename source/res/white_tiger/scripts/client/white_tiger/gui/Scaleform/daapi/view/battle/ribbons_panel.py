# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/ribbons_panel.py
from gui.Scaleform.daapi.view.battle.shared.ribbons_panel import BattleRibbonsPanel
from white_tiger.gui.Scaleform.genConsts.WHITE_TIGER_BATTLE_EFFICIENCY_TYPES import WHITE_TIGER_BATTLE_EFFICIENCY_TYPES
from gui.impl import backport
from gui.impl.gen import R
from white_tiger.gui.Scaleform.daapi.view.battle import ribbons_aggregator
from account_helpers.settings_core.settings_constants import BATTLE_EVENTS

class WTBattleRibbonsPanel(BattleRibbonsPanel):

    def __init__(self):
        super(WTBattleRibbonsPanel, self).__init__()
        self._ribbonsAggregator = ribbons_aggregator.createRibbonsAggregator()
        battleEfficiencyTypes = [ ribbon.TYPE for ribbon in ribbons_aggregator.WTReceiveDamageRibbonsFactory.ATTACK_REASONS.itervalues() ]
        self._ribbonsUserSettings = {BATTLE_EVENTS.RECEIVED_DAMAGE: battleEfficiencyTypes}

    def clear(self):
        self._ribbonsAggregator.clearRibbonsData()
        self.as_resetS()

    @property
    def aggregator(self):
        return self._ribbonsAggregator

    def _getRibbonsConfig(self):
        result = super(WTBattleRibbonsPanel, self)._getRibbonsConfig()
        result.extend([[WHITE_TIGER_BATTLE_EFFICIENCY_TYPES.HYPERION, backport.text(R.strings.white_tiger_battle.efficiencyRibbons.damageHyperion())], [WHITE_TIGER_BATTLE_EFFICIENCY_TYPES.CIRCUIT_OVERLOAD, backport.text(R.strings.white_tiger_battle.efficiencyRibbons.damageCircuitOverload())]])
        return result
