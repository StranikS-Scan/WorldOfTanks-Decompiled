# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_vehicles_statistics_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_loot_box_statistics_vehicle_model import NyLootBoxStatisticsVehicleModel

class NyVehiclesStatisticsTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(NyVehiclesStatisticsTooltipModel, self).__init__(properties=properties, commands=commands)

    def getCount(self):
        return self._getNumber(0)

    def setCount(self, value):
        self._setNumber(0, value)

    def getVehicles(self):
        return self._getArray(1)

    def setVehicles(self, value):
        self._setArray(1, value)

    def _initialize(self):
        super(NyVehiclesStatisticsTooltipModel, self)._initialize()
        self._addNumberProperty('count', 0)
        self._addArrayProperty('vehicles', Array())
