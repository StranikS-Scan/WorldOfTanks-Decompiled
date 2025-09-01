# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/loadout/crew/native_vehicle.py
from frameworks.wulf import ViewModel

class NativeVehicle(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(NativeVehicle, self).__init__(properties=properties, commands=commands)

    def getShortName(self):
        return self._getString(0)

    def setShortName(self, value):
        self._setString(0, value)

    def getType(self):
        return self._getString(1)

    def setType(self, value):
        self._setString(1, value)

    def getTier(self):
        return self._getNumber(2)

    def setTier(self, value):
        self._setNumber(2, value)

    def getNation(self):
        return self._getString(3)

    def setNation(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(NativeVehicle, self)._initialize()
        self._addStringProperty('shortName', '')
        self._addStringProperty('type', '')
        self._addNumberProperty('tier', 0)
        self._addStringProperty('nation', '')
