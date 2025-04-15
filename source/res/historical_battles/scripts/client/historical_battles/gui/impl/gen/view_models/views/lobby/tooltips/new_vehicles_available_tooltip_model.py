# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/tooltips/new_vehicles_available_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.tooltips.new_vehicle_item_model import NewVehicleItemModel

class NewVehiclesAvailableTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(NewVehiclesAvailableTooltipModel, self).__init__(properties=properties, commands=commands)

    def getVehicles(self):
        return self._getArray(0)

    def setVehicles(self, value):
        self._setArray(0, value)

    @staticmethod
    def getVehiclesType():
        return NewVehicleItemModel

    def _initialize(self):
        super(NewVehiclesAvailableTooltipModel, self)._initialize()
        self._addArrayProperty('vehicles', Array())
