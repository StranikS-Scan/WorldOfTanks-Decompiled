# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/events.py
import logging
from collections import namedtuple
import typing
from enum import Enum
from gui.shared.event_bus import SharedEvent
from shared_utils import CONST_CONTAINER
if typing.TYPE_CHECKING:
    from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
    from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
__all__ = ('ArgsEvent', 'ComponentEvent', 'LoadViewEvent', 'LoadGuiImplViewEvent', 'ShowDialogEvent', 'LoginEvent', 'LoginEventEx', 'LobbySimpleEvent', 'FightButtonDisablingEvent', 'FightButtonEvent', 'CloseWindowEvent', 'BrowserEvent', 'HangarVehicleEvent', 'HangarCustomizationEvent', 'GameEvent', 'ViewEventType', 'OpenLinkEvent', 'ChannelManagementEvent', 'PreBattleChannelEvent', 'AmmunitionSetupViewEvent', 'HasCtxEvent', 'DogTagsEvent', 'DeathCamEvent', 'FullscreenModeSelectorEvent', 'ModeSelectorPopoverEvent', 'ModeSubSelectorEvent')
_logger = logging.getLogger(__name__)

class HasCtxEvent(SharedEvent):

    def __init__(self, eventType=None, ctx=None):
        super(HasCtxEvent, self).__init__(eventType)
        self.ctx = ctx if ctx is not None else {}
        return


class AppLifeCycleEvent(SharedEvent):
    CREATING = 'app/creating'
    INITIALIZING = 'app/initializing'
    INITIALIZED = 'app/initialized'
    DESTROYED = 'app/destroyed'

    def __init__(self, ns, eventType):
        super(AppLifeCycleEvent, self).__init__(eventType)
        self.__ns = ns

    @property
    def ns(self):
        return self.__ns


class GameEvent(HasCtxEvent):
    SCREEN_SHOT_MADE = 'game/screenShotMade'
    SHOW_EXTENDED_INFO = 'game/showExtendedInfo'
    CHOICE_CONSUMABLE = 'game/choiceConsumable'
    MINIMAP_CMD = 'game/minimapCmd'
    MINIMAP_VISIBLE_CMD = 'game/minimapVisibleCmd'
    RADIAL_MENU_CMD = 'game/radialMenuCmd'
    TOGGLE_GUI = 'game/toggleGUI'
    GUI_VISIBILITY = 'game/guiVisibility'
    MARKERS_2D_VISIBILITY = 'game/markers2DVisibility'
    CROSSHAIR_VISIBILITY = 'game/crosshairVisibility'
    GUN_MARKER_VISIBILITY = 'game/gunMarkerVisibility'
    CROSSHAIR_VIEW = 'game/crosshairView'
    FULL_STATS = 'game/fullStats'
    EVENT_STATS = 'game/eventStats'
    FULL_STATS_QUEST_PROGRESS = 'game/fullStats/questProgress'
    FULL_STATS_PERSONAL_RESERVES = 'game/fullStats/personalReserves'
    HIDE_VEHICLE_UPGRADE = 'game/battleRoyale/hideVehicleUpgrade'
    SHOW_CURSOR = 'game/showCursor'
    HIDE_CURSOR = 'game/hideCursor'
    NEXT_PLAYERS_PANEL_MODE = 'game/nextPlayersPanelMode'
    PLAYING_TIME_ON_ARENA = 'game/playingTimeOnArena'
    CHANGE_APP_RESOLUTION = 'game/changeAppResolution'
    SHOW_EXTERNAL_COMPONENTS = 'game/showExternalComponents'
    HIDE_EXTERNAL_COMPONENTS = 'game/hideExternalComponents'
    ON_BACKGROUND_ALPHA_CHANGE = 'game/onBackgroundAlphaChange'
    HIDE_LOBBY_SUB_CONTAINER_ITEMS = 'game/hideLobbySubContainerItems'
    REVEAL_LOBBY_SUB_CONTAINER_ITEMS = 'game/revealLobbySubContainerItems'
    BATTLE_LOADING = 'game/battleLoading'
    SHOW_BTN_HINT = 'game/showBtnHint'
    HIDE_BTN_HINT = 'game/hideBtnHint'
    DESTROY_TIMERS_PANEL = 'game/destroyTimersPanel'
    SHOW_LOOT_BOX_WINDOWS = 'game/showLootBoxWindows'
    HIDE_LOOT_BOX_WINDOWS = 'game/hideLootBoxWindows'
    CLOSE_LOOT_BOX_WINDOWS = 'game/closeLootBoxWindows'
    CHARGE_RELEASED = 'game/chargeReleased'
    PRE_CHARGE = 'game/preCharge'
    CONTROL_MODE_CHANGE = 'game/controlModeChange'
    SNIPER_CAMERA_TRANSITION = 'game/sniperCameraTransition'
    FADE_OUT_AND_IN = 'game/fadeOutIn'
    CALLOUT_DISPLAY_EVENT = 'game/calloutDisplayEvent'
    RESPOND_TO_CALLOUT = 'game/respondToCallout'
    ARENA_BORDER_TYPE_CHANGED = 'game/arenaBorderTypeChanged'
    TOGGLE_VOIP_CHANNEL_ENABLED = 'game/voip/toggleEnabled'
    ROLE_HINT_TOGGLE = 'roleHintToggle'
    COMMANDER_HINT = 'game/commanderHint'
    CHANGE_AMMUNITION_SETUP = 'game/changeAmmunitionSetup'
    TOGGLE_DEBUG_PIERCING_PANEL = 'game/toggleDebugPiercingPanel'
    ON_TARGET_VEHICLE_CHANGED = 'game/onTargetVehicleChanged'
    POINT_OF_INTEREST_ADDED = 'game/changeAmmunitionSetup'
    POINT_OF_INTEREST_REMOVED = 'game/changeAmmunitionSetup'
    PREBATTLE_INPUT_STATE_LOCKED = 'game/inputStateLocked'


