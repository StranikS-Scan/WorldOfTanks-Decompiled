# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/bm2021/dialogs/black_market_confirm_vehicle_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.vehicle_model import VehicleModel

class BlackMarketConfirmVehicleModel(ViewModel):
    __slots__ = ('onConfirm',)

    def __init__(self, properties=3, commands=1):
        super(BlackMarketConfirmVehicleModel, self).__init__(properties=properties, commands=commands)

    def getEndDate(self):
        return self._getNumber(0)

    def setEndDate(self, value):
        self._setNumber(0, value)

    def getChosenVehicleId(self):
        return self._getNumber(1)

    def setChosenVehicleId(self, value):
        self._setNumber(1, value)

    def getVehicleList(self):
        return self._getArray(2)

    def setVehicleList(self, value):
        self._setArray(2, value)

    def _initialize(self):
        super(BlackMarketConfirmVehicleModel, self)._initialize()
        self._addNumberProperty('endDate', 0)
        self._addNumberProperty('chosenVehicleId', 0)
        self._addArrayProperty('vehicleList', Array())
        self.onConfirm = self._addCommand('onConfirm')
