# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/page/user_account_presenter.py
from __future__ import absolute_import
import typing
import BigWorld
from adisp import adisp_process
import constants
from PlayerEvents import g_playerEvents
from constants import PREMIUM_TYPE
from frameworks.wulf import ViewFlags
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getWotPlusShopUrl, getBuyPremiumUrl
from gui.clans.clan_cache import g_clanCache
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.page.header.premium_account_subscription_model import PremiumTypeEnum, PremiumStateEnum
from gui.impl.gen.view_models.views.lobby.page.header.subscriptions_model import SubscriptionsModel
from gui.impl.gen.view_models.views.lobby.page.header.user_account_model import UserAccountModel
from gui.impl.gen.view_models.views.lobby.page.header.user_info_model import SteamEmailStatusEnum
from gui.impl.gen.view_models.views.lobby.page.header.wot_plus_subscription_bonus_model import WotPlusSubscriptionBonusModel
from gui.impl.gen.view_models.views.lobby.page.header.wot_plus_subscription_model import WotPlusStateEnum, WotPlusTypeEnum, WotPlusPeriodicityEnum
from gui.impl.pub.view_component import ViewComponent
from gui.platform.base.statuses.constants import StatusTypes
from gui.server_events.bonuses_wot_plus import getAvailableCoreBonuses, getUniqueAvailableProBonuses
from gui.shared.event_dispatcher import showDashboardView, showSubscriptionsPage, showShop, closeViewsWithFlags
from gui.shared.missions.packers.bonus import getDefaultBonusPacker
from helpers import dependency, isPlayerAccount
from renewable_subscription_common.schema import renewableSubscriptionsConfigSchema
from renewable_subscription_common.settings_constants import WotPlusState, WotPlusTier
from renewable_subscription_common.settings_helpers import SubscriptionSettingsStorage
from skeletons.gui.game_control import IBadgesController, IWotPlusController, IGameSessionController, ISteamCompletionController, IAnonymizerController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.platform.wgnp_controllers import IWGNPSteamAccRequestController
from skeletons.gui.shared import IItemsCache
from uilogging.wot_plus.loggers import WotPlusHeaderLogger
from wg_async import wg_await, wg_async
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
    from gui.impl.gen.view_models.views.lobby.page.header.user_info_model import UserInfoModel
    from gui.platform.wgnp.steam_account.statuses import SteamAccEmailStatus
    from gui.impl.gen.view_models.views.lobby.page.header.wot_plus_subscription_model import WotPlusSubscriptionModel
    from typing import List, Callable
    from gui.server_events.bonuses import WoTPlusBonus
_STATUS_TYPES_MAP = {StatusTypes.UNDEFINED: SteamEmailStatusEnum.UNDEFINED,
 StatusTypes.ADD_NEEDED: SteamEmailStatusEnum.ADD_NEEDED,
 StatusTypes.ADDED: SteamEmailStatusEnum.ADDED,
 StatusTypes.CONFIRMATION_SENT: SteamEmailStatusEnum.CONFIRMATION_SENT,
 StatusTypes.CONFIRMED: SteamEmailStatusEnum.CONFIRMED,
 StatusTypes.PROCESSING: SteamEmailStatusEnum.PROCESSING}
_WOT_PLUS_TIER_MAP = {WotPlusTier.NONE: WotPlusTypeEnum.NONE,
 WotPlusTier.CORE: WotPlusTypeEnum.CORE,
 WotPlusTier.PRO: WotPlusTypeEnum.PRO}
_WOT_PLUS_STATES_MAP = {WotPlusState.INACTIVE: WotPlusStateEnum.INACTIVE,
 WotPlusState.ACTIVE: WotPlusStateEnum.ACTIVE,
 WotPlusState.CANCELLED: WotPlusStateEnum.CANCELLED}
