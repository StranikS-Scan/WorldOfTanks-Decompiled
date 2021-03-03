# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/bm2021/black_market_vehicle_list_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.vehicle_model import VehicleModel

class BlackMarketVehicleListModel(ViewModel):
    __slots__ = ('onBackClick', 'onVehiclePreview')

    def __init__(self, properties=2, commands=2):
        super(BlackMarketVehicleListModel, self).__init__(properties=properties, commands=commands)

    def getVehicleList(self):
        return self._getArray(0)

    def setVehicleList(self, value):
        self._setArray(0, value)

    def getSlotsNumber(self):
        return self._getNumber(1)

    def setSlotsNumber(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(BlackMarketVehicleListModel, self)._initialize()
        self._addArrayProperty('vehicleList', Array())
        self._addNumberProperty('slotsNumber', 0)
        self.onBackClick = self._addCommand('onBackClick')
        self.onVehiclePreview = self._addCommand('onVehiclePreview')
