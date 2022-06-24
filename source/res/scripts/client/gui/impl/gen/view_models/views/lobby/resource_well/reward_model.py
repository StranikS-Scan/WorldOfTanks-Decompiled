# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/resource_well/reward_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel

class RewardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(RewardModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleInfoType():
        return VehicleInfoModel

    def getIsTop(self):
        return self._getBool(1)

    def setIsTop(self, value):
        self._setBool(1, value)

    def getVehiclesLeftCount(self):
        return self._getNumber(2)

    def setVehiclesLeftCount(self, value):
        self._setNumber(2, value)

    def getIsEnabled(self):
        return self._getBool(3)

    def setIsEnabled(self, value):
        self._setBool(3, value)

    def getIsCountAvailable(self):
        return self._getBool(4)

    def setIsCountAvailable(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(RewardModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleInfoModel())
        self._addBoolProperty('isTop', False)
        self._addNumberProperty('vehiclesLeftCount', 0)
        self._addBoolProperty('isEnabled', False)
        self._addBoolProperty('isCountAvailable', False)
