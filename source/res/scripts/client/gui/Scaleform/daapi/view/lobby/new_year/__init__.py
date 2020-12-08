# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/new_year/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.framework import ScopeTemplates
    from gui.Scaleform.daapi.view.lobby.new_year.ny_main_view import NYMainView
    from gui.Scaleform.framework import ViewSettings, ComponentSettings
    from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
    from gui.Scaleform.daapi.view.lobby.new_year.ny_menu_component import NYMainMenuUBInject
    from gui.Scaleform.daapi.view.lobby.new_year.ny_gameface_component import NYMainViewGFInject
    from gui.Scaleform.daapi.view.lobby.new_year.ny_unbound_component import NYMainViewUBInject
    from gui.Scaleform.daapi.view.lobby.new_year.ny_sidebar_component import NYSidebarUBInject
    return (ViewSettings(VIEW_ALIAS.NY_MAIN_VIEW, NYMainView, 'nyMainView.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.NY_MAIN_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     ComponentSettings(HANGAR_ALIASES.NY_MAIN_VIEW_MAIN_MENU_INJECT, NYMainMenuUBInject, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.NY_MAIN_VIEW_SIDEBAR_UB_INJECT, NYSidebarUBInject, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.NY_MAIN_VIEW_GF_INJECT, NYMainViewGFInject, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.NY_MAIN_VIEW_UB_INJECT, NYMainViewUBInject, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (_NYBusinessHandler(),)


class InjectWithContext(InjectComponentAdaptor):
    __slots__ = ('__ctx',)

    def __init__(self, ctx):
        super(InjectWithContext, self).__init__()
        self.__ctx = ctx

    def _makeInjectView(self):
        return self._getInjectViewClass()(ctx=self.__ctx)

    def _getInjectViewClass(self):
        raise NotImplementedError


class _NYBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.NY_MAIN_VIEW, self.loadViewByCtxEvent),)
        super(_NYBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
