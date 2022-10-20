# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/battle/ribbons_panel.py
from halloween.gui.Scaleform.daapi.view.battle import ribbons_aggregator
from gui.Scaleform.daapi.view.battle.shared.ribbons_panel import BattleRibbonsPanel, _RIBBONS_FMTS
from gui.Scaleform.genConsts.BATTLE_EFFICIENCY_TYPES import BATTLE_EFFICIENCY_TYPES
from gui.impl import backport
from gui.impl.gen import R

def _halloweenRepairRibbonFormatter(ribbon, arenaDP, updater):
    updater(ribbonID=ribbon.getID(), ribbonType=ribbon.efficiencyType, leftFieldStr=ribbon.actionValue)


_RIBBONS_FMTS.update({BATTLE_EFFICIENCY_TYPES.HALLOWEEN_REPAIR: _halloweenRepairRibbonFormatter})

class HalloweenBattleRibbonsPanel(BattleRibbonsPanel):

    def __init__(self):
        super(HalloweenBattleRibbonsPanel, self).__init__()
        self._ribbonsAggregator = ribbons_aggregator.createRibbonsAggregator()

    def _populate(self):
        super(HalloweenBattleRibbonsPanel, self)._populate()
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onPostMortemSwitched += self._onPostMortemSwitched
            ctrl.onRespawnBaseMoving += self._onRespawnBaseMoving
        return

    def _dispose(self):
        super(HalloweenBattleRibbonsPanel, self)._dispose()
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onPostMortemSwitched -= self._onPostMortemSwitched
            ctrl.onRespawnBaseMoving -= self._onRespawnBaseMoving
        return

    def _onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        self.aggregator.suspend()
        self.clear()

    def _onRespawnBaseMoving(self):
        self.aggregator.resume()

    def clear(self):
        self._ribbonsAggregator.clearRibbonsData()
        self.as_resetS()

    @property
    def aggregator(self):
        return self._ribbonsAggregator

    def _getRibbonsConfig(self):
        result = super(HalloweenBattleRibbonsPanel, self)._getRibbonsConfig()
        result.extend([[BATTLE_EFFICIENCY_TYPES.HALLOWEEN_REPAIR, backport.text(R.strings.hw_ingame_gui.efficiencyRibbons.halloweenRepair())]])
        return result
