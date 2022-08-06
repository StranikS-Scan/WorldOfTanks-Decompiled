# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_matters/battle_matters_vehicle_selection_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.battle_matters.battle_matters_vehicle_model import BattleMattersVehicleModel

class BattleMattersVehicleSelectionViewModel(ViewModel):
    __slots__ = ('onGoBack', 'onShowVehicle', 'onCompareVehicle')
    ARG_VEHICLE_ID = 'vehCD'

    def __init__(self, properties=3, commands=3):
        super(BattleMattersVehicleSelectionViewModel, self).__init__(properties=properties, commands=commands)

    def getEndDate(self):
        return self._getNumber(0)

    def setEndDate(self, value):
        self._setNumber(0, value)

    def getTotalVehiclesCount(self):
        return self._getNumber(1)

    def setTotalVehiclesCount(self, value):
        self._setNumber(1, value)

    def getVehicles(self):
        return self._getArray(2)

    def setVehicles(self, value):
        self._setArray(2, value)

    @staticmethod
    def getVehiclesType():
        return BattleMattersVehicleModel

    def _initialize(self):
        super(BattleMattersVehicleSelectionViewModel, self)._initialize()
        self._addNumberProperty('endDate', 0)
        self._addNumberProperty('totalVehiclesCount', 0)
        self._addArrayProperty('vehicles', Array())
        self.onGoBack = self._addCommand('onGoBack')
        self.onShowVehicle = self._addCommand('onShowVehicle')
        self.onCompareVehicle = self._addCommand('onCompareVehicle')
