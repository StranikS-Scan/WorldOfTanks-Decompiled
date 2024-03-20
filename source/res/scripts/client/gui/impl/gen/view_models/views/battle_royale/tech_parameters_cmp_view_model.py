# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle_royale/tech_parameters_cmp_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.battle_royale.br_vehicle_specifications_model import BrVehicleSpecificationsModel

class TechParametersCmpViewModel(ViewModel):
    __slots__ = ('onGotoShopBtnClicked', 'onModulesBtnClick', 'onResized')

    def __init__(self, properties=3, commands=3):
        super(TechParametersCmpViewModel, self).__init__(properties=properties, commands=commands)

    def getBalance(self):
        return self._getNumber(0)

    def setBalance(self, value):
        self._setNumber(0, value)

    def getVehicleGoodSpec(self):
        return self._getArray(1)

    def setVehicleGoodSpec(self, value):
        self._setArray(1, value)

    @staticmethod
    def getVehicleGoodSpecType():
        return BrVehicleSpecificationsModel

    def getVehicleBadSpec(self):
        return self._getArray(2)

    def setVehicleBadSpec(self, value):
        self._setArray(2, value)

    @staticmethod
    def getVehicleBadSpecType():
        return BrVehicleSpecificationsModel

    def _initialize(self):
        super(TechParametersCmpViewModel, self)._initialize()
        self._addNumberProperty('balance', 0)
        self._addArrayProperty('vehicleGoodSpec', Array())
        self._addArrayProperty('vehicleBadSpec', Array())
        self.onGotoShopBtnClicked = self._addCommand('onGotoShopBtnClicked')
        self.onModulesBtnClick = self._addCommand('onModulesBtnClick')
        self.onResized = self._addCommand('onResized')
