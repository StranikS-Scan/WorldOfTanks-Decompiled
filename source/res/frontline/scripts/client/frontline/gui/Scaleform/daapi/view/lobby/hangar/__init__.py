# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/Scaleform/daapi/view/lobby/hangar/__init__.py
from gui.Scaleform.framework import WindowLayer, ScopeTemplates, ViewSettings
from frontline.constants.aliases import FrontlineHangarAliases
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared.event_bus import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    pass


def getViewSettings():
    from frontline.gui.impl.lobby.hangar_view import FrontlineHangarWindow
    return (ViewSettings(FrontlineHangarAliases.FRONTLINE_LOBBY_HANGAR, FrontlineHangarWindow, '', WindowLayer.SUB_VIEW, FrontlineHangarAliases.FRONTLINE_LOBBY_HANGAR, ScopeTemplates.LOBBY_SUB_SCOPE),)


def getBusinessHandlers():
    return (FrontlinePackageBusinessHandler(),)


class FrontlinePackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((FrontlineHangarAliases.FRONTLINE_LOBBY_HANGAR, self.loadViewByCtxEvent),)
        super(FrontlinePackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
