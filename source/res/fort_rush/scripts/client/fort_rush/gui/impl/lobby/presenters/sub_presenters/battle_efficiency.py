# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/lobby/presenters/sub_presenters/battle_efficiency.py
from __future__ import absolute_import
import typing
from fort_rush.gui.fort_rush_presenters_packers import FortRushPersonalEfficiency
from fort_rush.gui.impl.gen.view_models.views.lobby.post_battle_results_view.post_battle_results_view_model import PostBattleResultsViewModel
from gui.battle_results.presenters.battle_results_sub_presenter import BattleResultsSubPresenter
from gui.impl.gen import R
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel
    from gui.battle_results.stats_ctrl import BattleResults

class FortRushBattleEfficiencySubPresenter(BattleResultsSubPresenter):
    _PACKER_CLS = FortRushPersonalEfficiency

    @classmethod
    def getViewModelType(cls):
        return PostBattleResultsViewModel

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.tooltips.BattleResultsStatsTooltipView():
            from gui.impl.lobby.tooltips.battle_efficiency_tooltips_views import BattleResultsStatsTooltipView
            paramType = event.getArgument('paramType')
            userName = event.getArgument('userName')
            return BattleResultsStatsTooltipView(self.parentView.arenaUniqueID, paramType, userName)
        if contentID == R.views.mono.post_battle.tooltips.critical_damage():
            from gui.impl.lobby.tooltips.battle_efficiency_tooltips_views import BattleResultsCriticalDamageTooltipView
            paramType = event.getArgument('paramType')
            userName = event.getArgument('userName')
            return BattleResultsCriticalDamageTooltipView(self.parentView.arenaUniqueID, paramType, userName)
        return super(FortRushBattleEfficiencySubPresenter, self).createToolTipContent(event, contentID)

    def packBattleResults(self, battleResults):
        with self.getViewModel().transaction() as model:
            self._PACKER_CLS.packModel(model.getDetailedPersonalEfficiency(), battleResults)
