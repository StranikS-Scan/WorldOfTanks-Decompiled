# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/common/vehicle_model.py
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel

class VehicleModel(VehicleInfoModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(VehicleModel, self).__init__(properties=properties, commands=commands)

    def getVehicleCD(self):
        return self._getNumber(7)

    def setVehicleCD(self, value):
        self._setNumber(7, value)

    def getVehicleIconName(self):
        return self._getString(8)

    def setVehicleIconName(self, value):
        self._setString(8, value)

    def _initialize(self):
        super(VehicleModel, self)._initialize()
        self._addNumberProperty('vehicleCD', 0)
        self._addStringProperty('vehicleIconName', '')
