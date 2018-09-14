# Embedded file name: scripts/client/gui/Scaleform/daapi/business_layer.py
from debug_utils import *
from gui.Scaleform.daapi.settings.config import VIEWS_SETTINGS
from gui.Scaleform.framework import ViewTypes, g_entitiesFactories
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.loaders import SequenceIDLoader
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.genConsts.FALLOUT_ALIASES import FALLOUT_ALIASES
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import ShowDialogEvent, LoginEventEx, LoginCreateEvent

class BusinessHandler(SequenceIDLoader):

    def __init__(self):
        super(BusinessHandler, self).__init__()
        g_entitiesFactories.initSettings(VIEWS_SETTINGS)
        self.__lobbyHdlr = BusinessLobbyHandler()
        self.__dlgsHdlr = BusinessDlgsHandler()
        self._LISTENERS = {LoginEventEx.SET_LOGIN_QUEUE: (self.__showLoginQueue, EVENT_BUS_SCOPE.LOBBY),
         LoginEventEx.SET_AUTO_LOGIN: (self.__showLoginQueue, EVENT_BUS_SCOPE.LOBBY),
         LoginCreateEvent.CREATE_ACC: (self.__createAcc, EVENT_BUS_SCOPE.LOBBY),
         VIEW_ALIAS.LOGIN: (self.__showViewSimple, EVENT_BUS_SCOPE.LOBBY),
         VIEW_ALIAS.INTRO_VIDEO: (self.__showViewSimple, EVENT_BUS_SCOPE.LOBBY),
         VIEW_ALIAS.LOBBY: (self.__showViewSimple, EVENT_BUS_SCOPE.LOBBY),
         VIEW_ALIAS.LOBBY_MENU: (self.__lobbyHdlr.showViewSimple, EVENT_BUS_SCOPE.LOBBY),
         VIEW_ALIAS.LOBBY_HANGAR: (self.__showViewSimple, EVENT_BUS_SCOPE.LOBBY),
         VIEW_ALIAS.LOBBY_SHOP: (self.__showViewSimple, EVENT_BUS_SCOPE.LOBBY),
         VIEW_ALIAS.LOBBY_INVENTORY: (self.__showViewSimple, EVENT_BUS_SCOPE.LOBBY),
         VIEW_ALIAS.LOBBY_PROFILE: (self.__showViewSimple, EVENT_BUS_SCOPE.LOBBY),
         VIEW_ALIAS.LOBBY_BARRACKS: (self.__showViewSimple, EVENT_BUS_SCOPE.LOBBY),
         FORTIFICATION_ALIASES.FORTIFICATIONS_VIEW_ALIAS: (self.__showViewSimple, EVENT_BUS_SCOPE.LOBBY),
         VIEW_ALIAS.LOBBY_CUSTOMIZATION: (self.__showViewSimple, EVENT_BUS_SCOPE.LOBBY),
         VIEW_ALIAS.BATTLE_QUEUE: (self.__lobbyHdlr.showLobbyView, EVENT_BUS_SCOPE.LOBBY),
         VIEW_ALIAS.BATTLE_LOADING: (self.__showViewSimple, EVENT_BUS_SCOPE.LOBBY),
         VIEW_ALIAS.FALLOUT_MULTI_TEAM_BATTLE_LOADING: (self.__showViewSimple, EVENT_BUS_SCOPE.LOBBY),
         VIEW_ALIAS.TUTORIAL_LOADING: (self.__showViewSimple, EVENT_BUS_SCOPE.LOBBY),
         VIEW_ALIAS.REFERRAL_REFERRALS_INTRO_WINDOW: (self.__showViewSimple,),
         VIEW_ALIAS.REFERRAL_REFERRER_INTRO_WINDOW: (self.__showViewSimple,),
         VIEW_ALIAS.FREE_X_P_INFO_WINDOW: (self.__showFreeXPInfoWindow,),
         VIEW_ALIAS.EULA: (self.__showViewSimple,),
         VIEW_ALIAS.EULA_FULL: (self.__showViewSimple,),
         VIEW_ALIAS.LEGAL_INFO_WINDOW: (self.__showViewSimple,),
         VIEW_ALIAS.ELITE_WINDOW: (self.__showViewSimple,),
         VIEW_ALIAS.RECRUIT_WINDOW: (self.__showRecruitWindow,),
         VIEW_ALIAS.QUESTS_RECRUIT_WINDOW: (self.__showViewSimple,),
         VIEW_ALIAS.PROFILE_WINDOW: (self.__showViewSimple, EVENT_BUS_SCOPE.LOBBY),
         VIEW_ALIAS.VEHICLE_BUY_WINDOW: (self.__showViewSimple,),
         VIEW_ALIAS.NOTIFICATIONS_LIST: (self.__showViewSimple, EVENT_BUS_SCOPE.LOBBY),
         VIEW_ALIAS.CREW_OPERATIONS_POPOVER: (self.__showViewSimple, EVENT_BUS_SCOPE.LOBBY),
         VIEW_ALIAS.CREW_ABOUT_DOG_WINDOW: (self.__showViewSimple, EVENT_BUS_SCOPE.LOBBY),
         FORTIFICATION_ALIASES.FORT_BUILDING_CARD_POPOVER_ALIAS: (self.__showViewSimple, EVENT_BUS_SCOPE.LOBBY),
         FORTIFICATION_ALIASES.FORT_ORDER_POPOVER_ALIAS: (self.__showViewSimple, EVENT_BUS_SCOPE.LOBBY),
         FORTIFICATION_ALIASES.FORT_BATTLE_DIRECTION_POPOVER_ALIAS: (self.__showViewSimple, EVENT_BUS_SCOPE.LOBBY),
         FORTIFICATION_ALIASES.FORT_INTELLIGENCE_CLAN_FILTER_POPOVER_ALIAS: (self.__showViewSimple, EVENT_BUS_SCOPE.LOBBY),
         VIEW_ALIAS.BATTLE_TYPE_SELECT_POPOVER: (self.__showViewSimple, EVENT_BUS_SCOPE.LOBBY),
         VIEW_ALIAS.ACCOUNT_POPOVER: (self.__showViewSimple, EVENT_BUS_SCOPE.LOBBY),
         FORTIFICATION_ALIASES.FORT_SETTINGS_PERIPHERY_POPOVER_ALIAS: (self.__showViewSimple, EVENT_BUS_SCOPE.LOBBY),
         FORTIFICATION_ALIASES.FORT_SETTINGS_DEFENCE_HOUR_POPOVER_ALIAS: (self.__showViewSimple, EVENT_BUS_SCOPE.LOBBY),
         FORTIFICATION_ALIASES.FORT_SETTINGS_VACATION_POPOVER_ALIAS: (self.__showViewSimple, EVENT_BUS_SCOPE.LOBBY),
         FORTIFICATION_ALIASES.FORT_SETTINGS_DAYOFF_POPOVER_ALIAS: (self.__showViewSimple, EVENT_BUS_SCOPE.LOBBY),
         FORTIFICATION_ALIASES.FORT_DATE_PICKER_POPOVER_ALIAS: (self.__showViewSimple, EVENT_BUS_SCOPE.LOBBY),
         FORTIFICATION_ALIASES.FORT_ORDER_SELECT_POPOVER_ALIAS: (self.__showViewSimple, EVENT_BUS_SCOPE.LOBBY),
         VIEW_ALIAS.AWARD_WINDOW: (self.__showViewSimple,),
         VIEW_ALIAS.REFERRAL_MANAGEMENT_WINDOW: (self.__showViewSimple,),
         VIEW_ALIAS.BOOSTERS_WINDOW: (self.__showViewSimple,),
         VIEW_ALIAS.RETRAIN_CREW: (self.__showViewSimple,),
         VIEW_ALIAS.SETTINGS_WINDOW: (self.__showViewSimple,),
         VIEW_ALIAS.DEMONSTRATOR_WINDOW: (self.__showViewSimple,),
         VIEW_ALIAS.VEHICLE_INFO_WINDOW: (self.__showViewSimple,),
         VIEW_ALIAS.MODULE_INFO_WINDOW: (self.__showViewSimple,),
         VIEW_ALIAS.TECHNICAL_MAINTENANCE: (self.__showViewSimple, EVENT_BUS_SCOPE.LOBBY),
         VIEW_ALIAS.VEHICLE_SELL_DIALOG: (self.__showViewSimple,),
         VIEW_ALIAS.PREMIUM_WINDOW: (self.__showViewSimple,),
         VIEW_ALIAS.PREMIUM_CONGRATULATION_WINDOW: (self.__showViewSimple,),
         VIEW_ALIAS.GOLD_FISH_WINDOW: (self.__showViewSimple,),
         VIEW_ALIAS.PERSONAL_CASE: (self.__showViewSimple,),
         VIEW_ALIAS.ROLE_CHANGE: (self.__showViewSimple,),
         VIEW_ALIAS.BATTLE_RESULTS: (self.__showViewSimple,),
         VIEW_ALIAS.EVENTS_WINDOW: (self.__showEventWindow,),
         VIEW_ALIAS.TANKMAN_SKILLS_DROP_WINDOW: (self.__showViewSimple,),
         VIEW_ALIAS.PROMO_PREMIUM_IGR_WINDOW: (self.__showViewSimple,),
         VIEW_ALIAS.QUESTS_SEASON_AWARDS_WINDOW: (self.__showViewSimple,),
         VIEW_ALIAS.SQUAD_PROMO_WINDOW: (self.__showViewSimple,),
         VIEW_ALIAS.SWITCH_PERIPHERY_WINDOW: (self.__showViewSimple,),
         FALLOUT_ALIASES.FALLOUT_BATTLE_SELECTOR_WINDOW: (self.__showViewSimple, EVENT_BUS_SCOPE.LOBBY),
         VIEW_ALIAS.BROWSER_WINDOW: (self.__showViewSimple, EVENT_BUS_SCOPE.LOBBY),
         VIEW_ALIAS.GET_PREMIUM_POPOVER: (self.__showViewSimple, EVENT_BUS_SCOPE.LOBBY),
         ShowDialogEvent.SHOW_SIMPLE_DLG: (self.__dlgsHdlr,),
         ShowDialogEvent.SHOW_ICON_DIALOG: (self.__dlgsHdlr,),
         ShowDialogEvent.SHOW_ICON_PRICE_DIALOG: (self.__dlgsHdlr,),
         ShowDialogEvent.SHOW_DEMOUNT_DEVICE_DIALOG: (self.__dlgsHdlr,),
         ShowDialogEvent.SHOW_DESTROY_DEVICE_DIALOG: (self.__dlgsHdlr,),
         ShowDialogEvent.SHOW_CONFIRM_MODULE: (self.__dlgsHdlr,),
         ShowDialogEvent.SHOW_SYSTEM_MESSAGE_DIALOG: (self.__dlgsHdlr,),
         ShowDialogEvent.SHOW_CAPTCHA_DIALOG: (self.__dlgsHdlr,),
         ShowDialogEvent.SHOW_DISMISS_TANKMAN_DIALOG: (self.__dlgsHdlr,),
         ShowDialogEvent.SHOW_PUNISHMENT_DIALOG: (self.__dlgsHdlr,),
         ShowDialogEvent.SHOW_CHECK_BOX_DIALOG: (self.__dlgsHdlr,)}

    def _populate(self):
        EventSystemEntity._populate(self)
        for event, argValues in self._LISTENERS.iteritems():
            self.addListener(event, *argValues)

    def _dispose(self):
        for event, argValues in self._LISTENERS.iteritems():
            self.removeListener(event, *argValues)

        self.__lobbyHdlr.destroy()
        self.__lobbyHdlr = None
        self.__dlgsHdlr.destroy()
        self.__dlgsHdlr = None
        self._LISTENERS.clear()
        self._LISTENERS = None
        EventSystemEntity._dispose(self)
        return

    def __showFreeXPInfoWindow(self, event):
        self.app.loadView(VIEW_ALIAS.FREE_X_P_INFO_WINDOW, VIEW_ALIAS.FREE_X_P_INFO_WINDOW, {'meta': event.meta,
         'handler': event.handler})

    def __showLoginQueue(self, event):
        self._loadView(VIEW_ALIAS.LOGIN_QUEUE, event.waitingOpen, event.msg, event.waitingClose, event.showAutoLoginBtn)

    def __createAcc(self, event):
        self._loadView(VIEW_ALIAS.LOGIN_CREATE_AN_ACC, event.title, event.message, event.submit)

    def __showViewSimple(self, event):
        self.app.loadView(event.eventType, event.name, event.ctx)

    def __showEventWindow(self, event):
        container = self.app.containerManager.getContainer(ViewTypes.WINDOW)
        window = container.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.EVENTS_WINDOW})
        if window is None:
            self.__showViewSimple(event)
        else:
            window.navigate(event.ctx.get('eventType'), event.ctx.get('eventID'))
        return

    def __showRecruitWindow(self, event):
        windowContainer = self.app.containerManager.getContainer(ViewTypes.WINDOW)
        recruitWindow = windowContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.RECRUIT_WINDOW})
        if recruitWindow is not None:
            recruitWindow.destroy()
        self.app.loadView(VIEW_ALIAS.RECRUIT_WINDOW, None, event.ctx)
        return


