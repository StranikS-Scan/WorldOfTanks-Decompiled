# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/boosters/__init__.py
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewSettings, GroupedViewSettings, ViewTypes, ScopeTemplates
from gui.Scaleform.framework.package_layout import PackageBusinessHandler

def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.boosters.BoostersPanelComponent import BoostersPanelComponent
    from gui.Scaleform.daapi.view.lobby.boosters.BoostersWindow import BoostersWindow
    return (GroupedViewSettings(VIEW_ALIAS.BOOSTERS_WINDOW, BoostersWindow, 'boostersWindow.swf', ViewTypes.WINDOW, 'BoostersWindow', None, ScopeTemplates.DEFAULT_SCOPE), ViewSettings(VIEW_ALIAS.BOOSTERS_PANEL, BoostersPanelComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (BoostersPackageBusinessHandler(),)


class BoostersPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.BOOSTERS_WINDOW, self.loadViewByCtxEvent),)
        super(BoostersPackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
