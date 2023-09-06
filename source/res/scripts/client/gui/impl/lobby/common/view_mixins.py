# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/common/view_mixins.py
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE

class LobbyHeaderVisibility(object):
    __slots__ = ()

    @classmethod
    def suspendLobbyHeader(cls, state=HeaderMenuVisibilityState.NOTHING):
        cls._toggleLobbyHeaderVisibility(state)

    @classmethod
    def resumeLobbyHeader(cls, state=HeaderMenuVisibilityState.ALL):
        cls._toggleLobbyHeaderVisibility(state)

    @classmethod
    def _toggleLobbyHeaderVisibility(cls, state):
        event = events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': state})
        g_eventBus.handleEvent(event, EVENT_BUS_SCOPE.LOBBY)
