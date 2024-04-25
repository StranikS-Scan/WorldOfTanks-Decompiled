# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/tooltips/hb_special_vehicles_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class HbSpecialVehiclesTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(HbSpecialVehiclesTooltipModel, self).__init__(properties=properties, commands=commands)

    def getVehicles(self):
        return self._getArray(0)

    def setVehicles(self, value):
        self._setArray(0, value)

    def getIsVehiclesUnlocked(self):
        return self._getBool(1)

    def setIsVehiclesUnlocked(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(HbSpecialVehiclesTooltipModel, self)._initialize()
        self._addArrayProperty('vehicles', Array())
        self._addBoolProperty('isVehiclesUnlocked', False)
