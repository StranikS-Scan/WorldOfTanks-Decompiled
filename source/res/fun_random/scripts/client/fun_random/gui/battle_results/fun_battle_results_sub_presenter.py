# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/battle_results/fun_battle_results_sub_presenter.py
from __future__ import absolute_import
import typing
from fun_random.gui.battle_results.sub_presenters.fun_battle_info import FunBattleInfoSubPresenter
from fun_random.gui.battle_results.sub_presenters.fun_personal_info import FunPersonalInfoSubPresenter
from fun_random.gui.battle_results.sub_presenters.fun_personal_efficiency import FunPersonalEfficiencySubPresenter
from fun_random.gui.battle_results.sub_presenters.fun_personal_rewards import FunPersonalRewardSubPresenter
from fun_random.gui.battle_results.sub_presenters.fun_premium_plus import FunPremiumPlusSubPresenter
from fun_random.gui.battle_results.sub_presenters.fun_progression import FunProgressionSubPresenter
from fun_random.gui.battle_results.sub_presenters.fun_team_stats import FunTeamStatsSubPresenter
from fun_random.gui.impl.gen.view_models.views.lobby.feature.battle_results.fun_battle_results_view_model import FunBattleResultsViewModel
from gui.battle_results.presenters.battle_results_sub_presenter import BattleResultsSubPresenter
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel

class FunBattleResultsSubPresenter(BattleResultsSubPresenter):

    def __init__(self, viewModel, parentView):
        super(FunBattleResultsSubPresenter, self).__init__(viewModel, parentView)
        self.addSubPresenter(FunPersonalInfoSubPresenter(viewModel, parentView))
        self.addSubPresenter(FunPersonalEfficiencySubPresenter(viewModel.getEfficiency(), parentView))
        self.addSubPresenter(FunBattleInfoSubPresenter(viewModel.battleInfo, parentView))
        self.addSubPresenter(FunPersonalRewardSubPresenter(viewModel.getRewards(), parentView))
        self.addSubPresenter(FunTeamStatsSubPresenter(viewModel.teamStats, parentView))
        self.addSubPresenter(FunProgressionSubPresenter(viewModel.progress, parentView))
        self.addSubPresenter(FunPremiumPlusSubPresenter(viewModel.premiumPlus, parentView))

    @classmethod
    def getViewModelType(cls):
        return FunBattleResultsViewModel
