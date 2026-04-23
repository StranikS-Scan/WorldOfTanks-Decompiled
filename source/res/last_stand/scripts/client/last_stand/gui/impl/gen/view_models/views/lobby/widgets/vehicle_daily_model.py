# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/widgets/vehicle_daily_model.py
from frameworks.wulf import ViewModel

class VehicleDailyModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(VehicleDailyModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getIsActive(self):
        return self._getBool(1)

    def setIsActive(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(VehicleDailyModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addBoolProperty('isActive', False)
