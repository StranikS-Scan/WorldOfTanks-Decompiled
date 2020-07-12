# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle_royale/tech_parameters_cmp_view_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel

class TechParametersCmpViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(TechParametersCmpViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleGoodSpec(self):
        return self._getViewModel(0)

    @property
    def vehicleBadSpec(self):
        return self._getViewModel(1)

    def getVehicleDescription(self):
        return self._getResource(2)

    def setVehicleDescription(self, value):
        self._setResource(2, value)

    def _initialize(self):
        super(TechParametersCmpViewModel, self)._initialize()
        self._addViewModelProperty('vehicleGoodSpec', ListModel())
        self._addViewModelProperty('vehicleBadSpec', ListModel())
        self._addResourceProperty('vehicleDescription', R.invalid())
