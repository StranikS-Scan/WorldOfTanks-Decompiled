# Embedded file name: scripts/client/gui/shared/events.py
from gui.shared.event_bus import SharedEvent
from gui.shared.utils import CONST_CONTAINER
__all__ = ['ArgsEvent',
 'LoadEvent',
 'ComponentEvent',
 'ShowViewEvent',
 'ShowDialogEvent',
 'LoginEvent',
 'LoginCreateEvent',
 'LoginEventEx',
 'ShowWindowEvent',
 'StatsStorageEvent',
 'LobbySimpleEvent',
 'FightButtonDisablingEvent',
 'FightButtonEvent',
 'CloseWindowEvent',
 'BrowserEvent']

class HasCtxEvent(SharedEvent):

    def __init__(self, eventType = None, ctx = None):
        super(HasCtxEvent, self).__init__(eventType)
        self.ctx = ctx if ctx is not None else {}
        return


class GUICommonEvent(SharedEvent):
    APP_STARTED = 'appStarted'
    APP_LOGOFF = 'appLogoff'


class GUIEditorEvent(HasCtxEvent):
    HIDE_GUIEditor = 'hideGUIEditor'

    def __init__(self, eventType = None, ctx = None):
        super(GUIEditorEvent, self).__init__(eventType, ctx)


class ArgsEvent(HasCtxEvent):
    UPDATE_ARGS = 'updateArguments'

    def __init__(self, eventType = None, alias = '', ctx = None):
        super(ArgsEvent, self).__init__(eventType, ctx)
        self.alias = alias


class LoadEvent(HasCtxEvent):
    LOAD_PREBATTLE = 'loadPrebattle'
    LOAD_HANGAR = 'loadHangar'
    LOAD_SHOP = 'loadShop'
    LOAD_INVENTORY = 'loadInventory'
    LOAD_PROFILE = 'loadProfile'
    LOAD_TECHTREE = 'loadTechTree'
    LOAD_RESEARCH = 'loadResearch'
    EXIT_FROM_RESEARCH = 'exitFromResearch'
    LOAD_BARRACKS = 'loadBarracks'
    LOAD_FORTIFICATIONS = 'loadFortifications'
    LOAD_CUSTOMIZATION = 'loadCustomization'
    LOAD_EULA = 'loadEULA'
    LOAD_BATTLE_LOADING = 'loadBattleLoading'
    LOAD_TUTORIAL_LOADING = 'loadTutorialLoading'
    LOAD_BATTLE_QUEUE = 'loadBattleQueue'
    LOAD_TRAININGS = 'loadTrainings'
    LOAD_TRAINING_ROOM = 'loadTrainingRoom'


class ComponentEvent(SharedEvent):
    COMPONENT_REGISTERED = 'onComponentRegistered'
    COMPONENT_UNREGISTERED = 'onComponentUnRegistered'

    def __init__(self, eventType, owner, componentPy, alias):
        super(ComponentEvent, self).__init__(eventType)
        self.owner = owner
        self.componentPy = componentPy
        self.alias = alias


class ShowViewEvent(HasCtxEvent):
    SHOW_LOGIN = 'showLogin'
    SHOW_INTRO_VIDEO = 'showIntroVideo'
    SHOW_LOBBY = 'showLobby'
    SHOW_LOBBY_MENU = 'showLobbyMenu'
    ClOSE_LOBBY_MENU = 'closeLobbyMenu'


class ShowDialogEvent(SharedEvent):
    SHOW_SIMPLE_DLG = 'showSimpleDialog'
    SHOW_ICON_DIALOG = 'showIconDialog'
    SHOW_ICON_PRICE_DIALOG = 'showIconPriceDialog'
    SHOW_DEMOUNT_DEVICE_DIALOG = 'showDemountDeviceDialog'
    SHOW_DESTROY_DEVICE_DIALOG = 'showDestroyDeviceDialog'
    SHOW_CONFIRM_MODULE = 'showConfirmModule'
    SHOW_SYSTEM_MESSAGE_DIALOG = 'showSystemMessageDialog'
    SHOW_CAPTCHA_DIALOG = 'showCaptchaDialog'
    SHOW_DISMISS_TANKMAN_DIALOG = 'showDismissTankmanDialog'
    SHOW_CYBER_SPORT_DIALOG = 'showCyberSportDialog'
    SHOW_CONFIRM_ORDER_DIALOG = 'showConfirmOrderDialog'

    def __init__(self, meta, handler):
        super(ShowDialogEvent, self).__init__(meta.getEventType())
        self.meta = meta
        self.handler = handler


