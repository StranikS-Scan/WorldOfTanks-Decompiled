# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/team_stats_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.battle_results.player_model import PlayerModel

class ColumnType(Enum):
    SQUAD = 'squad'
    PLAYER = 'player'
    DAMAGE = 'damage'
    FRAG = 'frag'
    XP = 'xp'
    VEHICLE = 'tank'


class SortingOrder(Enum):
    ASC = 'ascending'
    DESC = 'descending'


class TeamStatsModel(ViewModel):
    __slots__ = ('onStatsSorted',)

    def __init__(self, properties=5, commands=1):
        super(TeamStatsModel, self).__init__(properties=properties, commands=commands)

    def getAllies(self):
        return self._getArray(0)

    def setAllies(self, value):
        self._setArray(0, value)

    @staticmethod
    def getAlliesType():
        return PlayerModel

    def getEnemies(self):
        return self._getArray(1)

    def setEnemies(self, value):
        self._setArray(1, value)

    @staticmethod
    def getEnemiesType():
        return PlayerModel

    def getShownValueColumns(self):
        return self._getArray(2)

    def setShownValueColumns(self, value):
        self._setArray(2, value)

    @staticmethod
    def getShownValueColumnsType():
        return ColumnType

    def getSortingColumn(self):
        return ColumnType(self._getString(3))

    def setSortingColumn(self, value):
        self._setString(3, value.value)

    def getSortingOrder(self):
        return SortingOrder(self._getString(4))

    def setSortingOrder(self, value):
        self._setString(4, value.value)

    def _initialize(self):
        super(TeamStatsModel, self)._initialize()
        self._addArrayProperty('allies', Array())
        self._addArrayProperty('enemies', Array())
        self._addArrayProperty('shownValueColumns', Array())
        self._addStringProperty('sortingColumn', ColumnType.XP.value)
        self._addStringProperty('sortingOrder', SortingOrder.DESC.value)
        self.onStatsSorted = self._addCommand('onStatsSorted')
