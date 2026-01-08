# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/random/random_battle_results_view_model.py
from frameworks.wulf import Array, Map, ViewModel
from gui.impl.gen.view_models.views.lobby.battle_results.additional_bonus_model import AdditionalBonusModel
from gui.impl.gen.view_models.views.lobby.battle_results.base_capture_info_model import BaseCaptureInfoModel
from gui.impl.gen.view_models.views.lobby.battle_results.detailed_personal_efficiency_model import DetailedPersonalEfficiencyModel
from gui.impl.gen.view_models.views.lobby.battle_results.financial_report_model import FinancialReportModel
from gui.impl.gen.view_models.views.lobby.battle_results.player_satisfaction_model import PlayerSatisfactionModel
from gui.impl.gen.view_models.views.lobby.battle_results.postbattle_achievement_model import PostbattleAchievementModel
from gui.impl.gen.view_models.views.lobby.battle_results.random.random_battle_info_model import RandomBattleInfoModel
from gui.impl.gen.view_models.views.lobby.battle_results.random.random_team_stats_model import RandomTeamStatsModel
from gui.impl.gen.view_models.views.lobby.common.router_model import RouterModel

class RandomBattleResultsViewModel(ViewModel):
    __slots__ = ('onClose', 'onOpenMissions')
    OVERVIEW = 'overview'
    TEAMS_STATISTICS = 'teamScore'
    PROGRESSION = 'missionProgress'
    FINANCIAL_REPORT = 'financialReport'

    def __init__(self, properties=10, commands=2):
        super(RandomBattleResultsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def battleInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getBattleInfoType():
        return RandomBattleInfoModel

    @property
    def teamStats(self):
        return self._getViewModel(1)

    @staticmethod
    def getTeamStatsType():
        return RandomTeamStatsModel

    @property
    def baseCaptureInfo(self):
        return self._getViewModel(2)

    @staticmethod
    def getBaseCaptureInfoType():
        return BaseCaptureInfoModel

    @property
    def financialReport(self):
        return self._getViewModel(3)

    @staticmethod
    def getFinancialReportType():
        return FinancialReportModel

    @property
    def additionalBonus(self):
        return self._getViewModel(4)

    @staticmethod
    def getAdditionalBonusType():
        return AdditionalBonusModel

    @property
    def playerSatisfaction(self):
        return self._getViewModel(5)

    @staticmethod
    def getPlayerSatisfactionType():
        return PlayerSatisfactionModel

    @property
    def router(self):
        return self._getViewModel(6)

    @staticmethod
    def getRouterType():
        return RouterModel

    def getAchievements(self):
        return self._getArray(7)

    def setAchievements(self, value):
        self._setArray(7, value)

    @staticmethod
    def getAchievementsType():
        return PostbattleAchievementModel

    def getDetailedPersonalEfficiency(self):
        return self._getArray(8)

    def setDetailedPersonalEfficiency(self, value):
        self._setArray(8, value)

    @staticmethod
    def getDetailedPersonalEfficiencyType():
        return DetailedPersonalEfficiencyModel

    def getPathToPlugins(self):
        return self._getMap(9)

    def setPathToPlugins(self, value):
        self._setMap(9, value)

    @staticmethod
    def getPathToPluginsType():
        return (int, unicode)

    def _initialize(self):
        super(RandomBattleResultsViewModel, self)._initialize()
        self._addViewModelProperty('battleInfo', RandomBattleInfoModel())
        self._addViewModelProperty('teamStats', RandomTeamStatsModel())
        self._addViewModelProperty('baseCaptureInfo', BaseCaptureInfoModel())
        self._addViewModelProperty('financialReport', FinancialReportModel())
        self._addViewModelProperty('additionalBonus', AdditionalBonusModel())
        self._addViewModelProperty('playerSatisfaction', PlayerSatisfactionModel())
        self._addViewModelProperty('router', RouterModel())
        self._addArrayProperty('achievements', Array())
        self._addArrayProperty('detailedPersonalEfficiency', Array())
        self._addMapProperty('pathToPlugins', Map(int, unicode))
        self.onClose = self._addCommand('onClose')
        self.onOpenMissions = self._addCommand('onOpenMissions')
