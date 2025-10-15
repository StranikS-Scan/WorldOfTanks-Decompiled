# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/tooltips/vehicle_ttx.py
from frameworks.wulf import ViewModel

class VehicleTtx(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(VehicleTtx, self).__init__(properties=properties, commands=commands)

    def getDamage(self):
        return self._getNumber(0)

    def setDamage(self, value):
        self._setNumber(0, value)

    def getMobility(self):
        return self._getNumber(1)

    def setMobility(self, value):
        self._setNumber(1, value)

    def getArmor(self):
        return self._getNumber(2)

    def setArmor(self, value):
        self._setNumber(2, value)

    def getReload(self):
        return self._getNumber(3)

    def setReload(self, value):
        self._setNumber(3, value)

    def getHp(self):
        return self._getNumber(4)

    def setHp(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(VehicleTtx, self)._initialize()
        self._addNumberProperty('damage', 0)
        self._addNumberProperty('mobility', 0)
        self._addNumberProperty('armor', 0)
        self._addNumberProperty('reload', 0)
        self._addNumberProperty('hp', 0)
