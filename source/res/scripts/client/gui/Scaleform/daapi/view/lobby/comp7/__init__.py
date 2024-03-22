# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/comp7/__init__.py
from gui.Scaleform.framework import WindowLayer, ScopeTemplates, ViewSettings, ComponentSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared.event_bus import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.comp7.comp7_prime_time_view import Comp7PrimeTimeView
    from gui.Scaleform.daapi.view.lobby.comp7.comp7_entry_point import Comp7EntryPoint
    return (ViewSettings(HANGAR_ALIASES.COMP7_PRIME_TIME_ALIAS, Comp7PrimeTimeView, HANGAR_ALIASES.COMP7_PRIME_TIME, WindowLayer.SUB_VIEW, HANGAR_ALIASES.COMP7_PRIME_TIME_ALIAS, ScopeTemplates.LOBBY_SUB_SCOPE, True), ComponentSettings(HANGAR_ALIASES.COMP7_ENTRY_POINT, Comp7EntryPoint, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (Comp7PackageBusinessHandler(),)


class Comp7PackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((HANGAR_ALIASES.COMP7_PRIME_TIME_ALIAS, self.loadViewByCtxEvent),)
        super(Comp7PackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
