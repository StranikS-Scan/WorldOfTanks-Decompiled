# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/tooltips/carousel_vehicle_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from shared_utils import first
from white_tiger_common.wt_constants import WT_VEHICLE_TAGS
from white_tiger.gui.impl.gen.view_models.views.lobby.tooltips.carousel_vehicle_tooltip_view_model import CarouselVehicleTooltipViewModel

class CarouselVehicleTooltipView(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.white_tiger.mono.lobby.tooltips.carousel_vehicle_tooltip())
        settings.model = CarouselVehicleTooltipViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(CarouselVehicleTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(CarouselVehicleTooltipView, self)._onLoading(*args, **kwargs)
        vehInvID = kwargs.get('vehInvID', 0)
        vehicle = self.__itemsCache.items.getVehicle(vehInvID)
        if not vehicle:
            return
        with self.viewModel.transaction() as trx:
            vehicleType = first(vehicle.tags & WT_VEHICLE_TAGS.EVENT_VEHS)
            trx.setTitle(vehicle.userName)
            trx.setSubtitle(vehicle.shortDescriptionSpecial)
            trx.setIcon(R.images.white_tiger.gui.maps.icons.hangar.dyn(vehicleType)())
            trx.setDescription(vehicle.fullDescription)