class LoginEvent(SharedEvent):
    CANCEL_LGN_QUEUE = 'cancelLoginQueue'
    CLOSE_CREATE_AN_ACCOUNT = 'closeCreateAnAccount'

    def __init__(self, eventType, alias = '', isSuccess = False, errorMsg = ''):
        super(LoginEvent, self).__init__(eventType=eventType)
        self.alias = alias
        self.isSuccess = isSuccess
        self.errorMsg = errorMsg


class LoginCreateEvent(SharedEvent):
    CREATE_ACC = 'createAnAccount'
    CREATE_AN_ACCOUNT_REQUEST = 'createAnAccountRequest'

    def __init__(self, eventType, alias, title, message, submit):
        super(LoginCreateEvent, self).__init__(eventType=eventType)
        self.title = title
        self.message = message
        self.submit = submit


class LoginEventEx(LoginEvent):
    SET_AUTO_LOGIN = 'setAutoLogin'
    SET_LOGIN_QUEUE = 'setLoginQueue'
    ON_LOGIN_QUEUE_CLOSED = 'onLoginQueueClosed'

    def __init__(self, eventType, alias, waitingOpen, msg, waitingClose):
        super(LoginEventEx, self).__init__(eventType=eventType, alias=alias)
        self.waitingOpen = waitingOpen
        self.msg = msg
        self.waitingClose = waitingClose


class ShowWindowEvent(HasCtxEvent):
    SHOW_TEST_WINDOW = 'showTestWindow'
    SHOW_LEGAL_INFO_WINDOW = 'showLegalInfoWindow'
    SHOW_RECRUIT_WINDOW = 'showRecruitWindow'
    SHOW_EXCHANGE_WINDOW = 'showExchangeWindow'
    SHOW_PROFILE_WINDOW = 'showProfileWindow'
    SHOW_EXCHANGE_VCOIN_WINDOW = 'showExchangeVcoinWindow'
    SHOW_EXCHANGE_XP_WINDOW = 'showExchangeXPWindow'
    SHOW_EXCHANGE_FREE_TO_TANKMAN_XP_WINDOW = 'showExchangeFreeToTankmanXpWindow'
    SHOW_VEHICLE_BUY_WINDOW = 'showVehicleBuyWindow'
    SHOW_RETRAIN_CREW_WINDOW = 'showRetrainCrew'
    SHOW_EULA = 'showEULA'
    SHOW_SETTINGS_WINDOW = 'settingsWindow'
    SHOW_VEHICLE_INFO_WINDOW = 'vehicleInfo'
    SHOW_MODULE_INFO_WINDOW = 'moduleInfo'
    SHOW_VEHICLE_SELL_DIALOG = 'vehicleSellWindow'
    SHOW_PREMIUM_DIALOG = 'loadPremiumDialog'
    SHOW_TECHNICAL_MAINTENANCE = 'showTechnicalMaintenance'
    SHOW_TANKMAN_INFO = 'showTankmanInfo'
    SHOW_BATTLE_RESULTS = 'showBattleResults'
    SHOW_EVENTS_WINDOW = 'showEventsWindow'
    SHOW_TANKMAN_DROP_SKILLS_WINDOW = 'showTankmanDropSkillsWindow'
    SHOW_TRAINING_SETTINGS_WINDOW = 'showTrainingSettingsWindow'
    SHOW_SQUAD_WINDOW = 'showSquadWindow'
    SHOW_COMPANY_WINDOW = 'showCompanyWindow'
    SHOW_COMPANIES_WINDOW = 'showCompaniesWindow'
    SHOW_BATTLE_SESSION_WINDOW = 'showBattleSessionWindow'
    SHOW_BATTLE_SESSION_LIST = 'showBattleSessionList'
    SHOW_LAZY_CHANNEL_WINDOW = 'showLazyChannelWindow'
    SHOW_LOBBY_CHANNEL_WINDOW = 'showLobbyChannelWindow'
    SHOW_SEND_INVITES_WINDOW = 'showSendInvitesWindow'
    SHOW_TUTORIAL_BATTLE_HISTORY = 'Tutorial.Dispatcher.BattleHistory'
    SHOW_AUTO_INVITE_WINDOW = 'showAutoInviteWindow'
    SHOW_BROWSER_WINDOW = 'showBrowserWindow'
    SHOW_DEMONSTRATOR_WINDOW = 'showDemonstratorWindow'
    SHOW_FAQ_WINDOW = 'showFAQWindow'
    SHOW_CHANNEL_MANAGEMENT_WINDOW = 'showChannelsManagementWindow'
    SHOW_CONNECT_TO_SECURE_CHANNEL_WINDOW = 'showConnectToSecureChannelWindow'
    SHOW_ELITE_VEHICLE_WINDOW = 'showEliteVehicleWindow'
    SHOW_CONTACTS_WINDOW = 'showWindowEvent'
    SHOW_UNIT_WINDOW = 'showUnitWindow'
    SHOW_ROSTER_SLOT_SETTINGS_WINDOW = 'showRosterSlotSettingsWindow'
    SHOW_VEHICLE_SELECTOR_WINDOW = 'showVehicleSelectorWindow'
    SHOW_G_E_INSPECT_WINDOW = 'showGEInspectWindow'
    SHOW_G_E_DESIGNER_WINDOW = 'showGEDesignerWindow'
    SHOW_FREE_X_P_INFO_WINDOW = 'showFreeXPInfoWindow'
    SHOW_HISTORICAL_BATTLES_WINDOW = 'showHistoricalBattlesListWindow'
    SHOW_FORT_ORDER_CONFIRM_WINDOW = 'showOrderConfirmWindow'


