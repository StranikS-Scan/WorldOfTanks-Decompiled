# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/header/LobbyHeader.py
from __future__ import absolute_import, division
from builtins import filter, str, object
from past.utils import old_div
import math
import weakref
import typing
from itertools import chain
import BigWorld
import wg_async as future_async
import WWISE
from shared_utils import CONST_CONTAINER, BitmaskHelper, first
import constants
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from PlayerEvents import g_playerEvents
from SoundGroups import g_instance as SoundGroupsInstance
from account_helpers.AccountSettings import AccountSettings, QUESTS, QUEST_DELTAS, QUEST_DELTAS_COMPLETION, ACTIVE_TEST_PARTICIPATION_CONFIRMED
from account_helpers.AccountSettings import KNOWN_SELECTOR_BATTLES
from account_helpers.AccountSettings import NEW_LOBBY_TAB_COUNTER, RECRUIT_NOTIFICATIONS, NEW_SHOP_TABS, LAST_SHOP_ACTION_COUNTER_MODIFICATION, OVERRIDEN_HEADER_COUNTER_ACTION_ALIASES
from adisp import adisp_process, adisp_async
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as BONUS_CAPS
from constants import PREBATTLE_TYPE, PREMIUM_TYPE, EPlatoonButtonState
from debug_utils import LOG_ERROR
from frameworks.wulf import ViewFlags, WindowLayer
from gui import makeHtmlString
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.header.fight_btn_tooltips import getRankedFightBtnTooltipData, getEpicFightBtnTooltipData, getSandboxTooltipData, getSquadFightBtnTooltipData, getMapsTrainingTooltipData, getEpicBattlesOnlyVehicleTooltipData, getEventTooltipData, getPreviewTooltipData, getRandomTooltipData, getMapboxFightBtnTooltipData, getFunRandomFightBtnTooltipData, getComp7FightBtnTooltipData, getComp7BattlesOnlyVehicleTooltipData
from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
from gui.Scaleform.daapi.view.lobby.hof.hof_helpers import getAchievementsTabCounter
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBuyGoldUrl, getBuyRenewableSubscriptionUrl
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBuyPremiumUrl
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import isSubscriptionEnabled
from gui.Scaleform.daapi.view.meta.LobbyHeaderMeta import LobbyHeaderMeta
from gui.Scaleform.framework import g_entitiesFactories
from gui.Scaleform.framework.entities.View import ViewKey, ViewKeyDynamic
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.framework.managers.view_lifecycle_watcher import IViewLifecycleHandler, ViewLifecycleWatcher
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.PLATOON import PLATOON
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.settings import ICONS_SIZES
from gui.clans.clan_helpers import isStrongholdsEnabled, isClansTabReplaceStrongholds
from gui.game_control.ServerStats import STATS_TYPE
from gui.game_control.wallet import WalletController
from gui.gold_fish import isGoldFishActionActive, isTimeToShowGoldFishPromo
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.comp7.meta_view.meta_root_view import MetaRootViewWindow
from gui.impl.lobby.comp7.views.intro_screen import IntroScreenWindow
from gui.impl.lobby.comp7.views.no_vehicles_screen import NoVehiclesScreenWindow
from gui.platform.base.statuses.constants import StatusTypes
from gui.platform.wgnp.demo_account.controller import NICKNAME_CONTEXT
from gui.prb_control import prb_getters
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.settings import REQUEST_TYPE, PRE_QUEUE_RESTRICTION
from gui.server_events import recruit_helper
from gui.server_events import settings as quest_settings
from gui.server_events.events_helpers import isDailyQuest
from gui.shared import event_dispatcher as shared_events
from gui.shared import events
from gui.shared.ClanCache import g_clanCache
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showShop, showStorage, hideWebBrowserOverlay, showModeSelectorWindow, showActiveTestConfirmDialog
from gui.shared.events import PlatoonDropdownEvent, FullscreenModeSelectorEvent
from gui.shared.formatters import text_styles
from gui.shared.formatters.currency import getBWFormatter
from gui.shared.money import Currency
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.view_helpers.emblems import ClanEmblemsHelper
from helpers import dependency
from helpers import i18n, time_utils, isPlayerAccount
from predefined_hosts import g_preDefinedHosts, PING_STATUSES
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.storage_novelty import IStorageNovelty
from skeletons.gui.game_control import IAnonymizerController, IBadgesController, IBoostersController, IBootcampController, IChinaController, IEpicBattleMetaGameController, IGameSessionController, IIGRController, IFunRandomController, IRankedBattlesController, IServerStatsController, IWalletController, IClanNotificationController, IBattleRoyaleController, IUISpamController, IPlatoonController, IMapboxController, IMapsTrainingController, ISteamCompletionController, IEventBattlesController, IComp7Controller
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.battle_matters import IBattleMattersController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.login_manager import ILoginManager
from skeletons.gui.offers import IOffersNovelty
from skeletons.gui.platform.wgnp_controllers import IWGNPSteamAccRequestController, IWGNPDemoAccRequestController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.gui.techtree_events import ITechTreeEventsListener
from skeletons.tutorial import ITutorialLoader
from uilogging.personal_reserves.loggers import PersonalReservesActivationScreenFlowLogger
if typing.TYPE_CHECKING:
    from gui.platform.wgnp.steam_account.statuses import SteamAccEmailStatus
    from gui.platform.wgnp.demo_account.statuses import DemoAccNicknameStatus
    from account_helpers.renewable_subscription import RenewableSubscription
_MAX_HEADER_SERVER_NAME_LEN = 6
_SERVER_NAME_PREFIX = '%s..'
_SHORT_VALUE_PRECISION = 1
_SHORT_VALUE_D = 10 ** _SHORT_VALUE_PRECISION
_SHORT_VALUE_THRESHOLD_1 = 1000000
_SHORT_VALUE_THRESHOLD_2 = 10000000
_SHORT_VALUE_FMT_PATTERN = MENU.HANGAR_HEADER_MILLION
HEADER_BUTTONS_COUNTERS_CHANGED_EVENT = 'lobbyHeaderButtonsCountersChanged'
_DASHBOARD_SUPPRESSED_VIEWS = [VIEW_ALIAS.BADGES_PAGE]

def _getShortCurrencyValue(value, formatter):
    if value >= _SHORT_VALUE_THRESHOLD_2:
        return i18n.makeString(_SHORT_VALUE_FMT_PATTERN, value=old_div(value, _SHORT_VALUE_THRESHOLD_1))
    if value >= _SHORT_VALUE_THRESHOLD_1:
        shortValue = old_div(float(value), _SHORT_VALUE_THRESHOLD_1)
        shortValue = math.floor(shortValue * _SHORT_VALUE_D)
        shortValue = old_div(shortValue, _SHORT_VALUE_D)
        if shortValue < _SHORT_VALUE_THRESHOLD_2:
            formattedValue = '{:.{precision}f}'.format(shortValue, precision=_SHORT_VALUE_PRECISION)
        else:
            formattedValue = str()
        return i18n.makeString(_SHORT_VALUE_FMT_PATTERN, value=formattedValue)
    return formatter(value)


def _predicateLobbyTopSubViews(view):
    return view.layoutID != R.views.lobby.account_dashboard.AccountDashboard() and view.viewFlags & ViewFlags.LOBBY_TOP_SUB_VIEW


def _isActiveShopNewCounters():
    newTabCounters = AccountSettings.getCounters(NEW_SHOP_TABS)
    return not any(newTabCounters.values())


def _updateShopNewCounters():
    newTabCounters = AccountSettings.getCounters(NEW_SHOP_TABS)
    AccountSettings.setCounters(NEW_SHOP_TABS, dict.fromkeys(newTabCounters, True))


class TOOLTIP_TYPES(object):
    COMPLEX = 'complex'
    SPECIAL = 'special'
    WULF = 'wulf'
    NONE = 'none'


class HeaderMenuVisibilityState(BitmaskHelper):
    NOTHING = 0
    BG_OVERLAY = 1
    BUTTON_BAR = 2
    ONLINE_COUNTER = 4
    ALL = BG_OVERLAY | BUTTON_BAR | ONLINE_COUNTER


class _DisabledLobbyHeaderViewLifecycleHandler(IViewLifecycleHandler):

    def __init__(self, lobbyHeader, controlledViews):
        super(_DisabledLobbyHeaderViewLifecycleHandler, self).__init__(controlledViews)
        self.__lobbyHeader = weakref.proxy(lobbyHeader)

    def onViewCreated(self, view):
        self.__lobbyHeader.disableLobbyHeaderControls(True)

    def onViewDestroyed(self, view):
        self.__lobbyHeader.disableLobbyHeaderControls(False)

    def onViewAlreadyCreated(self, view):
        self.__lobbyHeader.disableLobbyHeaderControls(True)


class _RankedBattlesWelcomeViewLifecycleHandler(_DisabledLobbyHeaderViewLifecycleHandler):

    def __init__(self, lobbyHeader):
        super(_RankedBattlesWelcomeViewLifecycleHandler, self).__init__(lobbyHeader, [ViewKey(RANKEDBATTLES_ALIASES.RANKED_BATTLES_INTRO_ALIAS)])


class _MapboxIntroViewLifecycleHandler(_DisabledLobbyHeaderViewLifecycleHandler):

    def __init__(self, lobbyHeader):
        super(_MapboxIntroViewLifecycleHandler, self).__init__(lobbyHeader, [ViewKeyDynamic(R.views.lobby.mapbox.MapBoxIntro())])


class _LobbyHeaderVisibilityHelper(object):
    __slots__ = ('__headerStatesStack',)

    def __init__(self):
        self.__headerStatesStack = []

    def getActiveState(self):
        return self.__headerStatesStack[-1] if self.__headerStatesStack else HeaderMenuVisibilityState.ALL

    def updateStates(self, state):
        previousState = self.getActiveState()
        if previousState == HeaderMenuVisibilityState.NOTHING and state != previousState:
            self.__removePreviousState()
            if state != HeaderMenuVisibilityState.ALL:
                self.__addState(state)
        else:
            self.__addState(state)

    def clear(self):
        self.__headerStatesStack = []

    def __addState(self, state):
        self.__headerStatesStack.append(state)

    def __removePreviousState(self):
        return self.__headerStatesStack.pop() if self.__headerStatesStack else None


