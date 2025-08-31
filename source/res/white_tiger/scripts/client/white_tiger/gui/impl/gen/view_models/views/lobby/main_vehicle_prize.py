# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/main_vehicle_prize.py
from frameworks.wulf import ViewModel

class MainVehiclePrize(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(MainVehiclePrize, self).__init__(properties=properties, commands=commands)

    def getShortTankName(self):
        return self._getString(0)

    def setShortTankName(self, value):
        self._setString(0, value)

    def getTankLevel(self):
        return self._getNumber(1)

    def setTankLevel(self, value):
        self._setNumber(1, value)

    def getTankNation(self):
        return self._getString(2)

    def setTankNation(self, value):
        self._setString(2, value)

    def getTankType(self):
        return self._getString(3)

    def setTankType(self, value):
        self._setString(3, value)

    def getRoleName(self):
        return self._getString(4)

    def setRoleName(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(MainVehiclePrize, self)._initialize()
        self._addStringProperty('shortTankName', '')
        self._addNumberProperty('tankLevel', 0)
        self._addStringProperty('tankNation', '')
        self._addStringProperty('tankType', '')
        self._addStringProperty('roleName', '')
