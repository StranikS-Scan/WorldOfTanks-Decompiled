# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_parameters/vehicle_parameter_group_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.vehicle_parameters.vehicle_parameter_view_model import VehicleParameterViewModel

class VehicleParameterGroupViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(VehicleParameterGroupViewModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getCurrentValue(self):
        return self._getNumber(1)

    def setCurrentValue(self, value):
        self._setNumber(1, value)

    def getOriginalValue(self):
        return self._getNumber(2)

    def setOriginalValue(self, value):
        self._setNumber(2, value)

    def getIsExpanded(self):
        return self._getBool(3)

    def setIsExpanded(self, value):
        self._setBool(3, value)

    def getItems(self):
        return self._getArray(4)

    def setItems(self, value):
        self._setArray(4, value)

    def _initialize(self):
        super(VehicleParameterGroupViewModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addNumberProperty('currentValue', 0)
        self._addNumberProperty('originalValue', 0)
        self._addBoolProperty('isExpanded', False)
        self._addArrayProperty('items', Array())