class GUICommonEvent(SharedEvent):
    LOBBY_VIEW_LOADED = 'lobbyViewLoaded'


class GUIEditorEvent(HasCtxEvent):
    HIDE_GUIEditor = 'hideGUIEditor'


class ArgsEvent(HasCtxEvent):
    UPDATE_ARGS = 'updateArguments'

    def __init__(self, eventType=None, alias='', ctx=None):
        super(ArgsEvent, self).__init__(eventType, ctx)
        self.alias = alias


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


class ViewEventType(CONST_CONTAINER):
    LOAD_VIEW = 'viewEventLoadView'
    LOAD_GUI_IMPL_VIEW = 'ubViewEventLoadView'
    LOAD_VIEWS_CHAIN = 'viewEventLoadViewChain'
    PRELOAD_VIEW = 'viewEventPreLoadView'
    DESTROY_VIEW = 'viewEventDestroyView'
    DESTROY_GUI_IMPL_VIEW = 'ubViewEventDestroyView'


class _ViewEvent(HasCtxEvent):

    def __init__(self, eventType, alias, name=None, ctx=None):
        super(_ViewEvent, self).__init__(eventType, ctx)
        self.alias = alias
        self.name = name


class LoadViewEvent(_ViewEvent):

    def __init__(self, loadParams, *args, **kwargs):
        if isinstance(loadParams, str):
            _logger.error('Wrong loadParams type for "%s"! Replace it by SFViewLoadParams.', loadParams)
        super(LoadViewEvent, self).__init__(ViewEventType.LOAD_VIEW, loadParams.viewKey.alias, loadParams.viewKey.name, ctx=kwargs.get('ctx', None))
        self.loadParams = loadParams
        self.args = args
        self.kwargs = kwargs
        return

    def __repr__(self):
        return 'LoadViewEvent[loadParams={}, ctx={}, args={}, kwargs={}]'.format(repr(self.loadParams), self.ctx, self.args, self.kwargs)


class LoadViewsChainEvent(_ViewEvent):

    def __init__(self, viewLoadEvents):
        super(LoadViewsChainEvent, self).__init__(ViewEventType.LOAD_VIEWS_CHAIN, None, None)
        self.viewLoadEvents = viewLoadEvents
        return


class PreLoadViewEvent(_ViewEvent):

    def __init__(self, alias, name=None, ctx=None):
        super(PreLoadViewEvent, self).__init__(ViewEventType.PRELOAD_VIEW, alias, name, ctx)


class DestroyViewEvent(_ViewEvent):

    def __init__(self, alias, name=None):
        super(DestroyViewEvent, self).__init__(ViewEventType.DESTROY_VIEW, alias, name)


class LoadGuiImplViewEvent(_ViewEvent):

    def __init__(self, loadParams, *args, **kwargs):
        super(LoadGuiImplViewEvent, self).__init__(ViewEventType.LOAD_GUI_IMPL_VIEW, loadParams.viewKey.alias)
        self.loadParams = loadParams
        self.viewClass = loadParams.viewClass
        self.scope = loadParams.scope
        self.args = args
        self.kwargs = kwargs


class DestroyGuiImplViewEvent(_ViewEvent):

    def __init__(self, layoutID):
        super(DestroyGuiImplViewEvent, self).__init__(ViewEventType.DESTROY_GUI_IMPL_VIEW, layoutID)


class BrowserEvent(HasCtxEvent):
    BROWSER_CREATED = 'onBrowserCreated'


