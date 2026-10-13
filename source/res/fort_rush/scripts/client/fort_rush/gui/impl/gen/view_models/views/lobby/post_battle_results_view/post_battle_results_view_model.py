# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/gen/view_models/views/lobby/post_battle_results_view/post_battle_results_view_model.py
from frameworks.wulf import Array, ViewModel
from fort_rush.gui.impl.gen.view_models.views.lobby.post_battle_results_view.battle_info_model import BattleInfoModel
from fort_rush.gui.impl.gen.view_models.views.lobby.post_battle_results_view.battle_team_stats_model import BattleTeamStatsModel
from fort_rush.gui.impl.gen.view_models.views.lobby.post_battle_results_view.detailed_personal_efficiency_item_model import DetailedPersonalEfficiencyItemModel
from fort_rush.gui.impl.gen.view_models.views.lobby.post_battle_results_view.fort_rush_reward_item_model import FortRushRewardItemModel
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
    def router(self):
        return self._getViewModel(2)

    @staticmethod
    def getRouterType():
        return RouterModel

    def getIsLeaver(self):
        return self._getBool(3)

    def setIsLeaver(self, value):
        self._setBool(3, value)

    def getDetailedPersonalEfficiency(self):
        return self._getArray(4)

    def setDetailedPersonalEfficiency(self, value):
        self._setArray(4, value)

    @staticmethod
    def getDetailedPersonalEfficiencyType():
        return DetailedPersonalEfficiencyItemModel

    def getRewards(self):
        return self._getArray(5)

    def setRewards(self, value):
        self._setArray(5, value)

    @staticmethod
    def getRewardsType():
        return FortRushRewardItemModel

    def _initialize(self):
        super(PostBattleResultsViewModel, self)._initialize()
        self._addViewModelProperty('battleInfo', BattleInfoModel())
        self._addViewModelProperty('teamStats', BattleTeamStatsModel())
        self._addViewModelProperty('router', RouterModel())
        self._addBoolProperty('isLeaver', False)
        self._addArrayProperty('detailedPersonalEfficiency', Array())
        self._addArrayProperty('rewards', Array())
        self.onClose = self._addCommand('onClose')
