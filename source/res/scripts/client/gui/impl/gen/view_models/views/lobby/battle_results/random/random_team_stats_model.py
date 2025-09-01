# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/random/random_team_stats_model.py
from enum import Enum
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.battle_results.random.random_player_model import RandomPlayerModel
from gui.impl.gen.view_models.views.lobby.battle_results.team_stats_model import TeamStatsModel

class RandomColumnType(Enum):
    SQUAD = 'squad'
    PLAYER = 'player'
    DAMAGE = 'damage'
    FRAG = 'frag'
    XP = 'xp'
    VEHICLE = 'tank'
    MEDAL = 'medal'


class RandomTeamStatsModel(TeamStatsModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=1):
        super(RandomTeamStatsModel, self).__init__(properties=properties, commands=commands)

    def getAllies(self):
        return self._getArray(5)

    def setAllies(self, value):
        self._setArray(5, value)

    @staticmethod
    def getAlliesType():
        return RandomPlayerModel

    def getEnemies(self):
        return self._getArray(6)

    def setEnemies(self, value):
        self._setArray(6, value)

    @staticmethod
    def getEnemiesType():
        return RandomPlayerModel

    def getSortingColumn(self):
        return RandomColumnType(self._getString(7))

    def setSortingColumn(self, value):
        self._setString(7, value.value)

    def _initialize(self):
        super(RandomTeamStatsModel, self)._initialize()
        self._addArrayProperty('allies', Array())
        self._addArrayProperty('enemies', Array())
        self._addStringProperty('sortingColumn', RandomColumnType.PLAYER.value)