class HideWindowEvent(HasCtxEvent):
    HIDE_SQUAD_WINDOW = 'hideSquadWindow'
    HIDE_COMPANY_WINDOW = 'hideCompanyWindow'
    HIDE_BATTLE_SESSION_WINDOW = 'hideBattleSessionWindow'
    HIDE_UNIT_WINDOW = 'hideUnitWindow'
    HIDE_HISTORICAL_BATTLES_WINDOW = 'hideHistoricalBattlesWindow'
    HIDE_VEHICLE_SELECTOR_WINDOW = 'showVehicleSelectorWindow'
    HIDE_ROSTER_SLOT_SETTINGS_WINDOW = 'showRosterSlotSettingsWindow'
    HIDE_LEGAL_INFO_WINDOW = 'showLegalInfoWindow'


class ShowPopoverEvent(HasCtxEvent):
    SHOW_CREW_OPERATIONS_POPOVER = 'showCrewOperationsPopOver'
    SHOW_NOTIFICATIONS_LIST_POPOVER = 'showNotificationsListPopOver'
    SHOW_FORT_BUILDING_CARD_POPOVER_EVENT = 'showFortBuildingCardPopover'
    SHOW_FORT_ORDER_POPOVER_EVENT = 'showFortOrderPopover'
    SHOW_BATTLE_TYPE_SELECT_POPOVER_EVENT = 'battleTypeSelectPopover'


class HidePopoverEvent(HasCtxEvent):
    HIDE_POPOVER = 'hidePopover'
    POPOVER_DESTROYED = 'popoverDestroyed'


class StatsStorageEvent(HasCtxEvent):
    EXPERIENCE_RESPONSE = 'common.experienceResponse'
    TANKMAN_CHANGE_RESPONSE = 'common.tankmanChangeResponse'
    CREDITS_RESPONSE = 'common.creditsResponse'
    GOLD_RESPONSE = 'common.goldResponse'
    PREMIUM_RESPONSE = 'common.premiumResponse'
    VEHICLE_CHANGE_RESPONSE = 'common.vehicleChangeResponse'
    SPEAKING_PLAYERS_RESPONSE = 'common.speakingPlayersResponse'
    ACCOUNT_ATTRS = 'common.accountAttrs'
    DENUNCIATIONS = 'common.denunciations'
    NATIONS = 'common.nations'


class LobbySimpleEvent(HasCtxEvent):
    UPDATE_TANK_PARAMS = 'updateTankParams'
    HIGHLIGHT_TANK_PARAMS = 'highlightTankParams'
    SHOW_HELPLAYOUT = 'showHelplayout'
    CLOSE_HELPLAYOUT = 'closeHelplayout'
    EVENTS_UPDATED = 'questUpdated'


class TrainingSettingsEvent(HasCtxEvent):
    UPDATE_TRAINING_SETTINGS = 'updateTrainingSettings'


class FightButtonDisablingEvent(LobbySimpleEvent):
    FIGHT_BUTTON_DISABLE = 'fightButtonDisable'

    def __init__(self, eventType, isDisabled, toolTip):
        super(FightButtonDisablingEvent, self).__init__(eventType)
        self.isDisabled = isDisabled
        self.toolTip = toolTip


class FightButtonEvent(LobbySimpleEvent):
    FIGHT_BUTTON_UPDATE = 'updateFightButton'


class SkillDropEvent(SharedEvent):
    SKILL_DROPPED_SUCCESSFULLY = 'skillDroppedSuccess'


class CloseWindowEvent(SharedEvent):
    EULA_CLOSED = 'EULAClosed'

    def __init__(self, eventType = None, isAgree = False):
        super(CloseWindowEvent, self).__init__(eventType)
        self.isAgree = isAgree


class CoolDownEvent(SharedEvent):
    GLOBAL = 'globalCoolDown'
    PREBATTLE = 'prebattleCoolDown'
    FORTIFICATION = 'fortificationCoolDown'

    def __init__(self, eventType = None, requestID = 0, coolDown = 5.0):
        super(CoolDownEvent, self).__init__(eventType)
        self.coolDown = coolDown
        self.requestID = requestID


