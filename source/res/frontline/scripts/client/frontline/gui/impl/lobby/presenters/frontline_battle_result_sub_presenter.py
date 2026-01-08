# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/presenters/frontline_battle_result_sub_presenter.py
import typing
from gui.battle_results.presenters.battle_results_sub_presenter import BattleResultsSubPresenter
from frontline.gui.impl.gen.view_models.views.lobby.views.post_battle_results_view.post_battle_results_view_model import PostBattleResultsViewModel
from frontline.gui.impl.lobby.presenters.sub_presenters.battle_achievements import FrontlineBattleAchievementsSubPresenter
from frontline.gui.impl.lobby.presenters.sub_presenters.team_statistics import FrontlineTeamStatisticsSubPresenter
from frontline.gui.impl.lobby.presenters.sub_presenters.battle_info import FrontlineBattleInfoSubPresenter
from frontline.gui.impl.lobby.presenters.sub_presenters.financial_report import FrontlineFinancialReportSubPresenter
from frontline.gui.impl.lobby.presenters.sub_presenters.battle_efficiency import FrontlineBattleEfficiencySubPresenter
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel

class FrontlineBattleResultsSubPresenter(BattleResultsSubPresenter):

    def __init__(self, viewModel, parentView):
        super(FrontlineBattleResultsSubPresenter, self).__init__(viewModel, parentView)
        self.addSubPresenter(FrontlineBattleEfficiencySubPresenter(viewModel, parentView))
        self.addSubPresenter(FrontlineBattleAchievementsSubPresenter(viewModel.getAchievements(), parentView))
        self.addSubPresenter(FrontlineTeamStatisticsSubPresenter(viewModel.teamStats, parentView))
        self.addSubPresenter(FrontlineBattleInfoSubPresenter(viewModel.battleInfo, parentView))
        self.addSubPresenter(FrontlineFinancialReportSubPresenter(viewModel.financialReport, parentView))

    @classmethod
    def getViewModelType(cls):
        return PostBattleResultsViewModel
