# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/gen/view_models/views/lobby/tooltips/vehicle_tooltip_view_model.py
from frameworks.wulf import ViewModel
from battle_royale.gui.impl.gen.view_models.views.lobby.tooltips.rent_price_model import RentPriceModel

class VehicleTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(VehicleTooltipViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def rentPrice(self):
        return self._getViewModel(0)

    @staticmethod
    def getRentPriceType():
        return RentPriceModel

    def getVehicleName(self):
        return self._getString(1)

    def setVehicleName(self, value):
        self._setString(1, value)

    def getVehicleNation(self):
        return self._getString(2)

    def setVehicleNation(self, value):
        self._setString(2, value)

    def getRentState(self):
        return self._getString(3)

    def setRentState(self, value):
        self._setString(3, value)

    def getStatusLevel(self):
        return self._getString(4)

    def setStatusLevel(self, value):
        self._setString(4, value)

    def getStatusText(self):
        return self._getString(5)

    def setStatusText(self, value):
        self._setString(5, value)

    def getRentTimeLeft(self):
        return self._getString(6)

    def setRentTimeLeft(self, value):
        self._setString(6, value)

    def getHasSTPDailyFactor(self):
        return self._getBool(7)

    def setHasSTPDailyFactor(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(VehicleTooltipViewModel, self)._initialize()
        self._addViewModelProperty('rentPrice', RentPriceModel())
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('vehicleNation', '')
        self._addStringProperty('rentState', '')
        self._addStringProperty('statusLevel', '')
        self._addStringProperty('statusText', '')
        self._addStringProperty('rentTimeLeft', '')
        self._addBoolProperty('hasSTPDailyFactor', False)
