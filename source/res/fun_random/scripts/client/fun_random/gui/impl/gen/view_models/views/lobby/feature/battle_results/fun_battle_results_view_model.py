# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/gen/view_models/views/lobby/feature/battle_results/fun_battle_results_view_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.user_name_model import UserNameModel
from fun_random.gui.impl.gen.view_models.views.lobby.feature.battle_results.fun_random_battle_info_model import FunRandomBattleInfoModel
from fun_random.gui.impl.gen.view_models.views.lobby.feature.battle_results.fun_random_progress_model import FunRandomProgressModel
from fun_random.gui.impl.gen.view_models.views.lobby.feature.battle_results.fun_random_reward_item_model import FunRandomRewardItemModel
from gui.impl.gen.view_models.views.lobby.battle_results.personal_efficiency_model import PersonalEfficiencyModel
from gui.impl.gen.view_models.views.lobby.battle_results.premium_plus_model import PremiumPlusModel
from gui.impl.gen.view_models.views.lobby.battle_results.team_stats_model import TeamStatsModel
from gui.impl.gen.view_models.views.lobby.battle_results.user_status_model import UserStatusModel

class Tab(IntEnum):
    PERSONAL = 1
    TEAMSTATS = 2


class FunBattleResultsViewModel(ViewModel):
    __slots__ = ('onClose', 'onTabChanged')

    def __init__(self, properties=8, commands=2):
        super(FunBattleResultsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def userNames(self):
        return self._getViewModel(0)

    @staticmethod
    def getUserNamesType():
        return UserNameModel

    @property
    def userStatus(self):
        return self._getViewModel(1)

    @staticmethod
    def getUserStatusType():
        return UserStatusModel

    @property
    def battleInfo(self):
        return self._getViewModel(2)

    @staticmethod
    def getBattleInfoType():
        return FunRandomBattleInfoModel

    @property
    def premiumPlus(self):
        return self._getViewModel(3)

    @staticmethod
    def getPremiumPlusType():
        return PremiumPlusModel

    @property
    def teamStats(self):
        return self._getViewModel(4)

    @staticmethod
    def getTeamStatsType():
        return TeamStatsModel

    @property
    def progress(self):
        return self._getViewModel(5)

    @staticmethod
    def getProgressType():
        return FunRandomProgressModel

    def getEfficiency(self):
        return self._getArray(6)

    def setEfficiency(self, value):
        self._setArray(6, value)

    @staticmethod
    def getEfficiencyType():
        return PersonalEfficiencyModel

    def getRewards(self):
        return self._getArray(7)

    def setRewards(self, value):
        self._setArray(7, value)

    @staticmethod
    def getRewardsType():
        return FunRandomRewardItemModel

    def _initialize(self):
        super(FunBattleResultsViewModel, self)._initialize()
        self._addViewModelProperty('userNames', UserNameModel())
        self._addViewModelProperty('userStatus', UserStatusModel())
        self._addViewModelProperty('battleInfo', FunRandomBattleInfoModel())
        self._addViewModelProperty('premiumPlus', PremiumPlusModel())
        self._addViewModelProperty('teamStats', TeamStatsModel())
        self._addViewModelProperty('progress', FunRandomProgressModel())
        self._addArrayProperty('efficiency', Array())
        self._addArrayProperty('rewards', Array())
        self.onClose = self._addCommand('onClose')
        self.onTabChanged = self._addCommand('onTabChanged')
