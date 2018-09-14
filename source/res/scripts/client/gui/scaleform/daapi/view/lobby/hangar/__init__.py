# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/__init__.py
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewSettings, GroupedViewSettings, ViewTypes, ScopeTemplates
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.managers.context_menu import ContextMenuManager
ContextMenuManager.registerHandler(CONTEXT_MENU_HANDLER_TYPE.CREW, 'gui.Scaleform.daapi.view.lobby.hangar.hangar_cm_handlers', 'CrewContextMenuHandler')
ContextMenuManager.registerHandler(CONTEXT_MENU_HANDLER_TYPE.VEHICLE, 'gui.Scaleform.daapi.view.lobby.hangar.hangar_cm_handlers', 'VehicleContextMenuHandler')
ContextMenuManager.registerHandler(CONTEXT_MENU_HANDLER_TYPE.TECHNICAL_MAINTENANCE, 'gui.Scaleform.daapi.view.lobby.hangar.hangar_cm_handlers', 'TechnicalMaintenanceCMHandler')

def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.hangar.AmmunitionPanel import AmmunitionPanel
    from gui.Scaleform.daapi.view.lobby.hangar.Crew import Crew
    from gui.Scaleform.daapi.view.lobby.hangar.CrewAboutDogWindow import CrewAboutDogWindow
    from gui.Scaleform.daapi.view.lobby.hangar.Hangar import Hangar
    from gui.Scaleform.daapi.view.lobby.hangar.Params import Params
    from gui.Scaleform.daapi.view.lobby.hangar.ResearchPanel import ResearchPanel
    from gui.Scaleform.daapi.view.lobby.hangar.SwitchModePanel import SwitchModePanel
    from gui.Scaleform.daapi.view.lobby.hangar.TankCarousel import TankCarousel
    from gui.Scaleform.daapi.view.lobby.hangar.TechnicalMaintenance import TechnicalMaintenance
    from gui.Scaleform.daapi.view.lobby.hangar.TmenXpPanel import TmenXpPanel
    return (ViewSettings(VIEW_ALIAS.LOBBY_HANGAR, Hangar, 'hangar.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.LOBBY_HANGAR, ScopeTemplates.LOBBY_SUB_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.CREW_ABOUT_DOG_WINDOW, CrewAboutDogWindow, 'simpleWindow.swf', ViewTypes.WINDOW, 'aboutDogWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.TECHNICAL_MAINTENANCE, TechnicalMaintenance, 'technicalMaintenance.swf', ViewTypes.WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(Hangar.COMPONENTS.AMMO_PANEL, AmmunitionPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(Hangar.COMPONENTS.RESEARCH_PANEL, ResearchPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.SWITCH_MODE_PANEL, SwitchModePanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(Hangar.COMPONENTS.CAROUSEL, TankCarousel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(Hangar.COMPONENTS.TMEN_XP_PANEL, TmenXpPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(Hangar.COMPONENTS.PARAMS, Params, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(Hangar.COMPONENTS.CREW, Crew, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (HangarPackageBusinessHandler(),)


class HangarPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.CREW_ABOUT_DOG_WINDOW, self.loadViewByCtxEvent), (VIEW_ALIAS.LOBBY_HANGAR, self.loadViewByCtxEvent), (VIEW_ALIAS.TECHNICAL_MAINTENANCE, self.loadViewByCtxEvent))
        super(HangarPackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
