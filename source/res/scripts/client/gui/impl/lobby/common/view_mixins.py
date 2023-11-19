# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/common/view_mixins.py
from collections import namedtuple
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState, LobbyHeaderVisibilityAction
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
LobbyHeaderState = namedtuple('LobbyHeaderState', ('view', 'state', 'action'))

class LobbyHeaderVisibility(object):
    __slots__ = ()

    @classmethod
    def suspendLobbyHeader(cls, sourceView, state=HeaderMenuVisibilityState.NOTHING):
        cls._toggleLobbyHeaderVisibility(sourceView, state, action=LobbyHeaderVisibilityAction.ENTER)

    @classmethod
    def resumeLobbyHeader(cls, sourceView, state=HeaderMenuVisibilityState.ALL):
        cls._toggleLobbyHeaderVisibility(sourceView, state, action=LobbyHeaderVisibilityAction.EXIT)

    @classmethod
    def _toggleLobbyHeaderVisibility(cls, sourceView, state, action):
        state = LobbyHeaderState(sourceView, state, action)
        event = events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': state})
        g_eventBus.handleEvent(event, EVENT_BUS_SCOPE.LOBBY)
