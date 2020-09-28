# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/tooltips/wt_event_carousel_vehicle_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.tooltips.wt_event_carousel_vehicle_tooltip_view_model import WtEventCarouselVehicleTooltipViewModel
from helpers import dependency
from skeletons.gui.game_control import IGameEventController
from gui.impl.pub import ViewImpl

class WtEventCarouselVehicleTooltipView(ViewImpl):
    __slots__ = ('__vehicleType',)
    __gameEventCtrl = dependency.descriptor(IGameEventController)

    def __init__(self, vehicleType):
        settings = ViewSettings(R.views.lobby.wt_event.tooltips.WtEventCarouselVehicleTooltipView())
        settings.model = WtEventCarouselVehicleTooltipViewModel()
        self.__vehicleType = vehicleType
        super(WtEventCarouselVehicleTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WtEventCarouselVehicleTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WtEventCarouselVehicleTooltipView, self)._onLoading()
        with self.viewModel.transaction() as vModelTrx:
            vModelTrx.setVehicleType(self.__vehicleType)
