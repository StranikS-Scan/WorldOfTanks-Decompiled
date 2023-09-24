# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/vehicle_statistics_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel

class VehicleStatisticsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(VehicleStatisticsModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleInfoType():
        return VehicleModel

    def getBattles(self):
        return self._getNumber(1)

    def setBattles(self, value):
        self._setNumber(1, value)

    def getWinsPercent(self):
        return self._getReal(2)

    def setWinsPercent(self, value):
        self._setReal(2, value)

    def _initialize(self):
        super(VehicleStatisticsModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleModel())
        self._addNumberProperty('battles', 0)
        self._addRealProperty('winsPercent', 0.0)
