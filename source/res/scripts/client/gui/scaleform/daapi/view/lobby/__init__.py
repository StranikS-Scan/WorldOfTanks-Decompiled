# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/__init__.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewSettings, GroupedViewSettings, ViewTypes, ScopeTemplates
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import ShowDialogEvent
from gui.Scaleform.genConsts.FALLOUT_ALIASES import FALLOUT_ALIASES

def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.SandboxQueueDialog import SandboxQueueDialog
    from gui.Scaleform.daapi.view.BattleResultsWindow import BattleResultsWindow
    from gui.Scaleform.daapi.view.battle_loading import BattleLoading
    from gui.Scaleform.daapi.view.battle_loading import FalloutMultiTeamBattleLoading
    from gui.Scaleform.daapi.view.dialogs.CaptchaDialog import CaptchaDialog
    from gui.Scaleform.daapi.view.dialogs.CheckBoxDialog import CheckBoxDialog
    from gui.Scaleform.daapi.view.dialogs.ConfirmModuleDialog import ConfirmModuleDialog
    from gui.Scaleform.daapi.view.dialogs.DemountDeviceDialog import DemountDeviceDialog
    from gui.Scaleform.daapi.view.dialogs.DismissTankmanDialog import DismissTankmanDialog
    from gui.Scaleform.daapi.view.dialogs.FreeXPInfoWindow import FreeXPInfoWindow
    from gui.Scaleform.daapi.view.dialogs.IconDialog import IconDialog
    from gui.Scaleform.daapi.view.dialogs.IconPriceDialog import IconPriceDialog
    from gui.Scaleform.daapi.view.dialogs.PunishmentDialog import PunishmentDialog
    from gui.Scaleform.daapi.view.dialogs.SimpleDialog import SimpleDialog
    from gui.Scaleform.daapi.view.dialogs.SystemMessageDialog import SystemMessageDialog
    from gui.Scaleform.daapi.view.lobby.eliteWindow.EliteWindow import EliteWindow
    from gui.Scaleform.daapi.view.lobby.AwardWindow import AwardWindow
    from gui.Scaleform.daapi.view.lobby.BattleQueue import BattleQueue
    from gui.Scaleform.daapi.view.lobby.BrowserWindow import BrowserWindow
    from gui.Scaleform.daapi.view.lobby.components.CalendarComponent import CalendarComponent
    from gui.Scaleform.daapi.view.lobby.customization.VehicleCustomization import VehicleCustomization
    from gui.Scaleform.daapi.view.lobby.customization_2_0.main_view import MainView as CustomizationMainView
    from gui.Scaleform.daapi.view.lobby.DemonstratorWindow import DemonstratorWindow
    from gui.Scaleform.daapi.view.lobby.FalloutBattleSelectorWindow import FalloutBattleSelectorWindow
    from gui.Scaleform.daapi.view.lobby.GetPremiumPopover import GetPremiumPopover
    from gui.Scaleform.daapi.view.lobby.GoldFishWindow import GoldFishWindow
    from gui.Scaleform.daapi.view.lobby.LobbyMenu import LobbyMenu
    from gui.Scaleform.daapi.view.lobby.LobbyView import LobbyView
    from gui.Scaleform.daapi.view.lobby.MinimapLobby import MinimapLobby
    from gui.Scaleform.daapi.view.lobby.ModuleInfoWindow import ModuleInfoWindow
    from gui.Scaleform.daapi.view.lobby.PersonalCase import PersonalCase
    from gui.Scaleform.daapi.view.lobby.PremiumCongratulationWindow import PremiumCongratulationWindow
    from gui.Scaleform.daapi.view.lobby.PremiumWindow import PremiumWindow
    from gui.Scaleform.daapi.view.lobby.PromoPremiumIgrWindow import PromoPremiumIgrWindow
    from gui.Scaleform.daapi.view.lobby.recruitWindow.RecruitParamsComponent import RecruitParamsComponent
    from gui.Scaleform.daapi.view.lobby.recruitWindow.RecruitWindow import RecruitWindow
    from gui.Scaleform.daapi.view.lobby.recruitWindow.QuestsRecruitWindow import QuestsRecruitWindow
    from gui.Scaleform.daapi.view.lobby.ReferralManagementWindow import ReferralManagementWindow
    from gui.Scaleform.daapi.view.lobby.ReferralReferralsIntroWindow import ReferralReferralsIntroWindow
    from gui.Scaleform.daapi.view.lobby.ReferralReferrerIntroWindow import ReferralReferrerIntroWindow
    from gui.Scaleform.daapi.view.lobby.ReportBug import ReportBugPanel
    from gui.Scaleform.daapi.view.lobby.RoleChangeWindow import RoleChangeWindow
    from gui.Scaleform.daapi.view.lobby.ServerStats import ServerStats
    from gui.Scaleform.daapi.view.lobby.SkillDropWindow import SkillDropWindow
    from gui.Scaleform.daapi.view.lobby.VehicleBuyWindow import VehicleBuyWindow
    from gui.Scaleform.daapi.view.lobby.VehicleInfoWindow import VehicleInfoWindow
    from gui.Scaleform.daapi.view.lobby.VehicleSellDialog import VehicleSellDialog
    from gui.Scaleform.daapi.view.meta.MiniClientComponentMeta import MiniClientComponentMeta
    return (ViewSettings(VIEW_ALIAS.LOBBY, LobbyView, 'lobbyPage.swf', ViewTypes.DEFAULT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.BATTLE_LOADING, BattleLoading, 'battleLoading.swf', ViewTypes.DEFAULT, VIEW_ALIAS.BATTLE_LOADING, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.FALLOUT_MULTI_TEAM_BATTLE_LOADING, FalloutMultiTeamBattleLoading, 'falloutMultiTeamBattleLoading.swf', ViewTypes.DEFAULT, VIEW_ALIAS.FALLOUT_MULTI_TEAM_BATTLE_LOADING, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.TUTORIAL_LOADING, BattleLoading, 'tutorialLoading.swf', ViewTypes.DEFAULT, VIEW_ALIAS.TUTORIAL_LOADING, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.BATTLE_QUEUE, BattleQueue, 'battleQueue.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.BATTLE_QUEUE, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.LOBBY_CUSTOMIZATION, CustomizationMainView, 'customizationMainView.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.LOBBY_CUSTOMIZATION, ScopeTemplates.LOBBY_SUB_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.CAPTCHA_DIALOG, CaptchaDialog, 'CAPTCHA.swf', ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.CHECK_BOX_DIALOG, CheckBoxDialog, 'confirmDialog.swf', ViewTypes.TOP_WINDOW, 'confirmDialog', None, ScopeTemplates.DYNAMIC_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.CONFIRM_MODULE_DIALOG, ConfirmModuleDialog, 'confirmModuleWindow.swf', ViewTypes.TOP_WINDOW, 'confirmModuleDialog', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.DEMOUNT_DEVICE_DIALOG, DemountDeviceDialog, 'demountDeviceDialog.swf', ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DYNAMIC_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.DESTROY_DEVICE_DIALOG, IconDialog, 'destroyDeviceDialog.swf', ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DYNAMIC_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.DISMISS_TANKMAN_DIALOG, DismissTankmanDialog, 'dismissTankmanDialog.swf', ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DYNAMIC_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.ICON_DIALOG, IconDialog, 'iconDialog.swf', ViewTypes.WINDOW, '', None, ScopeTemplates.DYNAMIC_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.ICON_PRICE_DIALOG, IconPriceDialog, 'iconPriceDialog.swf', ViewTypes.WINDOW, '', None, ScopeTemplates.DYNAMIC_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.PUNISHMENT_DIALOG, PunishmentDialog, 'punishmentDialog.swf', ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DYNAMIC_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.SIMPLE_DIALOG, SimpleDialog, 'simpleDialog.swf', ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DYNAMIC_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.SYSTEM_MESSAGE_DIALOG, SystemMessageDialog, 'systemMessageDialog.swf', ViewTypes.WINDOW, 'systemMessageDialog', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.FREE_X_P_INFO_WINDOW, FreeXPInfoWindow, 'freeXPInfoWindow.swf', ViewTypes.TOP_WINDOW, 'freeXPInfoWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.RECRUIT_WINDOW, RecruitWindow, 'recruitWindow.swf', ViewTypes.WINDOW, 'recruitWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(FALLOUT_ALIASES.FALLOUT_BATTLE_SELECTOR_WINDOW, FalloutBattleSelectorWindow, FALLOUT_ALIASES.FALLOUT_BATTLE_SELECTOR_WINDOW_SWF, ViewTypes.WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.AWARD_WINDOW, AwardWindow, 'awardWindow.swf', ViewTypes.WINDOW, 'awardWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.BATTLE_RESULTS, BattleResultsWindow, 'battleResults.swf', ViewTypes.WINDOW, 'BattleResultsWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.BROWSER_WINDOW, BrowserWindow, 'browser.swf', ViewTypes.WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.DEMONSTRATOR_WINDOW, DemonstratorWindow, 'demonstratorWindow.swf', ViewTypes.WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.ELITE_WINDOW, EliteWindow, 'eliteWindow.swf', ViewTypes.WINDOW, 'eliteWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.GOLD_FISH_WINDOW, GoldFishWindow, 'goldFishWindow.swf', ViewTypes.WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.GET_PREMIUM_POPOVER, GetPremiumPopover, 'getPremiumPopover.swf', ViewTypes.TOP_WINDOW, 'getPremiumPopover', VIEW_ALIAS.GET_PREMIUM_POPOVER, ScopeTemplates.WINDOW_VIEWED_MULTISCOPE),
     GroupedViewSettings(VIEW_ALIAS.LOBBY_MENU, LobbyMenu, 'lobbyMenu.swf', ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.LOBBY_SUB_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.MODULE_INFO_WINDOW, ModuleInfoWindow, 'moduleInfo.swf', ViewTypes.WINDOW, 'moduleInfoWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.PERSONAL_CASE, PersonalCase, 'personalCase.swf', ViewTypes.WINDOW, 'personalCaseWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.PREMIUM_CONGRATULATION_WINDOW, PremiumCongratulationWindow, 'premiumCongratulationWindow.swf', ViewTypes.WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.PREMIUM_WINDOW, PremiumWindow, 'premiumWindow.swf', ViewTypes.WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.PROMO_PREMIUM_IGR_WINDOW, PromoPremiumIgrWindow, 'promoPremiumIgrWindow.swf', ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.QUESTS_RECRUIT_WINDOW, QuestsRecruitWindow, 'questRecruitWindow.swf', ViewTypes.WINDOW, 'questRecruitWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.REFERRAL_MANAGEMENT_WINDOW, ReferralManagementWindow, 'referralManagementWindow.swf', ViewTypes.WINDOW, 'ReferralManagementWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.REFERRAL_REFERRALS_INTRO_WINDOW, ReferralReferralsIntroWindow, 'referralReferralsIntroWindow.swf', ViewTypes.WINDOW, 'referralReferralsIntroWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.REFERRAL_REFERRER_INTRO_WINDOW, ReferralReferrerIntroWindow, 'referralReferrerIntroWindow.swf', ViewTypes.WINDOW, 'referralReferrerIntroWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.ROLE_CHANGE, RoleChangeWindow, 'roleChangeWindow.swf', ViewTypes.WINDOW, 'roleChangeWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.TANKMAN_SKILLS_DROP_WINDOW, SkillDropWindow, 'skillDropWindow.swf', ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.VEHICLE_BUY_WINDOW, VehicleBuyWindow, 'vehicleBuyWindow.swf', ViewTypes.TOP_WINDOW, 'vehicleBuyWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.VEHICLE_INFO_WINDOW, VehicleInfoWindow, 'vehicleInfo.swf', ViewTypes.WINDOW, 'vehicleInfoWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.VEHICLE_SELL_DIALOG, VehicleSellDialog, 'vehicleSellDialog.swf', ViewTypes.TOP_WINDOW, 'vehicleSellWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.SANDBOX_QUEUE_DIALOG, SandboxQueueDialog, 'PvESandboxQueueWindow.swf', ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.CALENDAR, CalendarComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.MINIMAP_LOBBY, MinimapLobby, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.MINI_CLIENT_LINKED, MiniClientComponentMeta, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.RECRUIT_PARAMS, RecruitParamsComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.REPORT_BUG, ReportBugPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.SERVERS_STATS, ServerStats, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (LobbyPackageBusinessHandler(), LobbyDialogsHandler())


class LobbyPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((FALLOUT_ALIASES.FALLOUT_BATTLE_SELECTOR_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.AWARD_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BATTLE_LOADING, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BATTLE_QUEUE, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BATTLE_RESULTS, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BROWSER_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.DEMONSTRATOR_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.ELITE_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.FALLOUT_MULTI_TEAM_BATTLE_LOADING, self.loadViewByCtxEvent),
         (VIEW_ALIAS.GOLD_FISH_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.GET_PREMIUM_POPOVER, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOBBY, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOBBY_CUSTOMIZATION, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOBBY_MENU, self.loadViewByCtxEvent),
         (VIEW_ALIAS.MODULE_INFO_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.PERSONAL_CASE, self.loadViewByCtxEvent),
         (VIEW_ALIAS.PREMIUM_CONGRATULATION_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.PREMIUM_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.PROMO_PREMIUM_IGR_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.QUESTS_RECRUIT_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.REFERRAL_MANAGEMENT_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.REFERRAL_REFERRALS_INTRO_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.REFERRAL_REFERRER_INTRO_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.ROLE_CHANGE, self.loadViewByCtxEvent),
         (VIEW_ALIAS.TANKMAN_SKILLS_DROP_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.TUTORIAL_LOADING, self.loadViewByCtxEvent),
         (VIEW_ALIAS.VEHICLE_BUY_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.VEHICLE_SELL_DIALOG, self.loadViewByCtxEvent),
         (VIEW_ALIAS.VEHICLE_INFO_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.SANDBOX_QUEUE_DIALOG, self.loadViewBySharedEvent))
        super(LobbyPackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)


class LobbyDialogsHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((ShowDialogEvent.SHOW_CAPTCHA_DIALOG, self.__handleShowCaptcha),
         (ShowDialogEvent.SHOW_CHECK_BOX_DIALOG, self.__checkBoxDialogHandler),
         (ShowDialogEvent.SHOW_CONFIRM_MODULE, self.__confirmModuleHandler),
         (ShowDialogEvent.SHOW_DEMOUNT_DEVICE_DIALOG, self.__demountDeviceDialogHandler),
         (ShowDialogEvent.SHOW_DESTROY_DEVICE_DIALOG, self.__destroyDeviceDialogHandler),
         (ShowDialogEvent.SHOW_DISMISS_TANKMAN_DIALOG, self.__dismissTankmanHandler),
         (ShowDialogEvent.SHOW_ICON_DIALOG, self.__iconDialogHandler),
         (ShowDialogEvent.SHOW_ICON_PRICE_DIALOG, self.__iconPriceDialogHandler),
         (ShowDialogEvent.SHOW_PUNISHMENT_DIALOG, self.__punishmentWindowHandler),
         (ShowDialogEvent.SHOW_SIMPLE_DLG, self.__simpleDialogHandler),
         (ShowDialogEvent.SHOW_SYSTEM_MESSAGE_DIALOG, self.__systemMsgDialogHandler),
         (VIEW_ALIAS.FREE_X_P_INFO_WINDOW, self.__showFreeXPInfoWindow),
         (VIEW_ALIAS.RECRUIT_WINDOW, self.__showRecruitWindow))
        super(LobbyDialogsHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.GLOBAL)

    def __checkBoxDialogHandler(self, event):
        self.loadViewWithGenName(VIEW_ALIAS.CHECK_BOX_DIALOG, event.meta, event.handler)

    def __confirmModuleHandler(self, event):
        self.loadViewWithGenName(VIEW_ALIAS.CONFIRM_MODULE_DIALOG, event.meta, event.handler)

    def __demountDeviceDialogHandler(self, event):
        self.loadViewWithGenName(VIEW_ALIAS.DEMOUNT_DEVICE_DIALOG, event.meta, event.handler)

    def __destroyDeviceDialogHandler(self, event):
        self.loadViewWithGenName(VIEW_ALIAS.DESTROY_DEVICE_DIALOG, event.meta, event.handler)

    def __dismissTankmanHandler(self, event):
        self.loadViewWithGenName(VIEW_ALIAS.DISMISS_TANKMAN_DIALOG, event.meta, event.handler)

    def __handleShowCaptcha(self, event):
        self.loadViewWithGenName(VIEW_ALIAS.CAPTCHA_DIALOG, event.meta, event.handler)

    def __iconDialogHandler(self, event):
        self.loadViewWithGenName(VIEW_ALIAS.ICON_DIALOG, event.meta, event.handler)

    def __iconPriceDialogHandler(self, event):
        self.loadViewWithGenName(VIEW_ALIAS.ICON_PRICE_DIALOG, event.meta, event.handler)

    def __punishmentWindowHandler(self, event):
        self.loadViewWithGenName(VIEW_ALIAS.PUNISHMENT_DIALOG, event.meta, event.handler)

    def __showFreeXPInfoWindow(self, event):
        self.loadViewWithDefName(VIEW_ALIAS.FREE_X_P_INFO_WINDOW, VIEW_ALIAS.FREE_X_P_INFO_WINDOW, {'meta': event.meta,
         'handler': event.handler})

    def __showRecruitWindow(self, event):
        windowContainer = self._app.containerManager.getContainer(ViewTypes.WINDOW)
        recruitWindow = windowContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.RECRUIT_WINDOW})
        if recruitWindow is not None:
            recruitWindow.destroy()
        self.loadViewWithDefName(VIEW_ALIAS.RECRUIT_WINDOW, None, event.ctx)
        return

    def __systemMsgDialogHandler(self, event):
        self.loadViewWithGenName(VIEW_ALIAS.SYSTEM_MESSAGE_DIALOG, event.meta, event.handler)

    def __simpleDialogHandler(self, event):
        meta = event.meta
        self.loadViewWithGenName(VIEW_ALIAS.SIMPLE_DIALOG, meta.getMessage(), meta.getTitle(), meta.getButtonLabels(), meta.getCallbackWrapper(event.handler), meta.getViewScopeType(), meta.getTimer())