class BusinessLobbyHandler(SequenceIDLoader):

    def showViewSimple(self, event):
        self.app.loadView(event.eventType, event.eventType, event.ctx)

    def showLobbyView(self, event):
        alias = g_entitiesFactories.getAliasByEvent(event.eventType)
        if alias is not None:
            if event.ctx is not None and len(event.ctx):
                self.app.loadView(alias, alias, event.ctx)
            else:
                self.app.loadView(alias)
        else:
            LOG_ERROR("Passes event '{0}' is not listed in event to alias dict".format(event))
        return


class BusinessDlgsHandler(SequenceIDLoader):

    def __init__(self):
        super(BusinessDlgsHandler, self).__init__()
        self.handlers = {ShowDialogEvent.SHOW_SIMPLE_DLG: self.__simpleDialogHandler,
         ShowDialogEvent.SHOW_ICON_DIALOG: self.__iconDialogHandler,
         ShowDialogEvent.SHOW_ICON_PRICE_DIALOG: self.__iconPriceDialogHandler,
         ShowDialogEvent.SHOW_DEMOUNT_DEVICE_DIALOG: self.__demountDeviceDialogHandler,
         ShowDialogEvent.SHOW_DESTROY_DEVICE_DIALOG: self.__destroyDeviceDialogHandler,
         ShowDialogEvent.SHOW_CONFIRM_MODULE: self.__confirmModuleHandler,
         ShowDialogEvent.SHOW_SYSTEM_MESSAGE_DIALOG: self.__systemMsgDialogHandler,
         ShowDialogEvent.SHOW_CAPTCHA_DIALOG: self.__handleShowCaptcha,
         ShowDialogEvent.SHOW_DISMISS_TANKMAN_DIALOG: self.__dismissTankmanHandler,
         ShowDialogEvent.SHOW_PUNISHMENT_DIALOG: self.__punishmentWindowHandler,
         ShowDialogEvent.SHOW_CHECK_BOX_DIALOG: self.__confirmDialogHandler}

    def _dispose(self):
        self.handlers.clear()
        self.handlers = None
        return

    def __dismissTankmanHandler(self, event):
        self._loadView(VIEW_ALIAS.DISMISS_TANKMAN_DIALOG, event.meta, event.handler)

    def __simpleDialogHandler(self, event):
        meta = event.meta
        self._loadView(VIEW_ALIAS.SIMPLE_DIALOG, meta.getMessage(), meta.getTitle(), meta.getButtonLabels(), meta.getCallbackWrapper(event.handler), meta.getViewScopeType(), meta.getTimer())

    def __confirmModuleHandler(self, event):
        self._loadView(VIEW_ALIAS.CONFIRM_MODULE_DIALOG, event.meta, event.handler)

    def __iconDialogHandler(self, event):
        self._loadView(VIEW_ALIAS.ICON_DIALOG, event.meta, event.handler)

    def __iconPriceDialogHandler(self, event):
        self._loadView(VIEW_ALIAS.ICON_PRICE_DIALOG, event.meta, event.handler)

    def __demountDeviceDialogHandler(self, event):
        self._loadView(VIEW_ALIAS.DEMOUNT_DEVICE_DIALOG, event.meta, event.handler)

    def __punishmentWindowHandler(self, event):
        self._loadView(VIEW_ALIAS.PUNISHMENT_DIALOG, event.meta, event.handler)

    def __destroyDeviceDialogHandler(self, event):
        self._loadView(VIEW_ALIAS.DESTROY_DEVICE_DIALOG, event.meta, event.handler)

    def __systemMsgDialogHandler(self, event):
        self._loadView(VIEW_ALIAS.SYSTEM_MESSAGE_DIALOG, event.meta, event.handler)

    def __handleShowCaptcha(self, event):
        self._loadView(VIEW_ALIAS.CAPTCHA_DIALOG, event.meta, event.handler)

    def __confirmDialogHandler(self, event):
        self._loadView(VIEW_ALIAS.CHECK_BOX_DIALOG, event.meta, event.handler)

    def __call__(self, event):
        if event.eventType in self.handlers:
            return self.handlers[event.eventType](event)
        LOG_WARNING('Unknown dialog event type', event.eventType)
