# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/tournaments/tournament_view_model.py
from enum import Enum
from frameworks.wulf import Array, ViewModel
from comp7.gui.impl.gen.view_models.views.lobby.tournaments.match_model import MatchModel
from comp7.gui.impl.gen.view_models.views.lobby.tournaments.team_model import TeamModel

class OverviewState(Enum):
    SCHEDULE = 'schedule'
    LIVE = 'live'
    FINALRESULT = 'finalResult'
    ERROR = 'error'


class Streaming(Enum):
    TWITCH = 'twitch'
    HUYA = 'huya'
    YOUTUBE = 'youtube'
    DOUYIN = 'douyin'


class PageState(Enum):
    LOADING = 'loading'
    CONTENT = 'content'


class TournamentViewModel(ViewModel):
    __slots__ = ('onWatchStreamingOne', 'onWatchStreamingTwo', 'onGoToShop', 'onGoToTokenStore', 'onRefresh', 'onClose')

    def __init__(self, properties=8, commands=6):
        super(TournamentViewModel, self).__init__(properties=properties, commands=commands)

    def getOverviewState(self):
        return OverviewState(self._getString(0))

    def setOverviewState(self, value):
        self._setString(0, value.value)

    def getPageState(self):
        return PageState(self._getString(1))

    def setPageState(self, value):
        self._setString(1, value.value)

    def getPrizeFund(self):
        return self._getNumber(2)

    def setPrizeFund(self, value):
        self._setNumber(2, value)

    def getIsRefreshing(self):
        return self._getBool(3)

    def setIsRefreshing(self, value):
        self._setBool(3, value)

    def getSchedule(self):
        return self._getArray(4)

    def setSchedule(self, value):
        self._setArray(4, value)

    @staticmethod
    def getScheduleType():
        return MatchModel

    def getFundDistribution(self):
        return self._getArray(5)

    def setFundDistribution(self, value):
        self._setArray(5, value)

    @staticmethod
    def getFundDistributionType():
        return TeamModel

    def getStreamingWithDrops(self):
        return Streaming(self._getString(6))

    def setStreamingWithDrops(self, value):
        self._setString(6, value.value)

    def getStreamingWithoutDrops(self):
        return Streaming(self._getString(7))

    def setStreamingWithoutDrops(self, value):
        self._setString(7, value.value)

    def _initialize(self):
        super(TournamentViewModel, self)._initialize()
        self._addStringProperty('overviewState')
        self._addStringProperty('pageState')
        self._addNumberProperty('prizeFund', 0)
        self._addBoolProperty('isRefreshing', False)
        self._addArrayProperty('schedule', Array())
        self._addArrayProperty('fundDistribution', Array())
        self._addStringProperty('streamingWithDrops')
        self._addStringProperty('streamingWithoutDrops')
        self.onWatchStreamingOne = self._addCommand('onWatchStreamingOne')
        self.onWatchStreamingTwo = self._addCommand('onWatchStreamingTwo')
        self.onGoToShop = self._addCommand('onGoToShop')
        self.onGoToTokenStore = self._addCommand('onGoToTokenStore')
        self.onRefresh = self._addCommand('onRefresh')
        self.onClose = self._addCommand('onClose')
