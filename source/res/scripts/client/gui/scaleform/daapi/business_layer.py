# Embedded file name: scripts/client/gui/Scaleform/daapi/business_layer.py
import BigWorld
from debug_utils import *
from gui.Scaleform.daapi.settings import VIEWS_SETTINGS, VIEWS_PACKAGES
from gui.Scaleform.framework import ViewTypes, g_entitiesFactories
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.loaders import SequenceIDLoader, PackageBusinessHandler
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import ShowDialogEvent, ShowViewEvent, LoadEvent, ShowWindowEvent, LoginEventEx, LoginCreateEvent, ShowPopoverEvent

class BusinessHandler(SequenceIDLoader):

    def __init__(self):
        super(BusinessHandler, self).__init__()
        g_entitiesFactories.initSettings(VIEWS_SETTINGS)
        self.__packagesHandlers = []
        self.__initPackages(VIEWS_PACKAGES)
        self.__lobbyHdlr = BusinessLobbyHandler()
        self.__dlgsHdlr = BusinessDlgsHandler()
        self._LISTENERS = {LoginEventEx.SET_LOGIN_QUEUE: (self.__showLoginQueue, EVENT_BUS_SCOPE.LOBBY),
         LoginEventEx.SET_AUTO_LOGIN: (self.__showLoginQueue, EVENT_BUS_SCOPE.LOBBY),
         LoginCreateEvent.CREATE_ACC: (self.__createAcc, EVENT_BUS_SCOPE.LOBBY),
         ShowViewEvent.SHOW_LOGIN: (self.__showLogin,),
         ShowViewEvent.SHOW_INTRO_VIDEO: (self.__showIntroVideo,),
         ShowViewEvent.SHOW_LOBBY: (self.__showLobby,),
         ShowViewEvent.SHOW_LOBBY_MENU: (self.__lobbyHdlr.showLobbyMenu, EVENT_BUS_SCOPE.LOBBY),
         LoadEvent.LOAD_HANGAR: (self.__lobbyHdlr.showLobbyView, EVENT_BUS_SCOPE.LOBBY),
         LoadEvent.LOAD_INVENTORY: (self.__lobbyHdlr.showLobbyView, EVENT_BUS_SCOPE.LOBBY),
         LoadEvent.LOAD_SHOP: (self.__lobbyHdlr.showLobbyView, EVENT_BUS_SCOPE.LOBBY),
         LoadEvent.LOAD_PROFILE: (self.__lobbyHdlr.showLobbyView, EVENT_BUS_SCOPE.LOBBY),
         LoadEvent.LOAD_BARRACKS: (self.__lobbyHdlr.showLobbyView, EVENT_BUS_SCOPE.LOBBY),
         LoadEvent.LOAD_FORTIFICATIONS: (self.__lobbyHdlr.showLobbyView, EVENT_BUS_SCOPE.LOBBY),
         LoadEvent.LOAD_CUSTOMIZATION: (self.__lobbyHdlr.showLobbyView, EVENT_BUS_SCOPE.LOBBY),
         LoadEvent.LOAD_BATTLE_QUEUE: (self.__lobbyHdlr.showLobbyView, EVENT_BUS_SCOPE.LOBBY),
         LoadEvent.LOAD_BATTLE_LOADING: (self.__lobbyHdlr.showLobbyView, EVENT_BUS_SCOPE.LOBBY),
         LoadEvent.LOAD_TUTORIAL_LOADING: (self.__lobbyHdlr.showLobbyView, EVENT_BUS_SCOPE.LOBBY),
         ShowWindowEvent.SHOW_FREE_X_P_INFO_WINDOW: (self.__showFreeXPInfoWindow,),
         ShowWindowEvent.SHOW_TEST_WINDOW: (self.__showTestWindow,),
         ShowWindowEvent.SHOW_EULA: (self.__showEULA,),
         ShowWindowEvent.SHOW_LEGAL_INFO_WINDOW: (self.__showLegalInfoWindow,),
         ShowWindowEvent.SHOW_ELITE_VEHICLE_WINDOW: (self.__showEliteWindow,),
         ShowWindowEvent.SHOW_RECRUIT_WINDOW: (self.__showRecruitWindow,),
         ShowWindowEvent.SHOW_EXCHANGE_WINDOW: (self.__showExchangeWindow, EVENT_BUS_SCOPE.LOBBY),
         ShowWindowEvent.SHOW_PROFILE_WINDOW: (self.__showProfileWindow, EVENT_BUS_SCOPE.LOBBY),
         ShowWindowEvent.SHOW_EXCHANGE_VCOIN_WINDOW: (self.__showExchangeVcoinWindow, EVENT_BUS_SCOPE.LOBBY),
         ShowWindowEvent.SHOW_EXCHANGE_XP_WINDOW: (self.__showExchangeXPWindow, EVENT_BUS_SCOPE.LOBBY),
         ShowWindowEvent.SHOW_EXCHANGE_FREE_TO_TANKMAN_XP_WINDOW: (self.__showExchangeFreeToTankmanXpWindow, EVENT_BUS_SCOPE.LOBBY),
         ShowWindowEvent.SHOW_VEHICLE_BUY_WINDOW: (self.__showVehicleBuyWindow,),
         ShowPopoverEvent.SHOW_NOTIFICATIONS_LIST_POPOVER: (self.__showNotificationsList,),
         ShowPopoverEvent.SHOW_CREW_OPERATIONS_POPOVER: (self.__showCrewOperationsPopOver,),
         ShowPopoverEvent.SHOW_FORT_BUILDING_CARD_POPOVER_EVENT: (self.__showFortBuildingsPopOver,),
         ShowPopoverEvent.SHOW_FORT_ORDER_POPOVER_EVENT: (self.__showFortOrderPopover,),
         ShowPopoverEvent.SHOW_FORT_BATTLE_DIRECTION_POPOVER_EVENT: (self.__showFortBattleDirectionPopover,),
         ShowPopoverEvent.SHOW_FORT_INTELLIGENCE_CLAN_FILTER_POPOVER_EVENT: (self.__showFortIntelligenceClanFilterPopover,),
         ShowPopoverEvent.SHOW_BATTLE_TYPE_SELECT_POPOVER_EVENT: (self.__showBattleTypeSelectPopover,),
         ShowPopoverEvent.SHOW_ACCOUNT_POPOVER_EVENT: (self.__showAccountPopover,),
         ShowPopoverEvent.SHOW_FORT_SETTINGS_PERIPHERY_POPOVER_EVENT: (self.__showFortSettingsPeripheryPopover,),
         ShowPopoverEvent.SHOW_FORT_SETTINGS_DEFENCE_HOUR_POPOVER_EVENT: (self.__showFortSettingsDefenceHourPopover,),
         ShowPopoverEvent.SHOW_FORT_SETTINGS_VACATION_POPOVER_EVENT: (self.__showFortSettingsVacationPopover,),
         ShowPopoverEvent.SHOW_FORT_SETTINGS_DAYOFF_POPOVER_EVENT: (self.__showFortSettingsDayoffPopover,),
         ShowPopoverEvent.SHOW_FORT_DATE_PICKER_POPOVER_EVENT: (self.__showFortDatePickerPopover,),
         ShowWindowEvent.SHOW_RETRAIN_CREW_WINDOW: (self.__showRetrainCrewWindow,),
         ShowWindowEvent.SHOW_SETTINGS_WINDOW: (self.__showSettingsWindow,),
         ShowWindowEvent.SHOW_DEMONSTRATOR_WINDOW: (self.__showDemonstratorWindow,),
         ShowWindowEvent.SHOW_VEHICLE_INFO_WINDOW: (self.__showVehicleInfoWindow,),
         ShowWindowEvent.SHOW_MODULE_INFO_WINDOW: (self.__showModuleInfoWindow,),
         ShowWindowEvent.SHOW_TECHNICAL_MAINTENANCE: (self.__showTechnicalMaintenance,),
         ShowWindowEvent.SHOW_VEHICLE_SELL_DIALOG: (self.__showVehicleSellDialog,),
         ShowWindowEvent.SHOW_PREMIUM_DIALOG: (self.__lobbyHdlr.showPremiumDialog,),
         ShowWindowEvent.SHOW_TANKMAN_INFO: (self.__lobbyHdlr.showCrewTankmanInfo,),
         ShowWindowEvent.SHOW_BATTLE_RESULTS: (self.__lobbyHdlr.showBattleResults,),
         ShowWindowEvent.SHOW_EVENTS_WINDOW: (self.__lobbyHdlr.showEventsWindow,),
         ShowWindowEvent.SHOW_HEADER_TUTORIAL_WINDOW: (self.__lobbyHdlr.showHeaderTutorialWindow,),
         ShowWindowEvent.SHOW_TANKMAN_DROP_SKILLS_WINDOW: (self.__lobbyHdlr.showTankmanDropSkillsWindow,),
         ShowWindowEvent.SHOW_BROWSER_WINDOW: (self.__lobbyHdlr.showBrowserWindow, EVENT_BUS_SCOPE.LOBBY),
         ShowDialogEvent.SHOW_SIMPLE_DLG: (self.__dlgsHdlr,),
         ShowDialogEvent.SHOW_ICON_DIALOG: (self.__dlgsHdlr,),
         ShowDialogEvent.SHOW_ICON_PRICE_DIALOG: (self.__dlgsHdlr,),
         ShowDialogEvent.SHOW_DEMOUNT_DEVICE_DIALOG: (self.__dlgsHdlr,),
         ShowDialogEvent.SHOW_DESTROY_DEVICE_DIALOG: (self.__dlgsHdlr,),
         ShowDialogEvent.SHOW_CONFIRM_MODULE: (self.__dlgsHdlr,),
         ShowDialogEvent.SHOW_SYSTEM_MESSAGE_DIALOG: (self.__dlgsHdlr,),
         ShowDialogEvent.SHOW_CAPTCHA_DIALOG: (self.__dlgsHdlr,),
         ShowDialogEvent.SHOW_HEADER_TUTORIAL_DIALOG: (self.__dlgsHdlr,),
         ShowDialogEvent.SHOW_DISMISS_TANKMAN_DIALOG: (self.__dlgsHdlr,),
         ShowDialogEvent.SHOW_PUNISHMENT_DIALOG: (self.__dlgsHdlr,)}

    def _populate(self):
        EventSystemEntity._populate(self)
        for event, argValues in self._LISTENERS.iteritems():
            self.addListener(event, *argValues)

        for handler in self.__packagesHandlers:
            handler.init()

    def _dispose(self):
        for event, argValues in self._LISTENERS.iteritems():
            self.removeListener(event, *argValues)

        self.__lobbyHdlr.destroy()
        self.__lobbyHdlr = None
        self.__dlgsHdlr.destroy()
        self.__dlgsHdlr = None
        self._LISTENERS.clear()
        self._LISTENERS = None
        while len(self.__packagesHandlers):
            self.__packagesHandlers.pop().fini()

        EventSystemEntity._dispose(self)
        return

    def __initPackages(self, packages):
        for package in packages:
            name = '{0:>s}.sf_settings'.format(package)
            imported = __import__(name, fromlist=['sf_settings'])
            getter = getattr(imported, 'getViewSettings', None)
            if getter is None or not callable(getter):
                raise Exception, 'Package {0} does not have method getViewSettings'.format(name)
            g_entitiesFactories.initSettings(getter())
            getter = getattr(imported, 'getBusinessHandlers', None)
            if getter is not None:
                if callable(getter):
                    handlers = getter()
                    for handler in handlers:
                        if not isinstance(handler, PackageBusinessHandler):
                            raise Exception, 'Package {0} returned invalid business handler'.format(name)
                        self.__packagesHandlers.append(handler)

                else:
                    raise Exception, 'Package {0} does not have method getBusinessHandler'.format(name)

        return

    def __showFreeXPInfoWindow(self, event):
        self._loadView(VIEW_ALIAS.FREE_X_P_INFO_WINDOW, event.meta, event.handler)

    def __showLoginQueue(self, event):
        self._loadView(VIEW_ALIAS.LOGIN_QUEUE, event.waitingOpen, event.msg, event.waitingClose, event.showAutoLoginBtn)

    def __createAcc(self, event):
        self._loadView(VIEW_ALIAS.LOGIN_CREATE_AN_ACC, event.title, event.message, event.submit)

    def __showLogin(self, event):
        self._loadView(VIEW_ALIAS.LOGIN, event.ctx)

    def __showIntroVideo(self, event):
        self._loadView(VIEW_ALIAS.INTRO_VIDEO, event.ctx)

    def __showLobby(self, event):
        self._loadView(VIEW_ALIAS.LOBBY, event.ctx.get('isInQueue', False))

    def __showTestWindow(self, event, arg1):
        self._loadView(VIEW_ALIAS.TEST_WINDOW, arg1)

    def __showLegalInfoWindow(self, event):
        eulaType = VIEW_ALIAS.EULA
        self.app.loadView(VIEW_ALIAS.LEGAL_INFO_WINDOW, VIEW_ALIAS.LEGAL_INFO_WINDOW)

    def __showEULA(self, event):
        eulaType = VIEW_ALIAS.EULA
        if event.ctx.get('isFull', False):
            eulaType = VIEW_ALIAS.EULA_FULL
        self._loadView(eulaType, {'text': event.ctx.get('text', '')})

    def __showEliteWindow(self, event):
        name = 'EliteWindow' + str(event.ctx.get('vehTypeCompDescr'))
        self.app.loadView(VIEW_ALIAS.ELITE_WINDOW, name, event.ctx)

    def __showRecruitWindow(self, event):
        windowContainer = self.app.containerManager.getContainer(ViewTypes.WINDOW)
        recruitWindow = windowContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.RECRUIT_WINDOW})
        if recruitWindow is not None:
            recruitWindow.destroy()
        self.app.loadView(VIEW_ALIAS.RECRUIT_WINDOW, None, event.ctx)
        return

    def __showExchangeWindow(self, event):
        self.app.loadView(VIEW_ALIAS.EXCHANGE_WINDOW, VIEW_ALIAS.EXCHANGE_WINDOW)

    def __showProfileWindow(self, event):
        self.app.loadView(VIEW_ALIAS.PROFILE_WINDOW, 'window_%s' % event.ctx.get('databaseID'), event.ctx)

    def __showExchangeVcoinWindow(self, event):
        self.app.loadView(VIEW_ALIAS.EXCHANGE_VCOIN_WINDOW, VIEW_ALIAS.EXCHANGE_VCOIN_WINDOW)

    def __showExchangeXPWindow(self, event):
        self.app.loadView(VIEW_ALIAS.EXCHANGE_XP_WINDOW, VIEW_ALIAS.EXCHANGE_XP_WINDOW)

    def __showExchangeFreeToTankmanXpWindow(self, event):
        self.app.loadView(VIEW_ALIAS.EXCHANGE_FREE_TO_TANKMAN_XP_WINDOW, VIEW_ALIAS.EXCHANGE_FREE_TO_TANKMAN_XP_WINDOW + '_' + str(event.ctx.get('tankManId')), event.ctx)

    def __showVehicleBuyWindow(self, event):
        self._loadView(VIEW_ALIAS.VEHICLE_BUY_WINDOW, event.ctx)

    def __showNotificationsList(self, event):
        self.app.loadView(VIEW_ALIAS.NOTIFICATIONS_LIST, VIEW_ALIAS.NOTIFICATIONS_LIST, event.ctx)

    def __showFortBuildingsPopOver(self, event):
        self.app.loadView(FORTIFICATION_ALIASES.FORT_BUILDING_CARD_POPOVER_ALIAS, FORTIFICATION_ALIASES.FORT_BUILDING_CARD_POPOVER_ALIAS, event.ctx)

    def __showFortOrderPopover(self, event):
        self.app.loadView(FORTIFICATION_ALIASES.FORT_ORDER_POPOVER_ALIAS, FORTIFICATION_ALIASES.FORT_ORDER_POPOVER_ALIAS, event.ctx)

    def __showFortBattleDirectionPopover(self, event):
        self.app.loadView(FORTIFICATION_ALIASES.FORT_BATTLE_DIRECTION_POPOVER_ALIAS, FORTIFICATION_ALIASES.FORT_BATTLE_DIRECTION_POPOVER_ALIAS, event.ctx)

    def __showFortIntelligenceClanFilterPopover(self, event):
        self.app.loadView(FORTIFICATION_ALIASES.FORT_INTELLIGENCE_CLAN_FILTER_POPOVER_ALIAS, FORTIFICATION_ALIASES.FORT_INTELLIGENCE_CLAN_FILTER_POPOVER_ALIAS, event.ctx)

    def __showFortSettingsPeripheryPopover(self, event):
        self.app.loadView(FORTIFICATION_ALIASES.FORT_SETTINGS_PERIPHERY_POPOVER_ALIAS, FORTIFICATION_ALIASES.FORT_SETTINGS_PERIPHERY_POPOVER_ALIAS, event.ctx)

    def __showFortSettingsDefenceHourPopover(self, event):
        self.app.loadView(FORTIFICATION_ALIASES.FORT_SETTINGS_DEFENCE_HOUR_POPOVER_ALIAS, FORTIFICATION_ALIASES.FORT_SETTINGS_DEFENCE_HOUR_POPOVER_ALIAS, event.ctx)

    def __showFortSettingsVacationPopover(self, event):
        self.app.loadView(FORTIFICATION_ALIASES.FORT_SETTINGS_VACATION_POPOVER_ALIAS, FORTIFICATION_ALIASES.FORT_SETTINGS_VACATION_POPOVER_ALIAS, event.ctx)

    def __showFortSettingsDayoffPopover(self, event):
        self.app.loadView(FORTIFICATION_ALIASES.FORT_SETTINGS_DAYOFF_POPOVER_ALIAS, FORTIFICATION_ALIASES.FORT_SETTINGS_DAYOFF_POPOVER_ALIAS, event.ctx)

    def __showFortDatePickerPopover(self, event):
        self.app.loadView(FORTIFICATION_ALIASES.FORT_DATE_PICKER_POPOVER_ALIAS, FORTIFICATION_ALIASES.FORT_DATE_PICKER_POPOVER_ALIAS, event.ctx)

    def __showBattleTypeSelectPopover(self, event):
        self.app.loadView(VIEW_ALIAS.BATTLE_TYPE_SELECT_POPOVER, VIEW_ALIAS.BATTLE_TYPE_SELECT_POPOVER, event.ctx)

    def __showAccountPopover(self, event):
        self.app.loadView(VIEW_ALIAS.ACCOUNT_POPOVER, VIEW_ALIAS.ACCOUNT_POPOVER, event.ctx)

    def __showRetrainCrewWindow(self, event):
        self._loadView(VIEW_ALIAS.RETRAIN_CREW, event.ctx)

    def __showCrewOperationsPopOver(self, event):
        self.app.loadView(VIEW_ALIAS.CREW_OPERATIONS_POPOVER, VIEW_ALIAS.CREW_OPERATIONS_POPOVER, event.ctx)

    def __showVehicleInfoWindow(self, event):
        vCompactDescr = 0
        if 'vehicleCompactDescr' in event.ctx:
            vCompactDescr = event.ctx['vehicleCompactDescr']
        self.app.loadView(VIEW_ALIAS.VEHICLE_INFO_WINDOW, '{0:>s}{1:n}'.format(VIEW_ALIAS.VEHICLE_INFO_WINDOW, vCompactDescr), **event.ctx)

    def __showModuleInfoWindow(self, event):
        self.app.loadView(VIEW_ALIAS.MODULE_INFO_WINDOW, ''.join([VIEW_ALIAS.MODULE_INFO_WINDOW, str(event.ctx.get('moduleCompactDescr', 0))]), **event.ctx)

    def __showTechnicalMaintenance(self, event):
        self.app.loadView(VIEW_ALIAS.TECHNICAL_MAINTENANCE, VIEW_ALIAS.TECHNICAL_MAINTENANCE, **event.ctx)

    def __showVehicleSellDialog(self, event):
        self._loadView(VIEW_ALIAS.VEHICLE_SELL_DIALOG, **event.ctx)

    def __showSettingsWindow(self, event):
        self._loadView(VIEW_ALIAS.SETTINGS_WINDOW, event.ctx)

    def __showDemonstratorWindow(self, event):
        self._loadView(VIEW_ALIAS.DEMONSTRATOR_WINDOW)


