# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/gen/view_models/views/lobby/post_battle_results_view/player_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.common.account_model import AccountModel
from fort_rush.gui.impl.gen.view_models.views.lobby.post_battle_results_view.fort_rush_stats_efficiency_model import FortRushStatsEfficiencyModel
from fort_rush.gui.impl.gen.view_models.views.lobby.post_battle_results_view.vehicle_stats_model import VehicleStatsModel

class PlayerModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
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
        return FortRushStatsEfficiencyModel

    def getIsPersonal(self):
        return self._getBool(2)

    def setIsPersonal(self, value):
        self._setBool(2, value)

    def getPlayerIndex(self):
        return self._getNumber(3)

    def setPlayerIndex(self, value):
        self._setNumber(3, value)

    def getDatabaseID(self):
        return self._getNumber(4)

    def setDatabaseID(self, value):
        self._setNumber(4, value)

    def getSquadIndex(self):
        return self._getNumber(5)

    def setSquadIndex(self, value):
        self._setNumber(5, value)

    def getVehiclesStats(self):
        return self._getArray(6)

    def setVehiclesStats(self, value):
        self._setArray(6, value)

    @staticmethod
    def getVehiclesStatsType():
        return VehicleStatsModel

    def _initialize(self):
        super(PlayerModel, self)._initialize()
        self._addViewModelProperty('userNames', AccountModel())
        self._addViewModelProperty('efficiencyValues', FortRushStatsEfficiencyModel())
        self._addBoolProperty('isPersonal', False)
        self._addNumberProperty('playerIndex', 0)
        self._addNumberProperty('databaseID', 0)
        self._addNumberProperty('squadIndex', 0)
        self._addArrayProperty('vehiclesStats', Array())
