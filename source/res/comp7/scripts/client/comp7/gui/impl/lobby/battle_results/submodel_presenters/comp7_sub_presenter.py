# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/battle_results/submodel_presenters/comp7_sub_presenter.py
from __future__ import absolute_import
import typing
from comp7.gui.impl.gen.view_models.views.lobby.comp7_battle_results_view_model import Comp7BattleResultsViewModel
from comp7.gui.impl.lobby.battle_results.submodel_presenters.battle_efficiency import Comp7BattleEfficiencySubPresenter
from comp7.gui.impl.lobby.battle_results.submodel_presenters.comp7_progression import Comp7ProgressionSubPresenter
from comp7.gui.impl.lobby.battle_results.submodel_presenters.financial_report import Comp7FinancialReportSubPresenter
from comp7.gui.impl.lobby.battle_results.submodel_presenters.team_statistics import Comp7TeamStatisticsSubPresenter
from comp7.gui.impl.lobby.battle_results.submodel_presenters.vehicle_ban_presenter import Comp7VehicleBanSubPresenter
from comp7.gui.impl.lobby.battle_results.submodel_presenters.battle_info import Comp7BattleInfoSubPresenter
from gui.battle_results.presenters.battle_results_sub_presenter import BattleResultsSubPresenter
from gui.impl.lobby.battle_results.submodel_presenters.battle_achievements import BattleAchievementsSubPresenter
from gui.impl.lobby.battle_results.submodel_presenters.financial_report import ManageableBonusSubPresenter
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel

class Comp7BattleResultsSubPresenter(BattleResultsSubPresenter):

    def __init__(self, viewModel, parentView):
        super(Comp7BattleResultsSubPresenter, self).__init__(viewModel, parentView)
        self.addSubPresenter(Comp7BattleEfficiencySubPresenter(viewModel, parentView))
        self.addSubPresenter(Comp7BattleInfoSubPresenter(viewModel.battleInfo, parentView))
        self.addSubPresenter(BattleAchievementsSubPresenter(viewModel.getAchievements(), parentView))
        self.addSubPresenter(Comp7TeamStatisticsSubPresenter(viewModel.teamStats, parentView))
        self.addSubPresenter(ManageableBonusSubPresenter(viewModel.additionalBonus, parentView))
        self.addSubPresenter(Comp7FinancialReportSubPresenter(viewModel.financialReport, parentView))
        self.addSubPresenter(Comp7VehicleBanSubPresenter(viewModel.bansModel, parentView))
        self.addSubPresenter(Comp7ProgressionSubPresenter(viewModel, parentView))

    @classmethod
    def getViewModelType(cls):
        return Comp7BattleResultsViewModel
