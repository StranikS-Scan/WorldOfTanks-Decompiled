# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/common/vehicle_model.py
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel

class VehicleModel(VehicleInfoModel):
    __slots__ = ()

    def __init__(self, properties=19, commands=0):
        super(VehicleModel, self).__init__(properties=properties, commands=commands)

    def getVehicleCD(self):
        return self._getNumber(17)

    def setVehicleCD(self, value):
        self._setNumber(17, value)

    def getVehicleIconName(self):
        return self._getString(18)

    def setVehicleIconName(self, value):
        self._setString(18, value)

    def _initialize(self):
        super(VehicleModel, self)._initialize()
        self._addNumberProperty('vehicleCD', 0)
        self._addStringProperty('vehicleIconName', '')
