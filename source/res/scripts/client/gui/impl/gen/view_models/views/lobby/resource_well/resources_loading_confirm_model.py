# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/resource_well/resources_loading_confirm_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.resource_well.loading_resource_model import LoadingResourceModel
from gui.impl.gen.view_models.views.lobby.resource_well.vehicle_counter_model import VehicleCounterModel

class OperationType(IntEnum):
    RETURN = 0
    CONTRIBUTE = 1


class ResourcesLoadingConfirmModel(ViewModel):
    __slots__ = ('confirm', 'cancel', 'close')

    def __init__(self, properties=4, commands=3):
        super(ResourcesLoadingConfirmModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleCounter(self):
        return self._getViewModel(0)

    def getOperationType(self):
        return OperationType(self._getNumber(1))

    def setOperationType(self, value):
        self._setNumber(1, value.value)

    def getProgressDiff(self):
        return self._getNumber(2)

    def setProgressDiff(self, value):
        self._setNumber(2, value)

    def getResources(self):
        return self._getArray(3)

    def setResources(self, value):
        self._setArray(3, value)

    def _initialize(self):
        super(ResourcesLoadingConfirmModel, self)._initialize()
        self._addViewModelProperty('vehicleCounter', VehicleCounterModel())
        self._addNumberProperty('operationType')
        self._addNumberProperty('progressDiff', 0)
        self._addArrayProperty('resources', Array())
        self.confirm = self._addCommand('confirm')
        self.cancel = self._addCommand('cancel')
        self.close = self._addCommand('close')
