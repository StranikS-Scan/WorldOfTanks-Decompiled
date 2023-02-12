# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_video_browser_view.py
from gui.Scaleform.daapi.view.lobby.shared.web_view import WebView
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE

class BattlePassVideoBrowserView(WebView):

    def _dispose(self):
        g_eventBus.handleEvent(events.BattlePassEvent(events.BattlePassEvent.VIDEO_SHOWN), scope=EVENT_BUS_SCOPE.LOBBY)
        super(BattlePassVideoBrowserView, self)._dispose()