class ShowDialogEvent(SharedEvent):
    SHOW_SIMPLE_DLG = 'showSimpleDialog'
    SHOW_BUTTON_DLG = 'showButtonDialog'
    SHOW_ICON_DIALOG = 'showIconDialog'
    SHOW_ICON_PRICE_DIALOG = 'showIconPriceDialog'
    SHOW_PM_CONFIRMATION_DIALOG = 'showPMConfirmationDialog'
    SHOW_CONFIRM_MODULE = 'showConfirmModule'
    SHOW_CONFIRM_BOOSTER = 'showConfirmBooster'
    SHOW_SYSTEM_MESSAGE_DIALOG = 'showSystemMessageDialog'
    SHOW_CYBER_SPORT_DIALOG = 'showCyberSportDialog'
    SHOW_CONFIRM_ORDER_DIALOG = 'showConfirmOrderDialog'
    SHOW_EXCHANGE_DIALOG = 'showExchangeDialog'
    SHOW_EXCHANGE_DIALOG_MODAL = 'showExchangeDialogModal'
    SHOW_CHECK_BOX_DIALOG = 'showCheckBoxDialog'
    SHOW_USE_AWARD_SHEET_DIALOG = 'useAwardSheetDialog'
    SHOW_CONFIRM_C11N_BUY_DIALOG = 'showConfirmC11nBuyDialog'
    SHOW_CONFIRM_C11N_SELL_DIALOG = 'showConfirmC11nSellDialog'

    def __init__(self, meta, handler, parent=None):
        super(ShowDialogEvent, self).__init__(ViewEventType.LOAD_VIEW)
        self.alias = meta.getEventType()
        self.meta = meta
        self.handler = handler
        self.parent = parent


class LoginEvent(SharedEvent):
    CANCEL_LGN_QUEUE = 'cancelLoginQueue'
    LOGIN_VIEW_READY = 'loginViewReady'
    DISCONNECTION_STARTED = 'disconnectionStarted'
    CONNECTION_FAILED = 'connectionFailed'

    def __init__(self, eventType, alias='', isSuccess=False, errorMsg=''):
        super(LoginEvent, self).__init__(eventType=eventType)
        self.alias = alias
        self.isSuccess = isSuccess
        self.errorMsg = errorMsg


class LoginEventEx(LoginEvent):
    ON_LOGIN_QUEUE_CLOSED = 'onLoginQueueClosed'
    SWITCH_LOGIN_QUEUE_TO_AUTO = 'switchLoginQueueToAuto'

    def __init__(self, eventType, alias, waitingOpen, msg, waitingClose, showAutoLoginBtn):
        super(LoginEventEx, self).__init__(eventType=eventType, alias=alias)
        self.waitingOpen = waitingOpen
        self.msg = msg
        self.waitingClose = waitingClose
        self.showAutoLoginBtn = showAutoLoginBtn


class RenameWindowEvent(HasCtxEvent):
    RENAME_WINDOW = 'renameWindow'

    def __init__(self, eventType, ctx):
        super(RenameWindowEvent, self).__init__(eventType=eventType, ctx=ctx)


class HideWindowEvent(HasCtxEvent):
    HIDE_BATTLE_RESULT_WINDOW = 'hideBattleResultsWindow'
    HIDE_BATTLE_SESSION_WINDOW = 'hideBattleSessionWindow'
    HIDE_UNIT_WINDOW = 'hideUnitWindow'
    HIDE_LEGAL_INFO_WINDOW = 'hideLegalInfoWindow'
    HIDE_VEHICLE_SELECTOR_WINDOW = 'hideVehicleSelectorWindow'
    HIDE_ROSTER_SLOT_SETTINGS_WINDOW = 'hideRosterSlotSettingsWindow'
    HIDE_MISSION_DETAILS_VIEW = 'hideMissionDetailsView'
    HIDE_PERSONAL_MISSION_DETAILS_VIEW = 'hidePersonalMissionDetailsView'
    HIDE_BROWSER_WINDOW = 'hideBrowserWindow'
    HIDE_VEHICLE_PREVIEW = 'hideVehiclePreview'
    HIDE_OVERLAY_BROWSER_VIEW = 'hideOverlayBrowserView'
    HIDE_MISSIONS_PAGE_VIEW = 'hideMissionsPageView'
    HIDE_SPECIAL_BATTLE_WINDOW = 'hideSpecialBattleWindow'


class HidePopoverEvent(HasCtxEvent):
    HIDE_POPOVER = 'hidePopover'
    POPOVER_DESTROYED = 'popoverDestroyed'


