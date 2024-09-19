# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/tooltips/wt_event_carousel_vehicle_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.tooltips.wt_event_carousel_vehicle_tooltip_view_model import WtEventCarouselVehicleTooltipViewModel
from gui.impl.pub import ViewImpl
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS as _TAGS
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from shared_utils import first

class WtEventCarouselVehicleTooltipView(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.lobby.wt_event.tooltips.WtEventCarouselVehicleTooltipView(), model=WtEventCarouselVehicleTooltipViewModel())
        settings.args = args
        settings.kwargs = kwargs
        super(WtEventCarouselVehicleTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WtEventCarouselVehicleTooltipView, self)._onLoading(*args, **kwargs)
        vehInvID = kwargs.get('vehInvID', 0)
        vehicle = self.__itemsCache.items.getVehicle(vehInvID)
        if not vehicle:
            return
        with self.viewModel.transaction() as trx:
            eventType = first(vehicle.tags & _TAGS.EVENT_VEHS)
            trx.setTitle(vehicle.userName)
            trx.setSubtitle(vehicle.shortDescriptionSpecial)
            trx.setIcon(R.images.gui.maps.icons.wtevent.hangar.dyn(eventType)())
            trx.setDescription(vehicle.fullDescription)
