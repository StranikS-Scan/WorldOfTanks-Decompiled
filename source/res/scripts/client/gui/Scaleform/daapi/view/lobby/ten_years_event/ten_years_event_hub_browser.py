# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/ten_years_event/ten_years_event_hub_browser.py
import BigWorld
from gui.Scaleform.daapi.view.lobby.shared.web_view import WebView
from gui.Scaleform.daapi.view.lobby.ten_years_event.web_handlers import createTenYearsEventWebHandlers

class TenYearsEventHubPageOverlay(WebView):

    def webHandlers(self):
        return createTenYearsEventWebHandlers()

    def _populate(self):
        super(TenYearsEventHubPageOverlay, self)._populate()
        BigWorld.worldDrawEnabled(False)

    def _dispose(self):
        BigWorld.worldDrawEnabled(True)
        super(TenYearsEventHubPageOverlay, self)._dispose()
