# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/page/user_account_presenter.py
from __future__ import absolute_import
import BigWorld
import typing
import constants
from adisp import adisp_process
from frameworks.wulf import ViewFlags
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getWotPlusShopUrl, getBuyPremiumUrl
from gui.clans.clan_cache import g_clanCache
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.page.header.user_account_model import UserAccountModel
from gui.impl.gen.view_models.views.lobby.page.header.user_info_model import SteamEmailStatusEnum
from gui.impl.lobby.subscription.wot_plus_tooltip import WotPlusTooltip
from gui.impl.pub.view_component import ViewComponent
from gui.platform.base.statuses.constants import StatusTypes
from gui.shared.event_dispatcher import showDashboardView, showSubscriptionsPage, showShop, closeViewsWithFlags
from helpers import dependency, isPlayerAccount
from skeletons.gui.game_control import IBadgesController, IWotPlusController, IGameSessionController, ISteamCompletionController, IAnonymizerController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.platform.wgnp_controllers import IWGNPSteamAccRequestController
from skeletons.gui.shared import IItemsCache
from uilogging.wot_plus.loggers import WotPlusHeaderLogger
from wg_async import wg_await, wg_async
if typing.TYPE_CHECKING:
    from frameworks.wulf import View, ViewEvent
    from gui.impl.gen.view_models.views.lobby.page.header.subscriptions_model import SubscriptionsModel
    from gui.impl.gen.view_models.views.lobby.page.header.user_info_model import UserInfoModel
    from gui.platform.wgnp.steam_account.statuses import SteamAccEmailStatus
_STATUS_TYPES_MAP = {StatusTypes.UNDEFINED: SteamEmailStatusEnum.UNDEFINED,
 StatusTypes.ADD_NEEDED: SteamEmailStatusEnum.ADD_NEEDED,
 StatusTypes.ADDED: SteamEmailStatusEnum.ADDED,
 StatusTypes.CONFIRMATION_SENT: SteamEmailStatusEnum.CONFIRMATION_SENT,
 StatusTypes.CONFIRMED: SteamEmailStatusEnum.CONFIRMED,
 StatusTypes.PROCESSING: SteamEmailStatusEnum.PROCESSING}