class LobbySimpleEvent(HasCtxEvent):
    UPDATE_TANK_PARAMS = 'updateTankParams'
    SHOW_HELPLAYOUT = 'showHelplayout'
    CLOSE_HELPLAYOUT = 'closeHelplayout'
    EVENTS_UPDATED = 'questUpdated'
    HIDE_HANGAR = 'hideHangar'
    NOTIFY_CURSOR_OVER_3DSCENE = 'notifyCursorOver3dScene'
    NOTIFY_CURSOR_DRAGGING = 'notifyCursorDragging'
    NOTIFY_SPACE_MOVED = 'notifySpaceMoved'
    PREMIUM_BOUGHT = 'premiumBought'
    PREMIUM_XP_BONUS_CHANGED = 'premiumXPBonusChanged'
    WAITING_SHOWN = 'waitingShown'
    WAITING_HIDDEN = 'waitingHidden'
    BATTLE_RESULTS_POSTED = 'battleResultsPosted'
    BATTLE_RESULTS_SHOW_QUEST = 'battleResultsWindowShowQuest'
    CHANGE_SOUND_ENVIRONMENT = 'changeSoundEnvironment'
    VEHICLE_PREVIEW_HIDDEN = 'vehiclePreviewHidden'


class MissionsEvent(HasCtxEvent):
    ON_FILTER_CHANGED = 'onFilterChanged'
    ON_FILTER_CLOSED = 'onFilterClosed'
    ON_GROUPS_DATA_CHANGED = 'onGroupsDataChanged'
    ON_ACTIVATE = 'onActivate'
    ON_DEACTIVATE = 'onDeactivate'
    ON_TAB_CHANGED = 'onTabChanged'
    PAGE_INVALIDATE = 'pageInvalidate'


class MissionsViewEvent(SharedEvent):
    EVENTS_FULL_UPDATE = 'missionsView/onEventsUpdate'


class PersonalMissionsEvent(HasCtxEvent):
    ON_DETAILS_VIEW_OPEN = 'onDetailsViewOpen'
    ON_DETAILS_VIEW_CLOSE = 'onDetailsViewClose'
    ON_AWARD_SCEEN_OPEN = 'onAwardScreenOpen'
    ON_AWARD_SCEEN_CLOSE = 'onAwardScreenClose'
    UPDATE_AWARD_SCREEN = 'updateAwardScreen'


class TrainingSettingsEvent(HasCtxEvent):
    UPDATE_TRAINING_SETTINGS = 'updateTrainingSettings'
    UPDATE_EPIC_TRAINING_SETTINGS = 'updateEpicTrainingSettings'


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


class LobbyHeaderMenuEvent(LobbySimpleEvent):
    UPDATE_PREBATTLE_CONTROLS = 'updateControlsHeaderMenu'
    TOGGLE_VISIBILITY = 'toggleVisibilityHeaderMenu'
    MENU_CLICK = 'headerMenuClick'


class CloseWindowEvent(SharedEvent):
    EULA_CLOSED = 'EULAClosed'
    GOLD_FISH_CLOSED = 'GoldFishClosed'
    ELITE_WINDOW_CLOSED = 'EliteWindowClosed'
    BUY_VEHICLE_VIEW_CLOSED = 'BuyVehicleViewClosed'

    def __init__(self, eventType=None, isAgree=False):
        super(CloseWindowEvent, self).__init__(eventType)
        self.isAgree = isAgree


coolDownEventParams = namedtuple('coolDownEventParams', 'eventType, requestScope, actionId')

class CoolDownEvent(SharedEvent):
    GLOBAL = 'globalCoolDown'
    PREBATTLE = 'prebattleCoolDown'
    FORTIFICATION = 'fortificationCoolDown'
    BW_CHAT2 = 'bwChat2CoolDown'
    XMPP = 'xmppCoolDown'
    BATTLE = 'battleCoolDown'
    WGCG = 'wgcg'
    STRONGHOLD = 'stronghold'
    BATTLE_ACTION = 'battleAction'
    WGNP = 'wgnp'

    def __init__(self, eventType=None, requestID=0, coolDown=5.0):
        super(CoolDownEvent, self).__init__(eventType)
        self.coolDown = coolDown
        self.requestID = requestID


class TutorialEvent(SharedEvent):
    START_TRAINING = 'startTraining'
    STOP_TRAINING = 'stopTraining'
    ON_COMPONENT_FOUND = 'onComponentFound'
    ON_COMPONENT_LOST = 'onComponentLost'
    ON_TRIGGER_ACTIVATED = 'onTriggerActivated'
    ON_ANIMATION_COMPLETE = 'onAnimationComplete'
    UPDATE_TUTORIAL_HINTS = 'updateTutorialHints'
    IMPORTANT_HINT_SHOWING = 'importantHintShowing'

    def __init__(self, eventType, settingsID='', targetID='', reloadIfRun=False, initialChapter=None, restoreIfRun=False, isStopForced=False, isAfterBattle=False, state=False, arguments=''):
        super(TutorialEvent, self).__init__(eventType)
        self.settingsID = settingsID
        self.targetID = targetID
        self.reloadIfRun = reloadIfRun
        self.initialChapter = initialChapter
        self.restoreIfRun = restoreIfRun
        self.isStopForced = isStopForced
        self.isAfterBattle = isAfterBattle
        self.componentState = state
        self.arguments = arguments

    def getState(self):
        return {'reloadIfRun': self.reloadIfRun,
         'initialChapter': self.initialChapter,
         'restoreIfRun': self.restoreIfRun,
         'isStopForced': self.isStopForced,
         'isAfterBattle': self.isAfterBattle}


