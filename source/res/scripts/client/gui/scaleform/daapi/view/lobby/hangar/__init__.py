# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/__init__.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.shared.fitting_select_popover import FittingSelectPopover
from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_fitting_popover import VehCmpConfigSelectPopover
from gui.Scaleform.framework import ViewSettings, GroupedViewSettings, ViewTypes, ScopeTemplates
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    from gui.Scaleform.daapi.view.lobby.hangar import hangar_cm_handlers
    return ((CONTEXT_MENU_HANDLER_TYPE.CREW, hangar_cm_handlers.CrewContextMenuHandler), (CONTEXT_MENU_HANDLER_TYPE.VEHICLE, hangar_cm_handlers.VehicleContextMenuHandler), (CONTEXT_MENU_HANDLER_TYPE.TECHNICAL_MAINTENANCE, hangar_cm_handlers.TechnicalMaintenanceCMHandler))


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.hangar.AmmunitionPanel import AmmunitionPanel
    from gui.Scaleform.daapi.view.lobby.hangar.Crew import Crew
    from gui.Scaleform.daapi.view.lobby.hangar.CrewAboutDogWindow import CrewAboutDogWindow
    from gui.Scaleform.daapi.view.lobby.hangar.Hangar import Hangar
    from gui.Scaleform.daapi.view.lobby.hangar.ResearchPanel import ResearchPanel
    from gui.Scaleform.daapi.view.lobby.hangar.SwitchModePanel import SwitchModePanel
    from gui.Scaleform.daapi.view.lobby.hangar.TechnicalMaintenance import TechnicalMaintenance
    from gui.Scaleform.daapi.view.lobby.hangar.TmenXpPanel import TmenXpPanel
    from gui.Scaleform.daapi.view.lobby.hangar.VehicleParameters import VehicleParameters
    from gui.Scaleform.daapi.view.lobby.hangar.filter_popover import FilterPopover
    from gui.Scaleform.daapi.view.lobby.hangar.carousels import TankCarousel
    from gui.Scaleform.daapi.view.lobby.hangar.carousels import FalloutTankCarousel
    from gui.Scaleform.daapi.view.lobby.hangar.academy import Academy
    from gui.Scaleform.daapi.view.lobby.hangar.Fortifications2View import Fortifications2View
    from gui.Scaleform.daapi.view.lobby.hangar.hangar_header import HangarHeader
    return (ViewSettings(VIEW_ALIAS.LOBBY_HANGAR, Hangar, 'hangar.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.LOBBY_HANGAR, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.LOBBY_ACADEMY, Academy, 'academyView.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.LOBBY_ACADEMY, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.FORTIFICATIONS2_VIEW, Fortifications2View, 'Fortifications2View.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.FORTIFICATIONS2_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.CREW_ABOUT_DOG_WINDOW, CrewAboutDogWindow, 'simpleWindow.swf', ViewTypes.WINDOW, 'aboutDogWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.TECHNICAL_MAINTENANCE, TechnicalMaintenance, 'technicalMaintenance.swf', ViewTypes.WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.TANK_CAROUSEL_FILTER_POPOVER, FilterPopover, 'filtersPopoverView.swf', ViewTypes.WINDOW, VIEW_ALIAS.TANK_CAROUSEL_FILTER_POPOVER, VIEW_ALIAS.TANK_CAROUSEL_FILTER_POPOVER, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.FITTING_SELECT_POPOVER, FittingSelectPopover, 'fittingSelectPopover.swf', ViewTypes.WINDOW, VIEW_ALIAS.FITTING_SELECT_POPOVER, VIEW_ALIAS.FITTING_SELECT_POPOVER, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.FITTING_CMP_SELECT_POPOVER, VehCmpConfigSelectPopover, 'fittingSelectPopover.swf', ViewTypes.WINDOW, VIEW_ALIAS.FITTING_CMP_SELECT_POPOVER, VIEW_ALIAS.FITTING_CMP_SELECT_POPOVER, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(HANGAR_ALIASES.AMMUNITION_PANEL, AmmunitionPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(HANGAR_ALIASES.RESEARCH_PANEL, ResearchPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(HANGAR_ALIASES.HEADER, HangarHeader, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.SWITCH_MODE_PANEL, SwitchModePanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(HANGAR_ALIASES.TANK_CAROUSEL, TankCarousel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(HANGAR_ALIASES.FALLOUT_TANK_CAROUSEL, FalloutTankCarousel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(HANGAR_ALIASES.TMEN_XP_PANEL, TmenXpPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(HANGAR_ALIASES.VEHICLE_PARAMETERS, VehicleParameters, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(HANGAR_ALIASES.CREW, Crew, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (HangarPackageBusinessHandler(),)


class HangarPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.TANK_CAROUSEL_FILTER_POPOVER, self.loadViewByCtxEvent),
         (VIEW_ALIAS.CREW_ABOUT_DOG_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOBBY_HANGAR, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOBBY_ACADEMY, self.loadAcademy),
         (VIEW_ALIAS.FORTIFICATIONS2_VIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.TECHNICAL_MAINTENANCE, self.loadViewByCtxEvent),
         (VIEW_ALIAS.FITTING_SELECT_POPOVER, self.loadViewByCtxEvent),
         (VIEW_ALIAS.FITTING_CMP_SELECT_POPOVER, self.loadViewByCtxEvent))
        super(HangarPackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)

    def loadAcademy(self, event):
        view = self.findViewByAlias(ViewTypes.LOBBY_SUB, VIEW_ALIAS.LOBBY_ACADEMY)
        if view is not None:
            view.reload()
        else:
            self.loadViewByCtxEvent(event)
        return
