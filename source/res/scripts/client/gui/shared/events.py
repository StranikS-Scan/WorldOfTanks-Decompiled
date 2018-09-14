# Embedded file name: scripts/client/gui/shared/events.py
from gui.shared.event_bus import SharedEvent
from shared_utils import CONST_CONTAINER
__all__ = ['ArgsEvent',
 'LoadEvent',
 'ComponentEvent',
 'LoadViewEvent',
 'ShowDialogEvent',
 'LoginEvent',
 'LoginCreateEvent',
 'LoginEventEx',
 'ShowWindowEvent',
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


class AppLifeCycleEvent(SharedEvent):
    INITIALIZING = 'app/initializing'
    INITIALIZED = 'app/initialized'
    DESTROYED = 'app/destroyed'

    def __init__(self, ns, eventType):
        super(AppLifeCycleEvent, self).__init__(eventType)
        self.__ns = ns

    @property
    def ns(self):
        return self.__ns


class GlobalSpaceEvent(SharedEvent):
    GO_NEXT = 'globalSpace/goNext'

    def __init__(self, eventType):
        super(GlobalSpaceEvent, self).__init__(eventType)


class GameEvent(HasCtxEvent):
    SCREEN_SHOT_MADE = 'game/screenShotMade'
    SHOW_EXTENDED_INFO = 'game/showExtendedInfo'
    CHOICE_CONSUMABLE = 'game/choiceConsumable'
    HELP = 'game/help'
    MINIMAP_CMD = 'game/minimapCmd'
    RADIAL_MENU_CMD = 'game/radialMenuCmd'
    GUI_VISIBILITY = 'game/guiVisibility'
    SHOW_CURSOR = 'game/showCursor'
    HIDE_CURSOR = 'game/hideCursor'
    PLAYING_TIME_ON_ARENA = 'game/playingTimeOnArena'


class GUICommonEvent(SharedEvent):
    LOBBY_VIEW_LOADED = 'lobbyViewLoaded'

    def __init__(self, eventType = None):
        super(GUICommonEvent, self).__init__(eventType)


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
    EXIT_FROM_RESEARCH = 'exitFromResearch'


class FocusEvent(HasCtxEvent):
    COMPONENT_FOCUSED = 'onComponentFocused'


class ComponentEvent(SharedEvent):
    COMPONENT_REGISTERED = 'onComponentRegistered'
    COMPONENT_UNREGISTERED = 'onComponentUnRegistered'

    def __init__(self, eventType, owner, componentPy, alias):
        super(ComponentEvent, self).__init__(eventType)
        self.owner = owner
        self.componentPy = componentPy
        self.alias = alias


class LoadViewEvent(HasCtxEvent):

    def __init__(self, alias = None, name = None, ctx = None):
        super(LoadViewEvent, self).__init__(alias, ctx)
        self.name = name if name is not None else alias
        return


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
    SHOW_PUNISHMENT_DIALOG = 'showPunishmentDialog'
    SHOW_EXCHANGE_DIALOG = 'showExchangeDialog'
    SHOW_CHECK_BOX_DIALOG = 'showCheckBoxDialog'

    def __init__(self, meta, handler):
        super(ShowDialogEvent, self).__init__(meta.getEventType())
        self.meta = meta
        self.handler = handler


class LoginEvent(SharedEvent):
    CANCEL_LGN_QUEUE = 'cancelLoginQueue'

    def __init__(self, eventType, alias = '', isSuccess = False, errorMsg = ''):
        super(LoginEvent, self).__init__(eventType=eventType)
        self.alias = alias
        self.isSuccess = isSuccess
        self.errorMsg = errorMsg


class LoginCreateEvent(SharedEvent):
    CREATE_ACC = 'createAnAccount'

    def __init__(self, eventType, alias, title, message, submit):
        super(LoginCreateEvent, self).__init__(eventType=eventType)
        self.title = title
        self.message = message
        self.submit = submit


class LoginEventEx(LoginEvent):
    SET_AUTO_LOGIN = 'setAutoLogin'
    SET_LOGIN_QUEUE = 'setLoginQueue'
    ON_LOGIN_QUEUE_CLOSED = 'onLoginQueueClosed'
    SWITCH_LOGIN_QUEUE_TO_AUTO = 'switchLoginQueueToAuto'

    def __init__(self, eventType, alias, waitingOpen, msg, waitingClose, showAutoLoginBtn):
        super(LoginEventEx, self).__init__(eventType=eventType, alias=alias)
        self.waitingOpen = waitingOpen
        self.msg = msg
        self.waitingClose = waitingClose
        self.showAutoLoginBtn = showAutoLoginBtn


class HideWindowEvent(HasCtxEvent):
    HIDE_COMPANY_WINDOW = 'hideCompanyWindow'
    HIDE_BATTLE_SESSION_WINDOW = 'hideBattleSessionWindow'
    HIDE_UNIT_WINDOW = 'hideUnitWindow'
    HIDE_VEHICLE_SELECTOR_WINDOW = 'showVehicleSelectorWindow'
    HIDE_ROSTER_SLOT_SETTINGS_WINDOW = 'showRosterSlotSettingsWindow'
    HIDE_LEGAL_INFO_WINDOW = 'showLegalInfoWindow'
    HIDE_SANDBOX_QUEUE_DIALOG = 'hideSandboxQueueDialog'
    HIDE_FALLOUT_WINDOW = 'hideFalloutWindow'


class HidePopoverEvent(HasCtxEvent):
    HIDE_POPOVER = 'hidePopover'
    POPOVER_DESTROYED = 'popoverDestroyed'


class LobbySimpleEvent(HasCtxEvent):
    UPDATE_TANK_PARAMS = 'updateTankParams'
    HIGHLIGHT_TANK_PARAMS = 'highlightTankParams'
    SHOW_HELPLAYOUT = 'showHelplayout'
    CLOSE_HELPLAYOUT = 'closeHelplayout'
    EVENTS_UPDATED = 'questUpdated'
    HIDE_HANGAR = 'hideHangar'
    NOTIFY_CURSOR_OVER_3DSCENE = 'notifyCursorOver3dScene'
    PREMIUM_BOUGHT = 'premiumBought'
    WAITING_SHOWN = 'waitingShown'


class TrainingSettingsEvent(HasCtxEvent):
    UPDATE_TRAINING_SETTINGS = 'updateTrainingSettings'


class TechnicalMaintenanceEvent(HasCtxEvent):
    RESET_EQUIPMENT = 'resetEquipment'


class ContactsEvent(HasCtxEvent):
    EDIT_GROUP = 'editGroup'
    REMOVE_GROUP = 'removeGroup'
    CREATE_CONTACT_NOTE = 'createContactNote'
    EDIT_CONTACT_NOTE = 'editContactNote'


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
    GOLD_FISH_CLOSED = 'GoldFishClosed'

    def __init__(self, eventType = None, isAgree = False):
        super(CloseWindowEvent, self).__init__(eventType)
        self.isAgree = isAgree


class CoolDownEvent(SharedEvent):
    GLOBAL = 'globalCoolDown'
    PREBATTLE = 'prebattleCoolDown'
    FORTIFICATION = 'fortificationCoolDown'
    BW_CHAT2 = 'bwChat2CoolDown'
    XMPP = 'xmppCoolDown'
    CLUB = 'club'
    CLAN = 'clan'

    def __init__(self, eventType = None, requestID = 0, coolDown = 5.0):
        super(CoolDownEvent, self).__init__(eventType)
        self.coolDown = coolDown
        self.requestID = requestID


class TutorialEvent(SharedEvent):
    START_TRAINING = 'startTraining'
    STOP_TRAINING = 'stopTraining'
    SHOW_TUTORIAL_BATTLE_HISTORY = 'Tutorial.Dispatcher.BattleHistory'
    ON_COMPONENT_FOUND = 'onComponentFound'
    ON_COMPONENT_LOST = 'onComponentLost'
    ON_TRIGGER_ACTIVATED = 'onTriggerActivated'
    SIMPLE_WINDOW_CLOSED = 'simpleWindowClosed'
    SIMPLE_WINDOW_PROCESSED = 'simpleWindowProcessed'

    def __init__(self, eventType, settingsID = '', targetID = '', reloadIfRun = False, initialChapter = None, restoreIfRun = False, isStopForced = False, isAfterBattle = False):
        super(TutorialEvent, self).__init__(eventType)
        self.settingsID = settingsID
        self.targetID = targetID
        self.reloadIfRun = reloadIfRun
        self.initialChapter = initialChapter
        self.restoreIfRun = restoreIfRun
        self.isStopForced = isStopForced
        self.isAfterBattle = isAfterBattle

    def getState(self):
        return {'reloadIfRun': self.reloadIfRun,
         'initialChapter': self.initialChapter,
         'restoreIfRun': self.restoreIfRun,
         'isStopForced': self.isStopForced,
         'isAfterBattle': self.isAfterBattle}


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
    REQUEST_TO_ACTIVATE = 'rqActivateChannel'
    REQUEST_TO_DEACTIVATE = 'rqDeactivateChannel'
    REQUEST_TO_EXIT = 'rqExitChannel'

    def __init__(self, clientID, eventType = None, ctx = None):
        super(ChannelManagementEvent, self).__init__(eventType, ctx)
        self.clientID = clientID


class PreBattleChannelEvent(ChannelManagementEvent):
    REQUEST_TO_ADD_PRE_BATTLE_CHANNEL = 'loadSquad'
    REQUEST_TO_REMOVE_PRE_BATTLE_CHANNEL = 'removeSquad'

    def __init__(self, clientID, eventType = None, ctx = None):
        super(PreBattleChannelEvent, self).__init__(clientID, eventType, ctx)


class ChannelCarouselEvent(SharedEvent):
    CAROUSEL_INITED = 'carouselInited'
    CAROUSEL_DESTROYED = 'carouselDestroyed'
    OPEN_BUTTON_CLICK = 'openButtonClick'
    MINIMIZE_ALL_CHANNELS = 'minimizeAllChannels'
    CLOSE_ALL_EXCEPT_CURRENT = 'closeAllExceptCurrent'
    CLOSE_BUTTON_CLICK = 'closeButtonClick'

    def __init__(self, target, eventType = None, clientID = None):
        super(ChannelCarouselEvent, self).__init__(eventType)
        self.target = target
        self.clientID = clientID


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
    REQUEST_TIMEOUT = 'requestTimeout'
    VIEW_LOADED = 'viewLoaded'
    SWITCH_TO_MODE = 'switchToMode'
    ON_INTEL_FILTER_APPLY = 'onIntelFilterApplied'
    ON_INTEL_FILTER_RESET = 'onIntelFilterReset'
    ON_INTEL_FILTER_DO_REQUEST = 'onIntelFilterDoRequest'
    TRANSPORTATION_STEP = 'transportationStep'
    CHOICE_DIVISION = 'testChoiceDivision'
    REQUEST_TRANSPORTATION = 'requestTransportation'

    class TRANSPORTATION_STEPS(CONST_CONTAINER):
        NONE = 0
        FIRST_STEP = 1
        NEXT_STEP = 2
        CONFIRMED = 3

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
    CLUB_SETTINGS = 'clubSettings'
    CLUB_HELP = 'clubHelp'
    MEDKIT_HELP = 'medkitHelp'
    REPAIRKITHELP_HELP = 'repairkitHelp'
    FIRE_EXTINGUISHERHELP_HELP = 'fireExtinguisherHelp'
    INVIETES_MANAGEMENT = 'invitesManagementURL'
    GLOBAL_MAP_SUMMARY = 'globalMapSummary'
    GLOBAL_MAP_PROMO_SUMMARY = 'globalMapPromoSummary'
    GLOBAL_MAP_CAP = 'globalMapCap'
    GLOBAL_MAP_PROMO = 'globalMapPromo'

    def __init__(self, eventType, url = '', title = ''):
        super(OpenLinkEvent, self).__init__(eventType)
        self.url = url
        self.title = title


class CalendarEvent(SharedEvent):
    MONTH_CHANGED = 'monthChanged'
    DATE_SELECTED = 'dateSelected'

    def __init__(self, eventType = None, timestamp = None):
        super(CalendarEvent, self).__init__(eventType)
        self.__timestamp = timestamp

    def getTimestamp(self):
        return self.__timestamp


class BubbleTooltipEvent(LobbySimpleEvent):
    SHOW = 'showBubble'

    def __init__(self, eventType, message = None, duration = 5000):
        super(BubbleTooltipEvent, self).__init__(eventType)
        self.__message = message
        self.__duration = duration

    def getMessage(self):
        return self.__message

    def getDuration(self):
        return self.__duration


class WGNCShowItemEvent(SharedEvent):
    SHOW_BASIC_WINDOW = 'wgnc/basicWindow/show'
    SHOW_POLL_WINDOW = 'wgnc/pollWindow/show'
    CLOSE_POLL_WINDOW = 'wgnc/pollWindow/close'

    def __init__(self, notID, target, eventType = None):
        super(WGNCShowItemEvent, self).__init__(eventType)
        self.__notID = notID
        self.__target = target

    def getNotID(self):
        return self.__notID

    def getTarget(self):
        return self.__target
