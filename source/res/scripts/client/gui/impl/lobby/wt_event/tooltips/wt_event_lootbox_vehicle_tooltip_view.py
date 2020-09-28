# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/tooltips/wt_event_lootbox_vehicle_tooltip_view.py
from frameworks.wulf import ViewSettings, Array
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.tooltips.wt_event_lootbox_vehicle_tooltip_view_model import WtEventLootboxVehicleTooltipViewModel
from gui.impl.pub import ViewImpl

class WtEventLootboxVehicleTooltipView(ViewImpl):
    __slots__ = ('__vehicles',)

    def __init__(self, vehiclesList):
        settings = ViewSettings(R.views.lobby.wt_event.tooltips.WtEventLootboxVehicleTooltipView())
        settings.model = WtEventLootboxVehicleTooltipViewModel()
        super(WtEventLootboxVehicleTooltipView, self).__init__(settings)
        self.__vehicles = vehiclesList

    @property
    def viewModel(self):
        return super(WtEventLootboxVehicleTooltipView, self).getViewModel()

    def _onLoaded(self, *args, **kwargs):
        super(WtEventLootboxVehicleTooltipView, self)._onLoaded(*args, **kwargs)
        with self.viewModel.transaction() as model:
            vehicles = Array()
            for vehicle in self.__vehicles:
                vehicles.addString(vehicle)

            model.setVehicles(vehicles)
