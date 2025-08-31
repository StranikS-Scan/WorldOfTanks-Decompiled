# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/lobby/header/__init__.py
from __future__ import absolute_import
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ScopeTemplates, ComponentSettings
from white_tiger.gui.Scaleform.daapi.view.lobby.header.wt_lobby_header import WTLobbyHeader

def getContextMenuHandlers():
    pass


def getViewSettings():
    return (ComponentSettings(VIEW_ALIAS.LOBBY_HEADER, WTLobbyHeader, ScopeTemplates.DEFAULT_SCOPE),)


def getBusinessHandlers():
    pass
