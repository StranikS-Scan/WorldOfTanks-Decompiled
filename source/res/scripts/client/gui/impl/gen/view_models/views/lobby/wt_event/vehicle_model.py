# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/vehicle_model.py
from frameworks.wulf import ViewModel

class VehicleModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(VehicleModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return self._getString(0)

    def setType(self, value):
        self._setString(0, value)

    def getLevel(self):
        return self._getString(1)

    def setLevel(self, value):
        self._setString(1, value)

    def getName(self):
        return self._getString(2)

    def setName(self, value):
        self._setString(2, value)

    def getSpecName(self):
        return self._getString(3)

    def setSpecName(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(VehicleModel, self)._initialize()
        self._addStringProperty('type', '')
        self._addStringProperty('level', '')
        self._addStringProperty('name', '')
        self._addStringProperty('specName', '')
