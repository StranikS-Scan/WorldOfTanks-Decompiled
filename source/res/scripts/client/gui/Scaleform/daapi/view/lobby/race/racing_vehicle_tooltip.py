# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/race/racing_vehicle_tooltip.py
import logging
from frameworks.wulf import ViewFlags, View
from gui.impl.gen import R
from gui.impl.gen.view_models.views.race.racing_tank_tooltip_view_model import RacingTankTooltipViewModel
from helpers import dependency
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class RacingVehicleTooltipContent(View):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, intCD):
        super(RacingVehicleTooltipContent, self).__init__(R.views.lobby.race.racing_tank_tooltip.RacingTankTooltip(), ViewFlags.COMPONENT, RacingTankTooltipViewModel, intCD)

    @property
    def viewModel(self):
        return super(RacingVehicleTooltipContent, self).getViewModel()

    def _initialize(self, intCD):
        super(RacingVehicleTooltipContent, self)._initialize(intCD)
        vehicle = self.itemsCache.items.getItemByCD(intCD)
        with self.viewModel.transaction() as model:
            model.setName(vehicle.userName)
            model.setDescription(R.strings.festival.race.hangar.vehicle.tooltip.num(intCD).description())
            model.techParams.setVehicleIntCD(intCD)
