# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/battle_results/submodel_presenters/comp7_light_sub_presenter.py
from __future__ import absolute_import
import typing
from comp7_light.gui.impl.gen.view_models.views.lobby.comp7_light_battle_results_view_model import Comp7LightBattleResultsViewModel
from comp7_light.gui.impl.lobby.battle_results.submodel_presenters.battle_info import Comp7LightBattleInfoSubPresenter
from comp7_light.gui.impl.lobby.battle_results.submodel_presenters.battle_efficiency import Comp7LightBattleEfficiencySubPresenter
from comp7_light.gui.impl.lobby.battle_results.submodel_presenters.team_statistics import Comp7LightTeamStatisticsSubPresenter
from gui.battle_results.presenters.battle_results_sub_presenter import BattleResultsSubPresenter
from gui.impl.lobby.battle_results.submodel_presenters.battle_achievements import BattleAchievementsSubPresenter
from comp7_light.gui.impl.lobby.battle_results.submodel_presenters.financial_report import Comp7LightFinancialReportSubPresenter
from gui.impl.lobby.battle_results.submodel_presenters.financial_report import ManageableBonusSubPresenter
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel

class Comp7LightBattleResultsSubPresenter(BattleResultsSubPresenter):

    def __init__(self, viewModel, parentView):
        super(Comp7LightBattleResultsSubPresenter, self).__init__(viewModel, parentView)
        self.addSubPresenter(Comp7LightBattleEfficiencySubPresenter(viewModel, parentView))
        self.addSubPresenter(Comp7LightBattleInfoSubPresenter(viewModel.battleInfo, parentView))
        self.addSubPresenter(BattleAchievementsSubPresenter(viewModel.getAchievements(), parentView))
        self.addSubPresenter(Comp7LightTeamStatisticsSubPresenter(viewModel.teamStats, parentView))
        self.addSubPresenter(ManageableBonusSubPresenter(viewModel.additionalBonus, parentView))
        self.addSubPresenter(Comp7LightFinancialReportSubPresenter(viewModel.financialReport, parentView))

    @classmethod
    def getViewModelType(cls):
        return Comp7LightBattleResultsViewModel
