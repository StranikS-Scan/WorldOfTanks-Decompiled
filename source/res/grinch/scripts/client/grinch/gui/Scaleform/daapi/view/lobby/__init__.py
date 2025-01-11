# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/Scaleform/daapi/view/lobby/__init__.py
from grinch.gui.Scaleform.genConsts.GRINCH_HANGAR_ALIASES import GRINCH_HANGAR_ALIASES
from gui.Scaleform.framework import ScopeTemplates, ComponentSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared.event_bus import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    pass


def getViewSettings():
    from grinch.gui.Scaleform.daapi.view.lobby.header.grinch_banner_entry_point import GrinchBannerEntryPoint
    return (ComponentSettings(GRINCH_HANGAR_ALIASES.GRINCH_ENTRY_POINT, GrinchBannerEntryPoint, ScopeTemplates.DEFAULT_SCOPE),)


def getBusinessHandlers():
    return (GrinchLobbyBusinessHandler(),)


class GrinchLobbyBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ()
        super(GrinchLobbyBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
