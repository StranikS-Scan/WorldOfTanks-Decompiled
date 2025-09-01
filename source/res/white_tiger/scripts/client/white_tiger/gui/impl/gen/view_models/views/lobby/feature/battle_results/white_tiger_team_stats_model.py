# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/feature/battle_results/white_tiger_team_stats_model.py
from frameworks.wulf import Array
from white_tiger.gui.impl.gen.view_models.views.lobby.feature.battle_results.white_tiger_player_model import WhiteTigerPlayerModel
from gui.impl.gen.view_models.views.lobby.battle_results.team_stats_model import TeamStatsModel

class WhiteTigerTeamStatsModel(TeamStatsModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=1):
        super(WhiteTigerTeamStatsModel, self).__init__(properties=properties, commands=commands)

    def getAllies(self):
        return self._getArray(5)

    def setAllies(self, value):
        self._setArray(5, value)

    @staticmethod
    def getAlliesType():
        return WhiteTigerPlayerModel

    def getEnemies(self):
        return self._getArray(6)

    def setEnemies(self, value):
        self._setArray(6, value)

    @staticmethod
    def getEnemiesType():
        return WhiteTigerPlayerModel

    def getIsSingleTeamPostbattle(self):
        return self._getBool(7)

    def setIsSingleTeamPostbattle(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(WhiteTigerTeamStatsModel, self)._initialize()
        self._addArrayProperty('allies', Array())
        self._addArrayProperty('enemies', Array())
        self._addBoolProperty('isSingleTeamPostbattle', False)
