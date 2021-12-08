# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.hangar.BrowserView import BrowserView
from gui.Scaleform.daapi.view.bootcamp.component_override import BootcampComponentOverride
from gui.Scaleform.daapi.view.dialogs.missions_dialogs import UseAwardSheetWindow
from gui.Scaleform.daapi.view.lobby.BoosterInfoWindow import BoosterInfoWindow
from gui.Scaleform.daapi.view.lobby.demount_kit_info_window import DemountKitInfoWindow
from gui.Scaleform.daapi.view.lobby.image_view.image_view import ImageView
from gui.Scaleform.daapi.view.lobby.wot_plus.wot_plus_browser_pages import WotPlusInfoView, VehicleRentalView
from gui.Scaleform.framework import ViewSettings, GroupedViewSettings, ContainerSettings, ScopeTemplates, ConditionalViewSettings, ComponentSettings
from gui.Scaleform.framework.managers import containers
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import ShowDialogEvent

def getContextMenuHandlers():
    from gui.Scaleform.daapi.view.lobby import user_cm_handlers
    from gui.Scaleform.daapi.view.lobby.rally.UnitUserCMHandler import UnitUserCMHandler
    return ((CONTEXT_MENU_HANDLER_TYPE.BATTLE_RESULTS_USER, user_cm_handlers.UserVehicleCMHandler),
     (CONTEXT_MENU_HANDLER_TYPE.BASE_USER, user_cm_handlers.BaseUserCMHandler),
     (CONTEXT_MENU_HANDLER_TYPE.UNIT_USER, UnitUserCMHandler),
     (CONTEXT_MENU_HANDLER_TYPE.CUSTOM_USER, user_cm_handlers.CustomUserCMHandler))


