# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/rts/leaderboard_view/leaderboard_ranking_view_model.py
from frameworks.wulf import ViewModel

class LeaderboardRankingViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(LeaderboardRankingViewModel, self).__init__(properties=properties, commands=commands)

    def getRank(self):
        return self._getNumber(0)

    def setRank(self, value):
        self._setNumber(0, value)

    def getSpaId(self):
        return self._getNumber(1)

    def setSpaId(self, value):
        self._setNumber(1, value)

    def getUserName(self):
        return self._getString(2)

    def setUserName(self, value):
        self._setString(2, value)

    def getClanTag(self):
        return self._getString(3)

    def setClanTag(self, value):
        self._setString(3, value)

    def getClanColor(self):
        return self._getString(4)

    def setClanColor(self, value):
        self._setString(4, value)

    def getGamePoints(self):
        return self._getString(5)

    def setGamePoints(self, value):
        self._setString(5, value)

    def getAverageDamage(self):
        return self._getString(6)

    def setAverageDamage(self, value):
        self._setString(6, value)

    def _initialize(self):
        super(LeaderboardRankingViewModel, self)._initialize()
        self._addNumberProperty('rank', 0)
        self._addNumberProperty('spaId', 0)
        self._addStringProperty('userName', '')
        self._addStringProperty('clanTag', '')
        self._addStringProperty('clanColor', '')
        self._addStringProperty('gamePoints', '')
        self._addStringProperty('averageDamage', '')
