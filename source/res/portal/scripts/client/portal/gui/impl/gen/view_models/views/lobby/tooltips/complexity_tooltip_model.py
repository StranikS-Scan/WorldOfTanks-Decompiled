# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/tooltips/complexity_tooltip_model.py
from frameworks.wulf import ViewModel

class ComplexityTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(ComplexityTooltipModel, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return self._getNumber(0)

    def setLevel(self, value):
        self._setNumber(0, value)

    def getIsLock(self):
        return self._getBool(1)

    def setIsLock(self, value):
        self._setBool(1, value)

    def getVehicleLevel(self):
        return self._getNumber(2)

    def setVehicleLevel(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(ComplexityTooltipModel, self)._initialize()
        self._addNumberProperty('level', 0)
        self._addBoolProperty('isLock', False)
        self._addNumberProperty('vehicleLevel', 0)
