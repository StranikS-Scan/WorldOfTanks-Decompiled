# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/tooltips/wt_carousel_vehicle_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from white_tiger.gui.impl.gen.view_models.views.lobby.tooltips.wt_carousel_vehicle_tooltip_view_model import WtCarouselVehicleTooltipViewModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from wt_settings import g_wt_config
import logging
_logger = logging.getLogger(__name__)

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
        vehCD = int(kwargs.get('vehInvID', 0))
        vehData = g_wt_config.getVehicleData(vehCD)
        if not vehData:
            return
        vehicle = vehData.vehicle
        with self.viewModel.transaction() as trx:
            trx.setTitle(vehicle.userName)
            trx.setSubtitle(vehicle.shortDescriptionSpecial)
            trx.setIcon(R.images.white_tiger.gui.maps.icons.hangar.dyn(vehData.type)())
            trx.setDescription(vehicle.fullDescription)
            trx.setWtVehicleType(vehData.type)
