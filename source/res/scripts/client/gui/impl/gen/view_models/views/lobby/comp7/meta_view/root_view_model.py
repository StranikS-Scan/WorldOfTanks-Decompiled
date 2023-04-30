# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/meta_view/root_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.pages.leaderboard_model import LeaderboardModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.pages.progression_model import ProgressionModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.pages.rank_rewards_model import RankRewardsModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.pages.weekly_quests_model import WeeklyQuestsModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.sidebar_model import SidebarModel
from gui.impl.gen.view_models.views.lobby.comp7.schedule_info_model import ScheduleInfoModel

class MetaRootViews(IntEnum):
    PROGRESSION = 0
    RANKREWARDS = 1
    WEEKLYQUESTS = 2
    LEADERBOARD = 3


class RootViewModel(ViewModel):
    __slots__ = ('onClose', 'onInfoPageOpen')

    def __init__(self, properties=7, commands=2):
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

    def getViewType(self):
        return MetaRootViews(self._getNumber(6))

    def setViewType(self, value):
        self._setNumber(6, value.value)

    def _initialize(self):
        super(RootViewModel, self)._initialize()
        self._addViewModelProperty('sidebar', SidebarModel())
        self._addViewModelProperty('scheduleInfo', ScheduleInfoModel())
        self._addViewModelProperty('progressionModel', ProgressionModel())
        self._addViewModelProperty('rankRewardsModel', RankRewardsModel())
        self._addViewModelProperty('weeklyQuestsModel', WeeklyQuestsModel())
        self._addViewModelProperty('leaderboardModel', LeaderboardModel())
        self._addNumberProperty('viewType')
        self.onClose = self._addCommand('onClose')
        self.onInfoPageOpen = self._addCommand('onInfoPageOpen')
