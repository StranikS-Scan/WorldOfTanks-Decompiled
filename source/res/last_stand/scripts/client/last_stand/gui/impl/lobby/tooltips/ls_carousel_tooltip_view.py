# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/tooltips/ls_carousel_tooltip_view.py
from __future__ import absolute_import
import logging
from gui.impl.gen import R
from gui.impl.lobby.tooltips.carousel_vehicle_tooltip import CarouselVehicleTooltipView
from last_stand.gui.impl.lobby.ls_helpers import getLSVehicleStatus
_logger = logging.getLogger(__name__)

class LSVehicleCarouselTooltipView(CarouselVehicleTooltipView):
    LAYOUT_ID = R.views.last_stand.mono.lobby.tooltips.vehicle_tooltip()

    def _getVehicleStatus(self, vehicle):
        return getLSVehicleStatus(vehicle)
