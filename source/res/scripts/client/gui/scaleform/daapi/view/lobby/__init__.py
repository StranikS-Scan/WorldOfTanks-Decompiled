# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/__init__.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.bootcamp.component_override import BootcampComponentOverride
from gui.Scaleform.daapi.view.dialogs.missions_dialogs import UseAwardSheetWindow
from gui.Scaleform.daapi.view.lobby.image_view.image_view import ImageView
from gui.Scaleform.framework import ViewSettings, GroupedViewSettings, ContainerSettings, ViewTypes, ScopeTemplates, ConditionalViewSettings
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
    from gui.Scaleform.daapi.view.lobby.SandboxQueueDialog import SandboxQueueDialog
    from gui.Scaleform.daapi.view.battle_results_window import BattleResultsWindow
    from gui.Scaleform.daapi.view.dialogs.CheckBoxDialog import CheckBoxDialog
    from gui.Scaleform.daapi.view.dialogs.ConfirmModuleDialog import ConfirmModuleDialog
    from gui.Scaleform.daapi.view.dialogs.ConfirmBoosterDialog import ConfirmBoosterDialog
    from gui.Scaleform.daapi.view.dialogs.DemountDeviceDialog import DemountDeviceDialog
    from gui.Scaleform.daapi.view.dialogs.TankmanOperationDialog import DismissTankmanDialog
    from gui.Scaleform.daapi.view.dialogs.FreeXPInfoWindow import FreeXPInfoWindow
    from gui.Scaleform.daapi.view.dialogs.IconDialog import IconDialog
    from gui.Scaleform.daapi.view.dialogs.IconPriceDialog import IconPriceDialog
    from gui.Scaleform.daapi.view.dialogs.PunishmentDialog import PunishmentDialog
    from gui.Scaleform.daapi.view.dialogs.TankmanOperationDialog import RestoreTankmanDialog
    from gui.Scaleform.daapi.view.dialogs.SystemMessageDialog import SystemMessageDialog
    from gui.Scaleform.daapi.view.lobby.eliteWindow.EliteWindow import EliteWindow
    from gui.Scaleform.daapi.view.lobby.AwardWindow import AwardWindow
    from gui.Scaleform.daapi.view.lobby.AwardWindow import MissionAwardWindow
    from gui.Scaleform.daapi.view.lobby.battle_queue import BattleQueue, BattleStrongholdsQueue
    from gui.Scaleform.daapi.view.lobby.BrowserWindow import BrowserWindow
    from gui.Scaleform.daapi.view.lobby.Browser import Browser
    from gui.Scaleform.daapi.view.lobby.components.CalendarComponent import CalendarComponent
    from gui.Scaleform.daapi.view.lobby.customization.main_view import MainView as CustomizationMainView
    from gui.Scaleform.daapi.view.lobby.DemonstratorWindow import DemonstratorWindow
    from gui.Scaleform.daapi.view.lobby.GetPremiumPopover import GetPremiumPopover
    from gui.Scaleform.daapi.view.lobby.GoldFishWindow import GoldFishWindow
    from gui.Scaleform.daapi.view.lobby.LobbyMenu import LobbyMenu
    from gui.Scaleform.daapi.view.lobby.lobby_vehicle_marker_view import LobbyVehicleMarkerView
    from gui.Scaleform.daapi.view.lobby.LobbyView import LobbyView
    from gui.Scaleform.daapi.view.lobby.MinimapLobby import MinimapLobby
    from gui.Scaleform.daapi.view.lobby.MinimapGrid import MinimapGrid
    from gui.Scaleform.daapi.view.lobby.ModuleInfoWindow import ModuleInfoWindow
    from gui.Scaleform.daapi.view.lobby.PersonalCase import PersonalCase
    from gui.Scaleform.daapi.view.lobby.PremiumWindow import PremiumWindow
    from gui.Scaleform.daapi.view.lobby.PromoPremiumIgrWindow import PromoPremiumIgrWindow
    from gui.Scaleform.daapi.view.lobby.recruitWindow.RecruitParamsComponent import RecruitParamsComponent
    from gui.Scaleform.daapi.view.lobby.recruitWindow.RecruitWindow import RecruitWindow
    from gui.Scaleform.daapi.view.lobby.recruitWindow.QuestsRecruitWindow import QuestsRecruitWindow
    from gui.Scaleform.daapi.view.lobby.ReferralManagementWindow import ReferralManagementWindow
    from gui.Scaleform.daapi.view.lobby.ReferralReferralsIntroWindow import ReferralReferralsIntroWindow
    from gui.Scaleform.daapi.view.lobby.ReferralReferrerIntroWindow import ReferralReferrerIntroWindow
    from gui.Scaleform.daapi.view.lobby.RoleChangeWindow import RoleChangeWindow
    from gui.Scaleform.daapi.view.lobby.ServerStats import ServerStats
    from gui.Scaleform.daapi.view.lobby.SkillDropWindow import SkillDropWindow
    from gui.Scaleform.daapi.view.lobby.vehicle_obtain_windows import VehicleBuyWindow
    from gui.Scaleform.daapi.view.lobby.vehicle_obtain_windows import VehicleRestoreWindow
    from gui.Scaleform.daapi.view.lobby.VehicleInfoWindow import VehicleInfoWindow
    from gui.Scaleform.daapi.view.lobby.CrystalPromoWindow import CrystalsPromoWindow
    from gui.Scaleform.daapi.view.lobby.VehicleSellDialog import VehicleSellDialog
    from gui.Scaleform.daapi.view.lobby.vehiclePreview.VehiclePreview import VehiclePreview
    from gui.Scaleform.daapi.view.lobby.vehiclePreview20.vehicle_preview_20 import VehiclePreview20
    from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_view import VehicleCompareView
    from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_configurator_view import VehicleCompareConfiguratorMain
    from gui.Scaleform.daapi.view.meta.MiniClientComponentMeta import MiniClientComponentMeta
    from gui.Scaleform.daapi.view.lobby.BadgesPage import BadgesPage
    from gui.Scaleform.daapi.view.lobby.tradein.TradeInPopup import TradeInPopup
    from gui.Scaleform.daapi.view.bootcamp.BCVehicleBuyWindow import BCVehicleBuyWindow
    from gui.Scaleform.daapi.view.bootcamp.BCPersonalCase import BCPersonalCase
    from gui.Scaleform.daapi.view.bootcamp.BCBattleResult import BCBattleResult
    from gui.Scaleform.daapi.view.bootcamp.BCVehiclePreview import BCVehiclePreview
    return (ViewSettings(VIEW_ALIAS.LOBBY, LobbyView, 'lobbyPage.swf', ViewTypes.DEFAULT, None, ScopeTemplates.DEFAULT_SCOPE, False, (ContainerSettings(ViewTypes.LOBBY_SUB, containers.DefaultContainer), ContainerSettings(ViewTypes.LOBBY_TOP_SUB, containers.PopUpContainer))),
     ViewSettings(VIEW_ALIAS.LOBBY_VEHICLE_MARKER_VIEW, LobbyVehicleMarkerView, 'lobbyVehicleMarkerView.swf', ViewTypes.MARKER, VIEW_ALIAS.LOBBY_VEHICLE_MARKER_VIEW, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.BATTLE_QUEUE, BattleQueue, 'battleQueue.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.BATTLE_QUEUE, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.BATTLE_STRONGHOLDS_QUEUE, BattleStrongholdsQueue, 'battleStrongholdsQueue.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.BATTLE_STRONGHOLDS_QUEUE, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.LOBBY_CUSTOMIZATION, CustomizationMainView, 'customizationMainView.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.LOBBY_CUSTOMIZATION, ScopeTemplates.LOBBY_SUB_SCOPE),
     ConditionalViewSettings(VIEW_ALIAS.VEHICLE_PREVIEW, BootcampComponentOverride(VehiclePreview, BCVehiclePreview), 'vehiclePreview.swf', ViewTypes.LOBBY_SUB, None, VIEW_ALIAS.VEHICLE_PREVIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ConditionalViewSettings(VIEW_ALIAS.HERO_VEHICLE_PREVIEW, BootcampComponentOverride(VehiclePreview, BCVehiclePreview), 'vehiclePreview.swf', ViewTypes.LOBBY_SUB, None, VIEW_ALIAS.HERO_VEHICLE_PREVIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.VEHICLE_PREVIEW_20, VehiclePreview20, 'vehiclePreview20.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.VEHICLE_PREVIEW_20, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.HERO_VEHICLE_PREVIEW_20, VehiclePreview20, 'vehiclePreview20.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.HERO_VEHICLE_PREVIEW_20, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.IMAGE_VIEW, ImageView, 'imageView.swf', ViewTypes.OVERLAY, VIEW_ALIAS.IMAGE_VIEW, ScopeTemplates.LOBBY_TOP_SUB_SCOPE, True),
     ViewSettings(VIEW_ALIAS.VEHICLE_COMPARE, VehicleCompareView, 'vehicleCompareView.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.VEHICLE_COMPARE, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.VEHICLE_COMPARE_MAIN_CONFIGURATOR, VehicleCompareConfiguratorMain, 'vehicleCompareConfiguratorMain.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.VEHICLE_COMPARE_MAIN_CONFIGURATOR, ScopeTemplates.LOBBY_SUB_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.CHECK_BOX_DIALOG, CheckBoxDialog, 'confirmDialog.swf', ViewTypes.TOP_WINDOW, 'confirmDialog', None, ScopeTemplates.DYNAMIC_SCOPE, isModal=True, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.CONFIRM_MODULE_DIALOG, ConfirmModuleDialog, 'confirmModuleWindow.swf', ViewTypes.TOP_WINDOW, 'confirmModuleDialog', None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.USE_FREEW_AWARD_SHEET_DIALOG, UseAwardSheetWindow, 'useAwardSheetWindow.swf', ViewTypes.TOP_WINDOW, 'useAwardSheetWindow', None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.CONFIRM_BOOSTER_DIALOG, ConfirmBoosterDialog, 'confirmBoostersWindow.swf', ViewTypes.TOP_WINDOW, 'confirmBoosterDialog', None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.DEMOUNT_DEVICE_DIALOG, DemountDeviceDialog, 'demountDeviceDialog.swf', ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DYNAMIC_SCOPE, isModal=True, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.DESTROY_DEVICE_DIALOG, IconDialog, 'destroyDeviceDialog.swf', ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DYNAMIC_SCOPE, isModal=True, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.DISMISS_TANKMAN_DIALOG, DismissTankmanDialog, 'tankmanOperationDialog.swf', ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DYNAMIC_SCOPE, isModal=True, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.RESTORE_TANKMAN_DIALOG, RestoreTankmanDialog, 'tankmanOperationDialog.swf', ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DYNAMIC_SCOPE, isModal=True, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.ICON_DIALOG, IconDialog, 'iconDialog.swf', ViewTypes.WINDOW, '', None, ScopeTemplates.DYNAMIC_SCOPE, isModal=True, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.ICON_PRICE_DIALOG, IconPriceDialog, 'iconPriceDialog.swf', ViewTypes.WINDOW, '', None, ScopeTemplates.DYNAMIC_SCOPE, isModal=True, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.PUNISHMENT_DIALOG, PunishmentDialog, 'punishmentDialog.swf', ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DYNAMIC_SCOPE, isModal=True, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.SYSTEM_MESSAGE_DIALOG, SystemMessageDialog, 'systemMessageDialog.swf', ViewTypes.WINDOW, 'systemMessageDialog', None, ScopeTemplates.DEFAULT_SCOPE, isModal=True),
     GroupedViewSettings(VIEW_ALIAS.FREE_X_P_INFO_WINDOW, FreeXPInfoWindow, 'freeXPInfoWindow.swf', ViewTypes.TOP_WINDOW, 'freeXPInfoWindow', None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canClose=False, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.RECRUIT_WINDOW, RecruitWindow, 'recruitWindow.swf', ViewTypes.WINDOW, 'recruitWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.ADVENT_CALENDAR, BrowserWindow, 'browserWindow.swf', ViewTypes.WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE, canDrag=True, isModal=False),
     GroupedViewSettings(VIEW_ALIAS.AWARD_WINDOW, AwardWindow, 'awardWindow.swf', ViewTypes.WINDOW, 'awardWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     ConditionalViewSettings(VIEW_ALIAS.BATTLE_RESULTS, BootcampComponentOverride(BattleResultsWindow, BCBattleResult), BootcampComponentOverride('battleResults.swf', 'BCBattleResult.swf'), BootcampComponentOverride(ViewTypes.WINDOW, ViewTypes.TOP_WINDOW), BootcampComponentOverride('BattleResultsWindow', ''), None, BootcampComponentOverride(ScopeTemplates.DEFAULT_SCOPE, ScopeTemplates.TOP_WINDOW_SCOPE)),
     GroupedViewSettings(VIEW_ALIAS.BROWSER_WINDOW, BrowserWindow, 'browserWindow.swf', ViewTypes.WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.BROWSER_WINDOW_MODAL, BrowserWindow, 'browserWindow.swf', ViewTypes.WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.DEMONSTRATOR_WINDOW, DemonstratorWindow, 'demonstratorWindow.swf', ViewTypes.WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.ELITE_WINDOW, EliteWindow, 'eliteWindow.swf', ViewTypes.WINDOW, 'eliteWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.GOLD_FISH_WINDOW, GoldFishWindow, 'goldFishWindow.swf', ViewTypes.WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.LOBBY_MENU, LobbyMenu, 'lobbyMenu.swf', ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.LOBBY_SUB_SCOPE, isModal=True, canClose=False, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.MODULE_INFO_WINDOW, ModuleInfoWindow, 'moduleInfo.swf', ViewTypes.WINDOW, 'moduleInfoWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     ConditionalViewSettings(VIEW_ALIAS.PERSONAL_CASE, BootcampComponentOverride(PersonalCase, BCPersonalCase), 'personalCase.swf', ViewTypes.WINDOW, 'personalCaseWindow', None, ScopeTemplates.LOBBY_SUB_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.PREMIUM_WINDOW, PremiumWindow, 'premiumWindow.swf', ViewTypes.WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.PROMO_PREMIUM_IGR_WINDOW, PromoPremiumIgrWindow, 'promoPremiumIgrWindow.swf', ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.QUESTS_RECRUIT_WINDOW, QuestsRecruitWindow, 'questRecruitWindow.swf', ViewTypes.WINDOW, 'questRecruitWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.REFERRAL_MANAGEMENT_WINDOW, ReferralManagementWindow, 'referralManagementWindow.swf', ViewTypes.WINDOW, 'ReferralManagementWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.REFERRAL_REFERRALS_INTRO_WINDOW, ReferralReferralsIntroWindow, 'referralReferralsIntroWindow.swf', ViewTypes.WINDOW, 'referralReferralsIntroWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.REFERRAL_REFERRER_INTRO_WINDOW, ReferralReferrerIntroWindow, 'referralReferrerIntroWindow.swf', ViewTypes.WINDOW, 'referralReferrerIntroWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.ROLE_CHANGE, RoleChangeWindow, 'roleChangeWindow.swf', ViewTypes.WINDOW, 'roleChangeWindow', None, ScopeTemplates.WINDOW_SCOPE, isModal=True, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.TANKMAN_SKILLS_DROP_WINDOW, SkillDropWindow, 'skillDropWindow.swf', ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canDrag=False),
     ConditionalViewSettings(VIEW_ALIAS.VEHICLE_BUY_WINDOW, BootcampComponentOverride(VehicleBuyWindow, BCVehicleBuyWindow), BootcampComponentOverride('vehicleBuyWindow.swf', 'BCVehicleBuyWindow.swf'), ViewTypes.TOP_WINDOW, 'vehicleBuyWindow', None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.VEHICLE_RESTORE_WINDOW, VehicleRestoreWindow, 'vehicleBuyWindow.swf', ViewTypes.TOP_WINDOW, 'vehicleRestoreWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.VEHICLE_INFO_WINDOW, VehicleInfoWindow, 'vehicleInfo.swf', ViewTypes.WINDOW, 'vehicleInfoWindow', None, ScopeTemplates.DEFAULT_SCOPE, isCentered=False),
     GroupedViewSettings(VIEW_ALIAS.VEHICLE_SELL_DIALOG, VehicleSellDialog, 'vehicleSellDialog.swf', ViewTypes.TOP_WINDOW, 'vehicleSellWindow', None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.SANDBOX_QUEUE_DIALOG, SandboxQueueDialog, 'PvESandboxQueueWindow.swf', ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canClose=False),
     GroupedViewSettings(VIEW_ALIAS.MISSION_AWARD_WINDOW, MissionAwardWindow, 'missionAwardWindow.swf', ViewTypes.WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.CRYSTALS_PROMO_WINDOW, CrystalsPromoWindow, 'crystalsPromoWindow.swf', ViewTypes.WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.GET_PREMIUM_POPOVER, GetPremiumPopover, 'getPremiumPopover.swf', ViewTypes.TOP_WINDOW, 'getPremiumPopover', VIEW_ALIAS.GET_PREMIUM_POPOVER, ScopeTemplates.WINDOW_VIEWED_MULTISCOPE),
     GroupedViewSettings(VIEW_ALIAS.TRADEIN_POPOVER, TradeInPopup, 'TradeInPopover.swf', ViewTypes.TOP_WINDOW, 'TradeInPopover', VIEW_ALIAS.TRADEIN_POPOVER, ScopeTemplates.TOP_WINDOW_SCOPE),
     ViewSettings(VIEW_ALIAS.BADGES_PAGE, BadgesPage, 'badgesPage.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.BADGES_PAGE, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.CALENDAR, CalendarComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.MINIMAP_LOBBY, MinimapLobby, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.MINIMAP_GRID, MinimapGrid, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.MINI_CLIENT_LINKED, MiniClientComponentMeta, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.RECRUIT_PARAMS, RecruitParamsComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.SERVERS_STATS, ServerStats, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.BROWSER, Browser, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (LobbyPackageBusinessHandler(), LobbyDialogsHandler())


class LobbyPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.ADVENT_CALENDAR, self.loadViewByCtxEvent),
         (VIEW_ALIAS.AWARD_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BATTLE_QUEUE, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BATTLE_STRONGHOLDS_QUEUE, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BATTLE_RESULTS, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BROWSER_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BROWSER_WINDOW_MODAL, self.loadViewByCtxEvent),
         (VIEW_ALIAS.DEMONSTRATOR_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.ELITE_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.GOLD_FISH_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.GET_PREMIUM_POPOVER, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOBBY, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOBBY_VEHICLE_MARKER_VIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOBBY_CUSTOMIZATION, self.loadViewByCtxEvent),
         (VIEW_ALIAS.VEHICLE_PREVIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.VEHICLE_PREVIEW_20, self.loadViewByCtxEvent),
         (VIEW_ALIAS.IMAGE_VIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.HERO_VEHICLE_PREVIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.HERO_VEHICLE_PREVIEW_20, self.loadViewByCtxEvent),
         (VIEW_ALIAS.VEHICLE_COMPARE, self.loadViewByCtxEvent),
         (VIEW_ALIAS.VEHICLE_COMPARE_MAIN_CONFIGURATOR, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOBBY_MENU, self.loadViewByCtxEvent),
         (VIEW_ALIAS.MODULE_INFO_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.PERSONAL_CASE, self.loadViewByCtxEvent),
         (VIEW_ALIAS.PREMIUM_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.PROMO_PREMIUM_IGR_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.QUESTS_RECRUIT_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.REFERRAL_MANAGEMENT_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.REFERRAL_REFERRALS_INTRO_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.REFERRAL_REFERRER_INTRO_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.ROLE_CHANGE, self.loadViewByCtxEvent),
         (VIEW_ALIAS.TANKMAN_SKILLS_DROP_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.VEHICLE_BUY_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.VEHICLE_RESTORE_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.VEHICLE_SELL_DIALOG, self.loadViewByCtxEvent),
         (VIEW_ALIAS.VEHICLE_INFO_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.SANDBOX_QUEUE_DIALOG, self.loadViewBySharedEvent),
         (VIEW_ALIAS.MISSION_AWARD_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.ACOUSTIC_POPOVER, self.loadViewByCtxEvent),
         (VIEW_ALIAS.TRADEIN_POPOVER, self.loadViewByCtxEvent),
         (VIEW_ALIAS.CRYSTALS_PROMO_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BADGES_PAGE, self.loadViewByCtxEvent),
         (VIEW_ALIAS.UNBOUND_INJECT_WINDOW, self.loadViewByCtxEvent))
        super(LobbyPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)


class LobbyDialogsHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((ShowDialogEvent.SHOW_CHECK_BOX_DIALOG, self.__checkBoxDialogHandler),
         (ShowDialogEvent.SHOW_CONFIRM_MODULE, self.__confirmModuleHandler),
         (ShowDialogEvent.SHOW_CONFIRM_BOOSTER, self.__confirmBoosterHandler),
         (ShowDialogEvent.SHOW_DEMOUNT_DEVICE_DIALOG, self.__demountDeviceDialogHandler),
         (ShowDialogEvent.SHOW_DESTROY_DEVICE_DIALOG, self.__destroyDeviceDialogHandler),
         (ShowDialogEvent.SHOW_DISMISS_TANKMAN_DIALOG, self.__dismissTankmanHandler),
         (ShowDialogEvent.SHOW_RESTORE_TANKMAN_DIALOG, self.__restoreTankmanHandler),
         (ShowDialogEvent.SHOW_ICON_DIALOG, self.__iconDialogHandler),
         (ShowDialogEvent.SHOW_ICON_PRICE_DIALOG, self.__iconPriceDialogHandler),
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

    def __confirmBoosterHandler(self, event):
        self.loadViewWithGenName(VIEW_ALIAS.CONFIRM_BOOSTER_DIALOG, event.meta, event.handler)

    def __demountDeviceDialogHandler(self, event):
        self.loadViewWithGenName(VIEW_ALIAS.DEMOUNT_DEVICE_DIALOG, event.meta, event.handler)

    def __destroyDeviceDialogHandler(self, event):
        self.loadViewWithGenName(VIEW_ALIAS.DESTROY_DEVICE_DIALOG, event.meta, event.handler)

    def __dismissTankmanHandler(self, event):
        self.loadViewWithGenName(VIEW_ALIAS.DISMISS_TANKMAN_DIALOG, event.meta, event.handler)

    def __restoreTankmanHandler(self, event):
        self.loadViewWithGenName(VIEW_ALIAS.RESTORE_TANKMAN_DIALOG, event.meta, event.handler)

    def __iconDialogHandler(self, event):
        self.loadViewWithGenName(VIEW_ALIAS.ICON_DIALOG, event.meta, event.handler)

    def __iconPriceDialogHandler(self, event):
        self.loadViewWithGenName(VIEW_ALIAS.ICON_PRICE_DIALOG, event.meta, event.handler)

    def __punishmentWindowHandler(self, event):
        self.loadViewWithGenName(VIEW_ALIAS.PUNISHMENT_DIALOG, event.meta, event.handler)

    def __useAwardSheetDialogHandler(self, event):
        self.loadViewWithGenName(VIEW_ALIAS.USE_FREEW_AWARD_SHEET_DIALOG, event.meta, event.handler)

    def __showFreeXPInfoWindow(self, event):
        self.loadViewWithDefName(VIEW_ALIAS.FREE_X_P_INFO_WINDOW, VIEW_ALIAS.FREE_X_P_INFO_WINDOW, {'meta': event.meta,
         'handler': event.handler})

    def __showRecruitWindow(self, event):
        windowContainer = self._app.containerManager.getContainer(ViewTypes.WINDOW)
        recruitWindow = windowContainer.getView(criteria={containers.POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.RECRUIT_WINDOW})
        if recruitWindow is not None:
            recruitWindow.destroy()
        self.loadViewWithDefName(VIEW_ALIAS.RECRUIT_WINDOW, None, event.ctx)
        return

    def __systemMsgDialogHandler(self, event):
        self.loadViewWithGenName(VIEW_ALIAS.SYSTEM_MESSAGE_DIALOG, event.meta, event.handler)
