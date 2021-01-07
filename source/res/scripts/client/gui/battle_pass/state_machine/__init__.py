# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/state_machine/__init__.py
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.shared.events import LobbySimpleEvent
_LOCK_SOURCE_NAME = 'FINAL_REWARD_STATE_MACHINE'

def lockOverlays(lock):
    ctx = {'source': _LOCK_SOURCE_NAME,
     'lock': lock}
    g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.LOCK_OVERLAY_SCREEN, ctx), EVENT_BUS_SCOPE.LOBBY)