class MessengerEvent(HasCtxEvent):
    PRB_CHANNEL_CTRL_INITED = 'prbChannelCtrlInited'
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
    REGISTER_BATTLE = 'registerBattleComponent'
    UNREGISTER_BATTLE = 'unregisterBattleComponent'
    MESSAGE_FADING_ENABLED = 'messageFadingEnabled'

    def __init__(self, clientID, eventType=None, ctx=None):
        super(ChannelManagementEvent, self).__init__(eventType, ctx)
        self.clientID = clientID


class PreBattleChannelEvent(ChannelManagementEvent):
    REQUEST_TO_ADD_PRE_BATTLE_CHANNEL = 'loadSquad'
    REQUEST_TO_REMOVE_PRE_BATTLE_CHANNEL = 'removeSquad'


class ChannelCarouselEvent(SharedEvent):
    CAROUSEL_INITED = 'carouselInited'
    CAROUSEL_DESTROYED = 'carouselDestroyed'
    OPEN_BUTTON_CLICK = 'openButtonClick'
    MINIMIZE_ALL_CHANNELS = 'minimizeAllChannels'
    CLOSE_ALL_EXCEPT_CURRENT = 'closeAllExceptCurrent'
    CLOSE_BUTTON_CLICK = 'closeButtonClick'
    ON_WINDOW_CHANGE_FOCUS = 'onWindowChangeFocus'
    ON_WINDOW_CHANGE_OPEN_STATE = 'onWindowChangeOpenState'

    def __init__(self, target, eventType=None, clientID=None, wndType=None, flag=False):
        super(ChannelCarouselEvent, self).__init__(eventType)
        self.target = target
        self.clientID = clientID
        self.wndType = wndType
        self.flag = flag


class AutoInviteEvent(SharedEvent):
    INVITE_RECEIVED = 'inviteReceived'

    def __init__(self, invite, eventType=None):
        super(AutoInviteEvent, self).__init__(eventType)
        self.invite = invite


class CSVehicleSelectEvent(HasCtxEvent):
    VEHICLE_SELECTED = 'CSVehicleSelectEvent/vehicleSelected'


class CSReserveSelectEvent(HasCtxEvent):
    RESERVE_SELECTED = 'reserveSelected'


class CSRosterSlotSettingsWindow(HasCtxEvent):
    APPLY_SLOT_SETTINGS = 'applySlotSettings'


class StrongholdEvent(HasCtxEvent):
    STRONGHOLD_ACTIVATED = 'strongholdActivated'
    STRONGHOLD_DEACTIVATED = 'strongholdDeactivated'
    STRONGHOLD_DATA_UNAVAILABLE = 'strongholdDataUnavailable'
    STRONGHOLD_ON_TIMER = 'strongholdOnTimer'
    STRONGHOLD_VEHICLES_SELECTED = 'strongholdVehicleSelected'
    STRONGHOLD_LOADED = 'strongholdLoaded'


class ShopEvent(HasCtxEvent):
    SHOP_ACTIVATED = 'shopActivated'
    SHOP_DEACTIVATED = 'shopDeactivated'
    SHOP_DATA_UNAVAILABLE = 'shopDataUnavailable'
    SHOP_ON_TIMER = 'shopOnTimer'
    CONFIRM_TRADE_IN = 'confirmTradeIn'
    SELECT_RENT_TERM = 'selectRentTerm'


class OpenLinkEvent(SharedEvent):
    SPECIFIED = 'openSpecifiedURL'
    PARSED = 'openParsedURL'
    REGISTRATION = 'openRegistrationURL'
    RECOVERY_PASSWORD = 'openRecoveryPasswordURL'
    PAYMENT = 'openPaymentURL'
    SECURITY_SETTINGS = 'openSecuritySettingsURL'
    CLAN_RULES = 'openClanRulesURL'
    SUPPORT = 'openSupportURL'
    MIGRATION = 'openMigrationURL'
    FORT_DESC = 'fortDescription'
    CLAN_SEARCH = 'clanSearch'
    CLAN_CREATE = 'clanCreate'
    MEDKIT_HELP = 'medkitHelp'
    REPAIRKITHELP_HELP = 'repairkitHelp'
    FIRE_EXTINGUISHERHELP_HELP = 'fireExtinguisherHelp'
    INVIETES_MANAGEMENT = 'invitesManagementURL'
    GLOBAL_MAP_SUMMARY = 'globalMapSummary'
    GLOBAL_MAP_PROMO_SUMMARY = 'globalMapPromoSummary'
    GLOBAL_MAP_CAP = 'globalMapCap'
    GLOBAL_MAP_PROMO = 'globalMapPromo'
    PREM_SHOP = 'premShopURL'
    TOKEN_SHOP = 'tokenShopUrl'
    FRONTLINE_CHANGES = 'frontlineChangesURL'
    WOT_PLUS_STEAM_SHOP = 'wotPlusSteamURL'
    WOT_PLUS_SHOP = 'wotPlusShopURL'
    STEAM_SUBSCRIPTION_MANAGEMENT = 'steamSubscriptionManagementURL'
    LOOT_BOXES_LIST = 'lootBoxesList'

    def __init__(self, eventType, url='', title='', params=None):
        super(OpenLinkEvent, self).__init__(eventType)
        self.url = url
        self.title = title
        self.params = params


