# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/views/post_battle_results_view/post_battle_results_view_model.py
from frameworks.wulf import Array, ViewModel
from frontline.gui.impl.gen.view_models.views.lobby.views.post_battle_results_view.achievement_model import AchievementModel
from frontline.gui.impl.gen.view_models.views.lobby.views.post_battle_results_view.battle_financial_report_model import BattleFinancialReportModel
from frontline.gui.impl.gen.view_models.views.lobby.views.post_battle_results_view.battle_info_model import BattleInfoModel
from frontline.gui.impl.gen.view_models.views.lobby.views.post_battle_results_view.battle_team_stats_model import BattleTeamStatsModel
from gui.impl.gen.view_models.views.lobby.battle_results.detailed_personal_efficiency_model import DetailedPersonalEfficiencyModel
from gui.impl.gen.view_models.views.lobby.common.router_model import RouterModel

class PostBattleResultsViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=6, commands=1):
        super(PostBattleResultsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def battleInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getBattleInfoType():
        return BattleInfoModel

    @property
    def teamStats(self):
        return self._getViewModel(1)

    @staticmethod
    def getTeamStatsType():
        return BattleTeamStatsModel

    @property
    def financialReport(self):
        return self._getViewModel(2)

    @staticmethod
    def getFinancialReportType():
        return BattleFinancialReportModel

    @property
    def router(self):
        return self._getViewModel(3)

    @staticmethod
    def getRouterType():
        return RouterModel

    def getAchievements(self):
        return self._getArray(4)

    def setAchievements(self, value):
        self._setArray(4, value)

    @staticmethod
    def getAchievementsType():
        return AchievementModel

    def getDetailedPersonalEfficiency(self):
        return self._getArray(5)

    def setDetailedPersonalEfficiency(self, value):
        self._setArray(5, value)

    @staticmethod
    def getDetailedPersonalEfficiencyType():
        return DetailedPersonalEfficiencyModel

    def _initialize(self):
        super(PostBattleResultsViewModel, self)._initialize()
        self._addViewModelProperty('battleInfo', BattleInfoModel())
        self._addViewModelProperty('teamStats', BattleTeamStatsModel())
        self._addViewModelProperty('financialReport', BattleFinancialReportModel())
        self._addViewModelProperty('router', RouterModel())
        self._addArrayProperty('achievements', Array())
        self._addArrayProperty('detailedPersonalEfficiency', Array())
        self.onClose = self._addCommand('onClose')
