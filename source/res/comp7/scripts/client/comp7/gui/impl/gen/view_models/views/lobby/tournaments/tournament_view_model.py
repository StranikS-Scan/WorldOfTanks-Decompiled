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
    __slots__ = ('onWatchStreamingOne', 'onWatchStreamingTwo', 'onGoToShop', 'onGoToTokenStore', 'onRefresh', 'onClose', 'pollServerTime')

    def __init__(self, properties=12, commands=7):
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

    def getIsDynamicPrizePool(self):
        return self._getBool(3)

    def setIsDynamicPrizePool(self, value):
        self._setBool(3, value)

    def getLastPrizePoolUpdate(self):
        return self._getNumber(4)

    def setLastPrizePoolUpdate(self, value):
        self._setNumber(4, value)

    def getIsRefreshing(self):
        return self._getBool(5)

    def setIsRefreshing(self, value):
        self._setBool(5, value)

    def getTokenStoreAvailabilityTimestamp(self):
        return self._getNumber(6)

    def setTokenStoreAvailabilityTimestamp(self, value):
        self._setNumber(6, value)

    def getServerTimestamp(self):
        return self._getNumber(7)

    def setServerTimestamp(self, value):
        self._setNumber(7, value)

    def getSchedule(self):
        return self._getArray(8)

    def setSchedule(self, value):
        self._setArray(8, value)

    @staticmethod
    def getScheduleType():
        return MatchModel

    def getFundDistribution(self):
        return self._getArray(9)

    def setFundDistribution(self, value):
        self._setArray(9, value)

    @staticmethod
    def getFundDistributionType():
        return TeamModel

    def getStreamingWithDrops(self):
        return Streaming(self._getString(10))

    def setStreamingWithDrops(self, value):
        self._setString(10, value.value)

    def getStreamingWithoutDrops(self):
        return Streaming(self._getString(11))

    def setStreamingWithoutDrops(self, value):
        self._setString(11, value.value)

    def _initialize(self):
        super(TournamentViewModel, self)._initialize()
        self._addStringProperty('overviewState')
        self._addStringProperty('pageState')
        self._addNumberProperty('prizeFund', 0)
        self._addBoolProperty('isDynamicPrizePool', False)
        self._addNumberProperty('lastPrizePoolUpdate', 0)
        self._addBoolProperty('isRefreshing', False)
        self._addNumberProperty('tokenStoreAvailabilityTimestamp', 0)
        self._addNumberProperty('serverTimestamp', 0)
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
        self.pollServerTime = self._addCommand('pollServerTime')
