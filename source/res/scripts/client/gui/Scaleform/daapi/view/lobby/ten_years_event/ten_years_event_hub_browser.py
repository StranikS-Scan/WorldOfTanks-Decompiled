# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/ten_years_event/ten_years_event_hub_browser.py
import BigWorld
from gui.Scaleform.daapi.view.lobby.shared.web_view import WebView
from gui.Scaleform.daapi.view.lobby.ten_years_event.web_handlers import createTenYearsEventWebHandlers
from PlayerEvents import g_playerEvents

class TenYearsEventHubPageOverlay(WebView):

    def __init__(self, ctx=None):
        super(TenYearsEventHubPageOverlay, self).__init__(ctx)
        self.isLogOff = False

    def webHandlers(self):
        return createTenYearsEventWebHandlers()

    def _populate(self):
        super(TenYearsEventHubPageOverlay, self)._populate()
        BigWorld.worldDrawEnabled(False)
        g_playerEvents.onDisconnected += self.__onDisconnected

    def _dispose(self):
        g_playerEvents.onDisconnected -= self.__onDisconnected
        if not self.isLogOff:
            BigWorld.worldDrawEnabled(True)
        super(TenYearsEventHubPageOverlay, self)._dispose()

    def __onDisconnected(self):
        self.isLogOff = True
