# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/gen/view_models/views/lobby/post_battle_results_view/vehicle_stats_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.battle_results.detailed_stats_parameter_model import DetailedStatsParameterModel
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel

class VehicleStatsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
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

    def getDetailedStatistics(self):
        return self._getArray(2)

    def setDetailedStatistics(self, value):
        self._setArray(2, value)

    @staticmethod
    def getDetailedStatisticsType():
        return DetailedStatsParameterModel

    def _initialize(self):
        super(VehicleStatsModel, self)._initialize()
        self._addViewModelProperty('vehicle', VehicleModel())
        self._addBoolProperty('isGeneralInfo', False)
        self._addArrayProperty('detailedStatistics', Array())
