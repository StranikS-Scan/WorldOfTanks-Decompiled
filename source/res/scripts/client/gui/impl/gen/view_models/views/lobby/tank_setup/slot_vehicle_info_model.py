# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/slot_vehicle_info_model.py
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel

class SlotVehicleInfoModel(VehicleInfoModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(SlotVehicleInfoModel, self).__init__(properties=properties, commands=commands)

    def getVehicleID(self):
        return self._getNumber(4)

    def setVehicleID(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(SlotVehicleInfoModel, self)._initialize()
        self._addNumberProperty('vehicleID', 0)
