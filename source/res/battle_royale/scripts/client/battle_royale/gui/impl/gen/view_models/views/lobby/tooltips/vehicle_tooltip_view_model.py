# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/gen/view_models/views/lobby/tooltips/vehicle_tooltip_view_model.py
from frameworks.wulf import ViewModel
from battle_royale.gui.impl.gen.view_models.views.lobby.tooltips.tech_parameters_cmp_view_model import TechParametersCmpViewModel

class VehicleTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(VehicleTooltipViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def tech(self):
        return self._getViewModel(0)

    @staticmethod
    def getTechType():
        return TechParametersCmpViewModel

    def getVehicleName(self):
        return self._getString(1)

    def setVehicleName(self, value):
        self._setString(1, value)

    def getVehicleNation(self):
        return self._getString(2)

    def setVehicleNation(self, value):
        self._setString(2, value)

    def getVehicleType(self):
        return self._getString(3)

    def setVehicleType(self, value):
        self._setString(3, value)

    def getStatusLevel(self):
        return self._getString(4)

    def setStatusLevel(self, value):
        self._setString(4, value)

    def getStatusText(self):
        return self._getString(5)

    def setStatusText(self, value):
        self._setString(5, value)

    def _initialize(self):
        super(VehicleTooltipViewModel, self)._initialize()
        self._addViewModelProperty('tech', TechParametersCmpViewModel())
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('vehicleNation', '')
        self._addStringProperty('vehicleType', '')
        self._addStringProperty('statusLevel', '')
        self._addStringProperty('statusText', '')
