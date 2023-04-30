# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/wot_plus/wot_plus_browser_pages.py
import WWISE
from gui.Scaleform.daapi.view.lobby.shared.web_view import WebView
from gui.Scaleform.daapi.view.lobby.wot_plus.sound_constants import VEHICLE_RENTAL_SOUND_SPACE, WOT_PLUS_INFO_SOUND_SPACE
from gui.impl import backport
from gui.impl.gen import R

class WotPlusInfoView(WebView):
    _COMMON_SOUND_SPACE = WOT_PLUS_INFO_SOUND_SPACE


class VehicleRentalView(WebView):
    _COMMON_SOUND_SPACE = VEHICLE_RENTAL_SOUND_SPACE

    @property
    def webHandlersReplacements(self):
        from gui.Scaleform.daapi.view.lobby.wot_plus.web_handlers import getReplaceHandlers
        return getReplaceHandlers()

    def _populate(self):
        super(VehicleRentalView, self)._populate()
        WWISE.WW_eventGlobal(backport.sound(R.sounds.ev_cn_wotplus_tank_rental_enter()))

    def _dispose(self):
        WWISE.WW_eventGlobal(backport.sound(R.sounds.ev_cn_wotplus_tank_rental_exit()))
        super(VehicleRentalView, self)._dispose()
