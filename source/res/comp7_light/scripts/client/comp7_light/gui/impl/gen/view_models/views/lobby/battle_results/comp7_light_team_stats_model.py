# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/gen/view_models/views/lobby/battle_results/comp7_light_team_stats_model.py
from enum import Enum
from frameworks.wulf import Array
from comp7_light.gui.impl.gen.view_models.views.lobby.battle_results.comp7_light_player_model import Comp7LightPlayerModel
from gui.impl.gen.view_models.views.lobby.battle_results.team_stats_model import TeamStatsModel

class Comp7LightColumnType(Enum):
    SQUAD = 'squad'
    PLAYER = 'player'
    DAMAGE = 'damage'
    FRAG = 'frag'
    XP = 'xp'
    VEHICLE = 'tank'
    MEDAL = 'medal'
    PRESTIGEPOINTS = 'prestigePoints'


class Comp7LightTeamStatsModel(TeamStatsModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=1):
        super(Comp7LightTeamStatsModel, self).__init__(properties=properties, commands=commands)

    def getAllies(self):
        return self._getArray(5)

    def setAllies(self, value):
        self._setArray(5, value)

    @staticmethod
    def getAlliesType():
        return Comp7LightPlayerModel

    def getEnemies(self):
        return self._getArray(6)

    def setEnemies(self, value):
        self._setArray(6, value)

    @staticmethod
    def getEnemiesType():
        return Comp7LightPlayerModel

    def getSortingColumn(self):
        return Comp7LightColumnType(self._getString(7))

    def setSortingColumn(self, value):
        self._setString(7, value.value)

    def _initialize(self):
        super(Comp7LightTeamStatsModel, self)._initialize()
        self._addArrayProperty('allies', Array())
        self._addArrayProperty('enemies', Array())
        self._addStringProperty('sortingColumn', Comp7LightColumnType.PLAYER.value)
