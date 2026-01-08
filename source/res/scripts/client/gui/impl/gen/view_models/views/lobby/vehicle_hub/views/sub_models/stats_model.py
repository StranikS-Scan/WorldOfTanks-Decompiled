# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_hub/views/sub_models/stats_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.common.vehicle_mechanic_model import VehicleMechanicModel
from gui.impl.gen.view_models.views.lobby.vehicle_hub.special_vehicle_param_model import SpecialVehicleParamModel

class StatsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(StatsModel, self).__init__(properties=properties, commands=commands)

    @property
    def specialMechanic(self):
        return self._getViewModel(0)

    @staticmethod
    def getSpecialMechanicType():
        return VehicleMechanicModel

    def getSpecialMechanicParams(self):
        return self._getArray(1)

    def setSpecialMechanicParams(self, value):
        self._setArray(1, value)

    @staticmethod
    def getSpecialMechanicParamsType():
        return SpecialVehicleParamModel

    def _initialize(self):
        super(StatsModel, self)._initialize()
        self._addViewModelProperty('specialMechanic', VehicleMechanicModel())
        self._addArrayProperty('specialMechanicParams', Array())
