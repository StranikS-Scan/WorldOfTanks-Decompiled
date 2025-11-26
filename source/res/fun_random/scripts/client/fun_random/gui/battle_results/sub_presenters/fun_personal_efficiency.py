# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/battle_results/sub_presenters/fun_personal_efficiency.py
from __future__ import absolute_import
import typing
from frameworks.wulf import Array
from fun_random.gui.battle_results.packers.fun_packers import FunRandomPersonalEfficiency
from fun_random.gui.impl.gen.view_models.views.lobby.feature.battle_results.fun_stats_efficiency_model import FunStatsEfficiencyModel
from fun_random.gui.impl.lobby.tooltips.fun_random_battle_results_efficiency_tooltip_view import PersonalEfficiencyParamTooltip
from gui.impl.gen import R
from gui.battle_results.presenters.battle_results_sub_presenter import BattleResultsSubPresenter
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel
    from gui.battle_results.stats_ctrl import BattleResults

class FunPersonalEfficiencySubPresenter(BattleResultsSubPresenter):

    @classmethod
    def getViewModelType(cls):
        return Array[FunStatsEfficiencyModel]

    def packBattleResults(self, battleResults):
        with self.getViewModel().transaction() as model:
            FunRandomPersonalEfficiency.packModel(model, battleResults)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.tooltips.BattleResultsStatsTooltipView():
            paramType = event.getArgument('paramType')
            return PersonalEfficiencyParamTooltip(self.parentView.arenaUniqueID, paramType)
        return super(FunPersonalEfficiencySubPresenter, self).createToolTipContent(event, contentID)