class CalendarEvent(SharedEvent):
    MONTH_CHANGED = 'monthChanged'
    DATE_SELECTED = 'dateSelected'

    def __init__(self, eventType=None, timestamp=None):
        super(CalendarEvent, self).__init__(eventType)
        self.__timestamp = timestamp

    def getTimestamp(self):
        return self.__timestamp


class BubbleTooltipEvent(LobbySimpleEvent):
    SHOW = 'showBubble'

    def __init__(self, eventType, message=None, duration=5000):
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

    def __init__(self, notID, target, alias=None):
        super(WGNCShowItemEvent, self).__init__(ViewEventType.LOAD_VIEW)
        self.alias = alias
        self.__notID = notID
        self.__target = target

    def getNotID(self):
        return self.__notID

    def getTarget(self):
        return self.__target


class MarkersManagerEvent(SharedEvent):
    MARKERS_CREATED = 'markersCreated'

    def __init__(self, eventType=None, markersManager=None):
        super(MarkersManagerEvent, self).__init__(eventType)
        self.__markersManager = markersManager

    def getMarkersManager(self):
        return self.__markersManager


class VehicleBuyEvent(HasCtxEvent):
    VEHICLE_SELECTED = 'vehicleBuyEvent/vehicleSelected'


class HangarVehicleEvent(HasCtxEvent):
    ON_HERO_TANK_LOADED = 'hangarVehicle/onHeroTankLoaded'
    ON_HERO_TANK_DESTROY = 'hangarVehicle/onHeroTankDestroy'
    ON_PLATOON_TANK_LOADED = 'hangarVehicle/onPlatoonTankLoaded'
    ON_PLATOON_TANK_DESTROY = 'hangarVehicle/onPlatoonTankDestroy'
    PLATOON_TANK_MARKER = 'hangarVehicle/platoonTankMarker'
    SELECT_VEHICLE_IN_HANGAR = 'hangarVehicle/selectVehicleInHangar'


class ManualEvent(HasCtxEvent):
    CHAPTER_OPENED = 'manual/chapterOpened'
    CHAPTER_CLOSED = 'manual/chapterClosed'


class StorageEvent(HasCtxEvent):
    SELECT_MODULE_FOR_SELL = 'storage/forSellView/selectModule'
    VEHICLE_SELECTED = 'storage/inventory/vehicleSelected'


class HangarCustomizationEvent(HasCtxEvent):
    CHANGE_VEHICLE_MODEL_TRANSFORM = 'hangarCustomization/changeVehicleModelTransform'
    RESET_VEHICLE_MODEL_TRANSFORM = 'hangarCustomization/resetVehicleModelTransform'


class SeniorityAwardsEvent(HasCtxEvent):
    ON_REWARD_VIEW_CLOSED = 'seniorityAwards/onRewardViewClosed'
    ON_ENTRY_VIEW_LOADED = 'seniorityAwards/onEntryViewLoaded'


class ReferralProgramEvent(HasCtxEvent):
    REFERRAL_PROGRAM_ACTIVATED = 'referralProgramActivated'
    REFERRAL_PROGRAM_DEACTIVATED = 'referralProgrammDeactivated'
    SHOW_REFERRAL_PROGRAM_WINDOW = 'showReferralProgramWindow'
    DISABLE_REFERRAL_PROGRAM = 'disableReferralProgram'


class AdventCalendarEvent(HasCtxEvent):
    ADVENT_CALENDAR = 'adventCalendar'
    HERO_ADVENT_ACTION_STATE_CHANGED = 'heroAdventActionStateChanged'


class ProgressiveRewardEvent(HasCtxEvent):
    WIDGET_WAS_SHOWN = 'progressiveWidgetWasShown'


class Comp7Event(SharedEvent):
    OPEN_META = 'openMeta'


class AirDropEvent(HasCtxEvent):
    AIR_DROP_SPAWNED = 'onAirDropSpawned'
    AIR_DROP_LANDED = 'onAirDropLanded'
    AIR_DROP_LOOP_ENTERED = 'onAirDropLootEntered'
    AIR_DROP_LOOP_LEFT = 'onAirDropLootLeft'
    AIR_DROP_NXT_SPAWNED = 'onAirDropNxtSpawned'


