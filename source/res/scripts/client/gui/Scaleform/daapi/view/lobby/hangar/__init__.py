# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/__init__.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewSettings, GroupedViewSettings, ViewTypes, ScopeTemplates, ConditionalViewSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.daapi.view.bootcamp.component_override import BootcampComponentOverride

def getContextMenuHandlers():
    from gui.Scaleform.daapi.view.lobby.hangar import hangar_cm_handlers
    from gui.Scaleform.daapi.view.bootcamp.bootcamp_cm_handlers import BCVehicleContextMenuHandler
    from gui.Scaleform.daapi.view.bootcamp.bootcamp_cm_handlers import BCCrewContextMenuHandler
    from gui.Scaleform.daapi.view.bootcamp.bootcamp_cm_handlers import BCTechnicalMaintenanceCMHandler
    return ((CONTEXT_MENU_HANDLER_TYPE.CREW, BootcampComponentOverride(hangar_cm_handlers.CrewContextMenuHandler, BCCrewContextMenuHandler)), (CONTEXT_MENU_HANDLER_TYPE.VEHICLE, BootcampComponentOverride(hangar_cm_handlers.VehicleContextMenuHandler, BCVehicleContextMenuHandler)), (CONTEXT_MENU_HANDLER_TYPE.TECHNICAL_MAINTENANCE, BootcampComponentOverride(hangar_cm_handlers.TechnicalMaintenanceCMHandler, BCTechnicalMaintenanceCMHandler)))


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
    from gui.Scaleform.daapi.view.lobby.hangar.filter_popover import TankCarouselFilterPopover
    from gui.Scaleform.daapi.view.lobby.hangar.carousels import TankCarousel
    from gui.Scaleform.daapi.view.lobby.hangar.carousels import RankedTankCarousel
    from gui.Scaleform.daapi.view.lobby.hangar.academy import Academy
    from gui.Scaleform.daapi.view.lobby.hangar.StrongholdView import StrongholdView
    from gui.Scaleform.daapi.view.lobby.hangar.BrowserView import BrowserView
    from gui.Scaleform.daapi.view.lobby.hangar.hangar_header import HangarHeader
    from gui.Scaleform.daapi.view.lobby.shared.fitting_select_popover import HangarFittingSelectPopover
    from gui.Scaleform.daapi.view.lobby.shared.fitting_select_popover import OptionalDeviceSelectPopover
    from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_fitting_popover import VehCmpConfigSelectPopover
    from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_fitting_popover import VehCmpBattleBoosterSelectPopover
    from gui.Scaleform.daapi.view.lobby.shared.fitting_select_popover import BattleBoosterSelectPopover
    from gui.Scaleform.daapi.view.lobby.booster_buy_window import BoosterBuyWindow
    from gui.Scaleform.daapi.view.lobby.hangar.ranked_battles_widget import RankedBattlesWidget
    from gui.Scaleform.daapi.view.lobby.hangar.alert_message_block import AlertMessageBlock
    from gui.Scaleform.daapi.view.bootcamp.BCResearchPanel import BCResearchPanel
    from gui.Scaleform.daapi.view.bootcamp.BCAmmunitionPanel import BCAmmunitionPanel
    from gui.Scaleform.daapi.view.bootcamp.BCTankCarousel import BCTankCarousel
    from gui.Scaleform.daapi.view.bootcamp.BCHangarHeader import BCHangarHeader
    from gui.Scaleform.daapi.view.bootcamp.BCCrew import BCCrew
    from gui.Scaleform.daapi.view.bootcamp.BCHangar import BCHangar
    from gui.Scaleform.daapi.view.bootcamp.BCTechnicalMaintenance import BCTechnicalMaintenance
    return (ConditionalViewSettings(VIEW_ALIAS.LOBBY_HANGAR, BootcampComponentOverride(Hangar, BCHangar), 'hangar.swf', ViewTypes.LOBBY_SUB, None, VIEW_ALIAS.LOBBY_HANGAR, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.LOBBY_ACADEMY, Academy, 'academyView.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.LOBBY_ACADEMY, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.LOBBY_STRONGHOLD, StrongholdView, 'StrongholdView.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.LOBBY_STRONGHOLD, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.BROWSER_VIEW, BrowserView, 'browserView.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.BROWSER_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     GroupedViewSettings(VIEW_ALIAS.CREW_ABOUT_DOG_WINDOW, CrewAboutDogWindow, 'simpleWindow.swf', ViewTypes.WINDOW, 'aboutDogWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     ConditionalViewSettings(VIEW_ALIAS.TECHNICAL_MAINTENANCE, BootcampComponentOverride(TechnicalMaintenance, BCTechnicalMaintenance), 'technicalMaintenance.swf', ViewTypes.WINDOW, '', None, BootcampComponentOverride(ScopeTemplates.DEFAULT_SCOPE, ScopeTemplates.LOBBY_SUB_SCOPE)),
     GroupedViewSettings(VIEW_ALIAS.BOOSTER_BUY_WINDOW, BoosterBuyWindow, 'boosterBuyWindow.swf', ViewTypes.WINDOW, VIEW_ALIAS.BOOSTER_BUY_WINDOW, None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.TANK_CAROUSEL_FILTER_POPOVER, TankCarouselFilterPopover, 'filtersPopoverView.swf', ViewTypes.WINDOW, VIEW_ALIAS.TANK_CAROUSEL_FILTER_POPOVER, VIEW_ALIAS.TANK_CAROUSEL_FILTER_POPOVER, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.FITTING_SELECT_POPOVER, HangarFittingSelectPopover, 'fittingSelectPopover.swf', ViewTypes.WINDOW, VIEW_ALIAS.FITTING_SELECT_POPOVER, VIEW_ALIAS.FITTING_SELECT_POPOVER, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.FITTING_CMP_SELECT_POPOVER, VehCmpConfigSelectPopover, 'fittingSelectPopover.swf', ViewTypes.WINDOW, VIEW_ALIAS.FITTING_CMP_SELECT_POPOVER, VIEW_ALIAS.FITTING_CMP_SELECT_POPOVER, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.BOOSTER_CMP_SELECT_POPOVER, VehCmpBattleBoosterSelectPopover, 'fittingSelectPopover.swf', ViewTypes.WINDOW, VIEW_ALIAS.BOOSTER_CMP_SELECT_POPOVER, VIEW_ALIAS.BOOSTER_CMP_SELECT_POPOVER, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.BOOSTER_SELECT_POPOVER, BattleBoosterSelectPopover, 'fittingSelectPopover.swf', ViewTypes.WINDOW, VIEW_ALIAS.BOOSTER_SELECT_POPOVER, VIEW_ALIAS.BOOSTER_SELECT_POPOVER, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.OPT_DEVICES_SELECT_POPOVER, OptionalDeviceSelectPopover, 'fittingSelectPopover.swf', ViewTypes.WINDOW, VIEW_ALIAS.OPT_DEVICES_SELECT_POPOVER, VIEW_ALIAS.OPT_DEVICES_SELECT_POPOVER, ScopeTemplates.DEFAULT_SCOPE),
     ConditionalViewSettings(HANGAR_ALIASES.AMMUNITION_PANEL, BootcampComponentOverride(AmmunitionPanel, BCAmmunitionPanel), None, ViewTypes.COMPONENT, None, None, ScopeTemplates.DEFAULT_SCOPE),
     ConditionalViewSettings(HANGAR_ALIASES.RESEARCH_PANEL, BootcampComponentOverride(ResearchPanel, BCResearchPanel), None, ViewTypes.COMPONENT, None, None, ScopeTemplates.DEFAULT_SCOPE),
     ConditionalViewSettings(HANGAR_ALIASES.HEADER, BootcampComponentOverride(HangarHeader, BCHangarHeader), None, ViewTypes.COMPONENT, None, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.SWITCH_MODE_PANEL, SwitchModePanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ConditionalViewSettings(HANGAR_ALIASES.TANK_CAROUSEL, BootcampComponentOverride(TankCarousel, BCTankCarousel), None, ViewTypes.COMPONENT, None, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(HANGAR_ALIASES.RANKED_TANK_CAROUSEL, RankedTankCarousel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(HANGAR_ALIASES.TMEN_XP_PANEL, TmenXpPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(HANGAR_ALIASES.VEHICLE_PARAMETERS, VehicleParameters, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ConditionalViewSettings(HANGAR_ALIASES.CREW, BootcampComponentOverride(Crew, BCCrew), None, ViewTypes.COMPONENT, None, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(HANGAR_ALIASES.RANKED_WIDGET, RankedBattlesWidget, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(HANGAR_ALIASES.ALERT_MESSAGE_BLOCK, AlertMessageBlock, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (HangarPackageBusinessHandler(),)


class HangarPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.TANK_CAROUSEL_FILTER_POPOVER, self.loadViewByCtxEvent),
         (VIEW_ALIAS.CREW_ABOUT_DOG_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOBBY_HANGAR, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOBBY_ACADEMY, self.loadAcademy),
         (VIEW_ALIAS.LOBBY_STRONGHOLD, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BROWSER_VIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.TECHNICAL_MAINTENANCE, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BOOSTER_BUY_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.FITTING_SELECT_POPOVER, self.loadViewByCtxEvent),
         (VIEW_ALIAS.FITTING_CMP_SELECT_POPOVER, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BOOSTER_CMP_SELECT_POPOVER, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BOOSTER_SELECT_POPOVER, self.loadViewByCtxEvent),
         (VIEW_ALIAS.OPT_DEVICES_SELECT_POPOVER, self.loadViewByCtxEvent),
         (VIEW_ALIAS.VEHICLES_FILTER_POPOVER, self.loadViewByCtxEvent))
        super(HangarPackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)

    def loadAcademy(self, event):
        view = self.findViewByAlias(ViewTypes.LOBBY_SUB, VIEW_ALIAS.LOBBY_ACADEMY)
        if view is not None:
            view.reload()
        else:
            self.loadViewByCtxEvent(event)
        return
