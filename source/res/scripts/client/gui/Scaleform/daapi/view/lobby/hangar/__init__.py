# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.bootcamp.component_override import BootcampComponentOverride
from gui.Scaleform.daapi.view.lobby.hangar.crew_panel_inject import CrewPanelInject
from gui.Scaleform.framework import ViewSettings, GroupedViewSettings, ScopeTemplates, ConditionalViewSettings, ComponentSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    from gui.Scaleform.daapi.view.lobby.hangar import hangar_cm_handlers
    from gui.Scaleform.daapi.view.bootcamp.bootcamp_cm_handlers import BCVehicleContextMenuHandler
    from gui.Scaleform.daapi.view.bootcamp.bootcamp_cm_handlers import BCTechnicalMaintenanceCMHandler
    from gui.impl.lobby.crew.widget.crew_widget_cm_handlers import CrewContextMenuHandler
    from gui.impl.lobby.crew.crew_cm_handlers import CrewTankmanContextMenuHandler
    return ((CONTEXT_MENU_HANDLER_TYPE.VEHICLE, BootcampComponentOverride(hangar_cm_handlers.VehicleContextMenuHandler, BCVehicleContextMenuHandler)),
     (CONTEXT_MENU_HANDLER_TYPE.TECHNICAL_MAINTENANCE, BootcampComponentOverride(hangar_cm_handlers.TechnicalMaintenanceCMHandler, BCTechnicalMaintenanceCMHandler)),
     (CONTEXT_MENU_HANDLER_TYPE.CREW_MEMBER, CrewContextMenuHandler),
     (CONTEXT_MENU_HANDLER_TYPE.CREW_TANKMAN, CrewTankmanContextMenuHandler))


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.hangar.ammunition_panel import AmmunitionPanel
    from gui.Scaleform.daapi.view.lobby.hangar.Hangar import Hangar
    from gui.Scaleform.daapi.view.lobby.hangar.ResearchPanel import ResearchPanel
    from gui.Scaleform.daapi.view.lobby.hangar.SwitchModePanel import SwitchModePanel
    from gui.Scaleform.daapi.view.lobby.hangar.VehicleParameters import VehicleParameters
    from gui.Scaleform.daapi.view.common.filter_popover import TankCarouselFilterPopover, BattlePassCarouselFilterPopover, BattleRoyaleCarouselFilterPopover
    from gui.Scaleform.daapi.view.lobby.hangar.carousels import TankCarousel
    from gui.Scaleform.daapi.view.lobby.hangar.carousels import RankedTankCarousel
    from gui.Scaleform.daapi.view.lobby.hangar.carousels import EpicBattleTankCarousel
    from gui.Scaleform.daapi.view.lobby.hangar.carousels import BattlePassTankCarousel
    from gui.Scaleform.daapi.view.lobby.hangar.carousels import MapboxTankCarousel
    from gui.Scaleform.daapi.view.lobby.hangar.carousels import Comp7TankCarousel
    from gui.Scaleform.daapi.view.lobby.hangar.StrongholdView import StrongholdView, StrongholdAdsView
    from gui.Scaleform.daapi.view.lobby.hangar.BrowserView import BrowserView
    from gui.Scaleform.daapi.view.lobby.hangar.hangar_header import HangarHeader
    from gui.Scaleform.daapi.view.lobby.shared.fitting_select_popover import ModuleFittingSelectPopover
    from gui.Scaleform.daapi.view.lobby.shared.web_view import WebView
    from gui.Scaleform.daapi.view.lobby.hangar.ranked_battles_widget import RankedBattlesHangarWidget
    from gui.Scaleform.daapi.view.lobby.hangar.battle_royale_widget import BattleRoyaleHangarWidget
    from gui.Scaleform.daapi.view.lobby.hangar.battle_royale_tournament_widget import BattleRoyaleTournamentHangarWidget
    from gui.Scaleform.daapi.view.lobby.hangar.alert_message_block import AlertMessageBlock
    from gui.Scaleform.daapi.view.bootcamp.BCResearchPanel import BCResearchPanel
    from gui.Scaleform.daapi.view.bootcamp.BCTankCarousel import BCTankCarousel
    from gui.Scaleform.daapi.view.bootcamp.BCHangarHeader import BCHangarHeader
    from gui.Scaleform.daapi.view.bootcamp.BCHangar import BCHangar
    from gui.Scaleform.daapi.view.bootcamp.bootcamp_quest_component import BootcampQuestComponent
    from gui.Scaleform.daapi.view.lobby.hangar.epic_battles_widget import EpicBattlesWidget
    from gui.Scaleform.daapi.view.lobby.manual.manual_main_view import ManualMainView
    from gui.Scaleform.daapi.view.lobby.manual.manual_chapter_view import ManualChapterView
    from gui.Scaleform.daapi.view.lobby.hangar.daily_quest_widget import DailyQuestWidget
    from gui.impl.lobby.new_year.widgets.ny_main_widget import NyMainWidgetInject
    from gui.impl.lobby.new_year.surprise_gift_entrypoint_view.surprise_gift_entrypoint_view import NyGiftWidgetInject
    from gui.impl.lobby.loot_box.reward_kit_entry_point import RewardKitEntrancePointInjectWidget
    from gui.Scaleform.daapi.view.lobby.hangar.progressive_reward_widget import ProgressiveRewardWidget
    from gui.Scaleform.daapi.view.lobby.hangar.ammunition_panel_inject import AmmunitionPanelInject
    from gui.impl.lobby.battle_pass.battle_pass_entry_point_view import BattlePassEntryPointComponent
    from gui.impl.lobby.battle_pass.battle_pass_secondary_entry_point import BattlePassSecondaryEntryPointWidget
    from gui.Scaleform.daapi.view.lobby.hangar.entry_points.event_entry_points_container import EventEntryPointsContainer
    from gui.Scaleform.daapi.view.lobby.hangar.entry_points.craftmachine_entry_point import CraftMachineEntryPoint
    from gui.Scaleform.daapi.view.lobby.hangar.entry_points.mapbox_entry_point import MapBoxEntryPoint
    from gui.Scaleform.daapi.view.lobby.hangar.entry_points.marathon_entry_point import MarathonEntryPoint
    from gui.Scaleform.daapi.view.lobby.hangar.battle_matters_entry_point import BattleMattersEntryPoint
    from gui.Scaleform.daapi.view.lobby.hangar.TournamentsView import TournamentsView
    from gui.impl.lobby.resource_well.entry_point import ResourceWellEntryPointComponent
    from gui.impl.lobby.personal_reserves.personal_reserves_widget_inject import PersonalReservesWidgetInject
    from gui.impl.lobby.comp7.main_widget import Comp7MainWidgetComponent
    from gui.Scaleform.daapi.view.lobby.hangar.carousel_event_entry_widget import CarouselEventEntryHolder
    from gui.Scaleform.daapi.view.lobby.hangar.battle_royale_widget import BattleRoyaleHangarWidgetInject
    from gui.Scaleform.daapi.view.lobby.hangar.entry_points.stronghold_entry_point import StrongholdEntryPoint
    from gui.Scaleform.daapi.view.lobby.hangar.prestige_hangar_entry_point_inject import PrestigeHangarEntryPointInject
    return (ConditionalViewSettings(VIEW_ALIAS.LOBBY_HANGAR, BootcampComponentOverride(Hangar, BCHangar), 'hangar.swf', WindowLayer.SUB_VIEW, None, VIEW_ALIAS.LOBBY_HANGAR, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.LOBBY_STRONGHOLD, StrongholdView, 'StrongholdView.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.LOBBY_STRONGHOLD, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.STRONGHOLD_ADS, StrongholdAdsView, 'browserScreen.swf', WindowLayer.TOP_SUB_VIEW, VIEW_ALIAS.STRONGHOLD_ADS, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.BROWSER_VIEW, BrowserView, 'browserScreen.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.BROWSER_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     ViewSettings(VIEW_ALIAS.LOBBY_TOURNAMENTS, TournamentsView, 'browserScreen.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.LOBBY_TOURNAMENTS, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     ViewSettings(VIEW_ALIAS.WIKI_VIEW, ManualMainView, 'manual.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.WIKI_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.MANUAL_BROWSER_VIEW, WebView, 'browserScreen.swf', WindowLayer.TOP_SUB_VIEW, VIEW_ALIAS.MANUAL_BROWSER_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.MANUAL_CHAPTER_VIEW, ManualChapterView, 'manualChapterView.swf', WindowLayer.TOP_SUB_VIEW, VIEW_ALIAS.MANUAL_CHAPTER_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     GroupedViewSettings(VIEW_ALIAS.TANK_CAROUSEL_FILTER_POPOVER, TankCarouselFilterPopover, 'filtersPopoverView.swf', WindowLayer.WINDOW, VIEW_ALIAS.TANK_CAROUSEL_FILTER_POPOVER, VIEW_ALIAS.TANK_CAROUSEL_FILTER_POPOVER, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.BATTLEPASS_CAROUSEL_FILTER_POPOVER, BattlePassCarouselFilterPopover, 'filtersPopoverView.swf', WindowLayer.WINDOW, VIEW_ALIAS.BATTLEPASS_CAROUSEL_FILTER_POPOVER, VIEW_ALIAS.BATTLEPASS_CAROUSEL_FILTER_POPOVER, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.BATTLEROYALE_CAROUSEL_FILTER_POPOVER, BattleRoyaleCarouselFilterPopover, 'filtersPopoverView.swf', WindowLayer.WINDOW, VIEW_ALIAS.BATTLEROYALE_CAROUSEL_FILTER_POPOVER, VIEW_ALIAS.BATTLEROYALE_CAROUSEL_FILTER_POPOVER, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.FITTING_SELECT_POPOVER, ModuleFittingSelectPopover, 'fittingSelectPopover.swf', WindowLayer.WINDOW, VIEW_ALIAS.FITTING_SELECT_POPOVER, VIEW_ALIAS.FITTING_SELECT_POPOVER, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.AMMUNITION_PANEL, AmmunitionPanel, ScopeTemplates.DEFAULT_SCOPE),
     ConditionalViewSettings(HANGAR_ALIASES.RESEARCH_PANEL, BootcampComponentOverride(ResearchPanel, BCResearchPanel), None, WindowLayer.UNDEFINED, None, None, ScopeTemplates.DEFAULT_SCOPE),
     ConditionalViewSettings(HANGAR_ALIASES.HEADER, BootcampComponentOverride(HangarHeader, BCHangarHeader), None, WindowLayer.UNDEFINED, None, None, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VIEW_ALIAS.SWITCH_MODE_PANEL, SwitchModePanel, ScopeTemplates.DEFAULT_SCOPE),
     ConditionalViewSettings(HANGAR_ALIASES.TANK_CAROUSEL, BootcampComponentOverride(TankCarousel, BCTankCarousel), None, WindowLayer.UNDEFINED, None, None, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.RANKED_TANK_CAROUSEL, RankedTankCarousel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.EPICBATTLE_TANK_CAROUSEL, EpicBattleTankCarousel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.MAPBOX_TANK_CAROUSEL, MapboxTankCarousel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.COMP7_TANK_CAROUSEL, Comp7TankCarousel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.VEHICLE_PARAMETERS, VehicleParameters, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.RANKED_WIDGET, RankedBattlesHangarWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.ALERT_MESSAGE_BLOCK, AlertMessageBlock, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.EPIC_WIDGET, EpicBattlesWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.BATTLE_ROYALE_ENTRY_POINT, BattleRoyaleHangarWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.BATTLE_ROYALE_HANGAR_WIDGET, BattleRoyaleHangarWidgetInject, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.BATTLE_ROYALE_TOURNAMENT, BattleRoyaleTournamentHangarWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.PROGRESSIVE_REWARD_WIDGET, ProgressiveRewardWidget, ScopeTemplates.DEFAULT_SCOPE),
     ConditionalViewSettings(HANGAR_ALIASES.DAILY_QUEST_WIDGET, BootcampComponentOverride(DailyQuestWidget, BootcampQuestComponent), None, WindowLayer.UNDEFINED, None, None, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.BATTLEPASS_TANK_CAROUSEL, BattlePassTankCarousel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.BATTLE_PASSS_ENTRY_POINT, BattlePassEntryPointComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.COMP7_WIDGET, Comp7MainWidgetComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.SECONDARY_ENTRY_POINT, BattlePassSecondaryEntryPointWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.AMMUNITION_PANEL_INJECT, AmmunitionPanelInject, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.CREW_PANEL_INJECT, CrewPanelInject, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.PRESTIGE_PROGRESS_WIDGET, PrestigeHangarEntryPointInject, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.ENTRIES_CONTAINER, EventEntryPointsContainer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.CRAFT_MACHINE_ENTRY_POINT, CraftMachineEntryPoint, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.STRONGHOLD_ENTRY_POINT, StrongholdEntryPoint, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.MAPBOX_ENTRY_POINT, MapBoxEntryPoint, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.MARATHON_ENTRY_POINT, MarathonEntryPoint, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.RESOURCE_WELL_ENTRY_POINT, ResourceWellEntryPointComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.BATTLE_MATTERS_ENTRY_POINT, BattleMattersEntryPoint, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.PERSONAL_RESERVES_WIDGET_INJECT, PersonalReservesWidgetInject, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.CAROUSEL_EVENT_ENTRY_HOLDER, CarouselEventEntryHolder, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.NY_MAIN_WIDGET_UI, NyMainWidgetInject, None),
     ComponentSettings(HANGAR_ALIASES.NY_GIFT_WIDGET_UI, NyGiftWidgetInject, None),
     ComponentSettings(HANGAR_ALIASES.REWARD_KITS_ENTRANCE_POINT, RewardKitEntrancePointInjectWidget, None))


def getBusinessHandlers():
    return (HangarPackageBusinessHandler(),)


class HangarPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.TANK_CAROUSEL_FILTER_POPOVER, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BATTLEPASS_CAROUSEL_FILTER_POPOVER, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BATTLEROYALE_CAROUSEL_FILTER_POPOVER, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOBBY_HANGAR, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOBBY_STRONGHOLD, self.loadViewByCtxEvent),
         (VIEW_ALIAS.STRONGHOLD_ADS, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BROWSER_VIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOBBY_TOURNAMENTS, self.loadViewByCtxEvent),
         (VIEW_ALIAS.FITTING_SELECT_POPOVER, self.loadViewByCtxEvent),
         (VIEW_ALIAS.VEHICLES_FILTER_POPOVER, self.loadViewByCtxEvent),
         (VIEW_ALIAS.WIKI_VIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.MANUAL_CHAPTER_VIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.MANUAL_BROWSER_VIEW, self.loadViewByCtxEvent))
        super(HangarPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
