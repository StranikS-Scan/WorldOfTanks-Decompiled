# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/feature/battle_results/white_tiger_results_view_model.py
from enum import Enum, IntEnum
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.common.user_name_model import UserNameModel
from white_tiger.gui.impl.gen.view_models.views.lobby.feature.battle_results.simplified_quests_view_model import SimplifiedQuestsViewModel
from white_tiger.gui.impl.gen.view_models.views.lobby.feature.battle_results.white_tiger_battle_info_model import WhiteTigerBattleInfoModel
from white_tiger.gui.impl.gen.view_models.views.lobby.feature.battle_results.white_tiger_progress_model import WhiteTigerProgressModel
from white_tiger.gui.impl.gen.view_models.views.lobby.feature.battle_results.white_tiger_team_stats_model import WhiteTigerTeamStatsModel
from gui.impl.gen.view_models.views.lobby.battle_results.personal_efficiency_model import PersonalEfficiencyModel
from gui.impl.gen.view_models.views.lobby.battle_results.premium_plus_model import PremiumPlusModel
from gui.impl.gen.view_models.views.lobby.battle_results.user_status_model import UserStatusModel

class Tab(IntEnum):
    PERSONAL = 1
    TEAMSTATS = 2


class TankTypeEnum(Enum):
    HUNTER = 'wt_hunter'
    BOSS = 'wt_boss'
    SPECIALBOSS = 'wt_special_boss'


class WhiteTigerResultsViewModel(ViewModel):
    __slots__ = ('onClose', 'onTabChanged')

    def __init__(self, properties=11, commands=2):
        super(WhiteTigerResultsViewModel, self).__init__(properties=properties, commands=commands)

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
        return WhiteTigerBattleInfoModel

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
        return WhiteTigerTeamStatsModel

    @property
    def progress(self):
        return self._getViewModel(5)

    @staticmethod
    def getProgressType():
        return WhiteTigerProgressModel

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
        return BonusModel

    def getHarrierQuests(self):
        return self._getArray(8)

    def setHarrierQuests(self, value):
        self._setArray(8, value)

    @staticmethod
    def getHarrierQuestsType():
        return SimplifiedQuestsViewModel

    def getEngineerQuests(self):
        return self._getArray(9)

    def setEngineerQuests(self, value):
        self._setArray(9, value)

    @staticmethod
    def getEngineerQuestsType():
        return SimplifiedQuestsViewModel

    def getTankType(self):
        return TankTypeEnum(self._getString(10))

    def setTankType(self, value):
        self._setString(10, value.value)

    def _initialize(self):
        super(WhiteTigerResultsViewModel, self)._initialize()
        self._addViewModelProperty('userNames', UserNameModel())
        self._addViewModelProperty('userStatus', UserStatusModel())
        self._addViewModelProperty('battleInfo', WhiteTigerBattleInfoModel())
        self._addViewModelProperty('premiumPlus', PremiumPlusModel())
        self._addViewModelProperty('teamStats', WhiteTigerTeamStatsModel())
        self._addViewModelProperty('progress', WhiteTigerProgressModel())
        self._addArrayProperty('efficiency', Array())
        self._addArrayProperty('rewards', Array())
        self._addArrayProperty('harrierQuests', Array())
        self._addArrayProperty('engineerQuests', Array())
        self._addStringProperty('tankType')
        self.onClose = self._addCommand('onClose')
        self.onTabChanged = self._addCommand('onTabChanged')
