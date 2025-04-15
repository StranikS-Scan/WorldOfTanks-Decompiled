# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/hb_meta_view/division_vehicle_model.py
from frameworks.wulf import ViewModel

class DivisionVehicleModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(DivisionVehicleModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getNameShort(self):
        return self._getString(1)

    def setNameShort(self, value):
        self._setString(1, value)

    def getLevel(self):
        return self._getNumber(2)

    def setLevel(self, value):
        self._setNumber(2, value)

    def getIcon(self):
        return self._getString(3)

    def setIcon(self, value):
        self._setString(3, value)

    def getVehicleType(self):
        return self._getString(4)

    def setVehicleType(self, value):
        self._setString(4, value)

    def getVehicleCD(self):
        return self._getNumber(5)

    def setVehicleCD(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(DivisionVehicleModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('nameShort', '')
        self._addNumberProperty('level', 0)
        self._addStringProperty('icon', '')
        self._addStringProperty('vehicleType', '')
        self._addNumberProperty('vehicleCD', 0)
