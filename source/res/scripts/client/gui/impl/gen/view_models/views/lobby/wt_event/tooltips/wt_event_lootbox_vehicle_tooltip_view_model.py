# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/tooltips/wt_event_lootbox_vehicle_tooltip_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class WtEventLootboxVehicleTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(WtEventLootboxVehicleTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getVehicles(self):
        return self._getArray(0)

    def setVehicles(self, value):
        self._setArray(0, value)

    def _initialize(self):
        super(WtEventLootboxVehicleTooltipViewModel, self)._initialize()
        self._addArrayProperty('vehicles', Array())
