# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/shop_views/showcase_view_model.py
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.shop_views.bundle_item_view_model import BundleItemViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.shop_views.vehicle_item_view_model import VehicleItemViewModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel

class ShowcaseViewModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=3, commands=1):
        super(ShowcaseViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleBundle(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleBundleType():
        return VehicleItemViewModel

    @property
    def extraBundle(self):
        return self._getViewModel(1)

    @staticmethod
    def getExtraBundleType():
        return BundleItemViewModel

    @property
    def bundles(self):
        return self._getViewModel(2)

    @staticmethod
    def getBundlesType():
        return BundleItemViewModel

    def _initialize(self):
        super(ShowcaseViewModel, self)._initialize()
        self._addViewModelProperty('vehicleBundle', VehicleItemViewModel())
        self._addViewModelProperty('extraBundle', BundleItemViewModel())
        self._addViewModelProperty('bundles', ListModel())
        self.onClick = self._addCommand('onClick')