class UserAccountPresenter(ViewComponent[UserAccountModel]):
    __itemsCache = dependency.descriptor(IItemsCache)
    __badgesController = dependency.descriptor(IBadgesController)
    __gameSession = dependency.descriptor(IGameSessionController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __wotPlusCtrl = dependency.descriptor(IWotPlusController)
    __steamRegistrationCtrl = dependency.descriptor(ISteamCompletionController)
    __wgnpSteamAccCtrl = dependency.descriptor(IWGNPSteamAccRequestController)
    __anonymizerController = dependency.descriptor(IAnonymizerController)

    def __init__(self):
        super(UserAccountPresenter, self).__init__(model=UserAccountModel)
        self.__wotPlusUILogger = None
        return

    @property
    def viewModel(self):
        return super(UserAccountPresenter, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return WotPlusTooltip() if contentID == R.views.lobby.subscription.WotPlusTooltip() else super(UserAccountPresenter, self).createToolTipContent(event, contentID)

    def _getEvents(self):
        return ((self.viewModel.onOpenAccountDashboard, self.__onOpenAccountDashboard),
         (self.viewModel.subscriptions.onOpenPremium, self.__onOpenPremium),
         (self.viewModel.subscriptions.onOpenWotPlus, self.__onOpenWotPlus),
         (self.__badgesController.onUpdated, self.__updateBadgeInfo),
         (self.__gameSession.onPremiumTypeChanged, self.__onPremiumChanged),
         (self.__gameSession.onPremiumNotify, self.__onPremiumChanged),
         (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChange),
         (self.__wotPlusCtrl.onDataChanged, self.__onWotPlusStatusChanged),
         (self.__anonymizerController.onStateChanged, self.__updateAnonymizedState))

    def _subscribe(self):
        super(UserAccountPresenter, self)._subscribe()
        self.__wgnpSteamAccCtrl.statusEvents.subscribe(StatusTypes.CONFIRMED, self.__updateSteamEmailStatus)
        self.__wgnpSteamAccCtrl.statusEvents.subscribe(StatusTypes.ADDED, self.__updateSteamEmailStatus)
        self.__wgnpSteamAccCtrl.statusEvents.subscribe(StatusTypes.ADD_NEEDED, self.__updateSteamEmailStatus)

    def _unsubscribe(self):
        super(UserAccountPresenter, self)._unsubscribe()
        self.__wgnpSteamAccCtrl.statusEvents.unsubscribe(StatusTypes.CONFIRMED, self.__updateSteamEmailStatus)
        self.__wgnpSteamAccCtrl.statusEvents.unsubscribe(StatusTypes.ADDED, self.__updateSteamEmailStatus)
        self.__wgnpSteamAccCtrl.statusEvents.unsubscribe(StatusTypes.ADD_NEEDED, self.__updateSteamEmailStatus)

    def _getCallbacks(self):
        return (('stats.clanInfo', self.__updateClanInfo), ('cache.activeOrders', self.__updateClanInfo), ('account.activePremiumExpiryTime', self.__onPremiumChanged))

    def _onLoading(self, *args, **kwargs):
        super(UserAccountPresenter, self)._onLoading(*args, **kwargs)
        self.__wotPlusUILogger = WotPlusHeaderLogger()
        self.__onUserInfoUpdate()
        self.__updateWotPlusInfo()
        self.__updatePremiumInfo()

    def _finalize(self):
        self.__wotPlusUILogger = None
        super(UserAccountPresenter, self)._finalize()
        return

    def __updateClanInfo(self, _=None):
        clanInfo = g_clanCache.clanInfo
        if clanInfo and len(clanInfo) > 1:
            isInClan = g_clanCache.isInClan
            clanRole = constants.CLAN_ROLES.getRole(g_clanCache.clanRole)
            clanAbbrev = clanInfo[1]
        else:
            isInClan = False
            clanRole = ''
            clanAbbrev = None
        with self.viewModel.userInfo.transaction() as model:
            model.setIsInClan(isInClan)
            model.setRoleInClan(clanRole)
            model.setClanAbbrev(clanAbbrev)
        return

    @wg_async
    def __updateUserInfo(self):
        player = BigWorld.player()
        if player is None or not isPlayerAccount():
            nickname = 'player.name'
        else:
            nickname = player.name
        with self.viewModel.userInfo.transaction() as model:
            model.setUserName(nickname)
            model.setAnonymized(self.__anonymizerController.isAnonymized)
            hasSteamAccount = self.__steamRegistrationCtrl.isSteamAccount
            model.setHasSteamAccount(hasSteamAccount)
            if hasSteamAccount:
                steamEmailStatus = yield wg_await(self.__wgnpSteamAccCtrl.getEmailStatus())
                model.setSteamEmailStatus(_STATUS_TYPES_MAP[steamEmailStatus.type])
                model.setEmail(steamEmailStatus.email)
            model.setTeamKiller(self.__itemsCache.items.stats.isTeamKiller)
        return

    def __updateBadgeInfo(self, _=None):
        badge = self.__badgesController.getPrefix()
        selected = badge is not None
        self.viewModel.userInfo.setBadgeID(badge.badgeID if selected else 0)
        return

    def __updatePremiumInfo(self):
        accountStats = self.__itemsCache.items.stats
        with self.viewModel.subscriptions.transaction() as model:
            model.setPremiumSubscriptionEnabled(accountStats.isPremium)
            model.setActivePremiumType(accountStats.activePremiumType)
            model.setActivePremiumExpiryTime(accountStats.activePremiumExpiryTime)

    def __updateWotPlusInfo(self):
        with self.viewModel.subscriptions.transaction() as model:
            model.setWotPlusEnabled(self.__wotPlusCtrl.isEnabled())
            model.setWotPlusState(self.__wotPlusCtrl.getState().value)
            model.setWotPlusExpiryTime(self.__wotPlusCtrl.getExpiryTime())

    def __onWotPlusStatusChanged(self, _):
        self.__updateWotPlusInfo()

    def __onPremiumChanged(self, *_):
        self.__updatePremiumInfo()

    def __onServerSettingsChange(self, diff):
        if constants.RENEWABLE_SUBSCRIPTION_CONFIG in diff:
            self.__updateWotPlusInfo()
            self.__updatePremiumInfo()

    def __onUserInfoUpdate(self):
        self.__updateUserInfo()
        self.__updateBadgeInfo()
        self.__updateClanInfo()

    @adisp_process
    def __onOpenAccountDashboard(self):
        navigationPossible = yield self.__lobbyContext.isHeaderNavigationPossible()
        if navigationPossible:
            showDashboardView()

    @adisp_process
    def __onOpenPremium(self):
        navigationPossible = yield self.__lobbyContext.isHeaderNavigationPossible()
        if navigationPossible:
            showShop(getBuyPremiumUrl())

    def __onOpenWotPlus(self):
        wotPlusState = self.__wotPlusCtrl.getState()
        wotPlusEnabled = self.__wotPlusCtrl.isEnabled()
        self.__wotPlusUILogger.logClickEvent(wotPlusState)
        if wotPlusEnabled:
            closeViewsWithFlags([R.views.lobby.player_subscriptions.PlayerSubscriptions()], [ViewFlags.LOBBY_TOP_SUB_VIEW])
            views = self.gui.windowsManager.findViews(lambda view: view.layoutID == R.views.lobby.player_subscriptions.PlayerSubscriptions())
            if not views:
                self.__onOpenAccountDashboard()
                showSubscriptionsPage()
            return
        showShop(getWotPlusShopUrl())

    def __updateAnonymizedState(self, **_):
        self.viewModel.userInfo.setAnonymized(self.__anonymizerController.isAnonymized)

    def __updateSteamEmailStatus(self, status=None):
        with self.viewModel.userInfo.transaction() as model:
            if status is not None:
                model.setSteamEmailStatus(_STATUS_TYPES_MAP[status.type])
                model.setEmail(status.email)
            else:
                model.setSteamEmailStatus(_STATUS_TYPES_MAP[StatusTypes.UNDEFINED])
                model.setEmail('')
        return
