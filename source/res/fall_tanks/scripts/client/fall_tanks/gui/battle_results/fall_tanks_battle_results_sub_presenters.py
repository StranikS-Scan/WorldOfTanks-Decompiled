# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/battle_results/fall_tanks_battle_results_sub_presenters.py
from __future__ import absolute_import
import typing
from gui.battle_results.presenters.battle_results_sub_presenter import BattleResultsSubPresenter
from gui.impl.gen import R
from fun_random.gui.battle_results.sub_presenters.fun_battle_info import FunBattleInfoSubPresenter
from fun_random.gui.battle_results.sub_presenters.fun_personal_info import FunPersonalInfoSubPresenter
from fun_random.gui.battle_results.sub_presenters.fun_personal_efficiency import FunPersonalEfficiencySubPresenter
from fun_random.gui.battle_results.sub_presenters.fun_personal_rewards import FunPersonalRewardSubPresenter
from fun_random.gui.battle_results.sub_presenters.fun_premium_plus import FunPremiumPlusSubPresenter
from fun_random.gui.battle_results.sub_presenters.fun_progression import FunProgressionSubPresenter
from fun_random.gui.battle_results.sub_presenters.fun_team_stats import FunTeamStatsSubPresenter
from fun_random.gui.impl.gen.view_models.views.lobby.feature.battle_results.fun_battle_results_view_model import FunBattleResultsViewModel
from fun_random.gui.impl.lobby.tooltips.fun_random_battle_results_efficiency_tooltip_view import PersonalEfficiencyParamTooltip
from fall_tanks.gui.battle_results.fall_tanks_packers import FallTanksBattleInfo, FallTanksPersonalEfficiency, FallTanksTeamStats
from fall_tanks.gui.battle_results.tooltips.fall_tanks_total_efficiency_tooltips import FallTanksEfficiencyTooltipsPacker
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel

class FallTanksBattleResultsSubPresenter(BattleResultsSubPresenter):

    def __init__(self, viewModel, parentView):
        super(FallTanksBattleResultsSubPresenter, self).__init__(viewModel, parentView)
        self.addSubPresenter(FallTanksPersonalEfficiencySubPresenter(viewModel.getEfficiency(), parentView))
        self.addSubPresenter(FallTanksBattleInfoSubPresenter(viewModel.battleInfo, parentView))
        self.addSubPresenter(FallTanksTeamStatsSubPresenter(viewModel.teamStats, parentView))
        self.addSubPresenter(FunPersonalInfoSubPresenter(viewModel, parentView))
        self.addSubPresenter(FunPersonalRewardSubPresenter(viewModel.getRewards(), parentView))
        self.addSubPresenter(FunProgressionSubPresenter(viewModel.progress, parentView))
        self.addSubPresenter(FunPremiumPlusSubPresenter(viewModel.premiumPlus, parentView))

    @classmethod
    def getViewModelType(cls):
        return FunBattleResultsViewModel


class FallTanksBattleInfoSubPresenter(FunBattleInfoSubPresenter):
    _PACKER_CLS = FallTanksBattleInfo


class FallTanksPersonalEfficiencySubPresenter(FunPersonalEfficiencySubPresenter):
    _PACKER_CLS = FallTanksPersonalEfficiency

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.tooltips.BattleResultsStatsTooltipView():
            paramType = event.getArgument('paramType')
            return PersonalEfficiencyParamTooltip(self.parentView.arenaUniqueID, paramType, FallTanksEfficiencyTooltipsPacker)
        return super(FallTanksPersonalEfficiencySubPresenter, self).createToolTipContent(event, contentID)


class FallTanksTeamStatsSubPresenter(FunTeamStatsSubPresenter):
    _PACKER_CLS = FallTanksTeamStats
