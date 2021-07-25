# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/popovers/vehicle_selector_list_item_model.py
from gui.impl.gen.view_models.views.lobby.detachment.common.vehicle_model import VehicleModel

class VehicleSelectorListItemModel(VehicleModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
        super(VehicleSelectorListItemModel, self).__init__(properties=properties, commands=commands)

    def getIsInHangar(self):
        return self._getBool(8)

    def setIsInHangar(self, value):
        self._setBool(8, value)

    def getIsLearnedForDetachment(self):
        return self._getBool(9)

    def setIsLearnedForDetachment(self, value):
        self._setBool(9, value)

    def getVehicleSlotPriority(self):
        return self._getNumber(10)

    def setVehicleSlotPriority(self, value):
        self._setNumber(10, value)

    def _initialize(self):
        super(VehicleSelectorListItemModel, self)._initialize()
        self._addBoolProperty('isInHangar', False)
        self._addBoolProperty('isLearnedForDetachment', False)
        self._addNumberProperty('vehicleSlotPriority', 0)
