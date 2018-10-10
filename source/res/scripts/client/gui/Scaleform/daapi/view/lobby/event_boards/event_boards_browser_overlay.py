# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_boards/event_boards_browser_overlay.py
from gui.Scaleform.daapi.view.lobby.event_boards.browser_in_view_component import BrowserInViewComponent

class EventBoardsBrowserOverlay(BrowserInViewComponent):

    def setOpener(self, view):
        self.setUrl(view.ctx.get('url'))
        self.as_setTitleS(view.ctx.get('title'))
