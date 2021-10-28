# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/halloween/vehicle_result_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class VehicleResultModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(VehicleResultModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getImage(self):
        return self._getResource(2)

    def setImage(self, value):
        self._setResource(2, value)

    def getType(self):
        return self._getString(3)

    def setType(self, value):
        self._setString(3, value)

    def getLevel(self):
        return self._getNumber(4)

    def setLevel(self, value):
        self._setNumber(4, value)

    def getTooltip(self):
        return self._getString(5)

    def setTooltip(self, value):
        self._setString(5, value)

    def _initialize(self):
        super(VehicleResultModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('name', '')
        self._addResourceProperty('image', R.invalid())
        self._addStringProperty('type', '')
        self._addNumberProperty('level', 0)
        self._addStringProperty('tooltip', '')
