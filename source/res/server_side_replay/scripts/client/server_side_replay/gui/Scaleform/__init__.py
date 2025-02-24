# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: server_side_replay/scripts/client/server_side_replay/gui/Scaleform/__init__.py
from gui.shared.system_factory import registerLobbyHeaderTab
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import LobbyHeaderTabInfo
from gui.Scaleform.genConsts.SERVERSIDEREPLAY_ALIASES import SERVERSIDEREPLAY_ALIASES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl.gen import R
from server_side_replay.gui.shared.event_dispatcher import showReplays

def registerLobbyHeaderTabs():
    registerLobbyHeaderTab(SERVERSIDEREPLAY_ALIASES.LOBBY_REPLAYS, LobbyHeaderTabInfo(wulfAlias=R.views.server_side_replay.lobby.MetaReplaysView(), label=R.strings.menu.headerButtons.replays(), tooltip=TOOLTIPS.HEADER_BUTTONS_REPLAYS, showFunction=showReplays, conditionFunction=lambda lobbyHeader: lobbyHeader.itemsCache.items.stats.isSsrPlayEnabled))
