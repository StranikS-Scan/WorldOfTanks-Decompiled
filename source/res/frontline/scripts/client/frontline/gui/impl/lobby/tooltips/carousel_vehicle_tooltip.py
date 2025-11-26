# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/tooltips/carousel_vehicle_tooltip.py
import typing
from gui.impl.lobby.tooltips.carousel_vehicle_tooltip import CarouselVehicleTooltipView
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle

class FLCarouselVehicleTooltipView(CarouselVehicleTooltipView):

    def _getDailyXPFactor(self, vehicle):
        pass

    def _getBpProgression(self, vehicleIntCD):
        bpPoints, _ = self._battlePass.getVehicleProgression(vehicleIntCD)
        return (bpPoints, 0)

    def _getIsBpEntityValid(self):
        return False
