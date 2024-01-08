# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/meta_view/root_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.pages.leaderboard_model import LeaderboardModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.pages.progression_model import ProgressionModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.pages.rank_rewards_model import RankRewardsModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.pages.shop_model import ShopModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.pages.weekly_quests_model import WeeklyQuestsModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.pages.yearly_rewards_model import YearlyRewardsModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.pages.yearly_statistics_model import YearlyStatisticsModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.sidebar_model import SidebarModel
from gui.impl.gen.view_models.views.lobby.comp7.schedule_info_model import ScheduleInfoModel

class MetaRootViews(IntEnum):
    PROGRESSION = 0
    RANKREWARDS = 1
    YEARLYREWARDS = 2
    WEEKLYQUESTS = 3
    SHOP = 4
    LEADERBOARD = 5
    YEARLYSTATISTICS = 6


class RootViewModel(ViewModel):
    __slots__ = ('onClose', 'onInfoPageOpen', 'onWhatsNewScreenOpen')

    def __init__(self, properties=10, commands=3):
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

    def getPageViewId(self):
        return MetaRootViews(self._getNumber(9))

    def setPageViewId(self, value):
        self._setNumber(9, value.value)

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
        self._addNumberProperty('pageViewId')
        self.onClose = self._addCommand('onClose')
        self.onInfoPageOpen = self._addCommand('onInfoPageOpen')
        self.onWhatsNewScreenOpen = self._addCommand('onWhatsNewScreenOpen')