def getViewSettings():
    from gui.impl.lobby.battle_pass.battle_pass_browser_view import BattlePassBrowserView
    from gui.Scaleform.daapi.view.lobby.SandboxQueueDialog import SandboxQueueDialog
    from gui.Scaleform.daapi.view.battle_results_window import BattleResultsWindow
    from gui.Scaleform.daapi.view.dialogs.CheckBoxDialog import CheckBoxDialog
    from gui.Scaleform.daapi.view.dialogs.ConfirmModuleDialog import ConfirmModuleDialog
    from gui.Scaleform.daapi.view.dialogs.TankmanOperationDialog import DismissTankmanDialog
    from gui.Scaleform.daapi.view.dialogs.FreeXPInfoWindow import FreeXPInfoWindow
    from gui.Scaleform.daapi.view.dialogs.IconDialog import IconDialog
    from gui.Scaleform.daapi.view.dialogs.IconPriceDialog import IconPriceDialog
    from gui.Scaleform.daapi.view.dialogs.CrewSkinsCompensationDialog import CrewSkinsCompensationDialog
    from gui.Scaleform.daapi.view.dialogs.PunishmentDialog import PunishmentDialog
    from gui.Scaleform.daapi.view.dialogs.TankmanOperationDialog import RestoreTankmanDialog
    from gui.Scaleform.daapi.view.dialogs.SystemMessageDialog import SystemMessageDialog
    from gui.Scaleform.daapi.view.lobby.AwardWindow import AwardWindow
    from gui.Scaleform.daapi.view.lobby.AwardWindow import MissionAwardWindow
    from gui.Scaleform.daapi.view.lobby.battle_queue import BattleQueue, BattleStrongholdsQueue
    from gui.Scaleform.daapi.view.lobby.BrowserWindow import BrowserWindow
    from gui.Scaleform.daapi.view.lobby.Browser import Browser
    from gui.Scaleform.daapi.view.lobby.components.CalendarComponent import CalendarComponent
    from gui.Scaleform.daapi.view.lobby.customization.main_view import MainView as CustomizationMainView
    from gui.Scaleform.daapi.view.lobby.DemonstratorWindow import DemonstratorWindow
    from gui.Scaleform.daapi.view.lobby.GoldFishWindow import GoldFishWindow
    from gui.Scaleform.daapi.view.lobby.LobbyMenu import LobbyMenu
    from gui.Scaleform.daapi.view.lobby.lobby_vehicle_marker_view import LobbyVehicleMarkerView
    from gui.Scaleform.daapi.view.lobby.LobbyView import LobbyView
    from gui.Scaleform.daapi.view.lobby.MinimapLobby import MinimapLobby
    from gui.Scaleform.daapi.view.lobby.MinimapGrid import MinimapGrid
    from gui.Scaleform.daapi.view.lobby.ModuleInfoWindow import ModuleInfoWindow
    from gui.Scaleform.daapi.view.lobby.PersonalCase import PersonalCase
    from gui.Scaleform.daapi.view.lobby.PromoPremiumIgrWindow import PromoPremiumIgrWindow
    from gui.Scaleform.daapi.view.lobby.recruitWindow.RecruitParamsComponent import RecruitParamsComponent
    from gui.Scaleform.daapi.view.lobby.recruitWindow.RecruitWindow import RecruitWindow
    from gui.Scaleform.daapi.view.lobby.recruitWindow.QuestsRecruitWindow import QuestsRecruitWindow
    from gui.Scaleform.daapi.view.lobby.recruitWindow.token_recruit_window import TokenRecruitWindow
    from gui.Scaleform.daapi.view.lobby.RoleChangeWindow import RoleChangeWindow
    from gui.Scaleform.daapi.view.lobby.ServerStats import ServerStats
    from gui.Scaleform.daapi.view.lobby.shared.web_view import WebView
    from gui.Scaleform.daapi.view.lobby.SkillDropWindow import SkillDropWindow
    from gui.Scaleform.daapi.view.lobby.vehicle_obtain_windows import VehicleBuyWindow
    from gui.Scaleform.daapi.view.lobby.vehicle_obtain_windows import VehicleRestoreWindow
    from gui.Scaleform.daapi.view.lobby.VehicleInfoWindow import VehicleInfoWindow
    from gui.Scaleform.daapi.view.lobby.vehicle_sell_dialog import VehicleSellDialog
    from gui.Scaleform.daapi.view.lobby.vehicle_preview.vehicle_preview import VehiclePreview
    from gui.Scaleform.daapi.view.lobby.trade_in.trade_in_vehicle_preview import TradeInVehiclePreview
    from gui.Scaleform.daapi.view.lobby.vehicle_preview.marathon_vehicle_preview import MarathonVehiclePreview
    from gui.Scaleform.daapi.view.lobby.vehicle_preview.configurable_vehicle_preview import ConfigurableVehiclePreview
    from gui.Scaleform.daapi.view.lobby.vehicle_preview.offer_gift_vehicle_preview import OfferGiftVehiclePreview
    from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_view import VehicleCompareView
    from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_configurator_view import VehicleCompareConfiguratorMain
    from gui.Scaleform.daapi.view.meta.MiniClientComponentMeta import MiniClientComponentMeta
    from gui.Scaleform.daapi.view.lobby.BadgesPage import BadgesPage
    from gui.Scaleform.daapi.view.lobby.trade_in.trade_in_popup import TradeInPopup
    from gui.Scaleform.daapi.view.bootcamp.BCVehicleBuyWindow import BCVehicleBuyWindow
    from gui.Scaleform.daapi.view.bootcamp.BCPersonalCase import BCPersonalCase
    from gui.Scaleform.daapi.view.bootcamp.BCBattleResult import BCBattleResult
    from gui.Scaleform.daapi.view.lobby.vehicle_preview.style_preview import VehicleStylePreview
    from gui.Scaleform.daapi.view.lobby.vehicle_preview.progression_styles_style_preview import ProgressionStylesStylePreview
    from gui.Scaleform.daapi.view.lobby.trade_in.personal_trade_in_vehicle_preview import PersonalTradeInVehiclePreview
    from gui.Scaleform.daapi.view.lobby.vehicle_preview.bp_exchange_vehicle_preview import BlueprintsExchangeVehicleStypePreview
    from gui.impl.lobby.new_year.popovers.ny_select_vehicle_popover import NySelectVehiclePopover
    from gui.impl.lobby.new_year.ny_browser_view import NyBrowserView
    from gui.impl.new_year.views.ny_select_vehicle_for_discount_popover import NYSelectVehicleForDiscountPopover
    from gui.Scaleform.daapi.view.bootcamp.bootcamp_progress_component import BootcampProgressComponent
    from gui.Scaleform.daapi.view.lobby.vehicle_preview.wot_plus_vehicle_preview import WotPlusVehiclePreview
    from gui.Scaleform.daapi.view.lobby.loot_box_shop import LootBoxShopOverlay
    from gui.Scaleform.daapi.view.lobby.telecom_rentals.telecom_rentals_browser_pages import VehicleTelecomRentalView
    return (ViewSettings(VIEW_ALIAS.LOBBY, LobbyView, 'lobbyPage.swf', WindowLayer.VIEW, None, ScopeTemplates.DEFAULT_SCOPE, False, (ContainerSettings(WindowLayer.SUB_VIEW, containers.DefaultContainer), ContainerSettings(WindowLayer.TOP_SUB_VIEW, containers.PopUpContainer))),
     ViewSettings(VIEW_ALIAS.LOBBY_VEHICLE_MARKER_VIEW, LobbyVehicleMarkerView, 'lobbyVehicleMarkerView.swf', WindowLayer.MARKER, VIEW_ALIAS.LOBBY_VEHICLE_MARKER_VIEW, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.BATTLE_QUEUE, BattleQueue, 'battleQueue.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.BATTLE_QUEUE, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.BATTLE_STRONGHOLDS_QUEUE, BattleStrongholdsQueue, 'battleStrongholdsQueue.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.BATTLE_STRONGHOLDS_QUEUE, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.LOBBY_CUSTOMIZATION, CustomizationMainView, 'customizationMainView.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.LOBBY_CUSTOMIZATION, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.VEHICLE_PREVIEW, VehiclePreview, 'vehiclePreview.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.VEHICLE_PREVIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.HERO_VEHICLE_PREVIEW, VehiclePreview, 'vehiclePreview.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.HERO_VEHICLE_PREVIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.CONFIGURABLE_VEHICLE_PREVIEW, ConfigurableVehiclePreview, 'vehiclePreview.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.CONFIGURABLE_VEHICLE_PREVIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.WOT_PLUS_VEHICLE_PREVIEW, WotPlusVehiclePreview, 'vehiclePreview.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.WOT_PLUS_VEHICLE_PREVIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.STYLE_PREVIEW, VehicleStylePreview, 'vehicleBasePreview.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.STYLE_PREVIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.PROGRESSION_STYLES_STYLE_PREVIEW, ProgressionStylesStylePreview, 'vehicleBasePreview.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.PROGRESSION_STYLES_STYLE_PREVIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.BLUEPRINTS_EXCHANGE_STYLE_PREVIEW, BlueprintsExchangeVehicleStypePreview, 'vehicleBasePreview.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.BLUEPRINTS_EXCHANGE_STYLE_PREVIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.TRADE_IN_VEHICLE_PREVIEW, TradeInVehiclePreview, 'vehiclePreview.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.TRADE_IN_VEHICLE_PREVIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.PERSONAL_TRADE_IN_VEHICLE_PREVIEW, PersonalTradeInVehiclePreview, 'vehiclePreview.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.PERSONAL_TRADE_IN_VEHICLE_PREVIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.MARATHON_VEHICLE_PREVIEW, MarathonVehiclePreview, 'vehiclePreview.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.MARATHON_VEHICLE_PREVIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.OFFER_GIFT_VEHICLE_PREVIEW, OfferGiftVehiclePreview, 'vehiclePreview.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.OFFER_GIFT_VEHICLE_PREVIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.IMAGE_VIEW, ImageView, 'imageView.swf', WindowLayer.FULLSCREEN_WINDOW, VIEW_ALIAS.IMAGE_VIEW, ScopeTemplates.LOBBY_TOP_SUB_SCOPE, True),
     ViewSettings(VIEW_ALIAS.VEHICLE_COMPARE, VehicleCompareView, 'vehicleCompareView.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.VEHICLE_COMPARE, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.VEHICLE_COMPARE_MAIN_CONFIGURATOR, VehicleCompareConfiguratorMain, 'vehicleCompareConfiguratorMain.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.VEHICLE_COMPARE_MAIN_CONFIGURATOR, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.BROWSER_LOBBY_TOP_SUB, WebView, 'browserScreen.swf', WindowLayer.TOP_SUB_VIEW, VIEW_ALIAS.BROWSER_LOBBY_TOP_SUB, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.BROWSER_OVERLAY, WebView, 'browserScreen.swf', WindowLayer.FULLSCREEN_WINDOW, VIEW_ALIAS.BROWSER_OVERLAY, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.BATTLE_PASS_BROWSER_VIEW, BattlePassBrowserView, 'browserScreen.swf', WindowLayer.TOP_SUB_VIEW, VIEW_ALIAS.BATTLE_PASS_BROWSER_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.WOT_PLUS_INFO_VIEW, WotPlusInfoView, 'browserScreen.swf', WindowLayer.FULLSCREEN_WINDOW, VIEW_ALIAS.WOT_PLUS_INFO_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.VEHICLE_RENTAL_VIEW, VehicleRentalView, 'browserScreen.swf', WindowLayer.TOP_SUB_VIEW, VIEW_ALIAS.VEHICLE_RENTAL_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.TELECOM_RENTAL_VIEW, VehicleTelecomRentalView, 'browserScreen.swf', WindowLayer.TOP_SUB_VIEW, VIEW_ALIAS.TELECOM_RENTAL_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.NY_BROWSER_VIEW, NyBrowserView, 'browserScreen.swf', WindowLayer.FULLSCREEN_WINDOW, VIEW_ALIAS.NY_BROWSER_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.CHECK_BOX_DIALOG, CheckBoxDialog, 'confirmDialog.swf', WindowLayer.TOP_WINDOW, 'confirmDialog', None, ScopeTemplates.DYNAMIC_SCOPE, isModal=True, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.CONFIRM_MODULE_DIALOG, ConfirmModuleDialog, 'confirmModuleWindow.swf', WindowLayer.TOP_WINDOW, 'confirmModuleDialog', None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.USE_FREEW_AWARD_SHEET_DIALOG, UseAwardSheetWindow, 'useAwardSheetWindow.swf', WindowLayer.TOP_WINDOW, 'useAwardSheetWindow', None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.PM_CONFIRMATION_DIALOG, IconDialog, 'pmConfirmationDialog.swf', WindowLayer.TOP_WINDOW, '', None, ScopeTemplates.DYNAMIC_SCOPE, isModal=True, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.DISMISS_TANKMAN_DIALOG, DismissTankmanDialog, 'tankmanOperationDialog.swf', WindowLayer.TOP_WINDOW, '', None, ScopeTemplates.DYNAMIC_SCOPE, isModal=True, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.RESTORE_TANKMAN_DIALOG, RestoreTankmanDialog, 'tankmanOperationDialog.swf', WindowLayer.TOP_WINDOW, '', None, ScopeTemplates.DYNAMIC_SCOPE, isModal=True, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.ICON_DIALOG, IconDialog, 'iconDialog.swf', WindowLayer.WINDOW, '', None, ScopeTemplates.DYNAMIC_SCOPE, isModal=True, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.ICON_PRICE_DIALOG, IconPriceDialog, 'iconPriceDialog.swf', WindowLayer.WINDOW, '', None, ScopeTemplates.DYNAMIC_SCOPE, isModal=True, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.CREW_SKINS_COMPENSATION_DIALOG, CrewSkinsCompensationDialog, 'crewSkinsCompensationDialog.swf', WindowLayer.TOP_WINDOW, '', None, ScopeTemplates.DYNAMIC_SCOPE, isModal=True, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.PUNISHMENT_DIALOG, PunishmentDialog, 'punishmentDialog.swf', WindowLayer.TOP_WINDOW, '', None, ScopeTemplates.DYNAMIC_SCOPE, isModal=True, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.SYSTEM_MESSAGE_DIALOG, SystemMessageDialog, 'systemMessageDialog.swf', WindowLayer.WINDOW, 'systemMessageDialog', None, ScopeTemplates.DEFAULT_SCOPE, isModal=True),
     GroupedViewSettings(VIEW_ALIAS.FREE_X_P_INFO_WINDOW, FreeXPInfoWindow, 'freeXPInfoWindow.swf', WindowLayer.TOP_WINDOW, 'freeXPInfoWindow', None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canClose=False, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.RECRUIT_WINDOW, RecruitWindow, 'recruitWindow.swf', WindowLayer.WINDOW, 'recruitWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.ADVENT_CALENDAR, BrowserWindow, 'browserWindow.swf', WindowLayer.WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE, canDrag=True, isModal=False),
     GroupedViewSettings(VIEW_ALIAS.AWARD_WINDOW, AwardWindow, 'awardWindow.swf', WindowLayer.WINDOW, 'awardWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.AWARD_WINDOW_MODAL, AwardWindow, 'awardWindow.swf', WindowLayer.WINDOW, 'awardWindow', None, ScopeTemplates.DEFAULT_SCOPE, isModal=True),
     ConditionalViewSettings(VIEW_ALIAS.BATTLE_RESULTS, BootcampComponentOverride(BattleResultsWindow, BCBattleResult), BootcampComponentOverride('battleResults.swf', 'BCBattleResult.swf'), WindowLayer.WINDOW, BootcampComponentOverride('BattleResultsWindow', ''), None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.BROWSER_WINDOW, BrowserWindow, 'browserWindow.swf', WindowLayer.WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.BROWSER_WINDOW_MODAL, BrowserWindow, 'browserWindow.swf', WindowLayer.WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.DEMONSTRATOR_WINDOW, DemonstratorWindow, 'demonstratorWindow.swf', WindowLayer.WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.GOLD_FISH_WINDOW, GoldFishWindow, 'goldFishWindow.swf', WindowLayer.WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.LOBBY_MENU, LobbyMenu, 'lobbyMenu.swf', WindowLayer.TOP_WINDOW, '', None, ScopeTemplates.LOBBY_SUB_SCOPE, isModal=True, canClose=False, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.MODULE_INFO_WINDOW, ModuleInfoWindow, 'moduleInfo.swf', WindowLayer.WINDOW, VIEW_ALIAS.MODULE_INFO_WINDOW, None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.BOOSTER_INFO_WINDOW, BoosterInfoWindow, 'boosterInfo.swf', WindowLayer.WINDOW, VIEW_ALIAS.BOOSTER_INFO_WINDOW, None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.DEMOUNT_KIT_INFO_WINDOW, DemountKitInfoWindow, 'demountKitInfo.swf', WindowLayer.WINDOW, VIEW_ALIAS.DEMOUNT_KIT_INFO_WINDOW, None, ScopeTemplates.DEFAULT_SCOPE),
     ConditionalViewSettings(VIEW_ALIAS.PERSONAL_CASE, BootcampComponentOverride(PersonalCase, BCPersonalCase), 'personalCase.swf', WindowLayer.WINDOW, 'personalCaseWindow', None, ScopeTemplates.LOBBY_SUB_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.PROMO_PREMIUM_IGR_WINDOW, PromoPremiumIgrWindow, 'promoPremiumIgrWindow.swf', WindowLayer.TOP_WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.QUESTS_RECRUIT_WINDOW, QuestsRecruitWindow, 'questRecruitWindow.swf', WindowLayer.WINDOW, 'questRecruitWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.TOKEN_RECRUIT_WINDOW, TokenRecruitWindow, 'questRecruitWindow.swf', WindowLayer.WINDOW, 'questRecruitWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.ROLE_CHANGE, RoleChangeWindow, 'roleChangeWindow.swf', WindowLayer.WINDOW, 'roleChangeWindow', None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.TANKMAN_SKILLS_DROP_WINDOW, SkillDropWindow, 'skillDropWindow.swf', WindowLayer.TOP_WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canDrag=False),
     ConditionalViewSettings(VIEW_ALIAS.VEHICLE_BUY_WINDOW, BootcampComponentOverride(VehicleBuyWindow, BCVehicleBuyWindow), BootcampComponentOverride('vehicleBuyWindow.swf', 'BCVehicleBuyWindow.swf'), WindowLayer.TOP_WINDOW, 'vehicleBuyWindow', None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.VEHICLE_RESTORE_WINDOW, VehicleRestoreWindow, 'vehicleBuyWindow.swf', WindowLayer.TOP_WINDOW, 'vehicleRestoreWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.VEHICLE_INFO_WINDOW, VehicleInfoWindow, 'vehicleInfo.swf', WindowLayer.WINDOW, 'vehicleInfoWindow', None, ScopeTemplates.DEFAULT_SCOPE, isCentered=False),
     GroupedViewSettings(VIEW_ALIAS.VEHICLE_SELL_DIALOG, VehicleSellDialog, 'vehicleSellDialog.swf', WindowLayer.TOP_WINDOW, 'vehicleSellWindow', None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.SANDBOX_QUEUE_DIALOG, SandboxQueueDialog, 'PvESandboxQueueWindow.swf', WindowLayer.TOP_WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canClose=False),
     GroupedViewSettings(VIEW_ALIAS.MISSION_AWARD_WINDOW, MissionAwardWindow, 'missionAwardWindow.swf', WindowLayer.WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.TRADEIN_POPOVER, TradeInPopup, 'TradeInPopover.swf', WindowLayer.TOP_WINDOW, 'TradeInPopover', VIEW_ALIAS.TRADEIN_POPOVER, ScopeTemplates.TOP_WINDOW_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.NY_SELECT_VEHICLE_POPOVER, NySelectVehiclePopover, 'NYSelectVehiclePopover.swf', WindowLayer.TOP_WINDOW, VIEW_ALIAS.NY_SELECT_VEHICLE_POPOVER, VIEW_ALIAS.NY_SELECT_VEHICLE_POPOVER, ScopeTemplates.TOP_WINDOW_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.NY_SELECT_VEHICLE_FOR_DISCOUNT_POPOVER, NYSelectVehicleForDiscountPopover, 'NYSelectVehiclePopover.swf', WindowLayer.TOP_WINDOW, VIEW_ALIAS.NY_SELECT_VEHICLE_FOR_DISCOUNT_POPOVER, VIEW_ALIAS.NY_SELECT_VEHICLE_FOR_DISCOUNT_POPOVER, ScopeTemplates.TOP_WINDOW_SCOPE),
     ViewSettings(VIEW_ALIAS.REFERRAL_PROGRAM_WINDOW, BrowserView, 'browserScreen.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.BROWSER_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     ViewSettings(VIEW_ALIAS.CLAN_NOTIFICATION_WINDOW, BrowserView, 'browserScreen.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.BROWSER_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     ViewSettings(VIEW_ALIAS.BADGES_PAGE, BadgesPage, 'badgesPage.swf', WindowLayer.TOP_SUB_VIEW, VIEW_ALIAS.BADGES_PAGE, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.LOOT_BOX_SHOP_OVERLAY, LootBoxShopOverlay, 'browserScreen.swf', WindowLayer.OVERLAY, VIEW_ALIAS.BROWSER_OVERLAY, ScopeTemplates.LOBBY_SUB_SCOPE),
     ComponentSettings(VIEW_ALIAS.CALENDAR, CalendarComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VIEW_ALIAS.MINIMAP_LOBBY, MinimapLobby, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VIEW_ALIAS.MINIMAP_GRID, MinimapGrid, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VIEW_ALIAS.MINI_CLIENT_LINKED, MiniClientComponentMeta, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VIEW_ALIAS.RECRUIT_PARAMS, RecruitParamsComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VIEW_ALIAS.SERVERS_STATS, ServerStats, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VIEW_ALIAS.BROWSER, Browser, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VIEW_ALIAS.BOOTCAMP_PROGRESS, BootcampProgressComponent, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (LobbyPackageBusinessHandler(), LobbyDialogsHandler())


class LobbyPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.ADVENT_CALENDAR, self.loadViewByCtxEvent),
         (VIEW_ALIAS.AWARD_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.AWARD_WINDOW_MODAL, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BATTLE_QUEUE, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BATTLE_STRONGHOLDS_QUEUE, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BATTLE_RESULTS, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BROWSER_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BROWSER_WINDOW_MODAL, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BROWSER_LOBBY_TOP_SUB, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BROWSER_OVERLAY, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BATTLE_PASS_BROWSER_VIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.DEMONSTRATOR_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.GOLD_FISH_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOBBY, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOBBY_VEHICLE_MARKER_VIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOBBY_CUSTOMIZATION, self.loadViewByCtxEvent),
         (VIEW_ALIAS.VEHICLE_PREVIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.WOT_PLUS_VEHICLE_PREVIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.WOT_PLUS_INFO_VIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.VEHICLE_RENTAL_VIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.TELECOM_RENTAL_VIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.OFFER_GIFT_VEHICLE_PREVIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.STYLE_PREVIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.PROGRESSION_STYLES_STYLE_PREVIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BLUEPRINTS_EXCHANGE_STYLE_PREVIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.IMAGE_VIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.HERO_VEHICLE_PREVIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.CONFIGURABLE_VEHICLE_PREVIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.TRADE_IN_VEHICLE_PREVIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.PERSONAL_TRADE_IN_VEHICLE_PREVIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.MARATHON_VEHICLE_PREVIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.VEHICLE_COMPARE, self.loadViewByCtxEvent),
         (VIEW_ALIAS.VEHICLE_COMPARE_MAIN_CONFIGURATOR, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOBBY_MENU, self.loadViewByCtxEvent),
         (VIEW_ALIAS.MODULE_INFO_WINDOW, self.__moduleWindowHandler),
         (VIEW_ALIAS.BOOSTER_INFO_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.DEMOUNT_KIT_INFO_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.PERSONAL_CASE, self.loadViewByCtxEvent),
         (VIEW_ALIAS.PROMO_PREMIUM_IGR_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.QUESTS_RECRUIT_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.TOKEN_RECRUIT_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.ROLE_CHANGE, self.loadViewByCtxEvent),
         (VIEW_ALIAS.TANKMAN_SKILLS_DROP_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.VEHICLE_BUY_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.VEHICLE_RESTORE_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.VEHICLE_SELL_DIALOG, self.loadViewByCtxEvent),
         (VIEW_ALIAS.VEHICLE_INFO_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.SANDBOX_QUEUE_DIALOG, self.loadViewBySharedEvent),
         (VIEW_ALIAS.ADVENT_CALENDAR, self.showAdventCalendarWindow),
         (VIEW_ALIAS.MISSION_AWARD_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.ACOUSTIC_POPOVER, self.loadViewByCtxEvent),
         (VIEW_ALIAS.TRADEIN_POPOVER, self.loadViewByCtxEvent),
         (VIEW_ALIAS.REFERRAL_PROGRAM_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.NY_SELECT_VEHICLE_POPOVER, self.loadViewByCtxEvent),
         (VIEW_ALIAS.NY_SELECT_VEHICLE_FOR_DISCOUNT_POPOVER, self.loadViewByCtxEvent),
         (VIEW_ALIAS.NY_BROWSER_VIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.CLAN_NOTIFICATION_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BADGES_PAGE, self.loadViewByCtxEvent),
         (VIEW_ALIAS.UNBOUND_INJECT_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOOT_BOX_SHOP_OVERLAY, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BATTLE_PASS_BADGES_DEMO, self.loadViewByCtxEvent))
        super(LobbyPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)

    def __moduleWindowHandler(self, event):
        name = event.loadParams.viewKey.name
        window = self.findViewByName(WindowLayer.WINDOW, name)
        if window is not None:
            self.bringViewToFront(name)
        else:
            self.loadViewByCtxEvent(event)
        return

    def showAdventCalendarWindow(self, event):
        if self.findViewByName(WindowLayer.WINDOW, event.name) is not None:
            self.bringViewToFront(event.name)
        else:
            self.loadViewByCtxEvent(event)
        return


class LobbyDialogsHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((ShowDialogEvent.SHOW_CHECK_BOX_DIALOG, self.__checkBoxDialogHandler),
         (ShowDialogEvent.SHOW_CONFIRM_MODULE, self.__confirmModuleHandler),
         (ShowDialogEvent.SHOW_PM_CONFIRMATION_DIALOG, self.__pmConfirmationDialogHandler),
         (ShowDialogEvent.SHOW_DISMISS_TANKMAN_DIALOG, self.__dismissTankmanHandler),
         (ShowDialogEvent.SHOW_RESTORE_TANKMAN_DIALOG, self.__restoreTankmanHandler),
         (ShowDialogEvent.SHOW_ICON_DIALOG, self.__iconDialogHandler),
         (ShowDialogEvent.SHOW_ICON_PRICE_DIALOG, self.__iconPriceDialogHandler),
         (ShowDialogEvent.SHOW_CREW_SKINS_COMPENSATION_DIALOG, self.__crewSkinsCompensationDialogHandler),
         (ShowDialogEvent.SHOW_PUNISHMENT_DIALOG, self.__punishmentWindowHandler),
         (ShowDialogEvent.SHOW_SYSTEM_MESSAGE_DIALOG, self.__systemMsgDialogHandler),
         (ShowDialogEvent.SHOW_USE_AWARD_SHEET_DIALOG, self.__useAwardSheetDialogHandler),
         (VIEW_ALIAS.FREE_X_P_INFO_WINDOW, self.__showFreeXPInfoWindow),
         (VIEW_ALIAS.RECRUIT_WINDOW, self.__showRecruitWindow))
        super(LobbyDialogsHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.GLOBAL)

    def __checkBoxDialogHandler(self, event):
        self.loadViewWithGenName(VIEW_ALIAS.CHECK_BOX_DIALOG, event.meta, event.handler)

    def __confirmModuleHandler(self, event):
        self.loadViewWithGenName(VIEW_ALIAS.CONFIRM_MODULE_DIALOG, event.meta, event.handler)

    def __pmConfirmationDialogHandler(self, event):
        self.loadViewWithGenName(VIEW_ALIAS.PM_CONFIRMATION_DIALOG, event.meta, event.handler)

    def __dismissTankmanHandler(self, event):
        self.loadViewWithGenName(VIEW_ALIAS.DISMISS_TANKMAN_DIALOG, event.meta, event.handler)

    def __restoreTankmanHandler(self, event):
        self.loadViewWithGenName(VIEW_ALIAS.RESTORE_TANKMAN_DIALOG, event.meta, event.handler)

    def __iconDialogHandler(self, event):
        self.loadViewWithGenName(VIEW_ALIAS.ICON_DIALOG, event.meta, event.handler)

    def __iconPriceDialogHandler(self, event):
        self.loadViewWithGenName(VIEW_ALIAS.ICON_PRICE_DIALOG, event.meta, event.handler)

    def __crewSkinsCompensationDialogHandler(self, event):
        self.loadViewWithGenName(VIEW_ALIAS.CREW_SKINS_COMPENSATION_DIALOG, event.meta, event.handler)

    def __punishmentWindowHandler(self, event):
        self.loadViewWithGenName(VIEW_ALIAS.PUNISHMENT_DIALOG, event.meta, event.handler)

    def __useAwardSheetDialogHandler(self, event):
        self.loadViewWithGenName(VIEW_ALIAS.USE_FREEW_AWARD_SHEET_DIALOG, event.meta, event.handler)

    def __showFreeXPInfoWindow(self, event):
        self.loadViewWithDefName(VIEW_ALIAS.FREE_X_P_INFO_WINDOW, VIEW_ALIAS.FREE_X_P_INFO_WINDOW, {'meta': event.meta,
         'handler': event.handler})

    def __showRecruitWindow(self, event):
        windowContainer = self._app.containerManager.getContainer(WindowLayer.WINDOW)
        recruitWindow = windowContainer.getView(criteria={containers.POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.RECRUIT_WINDOW})
        if recruitWindow is not None:
            recruitWindow.destroy()
        self.loadViewWithDefName(VIEW_ALIAS.RECRUIT_WINDOW, None, event.ctx)
        return

    def __systemMsgDialogHandler(self, event):
        self.loadViewWithGenName(VIEW_ALIAS.SYSTEM_MESSAGE_DIALOG, event.meta, event.handler)