class BusinessLobbyHandler(SequenceIDLoader):

    def showLobbyMenu(self, event):
        self.app.loadView(VIEW_ALIAS.LOBBY_MENU)

    def showPremiumDialog(self, event):
        self.app.loadView(VIEW_ALIAS.PREMIUM_DIALOG)

    def showCrewTankmanInfo(self, event):
        name = 'personalCase' + str(event.ctx['tankmanID'])
        self.app.loadView(VIEW_ALIAS.PERSONAL_CASE, name, event.ctx)

    def showBattleResults(self, event):
        arenaUniqueID = event.ctx.get('data')
        self.app.loadView(VIEW_ALIAS.BATTLE_RESULTS, 'battleResults' + str(arenaUniqueID), {'data': arenaUniqueID})

    def showEventsWindow(self, event):
        windowContainer = self.app.containerManager.getContainer(ViewTypes.WINDOW)
        window = windowContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.EVENTS_WINDOW})
        if window is not None:
            window.selectCurrentEvent(event.ctx.get('eventID'))
        self.app.loadView(VIEW_ALIAS.EVENTS_WINDOW, VIEW_ALIAS.EVENTS_WINDOW, event.ctx)
        return

    def showHeaderTutorialWindow(self, event):
        viewAlias = VIEW_ALIAS.HEADER_TUTORIAL_WINDOW
        self.app.loadView(viewAlias, viewAlias, event.ctx)

    def showTankmanDropSkillsWindow(self, event):
        name = 'skillDrop_' + str(event.ctx['tankmanID'])
        self.app.loadView(VIEW_ALIAS.TANKMAN_SKILLS_DROP_WINDOW, name, event.ctx)

    def showBrowserWindow(self, event):
        self.app.loadView(VIEW_ALIAS.BROWSER_WINDOW, VIEW_ALIAS.BROWSER_WINDOW, event.ctx)

    def showLobbyView(self, event):
        alias = g_entitiesFactories.getAliasByEvent(event.eventType)
        if alias is not None:
            if event.ctx is not None and len(event.ctx):
                self.app.loadView(alias, ctx=event.ctx)
            else:
                self.app.loadView(alias)
        else:
            LOG_ERROR("Passes event '{0}' is not listed in event to alias dict".format(event))
        return


