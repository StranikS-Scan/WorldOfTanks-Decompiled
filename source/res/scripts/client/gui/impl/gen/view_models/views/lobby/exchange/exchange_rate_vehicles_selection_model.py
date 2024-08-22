# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/exchange/exchange_rate_vehicles_selection_model.py
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel

class ExchangeRateVehiclesSelectionModel(VehicleModel):
    __slots__ = ()

    def __init__(self, properties=14, commands=0):
        super(ExchangeRateVehiclesSelectionModel, self).__init__(properties=properties, commands=commands)

    def getIsFieldModernizationAvailable(self):
        return self._getBool(9)

    def setIsFieldModernizationAvailable(self, value):
        self._setBool(9, value)

    def getIsFieldModernizationComplited(self):
        return self._getBool(10)

    def setIsFieldModernizationComplited(self, value):
        self._setBool(10, value)

    def getLevelOfFieldModernization(self):
        return self._getNumber(11)

    def setLevelOfFieldModernization(self, value):
        self._setNumber(11, value)

    def getAmountOfCombatXp(self):
        return self._getNumber(12)

    def setAmountOfCombatXp(self, value):
        self._setNumber(12, value)

    def getNationOrder(self):
        return self._getNumber(13)

    def setNationOrder(self, value):
        self._setNumber(13, value)

    def _initialize(self):
        super(ExchangeRateVehiclesSelectionModel, self)._initialize()
        self._addBoolProperty('isFieldModernizationAvailable', False)
        self._addBoolProperty('isFieldModernizationComplited', False)
        self._addNumberProperty('levelOfFieldModernization', 1)
        self._addNumberProperty('amountOfCombatXp', 1)
        self._addNumberProperty('nationOrder', 1)
