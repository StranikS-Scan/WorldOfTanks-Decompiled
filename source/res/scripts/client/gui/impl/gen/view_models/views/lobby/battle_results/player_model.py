# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/player_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.user_name_model import UserNameModel
from gui.impl.gen.view_models.views.lobby.battle_results.detailed_stats_parameter_model import DetailedStatsParameterModel
from gui.impl.gen.view_models.views.lobby.battle_results.stats_efficiency_model import StatsEfficiencyModel
from gui.impl.gen.view_models.views.lobby.battle_results.user_status_model import UserStatusModel
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel

class PlayerModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(PlayerModel, self).__init__(properties=properties, commands=commands)

    @property
    def userNames(self):
        return self._getViewModel(0)

    @staticmethod
    def getUserNamesType():
        return UserNameModel

    @property
    def vehicle(self):
        return self._getViewModel(1)

    @staticmethod
    def getVehicleType():
        return VehicleModel

    @property
    def userStatus(self):
        return self._getViewModel(2)

    @staticmethod
    def getUserStatusType():
        return UserStatusModel

    @property
    def efficiencyValues(self):
        return self._getViewModel(3)

    @staticmethod
    def getEfficiencyValuesType():
        return StatsEfficiencyModel

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

    def getIsPersonal(self):
        return self._getBool(7)

    def setIsPersonal(self, value):
        self._setBool(7, value)

    def getDetailedStatistics(self):
        return self._getArray(8)

    def setDetailedStatistics(self, value):
        self._setArray(8, value)

    @staticmethod
    def getDetailedStatisticsType():
        return DetailedStatsParameterModel

    def _initialize(self):
        super(PlayerModel, self)._initialize()
        self._addViewModelProperty('userNames', UserNameModel())
        self._addViewModelProperty('vehicle', VehicleModel())
        self._addViewModelProperty('userStatus', UserStatusModel())
        self._addViewModelProperty('efficiencyValues', StatsEfficiencyModel())
        self._addNumberProperty('playerIndex', 0)
        self._addNumberProperty('databaseID', 0)
        self._addNumberProperty('squadIndex', 0)
        self._addBoolProperty('isPersonal', False)
        self._addArrayProperty('detailedStatistics', Array())
