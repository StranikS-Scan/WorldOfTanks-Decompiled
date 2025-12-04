# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/leaderboard/ny_leaderboard_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.leaderboard.ny_personalPoints_model import NyPersonalpointsModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.leaderboard.ny_player_model import NyPlayerModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.leaderboard.ny_tabs_model import NyTabsModel

class State(Enum):
    INITIAL = 'initial'
    SUCCESS = 'success'
    ERROR = 'error'
    RECALC = 'Recalc'


class LastAction(Enum):
    PAGE = 'page'
    TOP = 'top'
    PLAYER = 'player'


class NyLeaderboardModel(ViewModel):
    __slots__ = ('onClose', 'onInfoClick', 'onRewardsClick', 'onPersonalPositionClick', 'onRefresh', 'onPageClick', 'onTopClick')

    def __init__(self, properties=19, commands=7):
        super(NyLeaderboardModel, self).__init__(properties=properties, commands=commands)

    @property
    def selfRank(self):
        return self._getViewModel(0)

    @staticmethod
    def getSelfRankType():
        return NyPlayerModel

    @property
    def personalPoints(self):
        return self._getViewModel(1)

    @staticmethod
    def getPersonalPointsType():
        return NyPersonalpointsModel

    def getState(self):
        return State(self._getString(2))

    def setState(self, value):
        self._setString(2, value.value)

    def getLastAction(self):
        return LastAction(self._getString(3))

    def setLastAction(self, value):
        self._setString(3, value.value)

    def getIsLoading(self):
        return self._getBool(4)

    def setIsLoading(self, value):
        self._setBool(4, value)

    def getFromTimestamp(self):
        return self._getNumber(5)

    def setFromTimestamp(self, value):
        self._setNumber(5, value)

    def getToTimestamp(self):
        return self._getNumber(6)

    def setToTimestamp(self, value):
        self._setNumber(6, value)

    def getUpdatedTimestamp(self):
        return self._getNumber(7)

    def setUpdatedTimestamp(self, value):
        self._setNumber(7, value)

    def getStage(self):
        return self._getNumber(8)

    def setStage(self, value):
        self._setNumber(8, value)

    def getTop(self):
        return self._getNumber(9)

    def setTop(self, value):
        self._setNumber(9, value)

    def getPointsToTop(self):
        return self._getNumber(10)

    def setPointsToTop(self, value):
        self._setNumber(10, value)

    def getCurrentTab(self):
        return self._getNumber(11)

    def setCurrentTab(self, value):
        self._setNumber(11, value)

    def getPagesCount(self):
        return self._getNumber(12)

    def setPagesCount(self, value):
        self._setNumber(12, value)

    def getCurrentPage(self):
        return self._getNumber(13)

    def setCurrentPage(self, value):
        self._setNumber(13, value)

    def getIsRewardsCheck(self):
        return self._getBool(14)

    def setIsRewardsCheck(self, value):
        self._setBool(14, value)

    def getIsVehicleAvailable(self):
        return self._getBool(15)

    def setIsVehicleAvailable(self, value):
        self._setBool(15, value)

    def getIsFinal(self):
        return self._getBool(16)

    def setIsFinal(self, value):
        self._setBool(16, value)

    def getPlayers(self):
        return self._getArray(17)

    def setPlayers(self, value):
        self._setArray(17, value)

    @staticmethod
    def getPlayersType():
        return NyPlayerModel

    def getTabs(self):
        return self._getArray(18)

    def setTabs(self, value):
        self._setArray(18, value)

    @staticmethod
    def getTabsType():
        return NyTabsModel

    def _initialize(self):
        super(NyLeaderboardModel, self)._initialize()
        self._addViewModelProperty('selfRank', NyPlayerModel())
        self._addViewModelProperty('personalPoints', NyPersonalpointsModel())
        self._addStringProperty('state')
        self._addStringProperty('lastAction')
        self._addBoolProperty('isLoading', False)
        self._addNumberProperty('fromTimestamp', 0)
        self._addNumberProperty('toTimestamp', 0)
        self._addNumberProperty('updatedTimestamp', 0)
        self._addNumberProperty('stage', 0)
        self._addNumberProperty('top', 0)
        self._addNumberProperty('pointsToTop', 0)
        self._addNumberProperty('currentTab', 1)
        self._addNumberProperty('pagesCount', 0)
        self._addNumberProperty('currentPage', 0)
        self._addBoolProperty('isRewardsCheck', False)
        self._addBoolProperty('isVehicleAvailable', False)
        self._addBoolProperty('isFinal', False)
        self._addArrayProperty('players', Array())
        self._addArrayProperty('tabs', Array())
        self.onClose = self._addCommand('onClose')
        self.onInfoClick = self._addCommand('onInfoClick')
        self.onRewardsClick = self._addCommand('onRewardsClick')
        self.onPersonalPositionClick = self._addCommand('onPersonalPositionClick')
        self.onRefresh = self._addCommand('onRefresh')
        self.onPageClick = self._addCommand('onPageClick')
        self.onTopClick = self._addCommand('onTopClick')