class ProfilePageEvent(HasCtxEvent):
    SELECT_PROFILE_ALIAS = 'onProfileSelectAlias'


class ProfileStatisticEvent(HasCtxEvent):
    SELECT_BATTLE_TYPE = 'onProfileStatisticEventBattleTypeSelect'
    DISPOSE = 'onProfileStatisticEventDispose'


class ProfileTechniqueEvent(HasCtxEvent):
    SELECT_BATTLE_TYPE = 'onProfileTechniqueEventBattleTypeSelect'
    DISPOSE = 'onProfileTechniqueEventDispose'


class BattlePassEvent(HasCtxEvent):
    BUYING_THINGS = 'buyingThings'
    AWARD_VIEW_CLOSE = 'onAwardViewClose'
    ON_PURCHASE_LEVELS = 'onPurchaseLevels'
    ON_PREVIEW_PROGRESSION_STYLE_CLOSE = 'onPreviewProgressionStyleClose'
    ON_FINISH_BATTLE_PASS_PURCHASE = 'onFinishBattlePassPurchase'
    VIDEO_SHOWN = 'videoShown'


class LootBoxSystemEvent(HasCtxEvent):
    ON_STATISTICS_RESET = 'onStatisticsReset'
    OPENING_ERROR = 'openingError'


class ItemRemovalByDemountKitEvent(HasCtxEvent):
    DECLARED = 'item_removal_by_dk_declared'
    CANCELED = 'item_removal_by_dk_canceled'

    def __init__(self, eventType=None, slotIndex=None):
        self.slotIndex = slotIndex
        super(ItemRemovalByDemountKitEvent, self).__init__(eventType)


class TrainingEvent(HasCtxEvent):
    RETURN_TO_TRAINING_ROOM = 'trainingEvent/returnToTrainingRoom'
    SHOW_TRAINING_LIST = 'trainingEvent/showTrainingList'
    SHOW_EPIC_TRAINING_LIST = 'trainingEvent/showEpicTrainingList'


class RallyWindowEvent(HasCtxEvent):
    ON_CLOSE = 'rallyWindowEvent/onClose'


class CustomizationEvent(HasCtxEvent):
    SHOW = 'customizationEvent/show'


class PrbInvitesEvent(HasCtxEvent):
    ACCEPT = 'prbInvitesEvent/accept'

    def __init__(self, eventType=None, inviteID=None, postActions=None):
        super(PrbInvitesEvent, self).__init__(eventType)
        self.inviteID = inviteID
        self.postActions = postActions


class PrbActionEvent(HasCtxEvent):
    SELECT = 'prbActionEvent/select'
    LEAVE = 'prbActionEvent/leave'

    def __init__(self, action, eventType=None):
        super(PrbActionEvent, self).__init__(eventType)
        self.action = action


class AmmunitionSetupViewEvent(HasCtxEvent):
    GF_RESIZED = 'ammunitionSetupViewEvent/gfResized'
    UPDATE_TTC = 'ammunitionSetupViewEvent/updateTTC'
    HINT_ZONE_ADD = 'ammunitionSetupViewEvent/hintZoneAdd'
    HINT_ZONE_HIDE = 'ammunitionSetupViewEvent/hintZoneHide'
    HINT_ZONE_CLICK = 'ammunitionSetupViewEvent/hintZoneClick'
    CLOSE_VIEW = 'ammunitionSetupViewEvent/closeView'


class AmmunitionPanelViewEvent(HasCtxEvent):
    SECTION_SELECTED = 'ammunitionPanelViewEvent/sectionSelected'
    CLOSE_VIEW = 'ammunitionPanelViewEvent/closeView'


class AmmunitionInjectEvent(SharedEvent):
    INVALIDATE_INJECT_VIEW = 'AmmunitionInjectEvent/invalidateInjectView'


class RadialMenuEvent(SharedEvent):
    RADIAL_MENU_ACTION = 'radialMenuAction'


class HangarSpacesSwitcherEvent(HasCtxEvent):
    SWITCH_TO_HANGAR_SPACE = 'hangarSpacesSwitcherEvent/SwitchToHangarSpace'


class DogTagsEvent(SharedEvent):
    COUNTERS_UPDATED = 'onCountersUpdated'


class PlatoonDropdownEvent(HasCtxEvent):
    NAME = 'DropdownEvent'