class TutorialEvent(SharedEvent):
    UI_CONTROL_ADDED = 'tutorialUIControlAdded'
    UI_CONTROL_REMOVED = 'tutorialUIControlRemoved'
    RESTART = 'restartTutorial'
    REFUSE = 'refuseTutorial'

    def __init__(self, eventType = None, targetID = None):
        super(TutorialEvent, self).__init__(eventType)
        self.targetID = targetID


class MessengerEvent(HasCtxEvent):
    PRB_CHANNEL_CTRL_INITED = 'prbChannelCtrlInited'
    PRB_CHANNEL_CTRL_REQUEST_DESTROY = 'prbChannelCtrlRequestDestroy'
    PRB_CHANNEL_CTRL_DESTROYED = 'prbChannelCtrlDestroyed'
    LAZY_CHANNEL_CTRL_INITED = 'lazyChannelCtrlInited'
    LAZY_CHANNEL_CTRL_DESTROYED = 'lazyChannelCtrlDestroyed'
    LOBBY_CHANNEL_CTRL_INITED = 'lobbyChannelCtrlInited'
    LOBBY_CHANNEL_CTRL_DESTROYED = 'lobbyChannelCtrlDestroyed'
    BATTLE_CHANNEL_CTRL_INITED = 'battleChannelCtrlInited'
    BATTLE_CHANNEL_CTRL_DESTROY = 'battleChannelCtrlDestroyed'


class ChannelManagementEvent(HasCtxEvent):
    REQUEST_TO_ADD = 'requestToAdd'
    REQUEST_TO_REMOVE = 'requestToRemove'
    REQUEST_TO_CHANGE = 'requestToChange'
    REQUEST_TO_SHOW = 'requestToShow'

    def __init__(self, clientID, eventType = None, ctx = None):
        super(ChannelManagementEvent, self).__init__(eventType, ctx)
        self.clientID = clientID


class ChannelCarouselEvent(SharedEvent):
    CAROUSEL_INITED = 'carouselInited'
    CAROUSEL_DESTROYED = 'carouselDestroyed'
    OPEN_BUTTON_CLICK = 'openButtonClick'
    CLOSE_BUTTON_CLICK = 'closeButtonClick'

    def __init__(self, target, eventType = None, clientID = None):
        super(ChannelCarouselEvent, self).__init__(eventType)
        self.target = target
        self.clientID = clientID


class BrowserEvent(SharedEvent):
    BROWSER_LOAD_START = 'browserLoadStart'
    BROWSER_LOAD_END = 'browserLoadEnd'


class AutoInviteEvent(SharedEvent):
    INVITE_RECEIVED = 'inviteReceived'

    def __init__(self, invite, eventType = None):
        super(AutoInviteEvent, self).__init__(eventType)
        self.invite = invite


class CSVehicleSelectEvent(HasCtxEvent):
    VEHICLE_SELECTED = 'vehicleSelected'

    def __init__(self, eventType = None, ctx = None):
        super(CSVehicleSelectEvent, self).__init__(eventType, ctx)


class CSRosterSlotSettingsWindow(HasCtxEvent):
    APPLY_SLOT_SETTINGS = 'applySlotSettings'

    def __init__(self, eventType = None, ctx = None):
        super(CSRosterSlotSettingsWindow, self).__init__(eventType, ctx)


class FortEvent(HasCtxEvent):
    SWITCH_TO_MODE = 'switchToMode'
    TEST_CHOICE_DIVISION = 'testChoiceDivision'
    TRANSPORTATION_STEP = 'transportationStep'

    class TRANSPORTATION_STEPS(CONST_CONTAINER):
        INITIAL = 0
        FIRST_STEP = 1

    def __init__(self, eventType = None, ctx = None):
        super(FortEvent, self).__init__(eventType, ctx)


class FortOrderEvent(HasCtxEvent):
    USE_ORDER = 'useOrder'
    CREATE_ORDER = 'createOrder'

    def __init__(self, eventType = None, ctx = None):
        super(FortOrderEvent, self).__init__(eventType, ctx)


class OpenLinkEvent(SharedEvent):
    SPECIFIED = 'openSpecifiedURL'
    REGISTRATION = 'openRegistrationURL'
    RECOVERY_PASSWORD = 'openRecoveryPasswordURL'
    PAYMENT = 'openPaymentURL'
    SECURITY_SETTINGS = 'openSecuritySettingsURL'
    SUPPORT = 'openSupportURL'
    MIGRATION = 'openMigrationURL'
    FORT_DESC = 'fortDescription'
    CLAN_SEARCH = 'clanSearch'
    CLAN_CREATE = 'clanCreate'

    def __init__(self, eventType, url = ''):
        super(OpenLinkEvent, self).__init__(eventType)
        self.url = url
