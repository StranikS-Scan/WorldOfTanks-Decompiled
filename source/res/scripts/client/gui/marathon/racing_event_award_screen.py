# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/marathon/racing_event_award_screen.py
from gui.Scaleform.daapi.view.lobby.shared.web_overlay_base import WebOverlayBase

class RacingEventAwardScreen(WebOverlayBase):

    def webHandlers(self):
        from gui.marathon.web_handlers import createRacingEventWebHandlers
        return createRacingEventWebHandlers()
