# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/views/post_battle_results_view/player_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.common.account_model import AccountModel
from frontline.gui.impl.gen.view_models.views.lobby.views.post_battle_results_view.achievement_model import AchievementModel
from frontline.gui.impl.gen.view_models.views.lobby.views.post_battle_results_view.vehicle_stats_model import VehicleStatsModel
from gui.impl.gen.view_models.views.lobby.battle_results.stats_efficiency_model import StatsEfficiencyModel

class PlayerModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
        super(PlayerModel, self).__init__(properties=properties, commands=commands)

    @property
    def userNames(self):
        return self._getViewModel(0)

    @staticmethod
    def getUserNamesType():
        return AccountModel

    @property
    def efficiencyValues(self):
        return self._getViewModel(1)

    @staticmethod
    def getEfficiencyValuesType():
        return StatsEfficiencyModel

    def getPrebattleID(self):
        return self._getNumber(2)

    def setPrebattleID(self, value):
        self._setNumber(2, value)

    def getIsPersonal(self):
        return self._getBool(3)

    def setIsPersonal(self, value):
        self._setBool(3, value)

    def getPlayerIndex(self):
        return self._getNumber(4)

    def setPlayerIndex(self, value):
        self._setNumber(4, value)

    def getDatabaseID(self):
        return self._getNumber(5)

    def setDatabaseID(self, value):
        self._setNumber(5, value)

    def getSquadIndex(self):
        return self._getNumber(6)

    def setSquadIndex(self, value):
        self._setNumber(6, value)

    def getRank(self):
        return self._getNumber(7)

    def setRank(self, value):
        self._setNumber(7, value)

    def getRespawns(self):
        return self._getNumber(8)

    def setRespawns(self, value):
        self._setNumber(8, value)

    def getAchievements(self):
        return self._getArray(9)

    def setAchievements(self, value):
        self._setArray(9, value)

    @staticmethod
    def getAchievementsType():
        return AchievementModel

    def getVehiclesStats(self):
        return self._getArray(10)

    def setVehiclesStats(self, value):
        self._setArray(10, value)

    @staticmethod
    def getVehiclesStatsType():
        return VehicleStatsModel

    def _initialize(self):
        super(PlayerModel, self)._initialize()
        self._addViewModelProperty('userNames', AccountModel())
        self._addViewModelProperty('efficiencyValues', StatsEfficiencyModel())
        self._addNumberProperty('prebattleID', 0)
        self._addBoolProperty('isPersonal', False)
        self._addNumberProperty('playerIndex', 0)
        self._addNumberProperty('databaseID', 0)
        self._addNumberProperty('squadIndex', 0)
        self._addNumberProperty('rank', 1)
        self._addNumberProperty('respawns', 0)
        self._addArrayProperty('achievements', Array())
        self._addArrayProperty('vehiclesStats', Array())
