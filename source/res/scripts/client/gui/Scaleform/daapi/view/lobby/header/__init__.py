# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/header/__init__.py
from __future__ import absolute_import
from frameworks.wulf import WindowLayer
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import GroupedViewSettings, ScopeTemplates
from gui.Scaleform.framework.package_layout import PackageBusinessHandler

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.header.BattleTypeSelectPopover import BattleTypeSelectPopover
    from gui.Scaleform.daapi.view.lobby.header.SquadTypeSelectPopover import SquadTypeSelectPopover
    from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import LobbyHeader
    return (GroupedViewSettings(VIEW_ALIAS.BATTLE_TYPE_SELECT_POPOVER, BattleTypeSelectPopover, 'itemSelectorPopover.swf', WindowLayer.WINDOW, VIEW_ALIAS.BATTLE_TYPE_SELECT_POPOVER, VIEW_ALIAS.BATTLE_TYPE_SELECT_POPOVER, ScopeTemplates.DEFAULT_SCOPE), GroupedViewSettings(VIEW_ALIAS.SQUAD_TYPE_SELECT_POPOVER, SquadTypeSelectPopover, 'itemSelectorPopover.swf', WindowLayer.WINDOW, VIEW_ALIAS.SQUAD_TYPE_SELECT_POPOVER, VIEW_ALIAS.SQUAD_TYPE_SELECT_POPOVER, ScopeTemplates.DEFAULT_SCOPE), GroupedViewSettings(VIEW_ALIAS.LOBBY_HEADER, LobbyHeader, None, WindowLayer.UNDEFINED, None, None, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (HeaderPackageBusinessHandler(),)


class HeaderPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.BATTLE_TYPE_SELECT_POPOVER, self.loadViewByCtxEvent), (VIEW_ALIAS.SQUAD_TYPE_SELECT_POPOVER, self.loadViewByCtxEvent))
        super(HeaderPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
