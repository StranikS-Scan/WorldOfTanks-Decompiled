# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/premacc/dashboard/prem_dashboard_header.py
import time
import typing
import logging
import BigWorld
import async as future_async
from async import async, await
from constants import QUEUE_TYPE
from constants import RENEWABLE_SUBSCRIPTION_CONFIG
from frameworks.wulf import ViewSettings, ViewStatus
from gui import GUI_SETTINGS
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.clans.clan_helpers import getStrongholdClanCardUrl
from gui.clans.settings import getClanRoleName
from gui.goodies.goodie_items import MAX_ACTIVE_BOOSTERS_COUNT
from gui.impl.gen.view_models.views.lobby.subscription.subscription_card_model import SubscriptionCardState
from gui.impl.lobby.subscription.wot_plus_tooltip import WotPlusTooltip
from gui.impl import backport
from gui.impl.dialogs import dialogs
from gui.impl.dialogs.gf_builders import ResDialogBuilder
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.premacc.dashboard.prem_dashboard_header_model import PremDashboardHeaderModel
from gui.impl.gen.view_models.views.lobby.premacc.dashboard.prem_dashboard_header_reserve_model import PremDashboardHeaderReserveModel
from gui.impl.gen.view_models.views.lobby.premacc.dashboard.prem_dashboard_header_tooltips import PremDashboardHeaderTooltips
from gui.impl.lobby.account_completion.tooltips.hangar_tooltip_view import HangarTooltipView
from gui.impl.lobby.tooltips.clans import ClanShortInfoTooltipContent
from gui.impl.pub import ViewImpl
from gui.impl.pub.dialog_window import DialogButtons
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.platform.base.statuses.constants import StatusTypes
from gui.platform.wgnp.demo_account.controller import NICKNAME_CONTEXT
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.dispatcher import g_prbLoader
from gui.shared import event_dispatcher
from gui.shared.event_dispatcher import showStrongholds, showSteamAddEmailOverlay, showSteamConfirmEmailOverlay, showDemoAccRenamingOverlay, showWotPlusInfoPage
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IBadgesController, IBoostersController, ISteamCompletionController, IPlatoonController, IExternalLinksController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.platform.wgnp_controllers import IWGNPSteamAccRequestController, IWGNPDemoAccRequestController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.web import IWebController
if typing.TYPE_CHECKING:
    from typing import Optional
    from gui.clans.clan_account_profile import ClanAccountProfile
    from gui.platform.wgnp.steam_account.statuses import SteamAccEmailStatus
    from gui.platform.base.statuses.status import Status
_logger = logging.getLogger(__name__)

