# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/wot_plus/wot_plus_browser_pages.py
from gui.Scaleform.daapi.view.lobby.shared.web_view import WebView
from gui.Scaleform.daapi.view.lobby.wot_plus.sound_constants import VEHICLE_RENTAL_SOUND_SPACE, WOT_PLUS_INFO_SOUND_SPACE

class WotPlusInfoView(WebView):
    _COMMON_SOUND_SPACE = WOT_PLUS_INFO_SOUND_SPACE


class VehicleRentalView(WebView):
    _COMMON_SOUND_SPACE = VEHICLE_RENTAL_SOUND_SPACE

    @property
    def webHandlersReplacements(self):
        from gui.Scaleform.daapi.view.lobby.wot_plus.web_handlers import getReplaceHandlers
        return getReplaceHandlers()
