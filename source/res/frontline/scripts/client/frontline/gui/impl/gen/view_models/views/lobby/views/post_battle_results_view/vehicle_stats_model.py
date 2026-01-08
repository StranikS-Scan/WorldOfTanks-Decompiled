# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/views/post_battle_results_view/vehicle_stats_model.py
from enum import Enum
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.battle_results.detailed_stats_parameter_model import DetailedStatsParameterModel
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel

class FrontlineParamType(Enum):
    ATKOBJECTIVES = 'atkObjectives'
    DEFOBJECTIVES = 'defObjectives'


class VehicleStatsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(VehicleStatsModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicle(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleType():
        return VehicleModel

    def getIsGeneralInfo(self):
        return self._getBool(1)

    def setIsGeneralInfo(self, value):
        self._setBool(1, value)

    def getObjectivesReached(self):
        return self._getBool(2)

    def setObjectivesReached(self, value):
        self._setBool(2, value)

    def getObjectivesDestroyed(self):
        return self._getNumber(3)

    def setObjectivesDestroyed(self, value):
        self._setNumber(3, value)

    def getZoneCaptured(self):
        return self._getNumber(4)

    def setZoneCaptured(self, value):
        self._setNumber(4, value)

    def getDetailedStatistics(self):
        return self._getArray(5)

    def setDetailedStatistics(self, value):
        self._setArray(5, value)

    @staticmethod
    def getDetailedStatisticsType():
        return DetailedStatsParameterModel

    def _initialize(self):
        super(VehicleStatsModel, self)._initialize()
        self._addViewModelProperty('vehicle', VehicleModel())
        self._addBoolProperty('isGeneralInfo', False)
        self._addBoolProperty('objectivesReached', False)
        self._addNumberProperty('objectivesDestroyed', 0)
        self._addNumberProperty('zoneCaptured', 0)
        self._addArrayProperty('detailedStatistics', Array())
