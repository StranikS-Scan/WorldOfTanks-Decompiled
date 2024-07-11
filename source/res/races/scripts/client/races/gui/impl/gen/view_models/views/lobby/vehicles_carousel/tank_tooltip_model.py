# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/gen/view_models/views/lobby/vehicles_carousel/tank_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class TankTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(TankTooltipModel, self).__init__(properties=properties, commands=commands)

    def getSlotId(self):
        return self._getNumber(0)

    def setSlotId(self, value):
        self._setNumber(0, value)

    def getVehicleName(self):
        return self._getString(1)

    def setVehicleName(self, value):
        self._setString(1, value)

    def getVehicleUserName(self):
        return self._getString(2)

    def setVehicleUserName(self, value):
        self._setString(2, value)

    def getDescription(self):
        return self._getString(3)

    def setDescription(self, value):
        self._setString(3, value)

    def getInBattle(self):
        return self._getBool(4)

    def setInBattle(self, value):
        self._setBool(4, value)

    def getVehicleTth(self):
        return self._getArray(5)

    def setVehicleTth(self, value):
        self._setArray(5, value)

    @staticmethod
    def getVehicleTthType():
        return int

    def _initialize(self):
        super(TankTooltipModel, self)._initialize()
        self._addNumberProperty('slotId', 0)
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('vehicleUserName', '')
        self._addStringProperty('description', '')
        self._addBoolProperty('inBattle', False)
        self._addArrayProperty('vehicleTth', Array())
