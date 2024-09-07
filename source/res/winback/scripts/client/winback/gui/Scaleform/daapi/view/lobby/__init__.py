# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/Scaleform/daapi/view/lobby/__init__.py
from frameworks.wulf import WindowFlags, ViewFlags, WindowLayer
from gui.Scaleform.framework import ScopeTemplates, ViewSettings, ComponentSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.genConsts.WINBACK_ALIASES import WINBACK_ALIASES
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared.event_bus import EVENT_BUS_SCOPE
from winback_browser_view import WinbackBrowserView

def getContextMenuHandlers():
    pass


def getViewSettings():
    from winback.gui.Scaleform.daapi.view.lobby.hangar.entry_points.winback_entry_point import WinbackEntryPointWidget
    return (ViewSettings(WINBACK_ALIASES.WINBACK_BROWSER_VIEW, WinbackBrowserView, 'browserScreen.swf', WindowLayer.TOP_SUB_VIEW, WINBACK_ALIASES.WINBACK_BROWSER_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE), ComponentSettings(HANGAR_ALIASES.WINBACK_WIDGET, WinbackEntryPointWidget, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (WinbackPackageBusinessHandler(),)


class WinbackPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((WINBACK_ALIASES.WINBACK_BROWSER_VIEW, self.loadViewByCtxEvent),)
        super(WinbackPackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
