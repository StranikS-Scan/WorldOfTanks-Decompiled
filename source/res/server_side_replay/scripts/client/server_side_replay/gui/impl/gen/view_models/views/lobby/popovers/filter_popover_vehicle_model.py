# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: server_side_replay/scripts/client/server_side_replay/gui/impl/gen/view_models/views/lobby/popovers/filter_popover_vehicle_model.py
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel

class FilterPopoverVehicleModel(VehicleModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
        super(FilterPopoverVehicleModel, self).__init__(properties=properties, commands=commands)

    def getIsSelected(self):
        return self._getBool(10)

    def setIsSelected(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(FilterPopoverVehicleModel, self)._initialize()
        self._addBoolProperty('isSelected', False)
