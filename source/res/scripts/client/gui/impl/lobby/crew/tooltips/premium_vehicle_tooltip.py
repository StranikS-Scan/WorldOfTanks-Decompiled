# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/tooltips/premium_vehicle_tooltip.py
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from frameworks.wulf import ViewSettings
from skeletons.gui.shared import IItemsCache
from gui.impl.gen.view_models.views.lobby.crew.tooltips.premium_vehicle_tooltip_view_model import PremiumVehicleTooltipViewModel

class PremiumVehicleTooltip(ViewImpl):
    __slots__ = ('__vehType', '__nation')
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, vehicleCD, layoutID=R.views.lobby.crew.tooltips.PremiumVehicleTooltip()):
        settings = ViewSettings(layoutID)
        settings.model = PremiumVehicleTooltipViewModel()
        super(PremiumVehicleTooltip, self).__init__(settings)
        vehicle = self._itemsCache.items.getItemByCD(vehicleCD)
        self.__vehType = vehicle.type
        self.__nation = vehicle.nationName

    @property
    def viewModel(self):
        return super(PremiumVehicleTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(PremiumVehicleTooltip, self)._onLoading()
        with self.viewModel.transaction() as model:
            model.setVehTypeName(backport.text(R.strings.crew.premiumVehType.plural.lowerCase.dyn(self.__vehType.replace('-', '_'))()))
            model.setNationName(backport.text(R.strings.nations.dyn(self.__nation)()))
