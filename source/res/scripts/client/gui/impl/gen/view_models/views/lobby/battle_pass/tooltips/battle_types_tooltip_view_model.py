# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/tooltips/battle_types_tooltip_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class BattleTypesTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(BattleTypesTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getVehicleLevelFrom(self):
        return self._getNumber(0)

    def setVehicleLevelFrom(self, value):
        self._setNumber(0, value)

    def getVehicleLevelTo(self):
        return self._getNumber(1)

    def setVehicleLevelTo(self, value):
        self._setNumber(1, value)

    def getAvailableBattleTypes(self):
        return self._getArray(2)

    def setAvailableBattleTypes(self, value):
        self._setArray(2, value)

    @staticmethod
    def getAvailableBattleTypesType():
        return int

    def _initialize(self):
        super(BattleTypesTooltipViewModel, self)._initialize()
        self._addNumberProperty('vehicleLevelFrom', 1)
        self._addNumberProperty('vehicleLevelTo', 1)
        self._addArrayProperty('availableBattleTypes', Array())
