# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/shop_views/vehicle_item_view_model.py
from historical_battles.gui.impl.gen.view_models.views.common.vehicle_model import VehicleModel
from historical_battles.gui.impl.gen.view_models.views.lobby.shop_views.bundle_item_view_model import BundleItemViewModel

class VehicleItemViewModel(BundleItemViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(VehicleItemViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicle(self):
        return self._getViewModel(5)

    @staticmethod
    def getVehicleType():
        return VehicleModel

    def getIsSold(self):
        return self._getBool(6)

    def setIsSold(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(VehicleItemViewModel, self)._initialize()
        self._addViewModelProperty('vehicle', VehicleModel())
        self._addBoolProperty('isSold', False)
