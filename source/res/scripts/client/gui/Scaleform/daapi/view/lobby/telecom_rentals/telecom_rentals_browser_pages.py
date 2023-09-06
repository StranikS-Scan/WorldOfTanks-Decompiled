# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/telecom_rentals/telecom_rentals_browser_pages.py
from gui.Scaleform.daapi.view.lobby.wot_plus.sound_constants import VEHICLE_RENTAL_SOUND_SPACE
from gui.Scaleform.daapi.view.lobby.wot_plus.wot_plus_browser_pages import VehicleRentalView

class VehicleTelecomRentalView(VehicleRentalView):
    _COMMON_SOUND_SPACE = VEHICLE_RENTAL_SOUND_SPACE

    def webHandlers(self):
        from gui.Scaleform.daapi.view.lobby.telecom_rentals.web_handlers import replaceHandlers
        handlers = super(VehicleTelecomRentalView, self).webHandlers()
        replaceHandlers(handlers)
        return handlers
