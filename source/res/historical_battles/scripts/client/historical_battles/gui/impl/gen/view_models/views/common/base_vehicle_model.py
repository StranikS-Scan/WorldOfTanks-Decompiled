# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/common/base_vehicle_model.py
from frameworks.wulf import ViewModel

class BaseVehicleModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(BaseVehicleModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getType(self):
        return self._getString(2)

    def setType(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(BaseVehicleModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('name', '')
        self._addStringProperty('type', '')
