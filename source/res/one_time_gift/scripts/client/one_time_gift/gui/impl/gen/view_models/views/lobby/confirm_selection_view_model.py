# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/impl/gen/view_models/views/lobby/confirm_selection_view_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel

class ConfirmSelectionViewModel(ViewModel):
    __slots__ = ('onConfirm', 'onClose')

    def __init__(self, properties=3, commands=2):
        super(ConfirmSelectionViewModel, self).__init__(properties=properties, commands=commands)

    def getBranchName(self):
        return self._getString(0)

    def setBranchName(self, value):
        self._setString(0, value)

    def getCreditedVehicles(self):
        return self._getArray(1)

    def setCreditedVehicles(self, value):
        self._setArray(1, value)

    @staticmethod
    def getCreditedVehiclesType():
        return VehicleModel

    def getObtainedVehicles(self):
        return self._getArray(2)

    def setObtainedVehicles(self, value):
        self._setArray(2, value)

    @staticmethod
    def getObtainedVehiclesType():
        return VehicleModel

    def _initialize(self):
        super(ConfirmSelectionViewModel, self)._initialize()
        self._addStringProperty('branchName', '')
        self._addArrayProperty('creditedVehicles', Array())
        self._addArrayProperty('obtainedVehicles', Array())
        self.onConfirm = self._addCommand('onConfirm')
        self.onClose = self._addCommand('onClose')