class PremDashboardHeader(ViewImpl):
    __slots__ = ('__notConfirmedEmail', '_renewableSub', '__confirmationWindow')
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __webCtrl = dependency.descriptor(IWebController)
    __badgesController = dependency.descriptor(IBadgesController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __goodiesCache = dependency.descriptor(IGoodiesCache)
    __boosters = dependency.descriptor(IBoostersController)
    __externalLinks = dependency.descriptor(IExternalLinksController)
    lobbyContext = dependency.descriptor(ILobbyContext)
    connectionMgr = dependency.descriptor(IConnectionManager)
    platoonCtrl = dependency.descriptor(IPlatoonController)
    wgnpSteamAccCtrl = dependency.descriptor(IWGNPSteamAccRequestController)
    wgnpDemoAccCtrl = dependency.descriptor(IWGNPDemoAccRequestController)
    steamRegistrationCtrl = dependency.descriptor(ISteamCompletionController)
    __MAX_VIEWABLE_CLAN_RESERVES_COUNT = 2
    __TOOLTIPS_MAPPING = {PremDashboardHeaderTooltips.TOOLTIP_PERSONAL_RESERVE: TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO,
     PremDashboardHeaderTooltips.TOOLTIP_CLAN_RESERVE: TOOLTIPS_CONSTANTS.CLAN_RESERVE_INFO}

    def __init__(self):
        settings = ViewSettings(R.views.lobby.premacc.dashboard.prem_dashboard_header.PremDashboardHeader())
        settings.model = PremDashboardHeaderModel()
        super(PremDashboardHeader, self).__init__(settings)
        self.__notConfirmedEmail = ''
        self._renewableSub = BigWorld.player().renewableSubscription
        self.__confirmationWindow = None
        return

    @property
    def viewModel(self):
        return super(PremDashboardHeader, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = self.__getTooltipData(event)
            if tooltipData is None:
                return
            window = backport.BackportTooltipWindow(tooltipData, self.getParentWindow())
            window.load()
            return window
        else:
            return super(PremDashboardHeader, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.tooltips.clans.ClanShortInfoTooltipContent():
            return ClanShortInfoTooltipContent()
        if contentID == R.views.lobby.account_completion.tooltips.HangarTooltip():
            _logger.debug('Show not confirmed email: %s tooltip.', self.__notConfirmedEmail)
            return HangarTooltipView(self.__notConfirmedEmail)
        return WotPlusTooltip() if event.contentID == R.views.lobby.subscription.WotPlusTooltip() else super(PremDashboardHeader, self).createToolTipContent(event=event, contentID=contentID)

    def _initialize(self, *args, **kwargs):
        super(PremDashboardHeader, self)._initialize(*args, **kwargs)
        self.__initListeners()
        self.viewModel.onShowBadges += self.__onShowBadges
        self.viewModel.personalReserves.onUserItemClicked += self.__onPersonalReserveClick
        self.viewModel.clanReserves.onUserItemClicked += self.__onClanReserveClick
        self.viewModel.onEmailButtonClicked += self.__onEmailButtonClicked
        self.viewModel.onRenamingButtonClicked += self.__onRenamingButtonClicked
        self.viewModel.subscriptionCard.onCardClick += self.__onSubscriptionClick
        self.viewModel.subscriptionCard.onInfoButtonClik += self.__onSubscriptionInfoClick
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self._renewableSub.onRenewableSubscriptionDataChanged += self._onWotPlusDataChanged
        with self.viewModel.transaction() as model:
            userNameModel = model.userName
            userNameModel.setUserName(BigWorld.player().name)
            userNameModel.setIsTeamKiller(self.__itemsCache.items.stats.isTeamKiller)
            self.__updateClanInfo(model)
            self.__updateSubscriptionCard(model)
            self.__buildPersonalReservesList(model=model)
            self.__updateBadges(model=model)
            if self.steamRegistrationCtrl.isSteamAccount:
                self.__askEmailStatus()
            else:
                self.__askDemoAccountRenameStatus()

    def _finalize(self):
        super(PremDashboardHeader, self)._finalize()
        self.viewModel.onShowBadges -= self.__onShowBadges
        self.viewModel.personalReserves.onUserItemClicked -= self.__onPersonalReserveClick
        self.viewModel.clanReserves.onUserItemClicked -= self.__onClanReserveClick
        self.viewModel.onEmailButtonClicked -= self.__onEmailButtonClicked
        self.viewModel.onRenamingButtonClicked -= self.__onRenamingButtonClicked
        self.viewModel.subscriptionCard.onCardClick -= self.__onSubscriptionClick
        self.viewModel.subscriptionCard.onInfoButtonClik -= self.__onSubscriptionInfoClick
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        self._renewableSub.onRenewableSubscriptionDataChanged -= self._onWotPlusDataChanged
        if self.__confirmationWindow is not None:
            self.__confirmationWindow.stopWaiting(DialogButtons.CANCEL)
            self.__confirmationWindow = None
        self.__clearListeners()
        return

    def _onWotPlusDataChanged(self, diff):
        with self.viewModel.transaction() as model:
            self.__updateSubscriptionCard(model)

    def __initListeners(self):
        g_clientUpdateManager.addCallbacks({'stats.clanInfo': self.__onClanInfoChanged,
         'goodies': self.__onGoodiesUpdated,
         'cache.activeOrders': self.__onClanInfoChanged})
        g_prbCtrlEvents.onPreQueueJoined += self.__onPreQueueJoined
        self.__badgesController.onUpdated += self.__updateBadges
        self.__boosters.onBoosterChangeNotify += self.__onBoosterChangeNotify
        self.__boosters.onReserveTimerTick += self.__buildClanReservesList
        self.wgnpSteamAccCtrl.statusEvents.subscribe(StatusTypes.CONFIRMED, self.__setEmailConfirmed)
        self.wgnpSteamAccCtrl.statusEvents.subscribe(StatusTypes.ADDED, self.__setEmailActionNeeded)
        self.wgnpSteamAccCtrl.statusEvents.subscribe(StatusTypes.ADD_NEEDED, self.__setEmailActionNeeded)
        demoAccSubscribe = self.wgnpDemoAccCtrl.statusEvents.subscribe
        demoAccSubscribe(StatusTypes.ADD_NEEDED, self.__showDemoAccountRenaming, context=NICKNAME_CONTEXT)
        demoAccSubscribe(StatusTypes.PROCESSING, self.__showDemoAccountRenamingInProcess, context=NICKNAME_CONTEXT)
        demoAccSubscribe(StatusTypes.ADDED, self.__hideDemoAccountRenaming, context=NICKNAME_CONTEXT)
        demoAccSubscribe(StatusTypes.UNDEFINED, self.__hideDemoAccountRenaming, context=NICKNAME_CONTEXT)

    def __clearListeners(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_prbCtrlEvents.onPreQueueJoined -= self.__onPreQueueJoined
        self.__badgesController.onUpdated -= self.__updateBadges
        self.__boosters.onBoosterChangeNotify -= self.__onBoosterChangeNotify
        self.__boosters.onReserveTimerTick -= self.__buildClanReservesList
        self.wgnpSteamAccCtrl.statusEvents.unsubscribe(StatusTypes.CONFIRMED, self.__setEmailConfirmed)
        self.wgnpSteamAccCtrl.statusEvents.unsubscribe(StatusTypes.ADDED, self.__setEmailActionNeeded)
        self.wgnpSteamAccCtrl.statusEvents.unsubscribe(StatusTypes.ADD_NEEDED, self.__setEmailActionNeeded)
        demoAccUnsubscribe = self.wgnpDemoAccCtrl.statusEvents.unsubscribe
        demoAccUnsubscribe(StatusTypes.ADD_NEEDED, self.__showDemoAccountRenaming, context=NICKNAME_CONTEXT)
        demoAccUnsubscribe(StatusTypes.PROCESSING, self.__showDemoAccountRenamingInProcess, context=NICKNAME_CONTEXT)
        demoAccUnsubscribe(StatusTypes.ADDED, self.__hideDemoAccountRenaming, context=NICKNAME_CONTEXT)
        demoAccUnsubscribe(StatusTypes.UNDEFINED, self.__hideDemoAccountRenaming, context=NICKNAME_CONTEXT)

    def __onServerSettingsChange(self, diff):
        if RENEWABLE_SUBSCRIPTION_CONFIG in diff:
            with self.viewModel.transaction() as model:
                self.__updateSubscriptionCard(model)

    def __onClanInfoChanged(self, _):
        self.__updateClanInfo(self.viewModel)

    def __onGoodiesUpdated(self, *_):
        self.__buildPersonalReservesList()
        self.__buildClanReservesList()

    def __onBoosterChangeNotify(self, *_):
        self.__buildPersonalReservesList()

    def __updateSubscriptionCard(self, model):
        isWotPlusEnabled = self.__lobbyContext.getServerSettings().isRenewableSubEnabled()
        isWotPlusNSEnabled = self.__lobbyContext.getServerSettings().isWotPlusNewSubscriptionEnabled()
        hasWotPlusActive = self._renewableSub.isEnabled()
        showSubscriptionCard = isWotPlusEnabled and (hasWotPlusActive or isWotPlusNSEnabled)
        model.setIsSubscriptionEnable(showSubscriptionCard)
        if showSubscriptionCard:
            state = SubscriptionCardState.AVAILABLE
            if hasWotPlusActive:
                state = SubscriptionCardState.ACTIVE
                expirationTime = self._renewableSub.getExpiryTime()
                model.subscriptionCard.setNextCharge(time.strftime('%d.%m', time.localtime(expirationTime)))
            model.subscriptionCard.setState(state)

    def __updateClanInfo(self, model):
        clanProfile = self.__getAccountProfile()
        isInClan = clanProfile.isInClan()
        model.setIsInClan(isInClan)
        if isInClan:
            clanInfoModel = model.clanInfo
            clanAbbrev = clanProfile.getClanAbbrev()
            model.userName.setClanAbbrev(clanAbbrev)
            clanInfoModel.setClanAbbrev(clanAbbrev)
            clanInfoModel.setRoleInClan(getClanRoleName(clanProfile.getRole()) or '')
            self.__buildClanReservesList(model=model)

    @replaceNoneKwargsModel
    def __buildPersonalReservesList(self, _=None, model=None):
        listModel = model.personalReserves
        listModel.clearItems()
        activeBoosters = self.__goodiesCache.getBoosters(criteria=REQ_CRITERIA.BOOSTER.ACTIVE)
        activeBoostersList = sorted(activeBoosters.values(), key=lambda b: b.getUsageLeftTime(), reverse=True)
        for idx in range(MAX_ACTIVE_BOOSTERS_COUNT):
            itemModel = self.__makeReserveModel(activeBoostersList, idx)
            listModel.addViewModel(itemModel)

        listModel.invalidate()

    @replaceNoneKwargsModel
    def __buildClanReservesList(self, _=None, model=None):
        clanProfile = self.__getAccountProfile()
        mayActivate = clanProfile.getMyClanPermissions().canActivateReserves()
        activeReserves = sorted(self.__goodiesCache.getClanReserves().values(), key=lambda r: r.finishTime)
        showSection = mayActivate or activeReserves
        model.setHasClanReserves(bool(showSection))
        if showSection:
            listModel = model.clanReserves
            listItems = listModel.getItems()
            if listItems:
                listItems.clear()
            if mayActivate:
                slotsCount = self.__MAX_VIEWABLE_CLAN_RESERVES_COUNT
            else:
                slotsCount = min(len(activeReserves), self.__MAX_VIEWABLE_CLAN_RESERVES_COUNT)
            for idx in range(slotsCount):
                itemModel = self.__makeReserveModel(activeReserves, idx)
                listModel.addViewModel(itemModel)

            listModel.invalidate()

    def __getAccountProfile(self):
        return self.__webCtrl.getAccountProfile()

    def __getTooltipData(self, event):
        tooltipType = event.getArgument('tooltipType')
        tooltipAlias = self.__TOOLTIPS_MAPPING.get(tooltipType)
        if tooltipAlias:
            reserveId = event.getArgument('id')
            return backport.createTooltipData(isSpecial=True, specialAlias=tooltipAlias, specialArgs=(reserveId,))

    @replaceNoneKwargsModel
    def __updateBadges(self, model=None):
        prefixBadge = self.__badgesController.getPrefix()
        self.__setBadge(model.setPrefixBadgeId, prefixBadge)
        self.__setBadge(model.setSuffixBadgeId, self.__badgesController.getSuffix())
        if prefixBadge is not None:
            model.setIsDynamicBadge(prefixBadge.hasDynamicContent())
            model.setBadgeContent(prefixBadge.getDynamicContent() or '')
        else:
            model.setIsDynamicBadge(False)
            model.setBadgeContent('')
        return

    @replaceNoneKwargsModel
    def __setEmailConfirmed(self, status=None, model=None):
        model.setEmailButtonLabel(R.invalid())
        model.setIsWarningIconVisible(False)
        model.setShowEmailActionTooltip(False)
        self.__notConfirmedEmail = ''
        _logger.debug('User email confirmed.')

    @replaceNoneKwargsModel
    def __setEmailActionNeeded(self, status=None, model=None):
        model.setIsWarningIconVisible(True)
        model.setShowEmailActionTooltip(True)
        notConfirmedEmail = status.email if status else ''
        if notConfirmedEmail:
            model.setEmailButtonLabel(R.strings.badge.badgesPage.accountCompletion.button.confirmEmail())
        else:
            model.setEmailButtonLabel(R.strings.badge.badgesPage.accountCompletion.button.provideEmail())
        self.__notConfirmedEmail = notConfirmedEmail
        _logger.debug('User email: %s action needed.', notConfirmedEmail)

    @async
    def __askEmailStatus(self):
        if not self.steamRegistrationCtrl.isSteamAccount:
            _logger.debug('Account completion disabled.')
            return
        _logger.debug('Sending email status request.')
        status = yield await(self.wgnpSteamAccCtrl.getEmailStatus())
        if status.isUndefined or self.__isDestroyed:
            _logger.warning('Can not get account email status.')
            return
        if status.typeIs(StatusTypes.ADD_NEEDED):
            self.__setEmailActionNeeded()
        elif status.typeIs(StatusTypes.ADDED):
            self.__setEmailActionNeeded(status=status)
        else:
            self.__setEmailConfirmed()

    def __onEmailButtonClicked(self):
        label = self.viewModel.getEmailButtonLabel()
        if label == R.strings.badge.badgesPage.accountCompletion.button.confirmEmail():
            _logger.debug('Show email confirmation overlay with email=%s.', self.__notConfirmedEmail)
            showSteamConfirmEmailOverlay(email=self.__notConfirmedEmail)
        elif label == R.strings.badge.badgesPage.accountCompletion.button.provideEmail():
            _logger.debug('Show add email overlay.')
            showSteamAddEmailOverlay()
        else:
            _logger.warning('Unknown email button label: %s. Action skipped.', label)

    def __onRenamingButtonClicked(self):
        _logger.debug('Show demo account renaming overlay.')
        if self.platoonCtrl.isInPlatoon():
            self.__showLeaveSquadForRenamingDialog()
        else:
            showDemoAccRenamingOverlay()

    @future_async.async
    def __askDemoAccountRenameStatus(self):
        if not self.wgnpDemoAccCtrl.settings.isRenameApiEnabled():
            return
        status = yield future_async.await(self.wgnpDemoAccCtrl.getNicknameStatus())
        if status.isUndefined or self.__isDestroyed:
            return
        if status.typeIs(StatusTypes.ADD_NEEDED):
            self.__showDemoAccountRenaming()
        elif status.typeIs(StatusTypes.PROCESSING):
            self.__showDemoAccountRenamingInProcess()

    @replaceNoneKwargsModel
    def __showDemoAccountRenaming(self, status=None, model=None):
        model.setIsRenamingButtonVisible(True)
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            queueType = dispatcher.getEntity().getQueueType()
            self.__updateRenameButtonStatus(queueType)
        _logger.debug('Demo account renaming needed.')
        return

    @replaceNoneKwargsModel
    def __showDemoAccountRenamingInProcess(self, status=None, model=None):
        model.setIsWarningIconVisible(True)
        model.setIsRenamingButtonVisible(False)
        model.setIsRenamingProcessVisible(True)
        _logger.debug('Demo account renaming in process.')

    @replaceNoneKwargsModel
    def __hideDemoAccountRenaming(self, status=None, model=None):
        model.setIsWarningIconVisible(False)
        model.setIsRenamingButtonVisible(False)
        model.setIsRenamingProcessVisible(False)
        _logger.debug('Hide demo account renaming.')

    @replaceNoneKwargsModel
    def __updateRenameButtonStatus(self, queueType, model=None):
        isEnabled = queueType == QUEUE_TYPE.RANDOMS
        model.setIsRenamingButtonEnabled(isEnabled)

    def __onPreQueueJoined(self, queueType):
        self.__updateRenameButtonStatus(queueType)

    @future_async.async
    def __showLeaveSquadForRenamingDialog(self):
        builder = ResDialogBuilder()
        builder.setMessagesAndButtons(R.strings.dialogs.accountCompletion.leaveSquad)
        self.__confirmationWindow = builder.build()
        result = yield future_async.await(dialogs.show(self.__confirmationWindow))
        self.__confirmationWindow = None
        if result.result == DialogButtons.SUBMIT:
            self.platoonCtrl.leavePlatoon(ignoreConfirmation=True)
            showDemoAccRenamingOverlay()
        return

    @property
    def __isDestroyed(self):
        destroyed = self.viewStatus in (ViewStatus.DESTROYED, ViewStatus.DESTROYING)
        return destroyed or self.viewModel is None

    @staticmethod
    def __setBadge(setter, badge):
        setter(badge.getIconPostfix() if badge is not None and badge.isSelected else '')
        return

    @staticmethod
    def __onShowBadges():
        event_dispatcher.showBadges(backViewName=backport.text(R.strings.badge.badgesPage.header.backBtn.descrLabel()))

    @staticmethod
    def __onPersonalReserveClick(_):
        event_dispatcher.showStorage(defaultSection=STORAGE_CONSTANTS.PERSONAL_RESERVES)

    @staticmethod
    def __onClanReserveClick(_):
        showStrongholds(getStrongholdClanCardUrl())

    @staticmethod
    def __makeReserveModel(reserves, idx):
        itemModel = PremDashboardHeaderReserveModel()
        if idx < len(reserves):
            booster = reserves[idx]
            itemModel.setId(booster.boosterID)
            itemModel.setProgress(booster.getCooldownAsPercent())
            itemModel.setTimeleft(booster.getUsageLeftTime())
            itemModel.setIconId(booster.boosterGuiType)
        return itemModel

    def __onSubscriptionClick(self):
        url = GUI_SETTINGS.wotPlusManageSubscriptionUrl
        self.__externalLinks.open(url)

    def __onSubscriptionInfoClick(self):
        showWotPlusInfoPage()
