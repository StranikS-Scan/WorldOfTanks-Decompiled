# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/common/vehicle_model.py
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel

class VehicleModel(VehicleInfoModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(VehicleModel, self).__init__(properties=properties, commands=commands)

    def getIconPath(self):
        return self._getString(4)

    def setIconPath(self, value):
        self._setString(4, value)

    def getVehicleCD(self):
        return self._getNumber(5)

    def setVehicleCD(self, value):
        self._setNumber(5, value)

    def getVehicleFullName(self):
        return self._getString(6)

    def setVehicleFullName(self, value):
        self._setString(6, value)

    def _initialize(self):
        super(VehicleModel, self)._initialize()
        self._addStringProperty('iconPath', '')
        self._addNumberProperty('vehicleCD', 0)
        self._addStringProperty('vehicleFullName', '')
