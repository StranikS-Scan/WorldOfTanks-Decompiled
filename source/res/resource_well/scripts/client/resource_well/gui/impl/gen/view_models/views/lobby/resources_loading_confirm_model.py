# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/impl/gen/view_models/views/lobby/resources_loading_confirm_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from resource_well.gui.impl.gen.view_models.views.lobby.loading_resource_model import LoadingResourceModel
from resource_well.gui.impl.gen.view_models.views.lobby.vehicle_counter_model import VehicleCounterModel

class OperationType(IntEnum):
    RETURN = 0
    CONTRIBUTE = 1
    SWITCH = 2


class ResourcesLoadingConfirmModel(ViewModel):
    __slots__ = ('confirm', 'cancel', 'close')

    def __init__(self, properties=5, commands=3):
        super(ResourcesLoadingConfirmModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleCounter(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleCounterType():
        return VehicleCounterModel

    def getOperationType(self):
        return OperationType(self._getNumber(1))

    def setOperationType(self, value):
        self._setNumber(1, value.value)

    def getProgressDiff(self):
        return self._getNumber(2)

    def setProgressDiff(self, value):
        self._setNumber(2, value)

    def getVehicleName(self):
        return self._getString(3)

    def setVehicleName(self, value):
        self._setString(3, value)

    def getResources(self):
        return self._getArray(4)

    def setResources(self, value):
        self._setArray(4, value)

    @staticmethod
    def getResourcesType():
        return LoadingResourceModel

    def _initialize(self):
        super(ResourcesLoadingConfirmModel, self)._initialize()
        self._addViewModelProperty('vehicleCounter', VehicleCounterModel())
        self._addNumberProperty('operationType')
        self._addNumberProperty('progressDiff', 0)
        self._addStringProperty('vehicleName', '')
        self._addArrayProperty('resources', Array())
        self.confirm = self._addCommand('confirm')
        self.cancel = self._addCommand('cancel')
        self.close = self._addCommand('close')
