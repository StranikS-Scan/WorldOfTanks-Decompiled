# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/convert_slot_vehicle_model.py
from gui.impl.gen.view_models.views.lobby.detachment.common.vehicle_model import VehicleModel

class ConvertSlotVehicleModel(VehicleModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(ConvertSlotVehicleModel, self).__init__(properties=properties, commands=commands)

    def getIsLocked(self):
        return self._getBool(8)

    def setIsLocked(self, value):
        self._setBool(8, value)

    def getLevelReq(self):
        return self._getNumber(9)

    def setLevelReq(self, value):
        self._setNumber(9, value)

    def _initialize(self):
        super(ConvertSlotVehicleModel, self)._initialize()
        self._addBoolProperty('isLocked', False)
        self._addNumberProperty('levelReq', 0)
