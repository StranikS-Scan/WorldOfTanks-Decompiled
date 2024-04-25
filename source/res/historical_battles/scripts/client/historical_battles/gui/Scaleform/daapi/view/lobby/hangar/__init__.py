# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/lobby/hangar/__init__.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from historical_battles.gui.Scaleform.daapi.view.lobby.hangar.entry_point import EntryPoint
from gui.Scaleform.framework import ScopeTemplates, ComponentSettings
from historical_battles.gui.Scaleform.daapi.view.lobby.header.hb_lobby_header import HBLobbyHeader

def getContextMenuHandlers():
    pass


def getViewSettings():
    return (ComponentSettings(HANGAR_ALIASES.SE22_EVENT_ENTRY_POINT, EntryPoint, ScopeTemplates.DEFAULT_SCOPE), ComponentSettings(VIEW_ALIAS.LOBBY_HEADER, HBLobbyHeader, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    pass
