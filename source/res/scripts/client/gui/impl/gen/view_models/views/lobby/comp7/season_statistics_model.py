# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/season_statistics_model.py
from enum import Enum, IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.comp7.summary_statistics_model import SummaryStatisticsModel
from gui.impl.gen.view_models.views.lobby.comp7.vehicle_statistics_model import VehicleStatisticsModel

class Rank(IntEnum):
    FIRST = 6
    SECOND = 5
    THIRD = 4
    FOURTH = 3
    FIFTH = 2
    SIXTH = 1


class SeasonName(Enum):
    FIRST = 'first'
    SECOND = 'second'
    THIRD = 'third'


class Division(IntEnum):
    A = 1
    B = 2
    C = 3
    D = 4
    E = 5


class SeasonPointState(Enum):
    ACHIEVED = 'achieved'
    NOTACHIEVED = 'notAchieved'


class SeasonStatisticsModel(ViewModel):
    __slots__ = ('onClose',)
    DEFAULT_POSITION = -1

    def __init__(self, properties=11, commands=1):
        super(SeasonStatisticsModel, self).__init__(properties=properties, commands=commands)

    def getSeason(self):
        return SeasonName(self._getString(0))

    def setSeason(self, value):
        self._setString(0, value.value)

    def getUserName(self):
        return self._getString(1)

    def setUserName(self, value):
        self._setString(1, value)

    def getClanTag(self):
        return self._getString(2)

    def setClanTag(self, value):
        self._setString(2, value)

    def getClanTagColor(self):
        return self._getString(3)

    def setClanTagColor(self, value):
        self._setString(3, value)

    def getScore(self):
        return self._getNumber(4)

    def setScore(self, value):
        self._setNumber(4, value)

    def getRank(self):
        return Rank(self._getNumber(5))

    def setRank(self, value):
        self._setNumber(5, value.value)

    def getDivision(self):
        return Division(self._getNumber(6))

    def setDivision(self, value):
        self._setNumber(6, value.value)

    def getLeaderboardPosition(self):
        return self._getNumber(7)

    def setLeaderboardPosition(self, value):
        self._setNumber(7, value)

    def getSeasonPoints(self):
        return self._getArray(8)

    def setSeasonPoints(self, value):
        self._setArray(8, value)

    @staticmethod
    def getSeasonPointsType():
        return SeasonPointState

    def getSummaryStatistics(self):
        return self._getArray(9)

    def setSummaryStatistics(self, value):
        self._setArray(9, value)

    @staticmethod
    def getSummaryStatisticsType():
        return SummaryStatisticsModel

    def getVehicleStatistics(self):
        return self._getArray(10)

    def setVehicleStatistics(self, value):
        self._setArray(10, value)

    @staticmethod
    def getVehicleStatisticsType():
        return VehicleStatisticsModel

    def _initialize(self):
        super(SeasonStatisticsModel, self)._initialize()
        self._addStringProperty('season')
        self._addStringProperty('userName', '')
        self._addStringProperty('clanTag', '')
        self._addStringProperty('clanTagColor', '')
        self._addNumberProperty('score', 0)
        self._addNumberProperty('rank')
        self._addNumberProperty('division')
        self._addNumberProperty('leaderboardPosition', -1)
        self._addArrayProperty('seasonPoints', Array())
        self._addArrayProperty('summaryStatistics', Array())
        self._addArrayProperty('vehicleStatistics', Array())
        self.onClose = self._addCommand('onClose')
