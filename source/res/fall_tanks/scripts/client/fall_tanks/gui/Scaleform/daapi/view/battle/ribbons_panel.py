# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/Scaleform/daapi/view/battle/ribbons_panel.py
from account_helpers.settings_core.settings_constants import BATTLE_EVENTS
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.battle.shared.ribbons_panel import BattleRibbonsPanel
from fall_tanks.gui.Scaleform.daapi.view.battle import ribbons_aggregator
from fall_tanks.gui.Scaleform.genConsts.FALL_TANKS_BATTLE_EFFICIENCY_TYPES import FALL_TANKS_BATTLE_EFFICIENCY_TYPES
_BATTLE_EVENTS_SETTINGS_TO_BATTLE_EFFICIENCY_TYPES = {BATTLE_EVENTS.ENEMY_KILL: (FALL_TANKS_BATTLE_EFFICIENCY_TYPES.FALL_TANKS_DESTRUCTION,)}

class FallTanksBattleRibbonsPanel(BattleRibbonsPanel):

    def __init__(self):
        super(FallTanksBattleRibbonsPanel, self).__init__(ribbonsAggregator=ribbons_aggregator.createRibbonsAggregator())

    @classmethod
    def getBattleEventsSettingsToBattleEfficiencyTypes(cls):
        return _BATTLE_EVENTS_SETTINGS_TO_BATTLE_EFFICIENCY_TYPES

    def _getRibbonsConfig(self):
        return [[FALL_TANKS_BATTLE_EFFICIENCY_TYPES.FALL_TANKS_DESTRUCTION, backport.text(R.strings.fall_tanks.efficiencyRibbons.fallTanksKill())]]