class DeathCamEvent(HasCtxEvent):
    DEATH_CAM_STATE = 'deathCamEvent/deathCamState'
    DEATH_CAM_HIDDEN = 'deathCamEvent/deathCamHidden'
    DEATH_CAM_SPECTATOR_MODE = 'deathCamEvent/deathCamSpectatorMode'

    class State(Enum):
        NONE = 0
        INACTIVE = 1
        PREPARING = 2
        STARTING = 3
        ACTIVE = 4
        PAUSE = 5
        RESUME = 6
        ENDING = 7
        FINISHED = 8

    BEFORE_SIMULATION = (State.NONE, State.INACTIVE)
    SIMULATION_EXCL_FADES = (State.ACTIVE, State.PAUSE, State.RESUME)
    SIMULATION_INCL_FADES = (State.PREPARING,
     State.STARTING,
     State.ACTIVE,
     State.PAUSE,
     State.RESUME,
     State.ENDING)

    class EventType(Enum):
        NONE = 'none'
        ENABLED = 'enabled'
        TRANSITIONING = 'transitioning'
        INIT_SPOTTED = 'initSpotted'
        ROTATING_KILLER = 'rotatingKiller'
        MOVING_TO_PLAYER = 'movingToPlayer'
        INIT_UNSPOTTED = 'initUnspotted'
        UNSPOTTED_PHASE_ONE = 'unspottedPhaseOne'
        UNSPOTTED_PHASE_TWO = 'unspottedPhaseTwo'
        LAST_ROTATION = 'rotatingPlayer'


class FullscreenModeSelectorEvent(HasCtxEvent):
    NAME = 'FullscreenModeSelectorEvent'


class ModeSelectorPopoverEvent(HasCtxEvent):
    NAME = 'ModeSelectorPopoverEvent'


class ModeSubSelectorEvent(HasCtxEvent):
    CHANGE_VISIBILITY = 'subSelectorViewEvent/changeVisibility'
    CLICK_PROCESSING = 'subSelectorViewEvent/clickProcessing'


class GunMarkerEvent(HasCtxEvent):
    UPDATE_PIERCING_DATA = 'onPiercingDataUpdated'


class ResourceWellLoadingViewEvent(HasCtxEvent):
    LOAD = 'load'
    DESTROY = 'destroy'


class PointOfInterestEvent(HasCtxEvent):
    ADDED = 'poi/added'
    REMOVED = 'poi/removed'


class RoleSkillEvent(HasCtxEvent):
    STATE_CHANGED = 'roleSkill/stateChanged'
    COUNTER_CHANGED = 'roleSkill/counterChanged'


class CollectionsEvent(HasCtxEvent):
    NEW_ITEM_SHOWN = 'newItemShown'
    TAB_COUNTER_UPDATED = 'tabCounterUpdated'
    COLLECTION_VIEW_CLOSED = 'collectionViewClosed'
    COLLECTION_INTRO_CLOSED = 'collectionIntroClosed'


class Achievements20Event(HasCtxEvent):
    LAYOUT_CHANGED = 'layoutChanged'
    CLOSE_SUMMARY_VIEW = 'closeSummaryView'
    CLOSE_EDIT_VIEW = 'closeEditView'
    CHANGE_GF_VIEW = 'changeGamefaceView'
    ACHIEVEMENT_EARNED = 'achievementEarned'
    ACHIEVEMENT_EARNED_SHOWNED = 'achievementEarnedShowned'


class PrebattleEvent(HasCtxEvent):
    SWITCHED = 'PrebattleEvent/SWITCHED'
    NOT_SWITCHED = 'PrebattleEvent/NOT_SWITCHED'


class HangarCrewWidgetViewEvent(HasCtxEvent):
    GF_RESIZED = 'hangarCrewWidgetViewEvent/gfResized'


class BattleRoyalePlatoonEvent(SharedEvent):
    LEAVED_PLATOON = 'battleRoyalePlatoonEvent/leavedPlatoon'


class ScalableBattleMinimapEvent(HasCtxEvent):
    BORDERS_UPDATED = 'ScalableBattleMinimapEvent/BORDERS_UPDATED'
    ZOOM_UPDATED = 'ScalableBattleMinimapEvent/ZOOM_UPDATED'


class BoostersControllerEvent(SharedEvent):
    UPDATE_GAMEMODE_STATUS = 'boostersControllerEvent/updateGameModeStatus'


class DailyQuestWidgetEvent(SharedEvent):
    UPDATE_QUESTS_VISIBILITY = 'dailyQuestWidgetEvent/updateQuestsVisibility'


class HangarEvent(SharedEvent):
    UPDATE_ALERT_MESSAGE = 'hangar/updateAlertMessage'
    UPDATE_PREBATTLE_ENTITY = 'hangar/prebattleEntityUpdated'


class GameSessionEvent(SharedEvent):
    UPDATE_KICK_NOTIFICATION = 'gameSession/updateKickNotification'


class ExchangeRatesDiscountsEvent(HasCtxEvent):
    ON_SELECTED_AMOUNT_CHANGED = 'onSelectedAmountChanged'
    ON_PERSONAL_DISCOUNT_VIEWED = 'onPersonalDiscountViewed'


class ViewReadyEvent(SharedEvent):
    VIEW_READY = 'ViewReadyEvent.VIEW_READY'

    def __init__(self, viewID):
        super(ViewReadyEvent, self).__init__(self.VIEW_READY)
        self.viewID = viewID
