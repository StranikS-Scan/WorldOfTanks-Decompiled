# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/meta_view/root_view_model.py
from comp7.gui.impl.gen.view_models.views.lobby.enums import MetaRootViews
from frameworks.wulf import ViewModel
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.claim_rewards_model import ClaimRewardsModel
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.pages.leaderboard_model import LeaderboardModel
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.pages.progression_model import ProgressionModel
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.pages.rank_rewards_model import RankRewardsModel
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.pages.shop_model import ShopModel
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.pages.weekly_quests_model import WeeklyQuestsModel
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.pages.yearly_rewards_model import YearlyRewardsModel
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.pages.yearly_statistics_model import YearlyStatisticsModel
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.sidebar_model import SidebarModel
from comp7.gui.impl.gen.view_models.views.lobby.schedule_info_model import ScheduleInfoModel

class RootViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=11, commands=1):
        super(RootViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def sidebar(self):
        return self._getViewModel(0)

    @staticmethod
    def getSidebarType():
        return SidebarModel

    @property
    def scheduleInfo(self):
        return self._getViewModel(1)

    @staticmethod
    def getScheduleInfoType():
        return ScheduleInfoModel

    @property
    def progressionModel(self):
        return self._getViewModel(2)

    @staticmethod
    def getProgressionModelType():
        return ProgressionModel

    @property
    def rankRewardsModel(self):
        return self._getViewModel(3)

    @staticmethod
    def getRankRewardsModelType():
        return RankRewardsModel

    @property
    def weeklyQuestsModel(self):
        return self._getViewModel(4)

    @staticmethod
    def getWeeklyQuestsModelType():
        return WeeklyQuestsModel

    @property
    def leaderboardModel(self):
        return self._getViewModel(5)

    @staticmethod
    def getLeaderboardModelType():
        return LeaderboardModel

    @property
    def yearlyRewardsModel(self):
        return self._getViewModel(6)

    @staticmethod
    def getYearlyRewardsModelType():
        return YearlyRewardsModel

    @property
    def shopModel(self):
        return self._getViewModel(7)

    @staticmethod
    def getShopModelType():
        return ShopModel

    @property
    def yearlyStatisticsModel(self):
        return self._getViewModel(8)

    @staticmethod
    def getYearlyStatisticsModelType():
        return YearlyStatisticsModel

    @property
    def claimRewardsModel(self):
        return self._getViewModel(9)

    @staticmethod
    def getClaimRewardsModelType():
        return ClaimRewardsModel

    def getPageViewId(self):
        return MetaRootViews(self._getNumber(10))

    def setPageViewId(self, value):
        self._setNumber(10, value.value)

    def _initialize(self):
        super(RootViewModel, self)._initialize()
        self._addViewModelProperty('sidebar', SidebarModel())
        self._addViewModelProperty('scheduleInfo', ScheduleInfoModel())
        self._addViewModelProperty('progressionModel', ProgressionModel())
        self._addViewModelProperty('rankRewardsModel', RankRewardsModel())
        self._addViewModelProperty('weeklyQuestsModel', WeeklyQuestsModel())
        self._addViewModelProperty('leaderboardModel', LeaderboardModel())
        self._addViewModelProperty('yearlyRewardsModel', YearlyRewardsModel())
        self._addViewModelProperty('shopModel', ShopModel())
        self._addViewModelProperty('yearlyStatisticsModel', YearlyStatisticsModel())
        self._addViewModelProperty('claimRewardsModel', ClaimRewardsModel())
        self._addNumberProperty('pageViewId')
        self.onClose = self._addCommand('onClose')
