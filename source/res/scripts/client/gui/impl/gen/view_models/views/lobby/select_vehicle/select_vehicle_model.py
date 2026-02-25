# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/select_vehicle/select_vehicle_model.py
from frameworks.wulf import ViewModel

class SelectVehicleModel(ViewModel):
    __slots__ = ('onSelect', 'onIsAllVehiclesChange')

    def __init__(self, properties=3, commands=2):
        super(SelectVehicleModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getString(0)

    def setTitle(self, value):
        self._setString(0, value)

    def getCurrentVehicleCD(self):
        return self._getNumber(1)

    def setCurrentVehicleCD(self, value):
        self._setNumber(1, value)

    def getIsAllVehicles(self):
        return self._getBool(2)

    def setIsAllVehicles(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(SelectVehicleModel, self)._initialize()
        self._addStringProperty('title', '')
        self._addNumberProperty('currentVehicleCD', 0)
        self._addBoolProperty('isAllVehicles', False)
        self.onSelect = self._addCommand('onSelect')
        self.onIsAllVehiclesChange = self._addCommand('onIsAllVehiclesChange')
