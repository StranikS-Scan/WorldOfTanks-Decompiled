# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/rts/leaderboard_view/leaderboard_view_model.py
from enum import Enum, IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.rts.leaderboard_view.leaderboard_error_view_model import LeaderboardErrorViewModel
from gui.impl.gen.view_models.views.lobby.rts.leaderboard_view.leaderboard_ranking_view_model import LeaderboardRankingViewModel
from gui.impl.gen.view_models.views.lobby.rts.leaderboard_view.leaderboard_rewards_view_model import LeaderboardRewardsViewModel

class LeaderboardType(Enum):
    STRATEGIST1X1 = 'type1x1'
    STRATEGIST1X7 = 'type1x7'
    TANKER = 'typeTanker'


class PlayerState(IntEnum):
    INBOARD = 0
    INSUFFICIENTBATTLES = 1
    NOTPARTICIPATED = 2


class LeaderboardViewModel(ViewModel):
    __slots__ = ('onLeaderboardTypeSelect', 'onPageClick', 'onRefreshClick')

    def __init__(self, properties=11, commands=3):
        super(LeaderboardViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def error(self):
        return self._getViewModel(0)

    @property
    def currentPlayerRanking(self):
        return self._getViewModel(1)

    @property
    def rewards(self):
        return self._getViewModel(2)

    def getLeaderboardType(self):
        return LeaderboardType(self._getString(3))

    def setLeaderboardType(self, value):
        self._setString(3, value.value)

    def getRankings(self):
        return self._getArray(4)

    def setRankings(self, value):
        self._setArray(4, value)

    def getLastUpdated(self):
        return self._getNumber(5)

    def setLastUpdated(self, value):
        self._setNumber(5, value)

    def getCurrentPage(self):
        return self._getNumber(6)

    def setCurrentPage(self, value):
        self._setNumber(6, value)

    def getTotalPages(self):
        return self._getNumber(7)

    def setTotalPages(self, value):
        self._setNumber(7, value)

    def getIsLoading(self):
        return self._getBool(8)

    def setIsLoading(self, value):
        self._setBool(8, value)

    def getCurrentPlayerState(self):
        return PlayerState(self._getNumber(9))

    def setCurrentPlayerState(self, value):
        self._setNumber(9, value.value)

    def getMinBattlesRequired(self):
        return self._getNumber(10)

    def setMinBattlesRequired(self, value):
        self._setNumber(10, value)

    def _initialize(self):
        super(LeaderboardViewModel, self)._initialize()
        self._addViewModelProperty('error', LeaderboardErrorViewModel())
        self._addViewModelProperty('currentPlayerRanking', LeaderboardRankingViewModel())
        self._addViewModelProperty('rewards', LeaderboardRewardsViewModel())
        self._addStringProperty('leaderboardType')
        self._addArrayProperty('rankings', Array())
        self._addNumberProperty('lastUpdated', 0)
        self._addNumberProperty('currentPage', 0)
        self._addNumberProperty('totalPages', 0)
        self._addBoolProperty('isLoading', False)
        self._addNumberProperty('currentPlayerState')
        self._addNumberProperty('minBattlesRequired', 0)
        self.onLeaderboardTypeSelect = self._addCommand('onLeaderboardTypeSelect')
        self.onPageClick = self._addCommand('onPageClick')
        self.onRefreshClick = self._addCommand('onRefreshClick')
