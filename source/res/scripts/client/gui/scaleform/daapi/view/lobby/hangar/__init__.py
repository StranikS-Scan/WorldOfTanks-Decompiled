# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.bootcamp.component_override import BootcampComponentOverride
from gui.Scaleform.daapi.view.lobby.hangar.event.event_coins_counter import EventCoinsCounter
from gui.Scaleform.framework import ViewSettings, GroupedViewSettings, ScopeTemplates, ConditionalViewSettings, ComponentSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    from gui.Scaleform.daapi.view.lobby.hangar import hangar_cm_handlers
    from gui.Scaleform.daapi.view.bootcamp.bootcamp_cm_handlers import BCVehicleContextMenuHandler
    from gui.Scaleform.daapi.view.bootcamp.bootcamp_cm_handlers import BCCrewContextMenuHandler
    from gui.Scaleform.daapi.view.bootcamp.bootcamp_cm_handlers import BCTechnicalMaintenanceCMHandler
    return ((CONTEXT_MENU_HANDLER_TYPE.CREW, BootcampComponentOverride(hangar_cm_handlers.CrewContextMenuHandler, BCCrewContextMenuHandler)), (CONTEXT_MENU_HANDLER_TYPE.VEHICLE, BootcampComponentOverride(hangar_cm_handlers.VehicleContextMenuHandler, BCVehicleContextMenuHandler)), (CONTEXT_MENU_HANDLER_TYPE.TECHNICAL_MAINTENANCE, BootcampComponentOverride(hangar_cm_handlers.TechnicalMaintenanceCMHandler, BCTechnicalMaintenanceCMHandler)))


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.hangar.ammunition_panel import AmmunitionPanel
    from gui.Scaleform.daapi.view.lobby.hangar.Crew import Crew
    from gui.Scaleform.daapi.view.lobby.hangar.CrewAboutDogWindow import CrewAboutDogWindow
    from gui.Scaleform.daapi.view.lobby.hangar.Hangar import Hangar
    from gui.Scaleform.daapi.view.lobby.hangar.ResearchPanel import ResearchPanel
    from gui.Scaleform.daapi.view.lobby.hangar.event.event_crew_healing import FakeCrewHealing
    from gui.Scaleform.daapi.view.lobby.hangar.event.event_crew_booster import FakeCrewBooster
    from gui.Scaleform.daapi.view.lobby.hangar.event.event_tank_rent import EventTankRent
    from gui.Scaleform.daapi.view.lobby.hangar.SwitchModePanel import SwitchModePanel
    from gui.Scaleform.daapi.view.lobby.hangar.TmenXpPanel import TmenXpPanel
    from gui.Scaleform.daapi.view.lobby.hangar.VehicleParameters import VehicleParameters
    from gui.Scaleform.daapi.view.common.filter_popover import TankCarouselFilterPopover, BattlePassCarouselFilterPopover, BattleRoyaleCarouselFilterPopover
    from gui.Scaleform.daapi.view.lobby.hangar.carousels import TankCarousel
    from gui.Scaleform.daapi.view.lobby.hangar.carousels import RankedTankCarousel
    from gui.Scaleform.daapi.view.lobby.hangar.carousels import EpicBattleTankCarousel
    from gui.Scaleform.daapi.view.lobby.hangar.carousels import BattlePassTankCarousel
    from gui.Scaleform.daapi.view.lobby.hangar.carousels import RoyaleTankCarousel
    from gui.Scaleform.daapi.view.lobby.hangar.carousels import EventTankCarousel
    from gui.Scaleform.daapi.view.lobby.hangar.StrongholdView import StrongholdView
    from gui.Scaleform.daapi.view.lobby.hangar.BrowserView import BrowserView
    from gui.Scaleform.daapi.view.lobby.hangar.hangar_header import HangarHeader
    from gui.Scaleform.daapi.view.lobby.shared.fitting_select_popover import ModuleFittingSelectPopover
    from gui.Scaleform.daapi.view.lobby.hangar.ranked_battles_widget import RankedBattlesHangarWidget
    from gui.Scaleform.daapi.view.lobby.hangar.alert_message_block import AlertMessageBlock
    from gui.Scaleform.daapi.view.bootcamp.BCResearchPanel import BCResearchPanel
    from gui.Scaleform.daapi.view.bootcamp.BCTankCarousel import BCTankCarousel
    from gui.Scaleform.daapi.view.bootcamp.BCHangarHeader import BCHangarHeader
    from gui.Scaleform.daapi.view.bootcamp.BCCrew import BCCrew
    from gui.Scaleform.daapi.view.bootcamp.BCHangar import BCHangar
    from gui.Scaleform.daapi.view.lobby.hangar.epic_battles_widget import EpicBattlesWidget
    from gui.Scaleform.daapi.view.lobby.manual.manual_main_view import ManualMainView
    from gui.Scaleform.daapi.view.lobby.manual.manual_chapter_view import ManualChapterView
    from gui.Scaleform.daapi.view.lobby.hangar.seniority_awards import SeniorityAwardsHangarEntryPoint
    from gui.Scaleform.daapi.view.lobby.hangar.daily_quest_widget import DailyQuestWidget
    from gui.Scaleform.daapi.view.lobby.hangar.progressive_reward_widget import ProgressiveRewardWidget
    from gui.Scaleform.daapi.view.lobby.hangar.ammunition_panel_inject import AmmunitionPanelInject
    from gui.Scaleform.daapi.view.lobby.hangar.event.event_header import EventHeader
    from gui.Scaleform.daapi.view.lobby.hangar.event.event_quests_progress_view import EventQuestsProgressView
    from gui.Scaleform.daapi.view.lobby.hangar.event.event_shop import EventShopTab
    from gui.Scaleform.daapi.view.lobby.hangar.event.event_simple_item_confirmation import EventSimpleItemTab
    from gui.Scaleform.daapi.view.lobby.hangar.event.event_simple_item_congratulation import EventSimpleItemCongratulationTab
    from gui.Scaleform.daapi.view.lobby.hangar.event.event_about import EventAboutTab
    from gui.Scaleform.daapi.view.lobby.hangar.event.event_notes import EventNotesTab
    from gui.Scaleform.daapi.view.lobby.hangar.event.event_quests_panel import EventQuestsPanelView
    from gui.Scaleform.daapi.view.lobby.hangar.event.event_difficulty_view import EventDifficultyView
    from gui.Scaleform.daapi.view.lobby.hangar.event.event_ban_info import BanInfo
    from gui.Scaleform.daapi.view.lobby.hangar.event.event_items_for_tokens_adaptor import EventItemsForTokensAdaptor
    from gui.impl.lobby.battle_pass.battle_pass_entry_point_view import BattlePassEntryPointComponent
    from gui.Scaleform.daapi.view.lobby.hangar.event.event_pack_confirmation import EventPlayerPackConfirmation
    from gui.Scaleform.daapi.view.lobby.hangar.event.event_pack_confirmation import EventItemPackConfirmation
    from gui.Scaleform.daapi.view.lobby.hangar.event_entry_points_container import EventEntryPointsContainer
    from gui.impl.lobby.halloween.he20_entry_point import HE20EntryPoint
    return (ConditionalViewSettings(VIEW_ALIAS.LOBBY_HANGAR, BootcampComponentOverride(Hangar, BCHangar), 'hangar.swf', WindowLayer.SUB_VIEW, None, VIEW_ALIAS.LOBBY_HANGAR, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.LOBBY_STRONGHOLD, StrongholdView, 'StrongholdView.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.LOBBY_STRONGHOLD, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.BROWSER_VIEW, BrowserView, 'browserScreen.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.BROWSER_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     ViewSettings(VIEW_ALIAS.WIKI_VIEW, ManualMainView, 'manual.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.WIKI_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.MANUAL_CHAPTER_VIEW, ManualChapterView, 'manualChapterView.swf', WindowLayer.TOP_SUB_VIEW, VIEW_ALIAS.MANUAL_CHAPTER_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     ViewSettings(VIEW_ALIAS.EVENT_QUESTS, EventQuestsProgressView, 'eventQuestsView.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.EVENT_QUESTS, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.EVENT_SHOP, EventShopTab, 'eventShopTab.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.EVENT_SHOP, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.EVENT_ABOUT, EventAboutTab, 'eventBrowserScreen.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.EVENT_ABOUT, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     ViewSettings(VIEW_ALIAS.EVENT_NOTES, EventNotesTab, 'eventBrowserScreen.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.EVENT_NOTES, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     ViewSettings(VIEW_ALIAS.EVENT_SIMPLE_ITEM_CONFIRMATION, EventSimpleItemTab, 'eventItemsTradePage.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.EVENT_SIMPLE_ITEM_CONFIRMATION, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.EVENT_SIMPLE_ITEM_CONGRATULATION, EventSimpleItemCongratulationTab, 'eventItemsTradeCongratulationPage.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.EVENT_SIMPLE_ITEM_CONGRATULATION, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.EVENT_PLAYER_PACK_CONFIRMATION, EventPlayerPackConfirmation, 'eventPlayerPackTradePage.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.EVENT_PLAYER_PACK_CONFIRMATION, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.EVENT_ITEM_PACK_CONFIRMATION, EventItemPackConfirmation, 'eventItemPackTradePage.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.EVENT_ITEM_PACK_CONFIRMATION, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.EVENT_DIFFICULTY, EventDifficultyView, 'eventDifficultyView.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.EVENT_DIFFICULTY, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     ViewSettings(VIEW_ALIAS.EVENT_ITEMS_FOR_TOKENS, EventItemsForTokensAdaptor, 'eventItemsForTokens.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.EVENT_ITEMS_FOR_TOKENS, ScopeTemplates.LOBBY_SUB_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.CREW_ABOUT_DOG_WINDOW, CrewAboutDogWindow, 'simpleWindow.swf', WindowLayer.WINDOW, 'aboutDogWindow', None, ScopeTemplates.DEFAULT_SCOPE),
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
     ComponentSettings(HANGAR_ALIASES.ROYALE_TANK_CAROUSEL, RoyaleTankCarousel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.EVENT_TANK_CAROUSEL, EventTankCarousel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.TMEN_XP_PANEL, TmenXpPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.VEHICLE_PARAMETERS, VehicleParameters, ScopeTemplates.DEFAULT_SCOPE),
     ConditionalViewSettings(HANGAR_ALIASES.CREW, BootcampComponentOverride(Crew, BCCrew), None, WindowLayer.UNDEFINED, None, None, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.RANKED_WIDGET, RankedBattlesHangarWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.ALERT_MESSAGE_BLOCK, AlertMessageBlock, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.EPIC_WIDGET, EpicBattlesWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.PROGRESSIVE_REWARD_WIDGET, ProgressiveRewardWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.SENIORITY_AWARDS_ENTRY_POINT_2020, SeniorityAwardsHangarEntryPoint, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.DAILY_QUEST_WIDGET, DailyQuestWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.BATTLEPASS_TANK_CAROUSEL, BattlePassTankCarousel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.BATTLE_PASSS_ENTRY_POINT, BattlePassEntryPointComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.AMMUNITION_PANEL_INJECT, AmmunitionPanelInject, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.ENTRIES_CONTAINER, EventEntryPointsContainer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.EVENT_CREW_HEALING_COMPONENT, FakeCrewHealing, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.EVENT_CREW_BOOSTER_COMPONENT, FakeCrewBooster, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.EVENT_TANK_RENT_COMPONENT, EventTankRent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VIEW_ALIAS.EVENT_HEADER, EventHeader, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.EVENT_QUESTS_COMPONENT, EventQuestsPanelView, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.EVENT_BAN_INFO_COMPONENT, BanInfo, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.HE20_EVENT_ENTRY_POINT, HE20EntryPoint, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.EVENT_COINS_COMPONENT, EventCoinsCounter, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (HangarPackageBusinessHandler(),)


class HangarPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.TANK_CAROUSEL_FILTER_POPOVER, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BATTLEPASS_CAROUSEL_FILTER_POPOVER, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BATTLEROYALE_CAROUSEL_FILTER_POPOVER, self.loadViewByCtxEvent),
         (VIEW_ALIAS.CREW_ABOUT_DOG_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOBBY_HANGAR, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOBBY_STRONGHOLD, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BROWSER_VIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.FITTING_SELECT_POPOVER, self.loadViewByCtxEvent),
         (VIEW_ALIAS.VEHICLES_FILTER_POPOVER, self.loadViewByCtxEvent),
         (VIEW_ALIAS.WIKI_VIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.MANUAL_CHAPTER_VIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.EVENT_QUESTS, self.loadViewByCtxEvent),
         (VIEW_ALIAS.EVENT_SHOP, self.loadViewByCtxEvent),
         (VIEW_ALIAS.EVENT_ABOUT, self.loadViewByCtxEvent),
         (VIEW_ALIAS.EVENT_NOTES, self.loadViewByCtxEvent),
         (VIEW_ALIAS.EVENT_DIFFICULTY, self.loadViewByCtxEvent),
         (VIEW_ALIAS.EVENT_SIMPLE_ITEM_CONFIRMATION, self.loadViewByCtxEvent),
         (VIEW_ALIAS.EVENT_SIMPLE_ITEM_CONGRATULATION, self.loadViewByCtxEvent),
         (VIEW_ALIAS.EVENT_PLAYER_PACK_CONFIRMATION, self.loadViewByCtxEvent),
         (VIEW_ALIAS.EVENT_ITEM_PACK_CONFIRMATION, self.loadViewByCtxEvent))
        super(HangarPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