_PREMIUM_TYPE_MAP = {PREMIUM_TYPE.NONE: PremiumTypeEnum.NONE,
 PREMIUM_TYPE.BASIC: PremiumTypeEnum.BASIC,
 PREMIUM_TYPE.PLUS: PremiumTypeEnum.PLUS,
 PREMIUM_TYPE.VIP: PremiumTypeEnum.VIP}

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

    def _getEvents(self):
        return ((self.viewModel.onOpenAccountDashboard, self.__onOpenAccountDashboard),
         (self.viewModel.subscriptions.onOpenPremium, self.__onOpenPremium),
         (self.viewModel.subscriptions.onOpenWotPlus, self.__onOpenWotPlus),
         (self.__badgesController.onUpdated, self.__updateBadgeInfo),
         (self.__gameSession.onPremiumTypeChanged, self.__onPremiumChanged),
         (self.__gameSession.onPremiumNotify, self.__onPremiumChanged),
         (self.__wotPlusCtrl.onDataChanged, self.__onWotPlusStatusChanged),
         (self.__anonymizerController.onStateChanged, self.__updateAnonymizedState),
         (g_playerEvents.onConfigModelUpdated, self._onConfigModelUpdated))

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
        self.__setBadge(self.viewModel.userInfo.setBadgeID, self.__badgesController.getPrefix())
        self.__setBadge(self.viewModel.userInfo.setSuffixBadgeID, self.__badgesController.getSuffix())

    @staticmethod
    def __setBadge(setter, badge):
        setter(badge.badgeID if badge is not None and badge.isSelected else 0)
        return

    def __updatePremiumInfo(self):
        accountStats = self.__itemsCache.items.stats
        with self.viewModel.subscriptions.premiumAccount.transaction() as model:
            model.setState(PremiumStateEnum.ACTIVE if accountStats.isPremium else PremiumStateEnum.INACTIVE)
            model.setType(_PREMIUM_TYPE_MAP[accountStats.activePremiumType])
            model.setExpiryTime(accountStats.activePremiumExpiryTime)

    def __updateWotPlusInfo(self):
        hasSteamAccount = self.__steamRegistrationCtrl.isSteamAccount
        with self.viewModel.subscriptions.wotPlus.transaction() as model:
            model.setType(_WOT_PLUS_TIER_MAP[self.__wotPlusCtrl.getTier()])
            model.setState(_WOT_PLUS_STATES_MAP[self.__wotPlusCtrl.getState()])
            model.setPeriodicity(self.__wotPlusCtrl.getBillingPeriod() or WotPlusPeriodicityEnum.P6MONTHS)
            model.setExpiryTime(self.__wotPlusCtrl.getExpiryTime())
            model.setIsWotPlusEnabled(self.__wotPlusCtrl.isWotPlusVisible())
            self.__setModelBenefits(getAvailableCoreBonuses, model.getBenefits)
            self.__setModelBenefits(getUniqueAvailableProBonuses, model.getProBenefits)
        with self.viewModel.subscriptions.transaction() as model:
            model.setIsSteamPlatform(hasSteamAccount)
            model.setIsCnRealm(constants.IS_CHINA)

    def __setModelBenefits(self, getEnabledBonuses, getBenefits):
        self.__setModelBenefitsList(getEnabledBonuses(self.__wotPlusCtrl.getSettingsStorage()), getBenefits())

    def __setModelBenefitsList(self, enabledBonuses, benefitsList):
        benefitsList.clear()
        benefitsList.reserve(len(enabledBonuses))
        bonusPacker = getDefaultBonusPacker()
        for bonus in enabledBonuses:
            with WotPlusSubscriptionBonusModel() as wotPlusSubBonus:
                packedBonus = bonusPacker.pack(bonus)[0]
                wotPlusSubBonus.setLabel(packedBonus.getLabel())
                wotPlusSubBonus.setType(packedBonus.getName())
                benefitsList.addViewModel(wotPlusSubBonus)

        benefitsList.invalidate()

    def __onWotPlusStatusChanged(self, _):
        self.__updateWotPlusInfo()

    def __onPremiumChanged(self, *_):
        self.__updatePremiumInfo()

    def _onConfigModelUpdated(self, gpKey):
        if renewableSubscriptionsConfigSchema.gpKey == gpKey:
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
        self.__wotPlusUILogger.logClickEvent(wotPlusState)
        if constants.IS_CHINA or self.__steamRegistrationCtrl.isSteamAccount:
            if not self.__wotPlusCtrl.hasSubscription():
                showShop(getWotPlusShopUrl())
                return
        closeViewsWithFlags([R.views.lobby.player_subscriptions.PlayerSubscriptions()], [ViewFlags.LOBBY_TOP_SUB_VIEW])
        views = self.gui.windowsManager.findViews(lambda view: view.layoutID == R.views.lobby.player_subscriptions.PlayerSubscriptions())
        if not views:
            self.__onOpenAccountDashboard()
            showSubscriptionsPage()

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