class StatsStorageHandler(EventSystemEntity):
    pass


class BusinessDlgsHandler(SequenceIDLoader):

    def __init__(self):
        super(BusinessDlgsHandler, self).__init__()
        self.handlers = {ShowDialogEvent.SHOW_SIMPLE_DLG: self.__simpleDialogHandler,
         ShowDialogEvent.SHOW_ICON_DIALOG: self.__iconDialogHandler,
         ShowDialogEvent.SHOW_ICON_PRICE_DIALOG: self.__iconPriceDialogHandler,
         ShowDialogEvent.SHOW_DEMOUNT_DEVICE_DIALOG: self.__demountDeviceDialogHandler,
         ShowDialogEvent.SHOW_DESTROY_DEVICE_DIALOG: self.__destroyDeviceDialogHandler,
         ShowDialogEvent.SHOW_CONFIRM_MODULE: self.__confirmModuleHandler,
         ShowDialogEvent.SHOW_HEADER_TUTORIAL_DIALOG: self.__headerTutorialDialogHandler,
         ShowDialogEvent.SHOW_SYSTEM_MESSAGE_DIALOG: self.__systemMsgDialogHandler,
         ShowDialogEvent.SHOW_CAPTCHA_DIALOG: self.__handleShowCaptcha,
         ShowDialogEvent.SHOW_DISMISS_TANKMAN_DIALOG: self.__dismissTankmanHandler,
         ShowDialogEvent.SHOW_PUNISHMENT_DIALOG: self.__punishmentWindowHandler}

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

    def __headerTutorialDialogHandler(self, event):
        self._loadView(VIEW_ALIAS.HEADER_TUTORIAL_DIALOG, event.meta, event.handler)

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

    def __call__(self, event):
        if event.eventType in self.handlers:
            return self.handlers[event.eventType](event)
        LOG_WARNING('Unknown dialog event type', event.eventType)
