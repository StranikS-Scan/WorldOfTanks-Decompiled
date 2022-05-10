# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle_royale/tech_parameters_cmp_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.battle_royale.br_vehicle_specifications_model import BrVehicleSpecificationsModel

class TechParametersCmpViewModel(ViewModel):
    __slots__ = ('onModulesBtnClick', 'onResized')

    def __init__(self, properties=2, commands=2):
        super(TechParametersCmpViewModel, self).__init__(properties=properties, commands=commands)

    def getVehicleGoodSpec(self):
        return self._getArray(0)

    def setVehicleGoodSpec(self, value):
        self._setArray(0, value)

    def getVehicleBadSpec(self):
        return self._getArray(1)

    def setVehicleBadSpec(self, value):
        self._setArray(1, value)

    def _initialize(self):
        super(TechParametersCmpViewModel, self)._initialize()
        self._addArrayProperty('vehicleGoodSpec', Array())
        self._addArrayProperty('vehicleBadSpec', Array())
        self.onModulesBtnClick = self._addCommand('onModulesBtnClick')
        self.onResized = self._addCommand('onResized')
