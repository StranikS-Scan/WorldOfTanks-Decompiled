# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/tooltips/wt_carousel_vehicle_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from white_tiger.gui.impl.gen.view_models.views.lobby.tooltips.wt_carousel_vehicle_tooltip_view_model import WtCarouselVehicleTooltipViewModel
from gui.impl.pub import ViewImpl
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS as _TAGS
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from shared_utils import first

class WtCarouselVehicleTooltipView(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.white_tiger.lobby.tooltips.CarouselVehicleTooltipView(), model=WtCarouselVehicleTooltipViewModel())
        settings.args = args
        settings.kwargs = kwargs
        super(WtCarouselVehicleTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WtCarouselVehicleTooltipView, self)._onLoading(*args, **kwargs)
        vehInvID = kwargs.get('vehInvID', 0)
        vehicle = self.__itemsCache.items.getVehicle(vehInvID)
        if not vehicle:
            return
        with self.viewModel.transaction() as trx:
            eventType = first(vehicle.tags & _TAGS.WT_VEHICLES)
            trx.setTitle(vehicle.userName)
            trx.setSubtitle(vehicle.shortDescriptionSpecial)
            trx.setIcon(R.images.white_tiger.gui.maps.icons.hangar.dyn(eventType)())
            trx.setDescription(vehicle.fullDescription)
            trx.setIsSpecialBoss(_TAGS.WT_SPECIAL_BOSS in vehicle.tags)
