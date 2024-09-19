# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_event_vehicle_model.py
from frameworks.wulf import ViewModel

class WtEventVehicleModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(WtEventVehicleModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return self._getString(0)

    def setType(self, value):
        self._setString(0, value)

    def getLevel(self):
        return self._getNumber(1)

    def setLevel(self, value):
        self._setNumber(1, value)

    def getName(self):
        return self._getString(2)

    def setName(self, value):
        self._setString(2, value)

    def getSpecName(self):
        return self._getString(3)

    def setSpecName(self, value):
        self._setString(3, value)

    def getNation(self):
        return self._getString(4)

    def setNation(self, value):
        self._setString(4, value)

    def getIsElite(self):
        return self._getBool(5)

    def setIsElite(self, value):
        self._setBool(5, value)

    def getIntCD(self):
        return self._getNumber(6)

    def setIntCD(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(WtEventVehicleModel, self)._initialize()
        self._addStringProperty('type', '')
        self._addNumberProperty('level', 0)
        self._addStringProperty('name', '')
        self._addStringProperty('specName', '')
        self._addStringProperty('nation', '')
        self._addBoolProperty('isElite', False)
        self._addNumberProperty('intCD', 0)