class LobbyHeader(LobbyHeaderMeta, ClanEmblemsHelper, IGlobalListener):
    __PREM_WARNING_LIMIT = time_utils.ONE_DAY

    class BUTTONS(CONST_CONTAINER):
        SETTINGS = 'settings'
        ACCOUNT = 'account'
        WOT_PLUS = 'wotPlus'
        PREM = 'prem'
        PREMSHOP = 'premShop'
        SQUAD = 'squad'
        GOLD = Currency.GOLD
        CREDITS = Currency.CREDITS
        CRYSTAL = Currency.CRYSTAL
        FREE_XP = 'freeXP'
        BATTLE_SELECTOR = 'battleSelector'
        PERSONAL_RESERVES_WIDGET = 'personalReservesWidget'

    PRB_NAVIGATION_DISABLE_BUTTONS = (BUTTONS.PREM,
     BUTTONS.CREDITS,
     BUTTONS.GOLD,
     BUTTONS.CRYSTAL,
     BUTTONS.FREE_XP,
     BUTTONS.ACCOUNT,
     BUTTONS.PREMSHOP,
     BUTTONS.WOT_PLUS,
     BUTTONS.PERSONAL_RESERVES_WIDGET)
    RANKED_WELCOME_VIEW_DISABLE_CONTROLS = BUTTONS.ALL()

    class TABS(CONST_CONTAINER):
        HANGAR = VIEW_ALIAS.LOBBY_HANGAR
        STORE = VIEW_ALIAS.LOBBY_STORE
        STORAGE = VIEW_ALIAS.LOBBY_STORAGE
        PROFILE = VIEW_ALIAS.LOBBY_PROFILE
        TECHTREE = VIEW_ALIAS.LOBBY_TECHTREE
        BARRACKS = VIEW_ALIAS.LOBBY_BARRACKS
        BROWSER = VIEW_ALIAS.BROWSER
        RESEARCH = VIEW_ALIAS.LOBBY_RESEARCH
        PERSONAL_MISSIONS = VIEW_ALIAS.LOBBY_PERSONAL_MISSIONS
        MISSIONS = VIEW_ALIAS.LOBBY_MISSIONS
        STRONGHOLD = VIEW_ALIAS.LOBBY_STRONGHOLD
        PERSONAL_MISSIONS_PAGE = VIEW_ALIAS.PERSONAL_MISSIONS_PAGE

    ACCOUNT_SETTINGS_COUNTERS = (TABS.STORE,)
    DESELECT_TAB_ALIASES = (VIEW_ALIAS.WIKI_VIEW, R.views.lobby.maps_training.MapsTrainingPage())
    anonymizerController = dependency.descriptor(IAnonymizerController)
    badgesController = dependency.descriptor(IBadgesController)
    boosters = dependency.descriptor(IBoostersController)
    bootcampController = dependency.descriptor(IBootcampController)
    chinaCtrl = dependency.descriptor(IChinaController)
    connectionMgr = dependency.descriptor(IConnectionManager)
    storageNovelty = dependency.descriptor(IStorageNovelty)
    epicController = dependency.descriptor(IEpicBattleMetaGameController)
    eventsCache = dependency.descriptor(IEventsCache)
    techTreeEventsListener = dependency.descriptor(ITechTreeEventsListener)
    gameSession = dependency.descriptor(IGameSessionController)
    goodiesCache = dependency.descriptor(IGoodiesCache)
    gui = dependency.descriptor(IGuiLoader)
    hangarSpace = dependency.descriptor(IHangarSpace)
    igrCtrl = dependency.descriptor(IIGRController)
    itemsCache = dependency.descriptor(IItemsCache)
    battleMattersController = dependency.descriptor(IBattleMattersController)
    rankedController = dependency.descriptor(IRankedBattlesController)
    clanNotificationCtrl = dependency.descriptor(IClanNotificationController)
    serverStats = dependency.descriptor(IServerStatsController)
    settingsCore = dependency.descriptor(ISettingsCore)
    wallet = dependency.descriptor(IWalletController)
    offersNovelty = dependency.descriptor(IOffersNovelty)
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    __mapsTrainingController = dependency.descriptor(IMapsTrainingController)
    __eventBattlesController = dependency.descriptor(IEventBattlesController)
    __funRandomCtrl = dependency.descriptor(IFunRandomController)
    uiSpamController = dependency.descriptor(IUISpamController)
    platoonCtrl = dependency.descriptor(IPlatoonController)
    lobbyContext = dependency.descriptor(ILobbyContext)
    __tutorialLoader = dependency.descriptor(ITutorialLoader)
    __mapboxCtrl = dependency.descriptor(IMapboxController)
    __loginManager = dependency.descriptor(ILoginManager)
    wgnpSteamAccCtrl = dependency.descriptor(IWGNPSteamAccRequestController)
    steamRegistrationCtrl = dependency.descriptor(ISteamCompletionController)
    wgnpDemoAccCtrl = dependency.descriptor(IWGNPDemoAccRequestController)
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __SELECTOR_TOOLTIP_TYPE = TOOLTIPS.HEADER_BATTLETYPE

    def __init__(self):
        super(LobbyHeader, self).__init__()
        self.__currentScreen = None
        self.__shownCounters = set()
        self._isLobbyHeaderControlsDisabled = False
        self.__viewLifecycleWatcher = ViewLifecycleWatcher()
        self.__isFightBtnDisabled = self.bootcampController.isInBootcamp()
        self.__isSubscriptionEnabled = isSubscriptionEnabled()
        self.__clanIconID = None
        self.__visibility = HeaderMenuVisibilityState.ALL
        self.__menuVisibilityHelper = _LobbyHeaderVisibilityHelper()
        self._renewableSubInfo = BigWorld.player().renewableSubscription
        self._pr20UILogger = PersonalReservesActivationScreenFlowLogger()
        return

    @property
    def menuVisibilityHelper(self):
        return self.__menuVisibilityHelper

    def onClanEmblem16x16Received(self, clanDbID, emblem):
        if not self.isDisposed() and emblem:
            self.__clanIconID = self.getMemoryTexturePath(emblem, temp=False)
            self._updateHangarMenuData()

    def onPlayerStateChanged(self, entity, roster, accountInfo):
        if accountInfo.isCurrentPlayer():
            self._updatePrebattleControls()

    def onUnitPlayerStateChanged(self, pInfo):
        self._updatePrebattleControls()

    def onPrbEntitySwitched(self):
        self._updatePrebattleControls()

    def onDequeued(self, *_):
        self._updatePrebattleControls()

    def onKickedFromQueue(self, *_):
        self._updatePrebattleControls()

    def updateAccountInfo(self):
        self.updateMoneyStats()
        self.updateXPInfo()
        self.__updatePlayerInfoPanel(g_clanCache.clanInfo)
        self.__updateWotPlusAttrs()
        self.__updateAccountAttrs()
        self.__updateBadge()

    def updateMoneyStats(self):
        money = self.itemsCache.items.stats.actualMoney
        self.__setCredits(money.credits)
        self.__setGold(money.gold)
        self.__setCrystal(money.crystal)

    def updateXPInfo(self):
        self.__setFreeXP(self.itemsCache.items.stats.actualFreeXP)

    def showLobbyMenu(self):
        self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_MENU)), scope=EVENT_BUS_SCOPE.LOBBY)

    @adisp_process
    def menuItemClick(self, alias):
        navigationPossible = yield self.lobbyContext.isHeaderNavigationPossible()
        if navigationPossible:
            hideWebBrowserOverlay()
            self.__hideComp7Views()
            self.__triggerViewLoad(alias)
        else:
            self.as_doDeselectHeaderButtonS(alias)

    def onReservesClick(self):
        self._pr20UILogger.logOpenFromWidgetClick()
        shared_events.showPersonalReservesPage()

    def onCrystalClick(self):
        shared_events.showCrystalWindow(self.__visibility)

    def onPayment(self):
        self.__closeWindowsWithTopSubViewLayer()
        showShop(getBuyGoldUrl())

    def showExchangeWindow(self):
        shared_events.showExchangeCurrencyWindow()

    def showExchangeXPWindow(self):
        shared_events.showExchangeXPWindow()

    def showWotPlusView(self):
        showShop(getBuyRenewableSubscriptionUrl())

    def showPremiumView(self):
        self.__closeWindowsWithTopSubViewLayer()
        showShop(getBuyPremiumUrl())

    def onPremShopClick(self):
        self.fireEvent(events.OpenLinkEvent(events.OpenLinkEvent.PREM_SHOP))

    def _onRenewableSubscriptionDataChanged(self, itemDiff):
        self.updateAccountInfo()
        self._populateButtons()

    def _onServerSettingsChange(self, diff):
        if constants.RENEWABLE_SUBSCRIPTION_CONFIG in diff:
            self.updateAccountInfo()
            self._populateButtons()

    @adisp_process
    def showDashboard(self):
        navigationPossible = yield self.lobbyContext.isHeaderNavigationPossible()
        if navigationPossible:
            for alias in _DASHBOARD_SUPPRESSED_VIEWS:
                self.app.containerManager.destroyViews(alias)

            views = self.gui.windowsManager.findViews(_predicateLobbyTopSubViews)
            for view in views:
                view.destroyWindow()

            dashbordView = self.gui.windowsManager.getViewByLayoutID(R.views.lobby.account_dashboard.AccountDashboard())
            if dashbordView is None:
                shared_events.showDashboardView()
            else:
                hideWebBrowserOverlay()
        return

    @adisp_process
    def fightClick(self, mmData, actionName):
        navigationPossible = yield self.lobbyContext.isHeaderNavigationPossible()
        fightButtonPressPossible = yield self.lobbyContext.isFightButtonPressPossible()
        if navigationPossible and fightButtonPressPossible:
            if self.prbDispatcher:
                prbEntity = self.prbDispatcher.getEntity()
                result = yield self.platoonCtrl.processPlatoonActions(mmData, prbEntity, g_currentVehicle)
                if not result:
                    actionAllowed = yield self.__processMMActiveTestConfirm(prbEntity)
                else:
                    actionAllowed = False
                if actionAllowed:
                    self.prbDispatcher.doAction(PrbAction(actionName, mmData))
            else:
                LOG_ERROR('Prebattle dispatcher is not defined')

    def movePlatoonPopover(self, platoonButtonXOffset):
        self.platoonCtrl.setPlatoonPopoverPosition(platoonButtonXOffset)

    def showSquad(self, platoonButtonXOffset):
        if self.prbDispatcher:
            self.platoonCtrl.evaluateVisibility(platoonButtonXOffset, toggleUI=True)
        else:
            LOG_ERROR('Prebattle dispatcher is not defined')

    def openFullscreenBattleSelector(self):
        from gui.impl.lobby.mode_selector.mode_selector_view import ModeSelectorView
        view = self.gui.windowsManager.getViewByLayoutID(ModeSelectorView.layoutID)
        if view is None:
            showModeSelectorWindow(isEventEnabled=self.isEventEnabled)
        return

    def closeFullscreenBattleSelector(self):
        self._closeFullScreenBattleSelector()

    def _closeFullScreenBattleSelector(self):
        from gui.impl.lobby.mode_selector.mode_selector_view import ModeSelectorView
        view = self.gui.windowsManager.getViewByLayoutID(ModeSelectorView.layoutID)
        if view is not None:
            view.close()
        return

    def _onPopulateEnd(self):
        pass

    def _populateButtons(self):
        if self.__tutorialLoader.gui.lastHeaderMenuButtonsOverride is not None:
            self.__onOverrideHeaderMenuButtons()
            return
        else:
            buttonsToExclude = []
            if self.__loginManager.isWgcSteam:
                buttonsToExclude.append(self.BUTTONS.PREMSHOP)
            if not self._canShowWotPlus():
                buttonsToExclude.append(self.BUTTONS.WOT_PLUS)
            availableButtons = [ button for button in self.BUTTONS.ALL() if button not in buttonsToExclude ]
            self.as_setHeaderButtonsS(availableButtons)
            return

    def _populate(self):
        self._cleanupVisitedSettings()
        self._updateHangarMenuData()
        battle_selector_items.create()
        super(LobbyHeader, self)._populate()
        self._populateButtons()
        self._addListeners()
        Waiting.hide('enter')
        self._isLobbyHeaderControlsDisabled = False
        self.__viewLifecycleWatcher.start(self.app.containerManager, [_RankedBattlesWelcomeViewLifecycleHandler(self), _MapboxIntroViewLifecycleHandler(self)])
        if self.bootcampController.isInBootcamp():
            self.as_disableFightButtonS(self.__isFightBtnDisabled)
        self._onPopulateEnd()

    def _invalidate(self, *args, **kwargs):
        super(LobbyHeader, self)._invalidate(*args, **kwargs)
        self._addListeners()

    def _dispose(self):
        self.__removeClanIconFromMemory()
        battle_selector_items.clear()
        self.__viewLifecycleWatcher.stop()
        self._removeListeners()
        self.__clearMenuVisibiliby()
        super(LobbyHeader, self)._dispose()

    def _canShowWotPlus(self):
        isWotPlusEnabled = self.lobbyContext.getServerSettings().isRenewableSubEnabled()
        isWotPlusNSEnabled = self.lobbyContext.getServerSettings().isWotPlusNewSubscriptionEnabled()
        hasWotPlusActive = self._renewableSubInfo.isEnabled()
        return isWotPlusEnabled and (hasWotPlusActive or isWotPlusNSEnabled)

    def _getPremiumLabelText(self, premiumState):
        isWotPlusEnabled = self.lobbyContext.getServerSettings().isRenewableSubEnabled()
        if self.__isSubscriptionEnabled:
            return ''
        if premiumState & PREMIUM_TYPE.PLUS:
            if not isWotPlusEnabled:
                return text_styles.main(backport.text(R.strings.menu.headerButtons.doLabel.premium()))
            return text_styles.gold(backport.text(R.strings.menu.headerButtons.doLabel.premium()))
        return text_styles.main(backport.text(R.strings.menu.common.premiumBuy())) if premiumState & PREMIUM_TYPE.BASIC else text_styles.gold(backport.text(R.strings.menu.common.premiumBuy()))

    def _getPremiumTooltipText(self, premiumState):
        if premiumState & PREMIUM_TYPE.PLUS:
            return TOOLTIPS.HEADER_PREMIUM_EXTEND
        return TOOLTIPS.HEADER_PREMIUM_UPGRADE if premiumState & PREMIUM_TYPE.BASIC else TOOLTIPS.HEADER_PREMIUM_BUY

    def _addListeners(self):
        self.startGlobalListening()
        self.app.containerManager.onViewAddedToContainer += self.__onViewAddedToContainer
        self.wallet.onWalletStatusChanged += self.__onWalletChanged
        self.gameSession.onPremiumNotify += self.__onPremiumTimeChanged
        self.gameSession.onPremiumTypeChanged += self._onPremiumTypeChanged
        self.igrCtrl.onIgrTypeChanged += self.__onIGRChanged
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        g_currentVehicle.onChanged += self.__onVehicleChanged
        g_currentPreviewVehicle.onChanged += self.__onVehicleChanged
        self.hangarSpace.onSpaceCreate += self.__onHangarSpaceCreated
        self.hangarSpace.onSpaceDestroy += self.__onHangarSpaceDestroy
        self.eventsCache.onSyncCompleted += self.__onEventsCacheResync
        self.eventsCache.onProgressUpdated += self.__onEventsCacheResync
        self.eventsCache.onEventsVisited += self.__onEventsVisited
        self.eventsCache.onProfileVisited += self.__onProfileVisited
        self.eventsCache.onPersonalQuestsVisited += self.__onMissionsVisited
        self.itemsCache.onSyncCompleted += self.__onItemsCacheResync
        self.battleMattersController.onStateChanged += self.__onBattleMattersStateChanged
        self.rankedController.onUpdated += self.__updateRanked
        self.rankedController.onGameModeStatusUpdated += self.__updateRanked
        self.epicController.onUpdated += self.__updateEpic
        self.epicController.onEventEnded += self.__updateEpic
        self.epicController.onPrimeTimeStatusUpdated += self.__updateEpic
        self.__battleRoyaleController.onUpdated += self.__updateRoyale
        self.__battleRoyaleController.onPrimeTimeStatusUpdated += self.__updateRoyale
        self.__mapsTrainingController.onUpdated += self.__updateMapsTraining
        self.platoonCtrl.onMembersUpdate += self.__updatePlatoon
        self.badgesController.onUpdated += self.__updateBadge
        self.anonymizerController.onStateChanged += self.__updateAnonymizedState
        self.clanNotificationCtrl.onClanNotificationUpdated += self.__updateStrongholdCounter
        self.__mapboxCtrl.onPrimeTimeStatusUpdated += self.__updateMapbox
        self.__funRandomCtrl.subscription.addSubModesWatcher(self._updatePrebattleControls, True)
        self.__comp7Controller.onBanUpdated += self.__updateComp7
        self.__comp7Controller.onOfflineStatusUpdated += self.__updateComp7
        g_playerEvents.onEnqueued += self._updatePrebattleControls
        g_playerEvents.onDequeued += self._updatePrebattleControls
        g_playerEvents.onArenaCreated += self._updatePrebattleControls
        self.techTreeEventsListener.onSettingsChanged += self._updateHangarMenuData
        self._renewableSubInfo.onRenewableSubscriptionDataChanged += self._onRenewableSubscriptionDataChanged
        self.lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingsChange
        self.addListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__handleFightButtonUpdated, scope=EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.BubbleTooltipEvent.SHOW, self.__showBubbleTooltip, scope=EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.CloseWindowEvent.GOLD_FISH_CLOSED, self.__onGoldFishWindowClosed, scope=EVENT_BUS_SCOPE.LOBBY)
        self.addListener(HEADER_BUTTONS_COUNTERS_CHANGED_EVENT, self.__onCounterChanged, scope=EVENT_BUS_SCOPE.DEFAULT)
        g_clientUpdateManager.addCurrencyCallback(Currency.CREDITS, self.__setCredits)
        g_clientUpdateManager.addCurrencyCallback(Currency.GOLD, self.__setGold)
        g_clientUpdateManager.addCurrencyCallback(Currency.CRYSTAL, self.__setCrystal)
        g_clientUpdateManager.addCallbacks({'stats.freeXP': self.__setFreeXP,
         'stats.clanInfo': self.__updatePlayerInfoPanel,
         'account.activePremiumExpiryTime': self.__onPremiumExpireTimeChanged,
         'cache.SPA': self.__onSPAUpdated})
        self.as_setFightButtonS(i18n.makeString('#menu:headerButtons/battle'))
        self.as_setWalletStatusS(self.wallet.componentsStatuses)
        self.as_setPremShopDataS(RES_ICONS.MAPS_ICONS_LOBBY_ICON_PREMSHOP, MENU.HEADERBUTTONS_BTNLABEL_PREMSHOP, TOOLTIPS.HEADER_PREMSHOP, TOOLTIP_TYPES.COMPLEX)
        self.as_initOnlineCounterS(constants.IS_SHOW_SERVER_STATS)
        if constants.IS_SHOW_SERVER_STATS:
            self.serverStats.onStatsReceived += self.__onStatsReceived
            self.__onStatsReceived()
        else:
            self.as_setServerNameS(makeHtmlString('html_templates:lobby', 'onlineCounter', {'key': self.connectionMgr.serverUserNameShort,
             'delimiter': '',
             'value': ''}))
        self.updateAccountInfo()
        self.__updateServerData()
        if not isTimeToShowGoldFishPromo():
            enabledVal = isGoldFishActionActive()
            tooltip = TOOLTIPS.HEADER_BUTTONS_GOLD_ACTION if enabledVal else TOOLTIPS.HEADER_BUTTONS_GOLD
            self.as_setGoldFishEnabledS(enabledVal, False, tooltip, TOOLTIP_TYPES.COMPLEX)
        g_preDefinedHosts.onPingPerformed += self.__onPingPerformed
        g_preDefinedHosts.requestPing()
        self.settingsCore.onSettingsChanged += self.__onSettingsChanged
        self.addListener(events.TutorialEvent.OVERRIDE_HANGAR_MENU_BUTTONS, self.__onOverrideHangarMenuButtons, scope=EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.TutorialEvent.OVERRIDE_HEADER_MENU_BUTTONS, self.__onOverrideHeaderMenuButtons, scope=EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, self.__onToggleVisibilityMenu, scope=EVENT_BUS_SCOPE.LOBBY)
        self.storageNovelty.onUpdated += self.__updateStorageTabCounter
        self.offersNovelty.onUpdated += self.__updateStorageTabCounter
        AccountSettings.onSettingsChanging += self.__onAccountSettingsChanging
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitLeft += self.__onUnitLeft
            unitMgr.onUnitJoined += self.__onUnitJoined
        self.addListener(PlatoonDropdownEvent.NAME, self.__platoonDropdown)
        self.addListener(FullscreenModeSelectorEvent.NAME, self.__onFullScreenModeSelector)
        if not self.bootcampController.isInBootcamp():
            self._addWGNPListeners()
        self.addListener(events.Comp7Event.OPEN_META, self.__onComp7MetaOpened, scope=EVENT_BUS_SCOPE.LOBBY)

    def _removeListeners(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.stopGlobalListening()
        self.removeListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__handleFightButtonUpdated, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.BubbleTooltipEvent.SHOW, self.__showBubbleTooltip, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.CloseWindowEvent.GOLD_FISH_CLOSED, self.__onGoldFishWindowClosed, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(HEADER_BUTTONS_COUNTERS_CHANGED_EVENT, self.__onCounterChanged, scope=EVENT_BUS_SCOPE.DEFAULT)
        self.anonymizerController.onStateChanged -= self.__updateAnonymizedState
        self.gameSession.onPremiumNotify -= self.__onPremiumTimeChanged
        self.gameSession.onPremiumTypeChanged -= self._onPremiumTypeChanged
        self.wallet.onWalletStatusChanged -= self.__onWalletChanged
        self.igrCtrl.onIgrTypeChanged -= self.__onIGRChanged
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        g_currentVehicle.onChanged -= self.__onVehicleChanged
        g_currentPreviewVehicle.onChanged -= self.__onVehicleChanged
        self.hangarSpace.onSpaceCreate -= self.__onHangarSpaceCreated
        self.hangarSpace.onSpaceDestroy -= self.__onHangarSpaceDestroy
        self.eventsCache.onSyncCompleted -= self.__onEventsCacheResync
        self.eventsCache.onProgressUpdated -= self.__onEventsCacheResync
        self.eventsCache.onEventsVisited -= self.__onEventsVisited
        self.eventsCache.onProfileVisited -= self.__onProfileVisited
        self.eventsCache.onPersonalQuestsVisited -= self.__onMissionsVisited
        self.itemsCache.onSyncCompleted -= self.__onItemsCacheResync
        self.battleMattersController.onStateChanged -= self.__onBattleMattersStateChanged
        self.rankedController.onUpdated -= self.__updateRanked
        self.rankedController.onGameModeStatusUpdated -= self.__updateRanked
        self.epicController.onUpdated -= self.__updateEpic
        self.epicController.onEventEnded -= self.__updateEpic
        self.epicController.onPrimeTimeStatusUpdated -= self.__updateEpic
        self.__battleRoyaleController.onUpdated -= self.__updateRoyale
        self.__battleRoyaleController.onPrimeTimeStatusUpdated -= self.__updateRoyale
        self.__mapsTrainingController.onUpdated -= self.__updateMapsTraining
        self.platoonCtrl.onMembersUpdate -= self.__updatePlatoon
        self.badgesController.onUpdated -= self.__updateBadge
        self.__mapboxCtrl.onPrimeTimeStatusUpdated -= self.__updateMapbox
        self.__comp7Controller.onBanUpdated -= self.__updateComp7
        self.__comp7Controller.onOfflineStatusUpdated -= self.__updateComp7
        self.clanNotificationCtrl.onClanNotificationUpdated -= self.__updateStrongholdCounter
        self.__funRandomCtrl.subscription.removeSubModesWatcher(self._updatePrebattleControls, True)
        g_playerEvents.onEnqueued -= self._updatePrebattleControls
        g_playerEvents.onDequeued -= self._updatePrebattleControls
        g_playerEvents.onArenaCreated -= self._updatePrebattleControls
        self.app.containerManager.onViewAddedToContainer -= self.__onViewAddedToContainer
        if constants.IS_SHOW_SERVER_STATS:
            self.serverStats.onStatsReceived -= self.__onStatsReceived
        g_preDefinedHosts.onPingPerformed -= self.__onPingPerformed
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self.techTreeEventsListener.onSettingsChanged -= self._updateHangarMenuData
        self._renewableSubInfo.onRenewableSubscriptionDataChanged -= self._onRenewableSubscriptionDataChanged
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingsChange
        self.removeListener(events.TutorialEvent.OVERRIDE_HANGAR_MENU_BUTTONS, self.__onOverrideHangarMenuButtons, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.TutorialEvent.OVERRIDE_HEADER_MENU_BUTTONS, self.__onOverrideHeaderMenuButtons, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, self.__onToggleVisibilityMenu, scope=EVENT_BUS_SCOPE.LOBBY)
        self.storageNovelty.onUpdated -= self.__updateStorageTabCounter
        self.offersNovelty.onUpdated -= self.__updateStorageTabCounter
        AccountSettings.onSettingsChanging -= self.__onAccountSettingsChanging
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitLeft -= self.__onUnitLeft
            unitMgr.onUnitJoined -= self.__onUnitJoined
            if unitMgr.unit:
                unitMgr.unit.onSquadSizeChanged -= self._updatePrebattleControls
        self.removeListener(PlatoonDropdownEvent.NAME, self.__platoonDropdown)
        self.removeListener(FullscreenModeSelectorEvent.NAME, self.__onFullScreenModeSelector)
        self._removeWGNPListeners()
        self.removeListener(events.Comp7Event.OPEN_META, self.__onComp7MetaOpened, scope=EVENT_BUS_SCOPE.LOBBY)

    def _addWGNPListeners(self):
        self.wgnpSteamAccCtrl.statusEvents.subscribe(StatusTypes.CONFIRMED, self.__onEmailConfirmed)
        self.wgnpSteamAccCtrl.statusEvents.subscribe(StatusTypes.ADDED, self.__onEmailAdded)
        self.wgnpSteamAccCtrl.statusEvents.subscribe(StatusTypes.ADD_NEEDED, self.__onEmailAddNeeded)
        self.wgnpDemoAccCtrl.statusEvents.subscribe(StatusTypes.PROCESSING, self.__onDemoAccountRenameProcessing, context=NICKNAME_CONTEXT)
        self.wgnpDemoAccCtrl.statusEvents.subscribe(StatusTypes.ADDED, self.__onDemoAccountRenameCompleted, context=NICKNAME_CONTEXT)
        self.wgnpDemoAccCtrl.statusEvents.subscribe(StatusTypes.UNDEFINED, self.__onDemoAccountRenameCompleted, context=NICKNAME_CONTEXT)

    def _removeWGNPListeners(self):
        self.wgnpSteamAccCtrl.statusEvents.unsubscribe(StatusTypes.CONFIRMED, self.__onEmailConfirmed)
        self.wgnpSteamAccCtrl.statusEvents.unsubscribe(StatusTypes.ADDED, self.__onEmailAdded)
        self.wgnpSteamAccCtrl.statusEvents.unsubscribe(StatusTypes.ADD_NEEDED, self.__onEmailAddNeeded)
        self.wgnpDemoAccCtrl.statusEvents.unsubscribe(StatusTypes.PROCESSING, self.__onDemoAccountRenameProcessing, context=NICKNAME_CONTEXT)
        self.wgnpDemoAccCtrl.statusEvents.unsubscribe(StatusTypes.ADDED, self.__onDemoAccountRenameCompleted, context=NICKNAME_CONTEXT)
        self.wgnpDemoAccCtrl.statusEvents.unsubscribe(StatusTypes.UNDEFINED, self.__onDemoAccountRenameCompleted, context=NICKNAME_CONTEXT)

    def __closeWindowsWithTopSubViewLayer(self):
        windows = self.gui.windowsManager.findWindows(lambda w: w.layer == WindowLayer.TOP_SUB_VIEW)
        for window in windows:
            window.destroy()

    def __platoonDropdown(self, event):
        if event:
            self.as_setIsPlatoonDropdownShowingS(event.ctx['showing'])

    def __onFullScreenModeSelector(self, event):
        if event:
            self.as_setIsFullscreenBattleSelectorShowingS(event.ctx['showing'])

    def __updateAccountAttrs(self):
        accAttrs = self.itemsCache.items.stats.attributes
        battle_selector_items.getItems().validateAccountAttrs(accAttrs)
        self.__setAccountsAttrs()

    def __updateServerData(self):
        serverShortName = self.connectionMgr.serverUserNameShort.strip().split(' ')[-1]
        if len(serverShortName) > _MAX_HEADER_SERVER_NAME_LEN:
            serverShortName = _SERVER_NAME_PREFIX % serverShortName[:_MAX_HEADER_SERVER_NAME_LEN]
        self.as_setServerS(serverShortName, TOOLTIPS_CONSTANTS.SETTINGS_BUTTON, TOOLTIP_TYPES.SPECIAL)

    def __updateServerName(self):
        serverShortName = self.connectionMgr.serverUserNameShort.strip().split(' ')[-1]
        if len(serverShortName) > _MAX_HEADER_SERVER_NAME_LEN:
            serverShortName = _SERVER_NAME_PREFIX % serverShortName[:_MAX_HEADER_SERVER_NAME_LEN]
        self.as_setServerS(serverShortName, TOOLTIPS_CONSTANTS.SETTINGS_BUTTON, TOOLTIP_TYPES.SPECIAL)

    def __updateComp7(self):
        self._updatePrebattleControls()

    def __onComp7MetaOpened(self, *_):
        for alias in self.TABS.ALL():
            self.as_doDeselectHeaderButtonS(alias)

    @staticmethod
    def __hideComp7Views():
        for window in (MetaRootViewWindow, NoVehiclesScreenWindow, IntroScreenWindow):
            instances = window.getInstances()
            if instances:
                first(instances).destroy()

    def __updatePlayerInfoPanel(self, clanInfo, diff=None):
        if not isPlayerAccount():
            return
        else:
            name = BigWorld.player().name
            if clanInfo and len(clanInfo) > 1:
                clanAbbrev = clanInfo[1]
            else:
                clanAbbrev = None
            self.__setPlayerInfo(TOOLTIPS.HEADER_ACCOUNT, TOOLTIP_TYPES.COMPLEX, userVO={'fullName': self.lobbyContext.getPlayerFullName(name, clanInfo=clanInfo),
             'userName': name,
             'clanAbbrev': clanAbbrev})
            self.__updateAccountCompletionStatus()
            self.__updateDemoAccountRenamingStatus()
            self.__removeClanIconFromMemory()
            if g_clanCache.clanDBID:
                self.requestClanEmblem16x16(g_clanCache.clanDBID)
            else:
                self._updateHangarMenuData()
            if diff is not None and any((self.goodiesCache.haveBooster(itemId) for itemId in diff)):
                SoundGroupsInstance.playSound2D('warehouse_booster')
            return

    def __setPlayerInfo(self, tooltip, tooltipType, tooltipArgs=None, warningIcon=False, userVO=None):
        data = {'isTeamKiller': self.itemsCache.items.stats.isTeamKiller,
         'tooltip': tooltip,
         'tooltipType': tooltipType,
         'tooltipArgs': tooltipArgs,
         'isWarningIconVisible': warningIcon,
         'isWotPlusEnabled': self.lobbyContext.getServerSettings().isRenewableSubEnabled()}
        if userVO:
            data['userVO'] = userVO
        self.as_nameResponseS(data)

    def __onEmailConfirmed(self, status):
        self.__setPlayerInfo(TOOLTIPS.HEADER_ACCOUNT, TOOLTIP_TYPES.COMPLEX, warningIcon=False)

    def __onEmailAdded(self, status):
        self.__setPlayerInfo(TOOLTIPS_CONSTANTS.ACCOUNT_COMPLETION, TOOLTIP_TYPES.WULF, warningIcon=True, tooltipArgs=[status.email])

    def __onEmailAddNeeded(self, status=None):
        self.__setPlayerInfo(TOOLTIPS_CONSTANTS.ACCOUNT_COMPLETION, TOOLTIP_TYPES.WULF, warningIcon=True)

    def __onDemoAccountRenameProcessing(self, status=None):
        self.__setPlayerInfo(TOOLTIPS_CONSTANTS.DEMO_ACCOUNT_RENAME_PROCESSING, TOOLTIP_TYPES.WULF, warningIcon=True)

    def __onDemoAccountRenameCompleted(self, status=None):
        self.__setPlayerInfo(TOOLTIPS.HEADER_ACCOUNT, TOOLTIP_TYPES.COMPLEX, warningIcon=False)

    @future_async.wg_async
    def __updateAccountCompletionStatus(self):
        if not self.steamRegistrationCtrl.isSteamAccount or self.bootcampController.isInBootcamp():
            return
        status = yield future_async.wg_await(self.wgnpSteamAccCtrl.getEmailStatus())
        if status.isUndefined or self.isDisposed():
            return
        if status.typeIs(StatusTypes.ADD_NEEDED):
            self.__onEmailAddNeeded()
        elif status.typeIs(StatusTypes.ADDED):
            self.__onEmailAdded(status)

    @future_async.wg_async
    def __updateDemoAccountRenamingStatus(self):
        if self.steamRegistrationCtrl.isSteamAccount or self.bootcampController.isInBootcamp():
            return
        if not self.wgnpDemoAccCtrl.settings.isRenameApiEnabled():
            self.__onDemoAccountRenameCompleted()
            return
        status = yield future_async.wg_await(self.wgnpDemoAccCtrl.getNicknameStatus())
        if status.isUndefined or self.isDisposed():
            return
        if status.typeIs(StatusTypes.PROCESSING):
            self.__onDemoAccountRenameProcessing()
        elif status.typeIs(StatusTypes.ADDED):
            self.__onDemoAccountRenameCompleted()

    def __updateAnonymizedState(self, **_):
        self.as_updateAnonymizedStateS(self.anonymizerController.isAnonymized)

    def __updateBadge(self):
        badge = self.badgesController.getPrefix()
        selected = badge is not None
        data = {}
        if selected:
            data = badge.getBadgeVO(ICONS_SIZES.X48)
        self.as_setBadgeS(data, selected)
        return

    def __onPremiumExpireTimeChanged(self, _):
        self.__updateAccountAttrs()

    def __getWalletTooltipSettings(self, btnType):
        currencyStatus = self.wallet.componentsStatuses.get(btnType, WalletController.STATUS.SYNCING)
        if constants.IS_SINGAPORE and btnType in (LobbyHeader.BUTTONS.CREDITS, LobbyHeader.BUTTONS.GOLD):
            if not self.itemsCache.items.stats.mayConsumeWalletResources:
                tooltip = (TOOLTIPS.HEADER_BUTTONS + btnType, TOOLTIP_TYPES.COMPLEX)
            else:
                tooltip = (btnType + TOOLTIPS_CONSTANTS.SINGAPORE_WALLET_STATS, TOOLTIP_TYPES.SPECIAL)
        elif currencyStatus != WalletController.STATUS.AVAILABLE:
            tooltip = (TOOLTIPS.HEADER_BUTTONS + btnType, TOOLTIP_TYPES.COMPLEX)
        else:
            tooltip = (btnType + TOOLTIPS_CONSTANTS.HEADER_BUTTON_INFO, TOOLTIP_TYPES.SPECIAL)
        return tooltip

    def __setCredits(self, accCredits):
        btnType = LobbyHeader.BUTTONS.CREDITS
        if self.__isHeaderButtonPresent(btnType):
            isActionActive = self.itemsCache.items.shop.isCreditsConversionActionActive
            btnData = self._getWalletBtnData(btnType, accCredits, getBWFormatter(Currency.CREDITS), isActionActive)
            self.as_updateWalletBtnS(btnType, btnData)

    def __setGold(self, gold):
        btnType = LobbyHeader.BUTTONS.GOLD
        if self.__isHeaderButtonPresent(btnType):
            btnData = self._getWalletBtnData(btnType, gold, getBWFormatter(Currency.GOLD), isGoldFishActionActive())
            self.as_updateWalletBtnS(btnType, btnData)

    def __setCrystal(self, crystals):
        btnType = LobbyHeader.BUTTONS.CRYSTAL
        if self.__isHeaderButtonPresent(btnType):
            btnData = self._getWalletBtnData(btnType, crystals, getBWFormatter(Currency.CRYSTAL), False, False, False)
            self.as_updateWalletBtnS(btnType, btnData)

    def __setFreeXP(self, freeXP):
        btnType = LobbyHeader.BUTTONS.FREE_XP
        if self.__isHeaderButtonPresent(btnType):
            isActionActive = self.itemsCache.items.shop.isXPConversionActionActive
            btnData = self._getWalletBtnData(btnType, freeXP, backport.getIntegralFormat, isActionActive)
            self.as_updateWalletBtnS(btnType, btnData)

    def _getWalletBtnData(self, btnType, value, formatter, isHasAction=False, isDiscountEnabled=False, isNew=False):
        tooltip, tooltipType = self.__getWalletTooltipSettings(btnType)
        return {'money': formatter(value),
         'btnDoText': self._getWalletBtnDoText(btnType),
         'tooltip': tooltip,
         'tooltipType': tooltipType,
         'icon': btnType,
         'isHasAction': isHasAction,
         'isDiscountEnabled': isDiscountEnabled,
         'isNew': isNew,
         'shortMoneyValue': _getShortCurrencyValue(value, formatter)}

    def _getWalletBtnDoText(self, btnType):
        return MENU.HEADERBUTTONS_BTNLABEL + btnType

    def __updateWotPlusAttrs(self):
        hasWotPlus = self._renewableSubInfo.isEnabled()
        locale = R.strings.subscription.headerButton
        if hasWotPlus:
            icon = backport.image(R.images.gui.maps.icons.premacc.lobbyHeader.wotPlus_active())
            label = text_styles.main(backport.text(locale.label()))
            state = text_styles.standard(backport.text(locale.state.active()))
        else:
            icon = backport.image(R.images.gui.maps.icons.premacc.lobbyHeader.wotPlus_available())
            label = text_styles.main(backport.text(locale.label()))
            state = text_styles.gold(backport.text(locale.state.available()))
        self.as_setWotPlusDataS({'wotPlusIcon': icon,
         'label': label,
         'state': state,
         'tooltip': TOOLTIPS_CONSTANTS.WOT_PLUS,
         'tooltipType': TOOLTIP_TYPES.WULF})
        self.as_doSoftDisableHeaderButtonS(self.BUTTONS.WOT_PLUS, hasWotPlus)

    def __setAccountsAttrs(self):

        def _getPremiumBtnLabels():
            if not isPremiumAccount:
                btnLbl = text_styles.main(backport.text(R.strings.menu.accountTypes.base()))
                btnLblShort = text_styles.main(backport.text(R.strings.menu.accountTypes.base()))
            elif not self.itemsCache.items.stats.isActivePremium(PREMIUM_TYPE.PLUS):
                btnLbl = text_styles.neutral(backport.text(R.strings.menu.accountTypes.premium()))
                btnLblShort = text_styles.neutral(backport.text(R.strings.menu.accountTypes.premiumShort()))
            elif isWotPlusEnabled:
                btnLbl = text_styles.main(backport.text(R.strings.menu.accountTypes.premiumPlus()))
                btnLblShort = text_styles.main(backport.text(R.strings.menu.accountTypes.premiumPlusShort()))
            else:
                btnLbl = text_styles.gold(backport.text(R.strings.menu.accountTypes.premiumPlus()))
                btnLblShort = text_styles.gold(backport.text(R.strings.menu.accountTypes.premiumPlusShort()))
            return (btnLbl, btnLblShort)

        isWotPlusEnabled = self.lobbyContext.getServerSettings().isRenewableSubEnabled()
        premiumExpiryTime = self.itemsCache.items.stats.activePremiumExpiryTime
        isPremiumAccount = self.itemsCache.items.stats.isPremium
        premiumBtnLbl, premiumBtnLblShort = _getPremiumBtnLabels()
        if isPremiumAccount:
            iconName = 'premiumPlus'
            deltaInSeconds = float(time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(premiumExpiryTime)))
            if not self.itemsCache.items.stats.isActivePremium(PREMIUM_TYPE.PLUS):
                if deltaInSeconds > self.__PREM_WARNING_LIMIT:
                    iconName = 'premium'
            if deltaInSeconds <= self.__PREM_WARNING_LIMIT:
                htmlKey = 'premiumEnd-timeLabel'
            elif self.itemsCache.items.stats.isActivePremium(PREMIUM_TYPE.PLUS):
                htmlKey = 'premiumPlus-timeLabel'
            else:
                htmlKey = 'premium-timeLabel'
            timeLeft, timeMetric = self.__getPremiumExpiryTimeAttrs(deltaInSeconds)
            timeLabel = makeHtmlString('html_templates:lobby/header', htmlKey, {'time': timeLeft,
             'metric': timeMetric})
            premiumIcon = backport.image(R.images.gui.maps.icons.premacc.lobbyHeader.dyn(iconName)())
        else:
            timeLabel = ''
            premiumIcon = backport.image(R.images.gui.maps.icons.premacc.lobbyHeader.noPremium()) if isWotPlusEnabled else None
        premiumState = self.itemsCache.items.stats.activePremiumType
        self.as_setPremiumParamsS({'btnLabel': premiumBtnLbl,
         'btnLabelShort': premiumBtnLblShort,
         'doLabel': self._getPremiumLabelText(premiumState),
         'timeLabel': timeLabel,
         'isHasAction': self.__hasPremiumPacketDiscount(),
         'isPremium': isPremiumAccount,
         'isSubscription': self.__isSubscriptionEnabled and isPremiumAccount,
         'isWotPlusEnabled': isWotPlusEnabled,
         'premiumIcon': premiumIcon,
         'tooltip': self._getPremiumTooltipText(premiumState),
         'tooltipType': TOOLTIP_TYPES.COMPLEX})
        return

    @staticmethod
    def __getPremiumExpiryTimeAttrs(deltaInSeconds):
        if deltaInSeconds > time_utils.ONE_DAY:
            timeLeft = math.ceil(old_div(deltaInSeconds, time_utils.ONE_DAY))
            timeMetric = backport.text(R.strings.menu.header.account.premium.days())
        else:
            timeLeft = math.ceil(old_div(deltaInSeconds, time_utils.ONE_HOUR))
            timeMetric = backport.text(R.strings.menu.header.account.premium.hours())
        return (timeLeft, timeMetric)

    def __hasPremiumPacketDiscount(self):
        return self.itemsCache.items.shop.isActionOnPremium()

    def __triggerViewLoad(self, alias):
        if alias == self.TABS.BROWSER:
            self.chinaCtrl.showBrowser()
        elif alias == self.TABS.STORAGE:
            showStorage()
        else:
            event = g_entitiesFactories.makeLoadEvent(SFViewLoadParams(alias))
            if event is not None:
                self.fireEvent(event, scope=EVENT_BUS_SCOPE.LOBBY)
            else:
                LOG_ERROR('Invalid subview alias', alias)
                return
        self.__setCurrentScreen(alias)
        return

    def __setCurrentScreen(self, alias):
        self.__currentScreen = alias
        self.as_setScreenS(alias)

    def __onWalletChanged(self, status):
        self.__setGold(self.itemsCache.items.stats.actualGold)
        self.__setCrystal(self.itemsCache.items.stats.actualCrystal)
        if constants.IS_SINGAPORE:
            self.__setCredits(self.itemsCache.items.stats.actualCredits)
        self.__setFreeXP(self.itemsCache.items.stats.actualFreeXP)
        self.as_setWalletStatusS(status)

    def __onPremiumTimeChanged(self, *_):
        self.__updateAccountAttrs()

    def __onViewAddedToContainer(self, _, pyEntity):
        if pyEntity.layer is WindowLayer.SUB_VIEW:
            if pyEntity.alias in self.TABS.ALL():
                self.__setCurrentScreen(pyEntity.alias)
            elif self.__currentScreen is not None and pyEntity.alias in self.DESELECT_TAB_ALIASES:
                self.as_doDeselectHeaderButtonS(self.__currentScreen)
                self.__currentScreen = None
        return

    def __getContainer(self, layer):
        return self.app.containerManager.getContainer(layer) if self.app is not None and self.app.containerManager is not None else None

    def __getBattleTypeSelectPopover(self):
        container = self.__getContainer(WindowLayer.WINDOW)
        view = None
        if container:
            view = container.getView({POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.BATTLE_TYPE_SELECT_POPOVER})
        return view

    def __getSquadTypeSelectPopover(self):
        container = self.__getContainer(WindowLayer.WINDOW)
        view = None
        if container:
            view = container.getView({POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.SQUAD_TYPE_SELECT_POPOVER})
        return view

    def __closeBattleTypeSelectPopover(self):
        view = self.__getBattleTypeSelectPopover()
        if view:
            view.destroy()

    def __closeSquadTypeSelectPopover(self):
        view = self.__getSquadTypeSelectPopover()
        if view:
            view.destroy()

    def __updateBattleTypeSelectPopover(self):
        view = self.__getBattleTypeSelectPopover()
        if view:
            view.update()

    def __updateSquadTypeSelectPopover(self):
        view = self.__getSquadTypeSelectPopover()
        if view:
            view.update()

    def __onUnitLeft(self, *_):
        self._updatePrebattleControls()

    def __onUnitJoined(self, *_):
        self._updatePrebattleControls()
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr and unitMgr.unit:
            unitMgr.unit.onSquadSizeChanged += self._updatePrebattleControls

    @property
    def isEventEnabled(self):
        _, isBrCycle = self.__battleRoyaleController.getCurrentCycleInfo()
        brAvailable = isBrCycle and self.__battleRoyaleController.isEnabled()
        isEpicBattleAvailabe = self.epicController.isEnabled() and self.epicController.isCurrentCycleActive()
        isEventBattlesAvailable = self.__eventBattlesController.isEnabled()
        mapboxAvailable = self.__mapboxCtrl.isActive() and self.__mapboxCtrl.isInPrimeTime()
        return not self.bootcampController.isInBootcamp() and (self.rankedController.isAvailable() or self.__funRandomCtrl.subModesInfo.isAvailable() or isEpicBattleAvailabe or brAvailable or mapboxAvailable or isEventBattlesAvailable)

    def _updatePrebattleControls(self, *_):
        if self._isLobbyHeaderControlsDisabled:
            return
        elif not self.prbDispatcher:
            return
        else:
            items = battle_selector_items.getItems()
            squadItems = battle_selector_items.getSquadItems()
            state = self.prbDispatcher.getFunctionalState()
            selected = items.update(state)
            squadSelected = squadItems.update(state)
            isNewbie = self.uiSpamController.shouldBeHidden('ModeSelectorWidgetsBtnHint')
            hasNew = not self.bootcampController.isInBootcamp() and items.hasNew() and not isNewbie
            result = self.prbEntity.canPlayerDoAction()
            canDo, canDoMsg = result.isValid, result.restriction
            playerInfo = self.prbDispatcher.getPlayerInfo()
            isInSquad = selected.isInSquad(state)
            isSquadEnabled = isInSquad or self.prbDispatcher.getEntity().getPermissions().canCreateSquad()
            self.as_doDisableHeaderButtonS(self.BUTTONS.SQUAD, isEnabled=isSquadEnabled)
            isNavigationEnabled = not state.isNavigationDisabled()
            isEvent = state.isInPreQueue(constants.QUEUE_TYPE.EVENT_BATTLES) or state.isInUnit(constants.PREBATTLE_TYPE.EVENT)
            isRanked = state.isInPreQueue(constants.QUEUE_TYPE.RANKED)
            isSandbox = state.isInPreQueue(constants.QUEUE_TYPE.SANDBOX)
            isEpic = state.isInPreQueue(constants.QUEUE_TYPE.EPIC) or state.isInUnit(constants.PREBATTLE_TYPE.EPIC)
            isRoyale = state.isInPreQueue(constants.QUEUE_TYPE.BATTLE_ROYALE) or state.isInUnit(constants.PREBATTLE_TYPE.BATTLE_ROYALE)
            isRoyaleTournament = state.isInPreQueue(constants.QUEUE_TYPE.BATTLE_ROYALE_TOURNAMENT) or state.isInUnit(constants.PREBATTLE_TYPE.BATTLE_ROYALE_TOURNAMENT)
            isMapBox = state.isInPreQueue(constants.QUEUE_TYPE.MAPBOX) or state.isInUnit(constants.PREBATTLE_TYPE.MAPBOX)
            isMapsTraining = state.isInPreQueue(constants.QUEUE_TYPE.MAPS_TRAINING)
            isFunRandom = state.isInPreQueue(constants.QUEUE_TYPE.FUN_RANDOM) or state.isInUnit(constants.PREBATTLE_TYPE.FUN_RANDOM)
            isRandom = state.isInPreQueue(constants.QUEUE_TYPE.RANDOMS)
            isLegacyTraining = state.isInLegacy(PREBATTLE_TYPE.TRAINING)
            isComp7 = state.isInPreQueue(constants.QUEUE_TYPE.COMP7) or state.isInUnit(constants.PREBATTLE_TYPE.COMP7)
            if self.__isHeaderButtonPresent(LobbyHeader.BUTTONS.SQUAD):
                extendedSquadInfoVo = self.platoonCtrl.buildExtendedSquadInfoVo()
                if isSquadEnabled:
                    if not isNavigationEnabled:
                        tooltip = ''
                    elif extendedSquadInfoVo.platoonState == EPlatoonButtonState.SEARCHING_STATE.value:
                        tooltip = PLATOON.HEADERBUTTON_TOOLTIPS_SEARCHING
                    elif isMapBox:
                        if isInSquad:
                            tooltip = PLATOON.HEADERBUTTON_TOOLTIPS_INMAPBOXSQUAD
                        else:
                            tooltip = PLATOON.HEADERBUTTON_TOOLTIPS_MAPBOXSQUAD
                    elif isInSquad or isEvent:
                        tooltip = PLATOON.HEADERBUTTON_TOOLTIPS_INSQUAD
                    elif isRanked:
                        tooltip = PLATOON.HEADERBUTTON_TOOLTIPS_RANKEDSQUAD
                    elif isFunRandom:
                        tooltip = PLATOON.HEADERBUTTON_TOOLTIPS_FUNRANDOMSQUAD
                    elif isRoyale or isRoyaleTournament:
                        tooltip = PLATOON.HEADERBUTTON_TOOLTIPS_BATTLEROYALESQUAD if isRoyale else ''
                    elif isComp7:
                        tooltip = PLATOON.HEADERBUTTON_TOOLTIPS_COMP7SQUAD
                    else:
                        tooltip = PLATOON.HEADERBUTTON_TOOLTIPS_SQUAD
                else:
                    tooltip = ''
                    if isComp7 and canDoMsg == PRE_QUEUE_RESTRICTION.BAN_IS_SET:
                        tooltip = MENU.HEADERBUTTONS_FIGHTBTN_TOOLTIP_COMP7BANISSET
                hasEventSquadCap = bool(BONUS_CAPS.checkAny(constants.ARENA_BONUS_TYPE.EVENT_BATTLES, BONUS_CAPS.SQUADS))
                isEventSquadEnable = isEvent and hasEventSquadCap
                hasPopover = self.platoonCtrl.hasWelcomeWindow() or self.platoonCtrl.canSelectSquadSize()
                self.as_updateSquadS(isInSquad=isInSquad, tooltip=tooltip, tooltipType=TOOLTIP_TYPES.COMPLEX, isEvent=isEventSquadEnable, icon=squadSelected.squadIcon if hasattr(squadSelected, 'squadIcon') else None, hasPopover=hasPopover, data=extendedSquadInfoVo._asdict())
            self.__isFightBtnDisabled = self._checkFightButtonDisabled(canDo, selected.isLocked())
            tooltipData, isSpecial = '', False
            if self.__isFightBtnDisabled and not state.hasLockedState:
                if isSandbox:
                    tooltipData = getSandboxTooltipData(result)
                elif isEvent and state.isInUnit(constants.PREBATTLE_TYPE.EVENT):
                    tooltipData = getEventTooltipData()
                elif g_currentVehicle.isTooHeavy():
                    tooltipData = makeTooltip(body=backport.text(R.strings.tooltips.hangar.startBtn.vehicleToHeavy.body()))
                elif g_currentVehicle.isOnlyForEpicBattles() and (g_currentVehicle.isUnsuitableToQueue() or g_currentVehicle.isDisabledInRent()):
                    tooltipData = getEpicBattlesOnlyVehicleTooltipData(result)
                elif g_currentVehicle.isOnlyForComp7Battles() and (g_currentVehicle.isUnsuitableToQueue() or g_currentVehicle.isDisabledInRent()):
                    tooltipData = getComp7BattlesOnlyVehicleTooltipData(result)
                elif isEpic or isRoyale:
                    tooltipData = getEpicFightBtnTooltipData(result)
                elif isMapBox:
                    tooltipData = getMapboxFightBtnTooltipData(result)
                elif isFunRandom:
                    tooltipData = getFunRandomFightBtnTooltipData(result, isInSquad)
                elif isInSquad:
                    tooltipData = getSquadFightBtnTooltipData(canDoMsg)
                elif g_currentPreviewVehicle.isPresent():
                    tooltipData = getPreviewTooltipData()
                elif isRanked:
                    tooltipData = getRankedFightBtnTooltipData(result)
                elif isMapsTraining:
                    tooltipData = getMapsTrainingTooltipData()
                elif isRandom or isLegacyTraining:
                    tooltipData = getRandomTooltipData(result)
                elif isComp7:
                    tooltipData = getComp7FightBtnTooltipData(result)
            elif isRoyale and g_currentVehicle.isOnlyForBattleRoyaleBattles():
                tooltipData = TOOLTIPS_CONSTANTS.BATTLE_ROYALE_PERF_ADVANCED
                isSpecial = True
            self.as_setFightBtnTooltipS(tooltipData, isSpecial)
            if self.hangarSpace.spaceInited or not self.bootcampController.isInBootcamp():
                self.as_disableFightButtonS(self.__isFightBtnDisabled)
            self.as_setFightButtonS(selected.getFightButtonLabel(state, playerInfo))
            if self.__isHeaderButtonPresent(LobbyHeader.BUTTONS.BATTLE_SELECTOR):
                eventEnabled = self.isEventEnabled and not isNewbie
                self.as_updateBattleTypeS(i18n.makeString(selected.getLabel()), selected.getSmallIcon(), selected.isSelectorBtnEnabled(), self.__SELECTOR_TOOLTIP_TYPE, TOOLTIP_TYPES.COMPLEX, selected.getData(), eventEnabled, eventEnabled and not WWISE.WG_isMSR(), self.lobbyContext.getServerSettings().isLegacyModeSelectorEnabled(), hasNew)
            else:
                self.as_updateBattleTypeS('', '', False, '', TOOLTIP_TYPES.NONE, '', False, False, False, False)
            if selected.isDisabled():
                self.__closeBattleTypeSelectPopover()
            else:
                self.__updateBattleTypeSelectPopover()
            if squadSelected.isDisabled():
                self.__closeSquadTypeSelectPopover()
            else:
                self.__updateSquadTypeSelectPopover()
            for button in self.PRB_NAVIGATION_DISABLE_BUTTONS:
                self.as_doDisableHeaderButtonS(button, isNavigationEnabled)

            self.__updateNavButtonsState(isNavigationEnabled)
            self.__updateAccountAttrs()
            self._updateHangarMenuData()
            return

    def __onHangarSpaceCreated(self):
        if self.bootcampController.isInBootcamp():
            self.as_disableFightButtonS(self.__isFightBtnDisabled)

    def __onHangarSpaceDestroy(self, inited):
        if inited and self.bootcampController.isInBootcamp():
            self.as_disableFightButtonS(True)

    def __onToggleVisibilityMenu(self, event):
        state = event.ctx['state']
        self.__menuVisibilityHelper.updateStates(state)
        activeState = self.__menuVisibilityHelper.getActiveState()
        self.as_toggleVisibilityMenuS(activeState)

    def _checkFightButtonDisabled(self, canDo, isLocked):
        return not canDo or isLocked

    def _updateTabCounters(self):
        self._updatePremiumQuestsVisitedStatus(self.eventsCache.getPremiumQuests())
        self.__onProfileVisited()
        self.__updateStrongholdCounter()
        self.__updateShopTabCounter()
        self.__updateStorageTabCounter()
        self.__onEventsVisited()
        self.__updateMissionsTabCounter()
        self.__updateRecruitsTabCounter(self.TABS.BARRACKS)

    def _onPremiumTypeChanged(self, _):
        self._updateTabCounters()

    def __handleFightButtonUpdated(self, _):
        self._updatePrebattleControls()

    def __handleSetPrebattleCoolDown(self, event):
        if not self.prbDispatcher:
            return
        playerInfo = self.prbDispatcher.getPlayerInfo()
        isCreator = playerInfo.isCreator
        if event.requestID is REQUEST_TYPE.SET_PLAYER_STATE and not isCreator:
            self.as_setCoolDownForReadyS(event.coolDown)

    def __showBubbleTooltip(self, event):
        self.as_showBubbleTooltipS(event.getMessage(), event.getDuration())

    def __onVehicleChanged(self, *_):
        self._updatePrebattleControls()

    def __onEventsCacheResync(self, *_):
        self._updatePrebattleControls()
        self._updateTabCounters()
        self.updateMoneyStats()
        self.updateXPInfo()

    def __onItemsCacheResync(self, *_):
        self.__updateRecruitsTabCounter(self.TABS.BARRACKS)

    def __onBattleMattersStateChanged(self, *_):
        self.__onEventsCacheResync()

    def __onEventsVisited(self, counters=None):
        if counters is not None:
            self.uiSpamController.setVisited(self.TABS.MISSIONS)
            if 'missions' in counters:
                counter = counters['missions'] + self.__mapboxCtrl.getUnseenItemsCount()
                self.__onMissionVisited(counter)
        else:
            quests = self.eventsCache.getAdvisableQuests()
            counter = len(quest_settings.getNewCommonEvents(quests.values())) + self.__mapboxCtrl.getUnseenItemsCount()
            self.__onMissionVisited(counter)
        return

    @staticmethod
    def _updatePremiumQuestsVisitedStatus(quests):
        if not quests:
            return
        firstPremiumId = sorted(quests.keys())[0]
        currFirstPremMissionCompleted = quests[firstPremiumId].isCompleted()
        if currFirstPremMissionCompleted:
            return
        questSettings = AccountSettings.getSettings(QUESTS)
        prevFirstPremMissionCompleted = questSettings.get(QUEST_DELTAS, {}).get(QUEST_DELTAS_COMPLETION, {}).get(firstPremiumId, False)
        if prevFirstPremMissionCompleted and firstPremiumId in questSettings['visited']:
            questSettings['visited'] = tuple((t for t in questSettings['visited'] if t != firstPremiumId))
            AccountSettings.setSettings(QUESTS, questSettings)

    def __onMissionVisited(self, counter):
        if counter:
            if self.uiSpamController.shouldBeHidden(self.TABS.MISSIONS):
                counter = 1
            self.__setCounter(self.TABS.MISSIONS, counter)
        else:
            self.__hideCounter(self.TABS.MISSIONS)

    def __onProfileVisited(self):
        self.__updateProfileTabCounter()

    def __onMissionsVisited(self):
        alias = self.TABS.PERSONAL_MISSIONS
        counters = AccountSettings.getCounters(NEW_LOBBY_TAB_COUNTER)
        if alias in counters and counters[alias]:
            counters[alias] = False
            AccountSettings.setCounters(NEW_LOBBY_TAB_COUNTER, counters)
        self.__updateMissionsTabCounter()

    def __onIGRChanged(self, *_):
        self._updatePrebattleControls()

    def __updateRanked(self, *_):
        self._updatePrebattleControls()
        self._updateTabCounters()

    def __updateEpic(self, *_):
        self._updatePrebattleControls()

    def __updateMapbox(self, *_):
        self._updatePrebattleControls()

    def __updateRoyale(self, *_):
        self.__onEventsVisited()
        self._updatePrebattleControls()

    def __updateMapsTraining(self, *_):
        self._updatePrebattleControls()

    def __updatePlatoon(self, *_):
        self._updatePrebattleControls()

    def _updateStrongholdsSelector(self):
        strongholdEnabled = isStrongholdsEnabled()
        clansTabReplaceStrongholds = isClansTabReplaceStrongholds()
        clanDBID = self.itemsCache.items.stats.clanDBID
        if not clanDBID:
            strongholdsTabConfig = {(True, False): (MENU.HEADERBUTTONS_CLAN, TOOLTIPS.HEADER_BUTTONS_FORTS),
             (False, False): (MENU.HEADERBUTTONS_CLAN, TOOLTIPS.HEADER_BUTTONS_FORTS_TURNEDOFF),
             (True, True): (MENU.HEADERBUTTONS_CLANS, TOOLTIPS.HEADER_BUTTONS_CLANS),
             (False, True): (MENU.HEADERBUTTONS_CLANS, TOOLTIPS.HEADER_BUTTONS_CLANS_TURNEDOFF)}
            label, tooltip = strongholdsTabConfig[strongholdEnabled, clansTabReplaceStrongholds]
        else:
            label = MENU.HEADERBUTTONS_CLAN
            tooltip = TOOLTIPS.HEADER_BUTTONS_FORTS if strongholdEnabled else TOOLTIPS.HEADER_BUTTONS_FORTS_TURNEDOFF
        return {'label': label,
         'value': VIEW_ALIAS.LOBBY_STRONGHOLD,
         'tooltip': tooltip,
         'icon': self.__clanIconID,
         'enabled': strongholdEnabled}

    def _getPersonalMissionSelectorTabData(self):
        if self.lobbyContext.getServerSettings().isPersonalMissionsEnabled():
            tooltip = TOOLTIPS.HEADER_BUTTONS_PERSONALMISSIONS
            enabled = True
        else:
            tooltip = TOOLTIPS.HEADER_BUTTONS_PERSONALMISSIONSDISABLED
            enabled = False
        return {'label': MENU.HEADERBUTTONS_PERSONALMISSIONS,
         'value': self.TABS.PERSONAL_MISSIONS,
         'tooltip': tooltip,
         'enabled': enabled,
         'subValues': [self.TABS.PERSONAL_MISSIONS_PAGE]}

    def _getHangarMenuItemDataProvider(self):
        tabDataProvider = [{'label': MENU.HEADERBUTTONS_HANGAR,
          'value': self.TABS.HANGAR,
          'textColor': 16764006,
          'textColorOver': 16768409,
          'tooltip': TOOLTIPS.HEADER_BUTTONS_HANGAR},
         {'label': MENU.HEADERBUTTONS_SHOP,
          'value': self.TABS.STORE,
          'tooltip': TOOLTIPS.HEADER_BUTTONS_SHOP},
         {'label': MENU.HEADERBUTTONS_STORAGE,
          'value': self.TABS.STORAGE,
          'tooltip': TOOLTIPS.HEADER_BUTTONS_STORAGE},
         {'label': MENU.HEADERBUTTONS_MISSIONS,
          'value': self.TABS.MISSIONS,
          'tooltip': TOOLTIPS.HEADER_BUTTONS_MISSIONS},
         self._getPersonalMissionSelectorTabData(),
         {'label': MENU.HEADERBUTTONS_PROFILE,
          'value': self.TABS.PROFILE,
          'tooltip': TOOLTIPS.HEADER_BUTTONS_PROFILE}]
        techTreeData = {'label': MENU.HEADERBUTTONS_TECHTREE,
         'value': self.TABS.TECHTREE,
         'tooltip': TOOLTIPS.HEADER_BUTTONS_TECHTREE,
         'isTooltipSpecial': False,
         'subValues': [self.TABS.RESEARCH]}
        if self.techTreeEventsListener.actions:
            techTreeData['tooltip'] = TOOLTIPS_CONSTANTS.TECHTREE_DISCOUNT_INFO
            techTreeData['isTooltipSpecial'] = True
            if self.techTreeEventsListener.getNations(unviewed=True):
                techTreeData['actionIcon'] = backport.image(R.images.gui.maps.icons.library.discountIndicator())
        tabDataProvider.extend([techTreeData])
        tabDataProvider.extend([{'label': MENU.HEADERBUTTONS_BARRACKS,
          'value': self.TABS.BARRACKS,
          'tooltip': TOOLTIPS.HEADER_BUTTONS_BARRACKS}])
        tabDataProvider.append(self._updateStrongholdsSelector())
        override = self.__tutorialLoader.gui.lastHangarMenuButtonsOverride
        if override is not None:
            tabDataProvider[:] = filter(lambda item: item['value'] in override, tabDataProvider)
        return tabDataProvider

    def _updateHangarMenuData(self):
        self.as_setHangarMenuDataS(self._getHangarMenuItemDataProvider())
        self._updateTabCounters()

    def _rebootBattleSelector(self):
        battle_selector_items.clear()
        battle_selector_items.create()

    def __onOverrideHangarMenuButtons(self, _=None):
        self.__hideDisabledTabCounters()
        self._updateHangarMenuData()

    def __onOverrideHeaderMenuButtons(self, _=None):
        menuOverride = self.__tutorialLoader.gui.lastHeaderMenuButtonsOverride
        self.as_setHeaderButtonsS(menuOverride)
        if LobbyHeader.BUTTONS.BATTLE_SELECTOR in menuOverride:
            self._updatePrebattleControls()

    def __onSPAUpdated(self, _):
        self.__updateGoldFishState(False)
        self.__updateSubscriptionState()

    def __onGoldFishWindowClosed(self, _):
        self.__updateGoldFishState(True)

    def __updateGoldFishState(self, isAnimEnabled):
        enabledVal = isGoldFishActionActive()
        tooltip = TOOLTIPS.HEADER_BUTTONS_GOLD_ACTION if enabledVal else TOOLTIPS.HEADER_BUTTONS_GOLD
        self.as_setGoldFishEnabledS(enabledVal, isAnimEnabled, tooltip, TOOLTIP_TYPES.COMPLEX)

    def __updateSubscriptionState(self):
        subscriptionEnabled = isSubscriptionEnabled()
        if subscriptionEnabled != self.__isSubscriptionEnabled:
            self.__isSubscriptionEnabled = subscriptionEnabled
            self.__updateAccountAttrs()

    def __onServerSettingChanged(self, diff):
        legacyModelSelectorEnabledChanged = 'isLegacyModeSelectorEnabled' in diff
        strongholdSettingsChanged = 'strongholdSettings' in diff
        epicRandomStateChanged = 'isEpicRandomEnabled' in diff
        commandBattlesStateChanged = 'isCommandBattleEnabled' in diff
        bootcampStateChanged = 'isBootcampEnabled' in diff
        battleRoyaleStateChanged = constants.Configs.BATTLE_ROYALE_CONFIG.value in diff
        mapsTrainingStateChanged = 'isMapsTrainingEnabled' in diff
        eventBattlesStateChanged = 'event_battles_config' in diff
        renameApiSettingsChanged = 'wgnp' in diff and any((k in diff['wgnp'] for k in ['renameApiEnabled', 'enabled']))
        updateHangarMenuData = any((strongholdSettingsChanged,
         epicRandomStateChanged,
         commandBattlesStateChanged,
         'isRegularQuestEnabled' in diff))
        updatePrebattleControls = any((legacyModelSelectorEnabledChanged,
         strongholdSettingsChanged,
         epicRandomStateChanged,
         commandBattlesStateChanged,
         bootcampStateChanged,
         'isSandboxEnabled' in diff,
         'ranked_config' in diff,
         'epic_config' in diff,
         battleRoyaleStateChanged,
         mapsTrainingStateChanged,
         eventBattlesStateChanged))
        if bootcampStateChanged:
            self._rebootBattleSelector()
        if updateHangarMenuData:
            self._updateHangarMenuData()
        elif 'hallOfFame' in diff:
            self.__updateProfileTabCounter()
        if updatePrebattleControls:
            self._updatePrebattleControls()
        if legacyModelSelectorEnabledChanged:
            self.closeFullscreenBattleSelector()
            self.__closeBattleTypeSelectPopover()
        if renameApiSettingsChanged:
            self.__updateDemoAccountRenamingStatus()

    def __updateProfileTabCounter(self):
        if self.lobbyContext.getServerSettings().isHofEnabled() and not self.uiSpamController.shouldBeHidden(self.TABS.PROFILE):
            hofCounter = getAchievementsTabCounter()
            if hofCounter:
                self.__setCounter(self.TABS.PROFILE, hofCounter)
            else:
                self.__hideCounter(self.TABS.PROFILE)
        else:
            self.__hideCounter(self.TABS.PROFILE)

    def __updateMissionsTabCounter(self):
        counters = AccountSettings.getCounters(NEW_LOBBY_TAB_COUNTER)
        alias = self.TABS.PERSONAL_MISSIONS
        if alias not in counters:
            counters[alias] = True
            AccountSettings.setCounters(NEW_LOBBY_TAB_COUNTER, counters)
        if counters[alias] and not self.uiSpamController.shouldBeHidden(self.TABS.PERSONAL_MISSIONS):
            self.__setCounter(alias, 1)
        else:
            self.__hideCounter(alias)

    def __updateRecruitsTabCounter(self, alias):
        counter = recruit_helper.getNewRecruitsCounter()
        if counter:
            self.__setCounter(alias, counter)
        else:
            self.__hideCounter(alias)

    def __updateShopTabCounter(self):
        if self.uiSpamController.shouldBeHidden(self.TABS.STORE):
            return
        actionCounterAlias, actionCounterValue = self.eventsCache.getLobbyHeaderTabCounter()
        lastActionValue = AccountSettings.getSessionSettings(LAST_SHOP_ACTION_COUNTER_MODIFICATION)
        overridenActionAliases = AccountSettings.getSessionSettings(OVERRIDEN_HEADER_COUNTER_ACTION_ALIASES)
        isActionDisabled = actionCounterAlias in overridenActionAliases
        if actionCounterAlias == self.TABS.STORE and (actionCounterValue != lastActionValue or not isActionDisabled):
            self.__setCounter(self.TABS.STORE, actionCounterValue)
            overridenActionAliases.discard(actionCounterAlias)
            AccountSettings.setSessionSettings(OVERRIDEN_HEADER_COUNTER_ACTION_ALIASES, overridenActionAliases)
        else:
            self.__updateTabCounter(self.TABS.STORE)
        AccountSettings.setSessionSettings(LAST_SHOP_ACTION_COUNTER_MODIFICATION, actionCounterValue)

    def __updateStorageTabCounter(self):
        self.__updateTabCounter(self.TABS.STORAGE, self.storageNovelty.noveltyCount + self.offersNovelty.noveltyCount)

    def __updateStrongholdCounter(self):
        self.__updateTabCounter(self.TABS.STRONGHOLD, self.clanNotificationCtrl.newsCounter)

    def __updateTabCounter(self, alias, counter=None):
        if alias not in self.TABS.ALL():
            return
        elif self.uiSpamController.shouldBeHidden(alias):
            return
        else:
            if alias in self.ACCOUNT_SETTINGS_COUNTERS:
                counters = AccountSettings.getCounters(NEW_LOBBY_TAB_COUNTER)
                if counter is not None:
                    counters[alias] = counter
                    overridenActionAliases = AccountSettings.getSessionSettings(OVERRIDEN_HEADER_COUNTER_ACTION_ALIASES)
                    overridenActionAliases.add(alias)
                    AccountSettings.setSessionSettings(OVERRIDEN_HEADER_COUNTER_ACTION_ALIASES, overridenActionAliases)
                elif alias not in counters or _isActiveShopNewCounters():
                    counter = backport.text(R.strings.menu.headerButtons.defaultCounter())
                    _updateShopNewCounters()
                else:
                    counter = counters[alias]
                AccountSettings.setCounters(NEW_LOBBY_TAB_COUNTER, counters)
            if counter:
                self.__setCounter(alias, counter)
            else:
                self.__hideCounter(alias)
            return

    def __onPingPerformed(self, _):
        self.__updatePing()

    def __onSettingsChanged(self, diff):
        if 'isColorBlind' in diff:
            self.__updatePing()
        if KNOWN_SELECTOR_BATTLES in diff:
            self._updatePrebattleControls()

    def __updatePing(self):
        pingData = g_preDefinedHosts.getHostPingData(self.connectionMgr.url)
        pingStatus = pingData.status
        pingStatus = PING_STATUSES.UNDEFINED if pingStatus == PING_STATUSES.REQUESTED else pingStatus
        self.as_updatePingStatusS(pingStatus, self.settingsCore.getSetting('isColorBlind'))

    def __onCounterChanged(self, event):
        self.__updateTabCounter(event.ctx.get('alias'), event.ctx.get('value'))

    def __setCounter(self, alias, counter=None):
        if not self.__isTabPresent(alias):
            return
        self.__shownCounters.add(alias)
        counter = counter or i18n.makeString(MENU.HEADER_NOTIFICATIONSIGN)
        self.as_setButtonCounterS(alias, text_styles.counterLabelText(counter))

    def __hideCounter(self, alias):
        if alias in self.__shownCounters:
            self.__shownCounters.remove(alias)
            self.as_removeButtonCounterS(alias)

    def __onStatsReceived(self):
        clusterUsers, regionUsers, tooltipType = self.serverStats.getStats()
        if tooltipType == STATS_TYPE.UNAVAILABLE:
            tooltip = TOOLTIPS.HEADER_INFO_PLAYERS_UNAVAILABLE
            clusterUsers = regionUsers = ''
        elif tooltipType == STATS_TYPE.CLUSTER:
            tooltip = TOOLTIPS.HEADER_INFO_PLAYERS_ONLINE_REGION
        else:
            tooltip = TOOLTIPS.HEADER_INFO_PLAYERS_ONLINE_FULL
        clusterStats = makeHtmlString('html_templates:lobby', 'onlineCounter', {'key': self.connectionMgr.serverUserNameShort,
         'delimiter': backport.text(R.strings.common.common.colon()),
         'value': clusterUsers})
        if tooltipType == STATS_TYPE.FULL:
            regionStats = makeHtmlString('html_templates:lobby', 'onlineCounter', {'key': backport.text(R.strings.menu.onlineCounter.total()),
             'delimiter': backport.text(R.strings.common.common.colon()),
             'value': regionUsers})
        else:
            regionStats = ''
        body = i18n.makeString('{}/body'.format(tooltip), servername=self.connectionMgr.serverUserName)
        header = '{}/header'.format(tooltip)
        isAvailable = tooltipType != STATS_TYPE.UNAVAILABLE
        self.as_updateOnlineCounterS(clusterStats, regionStats, makeTooltip(header, body), isAvailable)

    def disableLobbyHeaderControls(self, disable):
        self._isLobbyHeaderControlsDisabled = disable
        self.as_disableFightButtonS(disable)
        for button in self.RANKED_WELCOME_VIEW_DISABLE_CONTROLS:
            self.as_doDisableHeaderButtonS(button, not disable)

        self.__updateNavButtonsState(not disable)

    def __isTabPresent(self, tabID):
        override = self.__tutorialLoader.gui.lastHangarMenuButtonsOverride
        return tabID in override if override is not None else True

    def __isHeaderButtonPresent(self, buttonID):
        override = self.__tutorialLoader.gui.lastHeaderMenuButtonsOverride
        return buttonID in override if override is not None else True

    def __hideDisabledTabCounters(self):
        for tabID in self.__shownCounters.copy():
            if not self.__isTabPresent(tabID):
                self.__hideCounter(tabID)

    def __onAccountSettingsChanging(self, key, _):
        if key == RECRUIT_NOTIFICATIONS:
            self.__updateRecruitsTabCounter(self.TABS.BARRACKS)

    def __removeClanIconFromMemory(self):
        if self.__clanIconID is not None:
            self.removeTextureFromMemory(self.__clanIconID)
            self.__clanIconID = None
        return

    def _cleanupVisitedSettings(self):
        currentDynamicQuests = list(self.eventsCache.getDailyQuests(includeEpic=True).keys())
        questSettings = AccountSettings.getSettings(QUESTS)
        for visitedKey in ['visited', 'naVisited']:
            visitedQuestIds = questSettings[visitedKey]
            questSettings[visitedKey] = tuple((q for q in visitedQuestIds if not isDailyQuest(q) or q in currentDynamicQuests))
            AccountSettings.setSettings(QUESTS, questSettings)

    def __clearMenuVisibiliby(self):
        self.__menuVisibilityHelper.clear()
        self.__menuVisibilityHelper = None
        return

    @adisp_async
    @future_async.wg_async
    def __processMMActiveTestConfirm(self, prbEntity, callback):
        config = self.lobbyContext.getServerSettings().getActiveTestConfirmationConfig()
        toShow = bool(not AccountSettings.getSessionSettings(ACTIVE_TEST_PARTICIPATION_CONFIRMED) and config.get('enabled') and prbEntity.getQueueType() == constants.QUEUE_TYPE.RANDOMS and g_currentVehicle.item.level == 10)
        if not self.connectionMgr.isStandalone():
            toShow = toShow and self.connectionMgr.peripheryID in config.get('peripheryIDs', ())
        if toShow:
            result = yield future_async.wg_await(showActiveTestConfirmDialog(config.get('startTime', 0.0), config.get('finishTime', 0.0), config.get('link', '')))
            if result:
                AccountSettings.setSessionSettings(ACTIVE_TEST_PARTICIPATION_CONFIRMED, True)
            callback(result)
        callback(True)

    def __updateNavButtonsState(self, isEnabled):
        if not isEnabled:
            self.as_doDisableNavigationS()
        else:
            self.as_setScreenS(self.__currentScreen)


