# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/lock_overlays.py
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.shared.events import LobbySimpleEvent

def lockOverlays(lock, source=__name__):
    ctx = {'source': source,
     'lock': lock}
    g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.LOCK_OVERLAY_SCREEN, ctx), EVENT_BUS_SCOPE.LOBBY)
