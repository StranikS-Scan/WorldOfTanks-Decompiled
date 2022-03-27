# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/rts/roster_view/supply_details_tooltip_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.vehicle_parameters.vehicle_parameters_view_model import VehicleParametersViewModel

class SupplyDetailsTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(SupplyDetailsTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def parameters(self):
        return self._getViewModel(0)

    def getType(self):
        return self._getString(1)

    def setType(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(SupplyDetailsTooltipModel, self)._initialize()
        self._addViewModelProperty('parameters', VehicleParametersViewModel())
        self._addStringProperty('type', '')