class _BoosterInfoPresenter(object):
    __MAX_BOOSTERS_TO_DISPLAY = 99

    def __init__(self, goodiesCache):
        self.__goodiesCache = goodiesCache
        self.__activeBoosters = list(goodiesCache.getBoosters(criteria=REQ_CRITERIA.BOOSTER.ACTIVE).values())
        self.__activeClanReserves = None
        return

    def hasActiveBoosters(self):
        return self.__hasActiveAccountBooster() or self.__hasActiveClanReserves()

    def hasAvailableBoosters(self):
        return self.__getAvailableBoostersCount() > 0

    def getIcon(self):
        if self.__hasActiveAccountBooster() and self.__getActiveClanReserves():
            return backport.image(R.images.gui.maps.icons.boosters.mixedBoosterIcon())
        elif self.__hasActiveAccountBooster():
            return backport.image(R.images.gui.maps.icons.boosters.activeBoosterIcon())
        elif self.__getActiveClanReserves():
            return backport.image(R.images.gui.maps.icons.boosters.clanBoosterIcon())
        else:
            return backport.image(R.images.gui.maps.icons.boosters.availableBoosterIcon()) if self.hasAvailableBoosters() else None

    def getBg(self):
        if self.__getActiveClanReserves() and not self.__hasActiveAccountBooster():
            return backport.image(R.images.gui.maps.icons.boosters.clanBoosterBg())
        else:
            return backport.image(R.images.gui.maps.icons.boosters.activeBoosterBg()) if self.hasActiveBoosters() or self.hasAvailableBoosters() else None

    def getText(self):
        if not self.hasActiveBoosters() and not self.hasAvailableBoosters():
            return None
        else:
            templateKey = 'accountBooster'
            if self.hasActiveBoosters():
                if not self.__hasActiveAccountBooster():
                    templateKey = 'clanBooster'
                allBoosters = chain(self.__activeBoosters, self.__getActiveClanReserves())
                minUsageTime = min((booster.getUsageLeftTime() for booster in allBoosters)) or 0
                message = time_utils.getTillTimeString(minUsageTime, MENU.BOOSTERS_TIMELEFT, removeLeadingZeros=True)
            else:
                boostersAvailable = self.__getAvailableBoostersCount()
                if boostersAvailable <= self.__MAX_BOOSTERS_TO_DISPLAY:
                    message = str(boostersAvailable)
                else:
                    message = str(self.__MAX_BOOSTERS_TO_DISPLAY) + '+'
            return makeHtmlString('html_templates:lobby/header', templateKey, {'message': message})

    def __getAvailableBoostersCount(self):
        readyBoosters = self.__goodiesCache.getBoosters(criteria=REQ_CRITERIA.BOOSTER.IS_READY_TO_ACTIVATE).values()
        return sum((booster.count for booster in readyBoosters))

    def __hasActiveAccountBooster(self):
        return len(self.__activeBoosters) > 0

    def __getActiveClanReserves(self):
        if self.__activeClanReserves is None:
            self.__activeClanReserves = list(self.__goodiesCache.getClanReserves().values())
        return self.__activeClanReserves

    def __hasActiveClanReserves(self):
        return len(self.__getActiveClanReserves()) > 0
