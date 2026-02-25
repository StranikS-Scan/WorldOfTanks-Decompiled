# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/player_subscriptions/player_subscriptions_view.py
from __future__ import absolute_import
import logging
import typing
from frameworks.wulf import ViewFlags, ViewSettings
from gui import GUI_SETTINGS
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getWotPlusShopUrl, getWotPlusProShopUrl
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.player_subscriptions.external_subscription_model import ExternalSubscriptionModel
from gui.impl.gen.view_models.views.lobby.player_subscriptions.player_subscriptions_model import PlayerSubscriptionsModel
from gui.impl.gen.view_models.views.lobby.player_subscriptions.subscription_model import SubscriptionTypeEnum
from gui.impl.gen.view_models.views.lobby.player_subscriptions.wot_subscription_model import WotPlusPeriodicityEnum
from gui.impl.gen.view_models.views.lobby.player_subscriptions.wot_subscription_model import WotSubscriptionModel
from gui.impl.pub import ViewImpl
from gui.platform.base.statuses.constants import StatusTypes
from gui.platform.products_fetcher.fetch_result import FetchResult
from gui.platform.products_fetcher.subscriptions.subscription_descriptors import WotPlusDescriptor
from gui.shared.event_dispatcher import showOfferGiftsWindow, showBrowserOverlayView, showShop, showWotPlusInfoPage, showWotPlusProductPage, showWotPlusSteamSubscriptionManagementPage
from helpers import dependency
from renewable_subscription_common.settings_constants import RS_TIER, WotPlusTier
from skeletons.gui.game_control import IExternalLinksController, ISteamCompletionController, IWotPlusController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.platform.product_fetch_controller import ISubscriptionProductsFetchController
from skeletons.gui.platform.wgnp_controllers import IWGNPSteamAccRequestController
from uilogging.wot_plus.loggers import WotPlusSubscriptionViewLogger
from uilogging.wot_plus.logging_constants import WotPlusInfoPageSource, SubscriptionPageKeys
from wg_async import wg_await, wg_async
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from typing import Optional, Dict, Any, List, Union
    from gui.game_control.wot_plus_controller import WotPlusController
    from gui.platform.products_fetcher.subscriptions.subscription_descriptors import SubscriptionDescriptor
    from gui.platform.wgnp.steam_account.statuses import SteamAccEmailStatus
    from gui.platform.products_fetcher import SubscriptionProductsFetchController
    from gui.impl.gen.view_models.views.lobby.player_subscriptions.subscription_model import SubscriptionModel
    from gui.platform.products_fetcher.subscriptions.subscription_descriptors import WotPlusProDescriptor

class BaseSubscriptionModelFactory(object):

    def type(self):
        raise NotImplementedError

    def fill(self, subscriptionDescr):
        model = self.type()()
        model.setSubscriptionType(subscriptionDescr.type)
        model.setId(subscriptionDescr.productID)
        model.setName(subscriptionDescr.name)
        model.setDescription(subscriptionDescr.description)
        model.setImageUriLarge(subscriptionDescr.largeImageURL)
        model.setImageUriMedium(subscriptionDescr.mediumImageURL)
        model.setImageUriSmall(subscriptionDescr.smallImageURL)
        model.setRefreshTime(subscriptionDescr.expirationTime)
        return model


class ExternalSubscriptionModelFactory(BaseSubscriptionModelFactory):

    def type(self):
        return ExternalSubscriptionModel

    def fill(self, subscriptionDescr):
        model = super(ExternalSubscriptionModelFactory, self).fill(subscriptionDescr)
        model.setHas3rdPartyRewardsToClaim(not subscriptionDescr.isRewardsClaimed())
        model.setHasDepotRewardsToClaim(subscriptionDescr.hasDepotRewards())
        return model


class WotPlusCoreSubscriptionModelFactory(BaseSubscriptionModelFactory):

    def type(self):
        return WotSubscriptionModel

    def fill(self, subscriptionDescr):
        model = super(WotPlusCoreSubscriptionModelFactory, self).fill(subscriptionDescr)
        model.setWotSubscriptionState(subscriptionDescr.state)
        model.setWotTier(subscriptionDescr.tierForUi)
        return model


class WotPlusProSubscriptionModelFactory(WotPlusCoreSubscriptionModelFactory):
    _wotPlusCtrl = dependency.descriptor(IWotPlusController)

    def fill(self, subscriptionDescr):
        model = super(WotPlusProSubscriptionModelFactory, self).fill(subscriptionDescr)
        model.setSubscriptionPeriodicity(self._wotPlusCtrl.getBillingPeriod() or WotPlusPeriodicityEnum.P6MONTHS)
        return model


def _isWotPlus(subscriptionType):
    return subscriptionType in (SubscriptionTypeEnum.WOTSUBSCRIPTION, SubscriptionTypeEnum.WOTPROSUBSCRIPTION)


_SUBSCRIPTION_TYPE_FACTORIES = {SubscriptionTypeEnum.EXTERNALSUBSCRIPTION: ExternalSubscriptionModelFactory(),
 SubscriptionTypeEnum.WOTSUBSCRIPTION: WotPlusCoreSubscriptionModelFactory(),
 SubscriptionTypeEnum.WOTPROSUBSCRIPTION: WotPlusProSubscriptionModelFactory()}

class PlayerSubscriptionsView(ViewImpl):
    _subscriptionProductsFetchController = dependency.descriptor(ISubscriptionProductsFetchController)
    _externalBrowser = dependency.descriptor(IExternalLinksController)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _wgnpSteamAccCtrl = dependency.descriptor(IWGNPSteamAccRequestController)
    _steamCompletionCtrl = dependency.descriptor(ISteamCompletionController)
    _wotPlusCtrl = dependency.descriptor(IWotPlusController)
    __slots__ = ('__subscriptionsFetchResult', '__incompleteSteamAccount', '__subscriptions', '_wotPlusUILogger')

    def __init__(self, layoutID=R.views.lobby.player_subscriptions.PlayerSubscriptions()):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = PlayerSubscriptionsModel()
        self.__subscriptionsFetchResult = None
        self.__subscriptions = {}
        self.__incompleteSteamAccount = False
        self._wotPlusUILogger = WotPlusSubscriptionViewLogger()
        super(PlayerSubscriptionsView, self).__init__(settings)
        return

    def _initialize(self, *args, **kwargs):
        super(PlayerSubscriptionsView, self)._initialize(*args, **kwargs)
        self._wotPlusCtrl.onDataChanged += self.__onWotPlusStatusChanged
        self._wotPlusUILogger.onViewInitialize()

    def _finalize(self):
        self._wotPlusCtrl.onDataChanged -= self.__onWotPlusStatusChanged
        self._wotPlusUILogger.onViewFinalize()
        super(PlayerSubscriptionsView, self)._finalize()

    @wg_async
    def __fetchExternalSubs(self):
        try:
            self.__incompleteSteamAccount = False
            fetchResult = FetchResult()
            if self._steamCompletionCtrl.isSteamAccount:
                status = yield wg_await(self._wgnpSteamAccCtrl.getEmailStatus('loadingData'))
                if not status.typeIs(StatusTypes.CONFIRMED):
                    self.__incompleteSteamAccount = True
                else:
                    fetchResult = yield wg_await(self._subscriptionProductsFetchController.getProducts())
            else:
                fetchResult = yield wg_await(self._subscriptionProductsFetchController.getProducts())
            self.__subscriptionsFetchResult = fetchResult
            self.__updateViewModel()
        finally:
            Waiting.hide('loadingData')

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(PlayerSubscriptionsView, self)._onLoading(*args, **kwargs)
        Waiting.show('loadingData')
        self.__fetchExternalSubs()

    def _getEvents(self):
        return ((self.viewModel.onBack, self.__onBackClick),
         (self.viewModel.onCardClick, self.__onCardClick),
         (self.viewModel.onButtonClick, self.__onButtonClick),
         (self._lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChange))

    def __onWotPlusStatusChanged(self, args):
        if RS_TIER in args:
            self.__fetchExternalSubs()

    def __updateViewModel(self):
        if not self.viewModel or not self.viewModel.proxy:
            return
        with self.viewModel.transaction() as model:
            model.setWarningTitle(R.invalid())
            if self.__incompleteSteamAccount:
                model.setWarningTitle(R.strings.player_subscriptions.confirmationNeeded())
                return
            subscriptions = model.getSubscriptions()
            subscriptions.clear()
            self.__subscriptions.clear()
            if self.__subscriptionsFetchResult.isProcessed and self.__subscriptionsFetchResult.products:
                subscriptions.reserve(len(self.__subscriptionsFetchResult.products))
                products = self.__getSortedProducts(self.__subscriptionsFetchResult.products)
                for subscriptionDescr in products:
                    if not self.isSubscriptionProductAvailable(subscriptionDescr):
                        continue
                    subsModel = _SUBSCRIPTION_TYPE_FACTORIES[subscriptionDescr.type].fill(subscriptionDescr)
                    subscriptions.addViewModel(subsModel)
                    self.__subscriptions[subscriptionDescr.productID] = subscriptionDescr.type

            else:
                model.setWarningTitle(R.strings.player_subscriptions.noSubscriptions())
            subscriptions.invalidate()

    def __getSortedProducts(self, products):
        return sorted(products, key=lambda product: not isinstance(product, WotPlusDescriptor))

    def __onBackClick(self):
        self._wotPlusUILogger.logCloseEvent()
        self.destroyWindow()

    def __onCardClick(self, args):
        id_ = args['subscriptionId']
        if _isWotPlus(self.__subscriptions[id_]):
            showWotPlusInfoPage(WotPlusInfoPageSource.SUBSCRIPTION_PAGE, includeSubscriptionInfo=True)
            return
        if self.__subscriptions[id_] == SubscriptionTypeEnum.EXTERNALSUBSCRIPTION:
            url = GUI_SETTINGS.playerSubscriptionsURL
            showBrowserOverlayView(url, VIEW_ALIAS.BROWSER_OVERLAY)

    def __onButtonClick(self, args):
        id_ = args['subscriptionId']
        if _isWotPlus(self.__subscriptions[id_]):
            self._wotPlusUILogger.logClickEvent(SubscriptionPageKeys.CTA_BUTTON)
            if self._wotPlusCtrl.hasSubscription():
                if self._wotPlusCtrl.shouldRedirectToSteam():
                    showWotPlusSteamSubscriptionManagementPage()
                    return
                if self.__subscriptions[id_] == SubscriptionTypeEnum.WOTSUBSCRIPTION or self._wotPlusCtrl.getTier() == WotPlusTier.PRO:
                    showWotPlusProductPage()
                else:
                    showShop(getWotPlusProShopUrl())
            else:
                if self.__subscriptions[id_] == SubscriptionTypeEnum.WOTSUBSCRIPTION:
                    url = getWotPlusShopUrl()
                else:
                    url = getWotPlusProShopUrl()
                showShop(url)
            return
        subscriptionDescriptor = self.__subscriptionsFetchResult.getProductByID(id_)
        if not subscriptionDescriptor:
            _logger.warning('Subscription descriptor with id=%s was not found', id_)
            return
        if not subscriptionDescriptor.isRewardsClaimed():
            self._externalBrowser.open(subscriptionDescriptor.claimURL)
        elif subscriptionDescriptor.hasDepotRewards():
            showOfferGiftsWindow(subscriptionDescriptor.getOfferID())

    def __onServerSettingsChange(self, *args, **kwargs):
        if not self._lobbyContext.getServerSettings().isPlayerSubscriptionsEnabled():
            self.destroyWindow()

    def isSubscriptionProductAvailable(self, subscription):
        if not _isWotPlus(subscription.type):
            return True
        if self._wotPlusCtrl.hasSubscription() and self._wotPlusCtrl.getTier() == subscription.tier:
            return True
        if not self._wotPlusCtrl.isWotPlusVisible():
            return False
        return self._wotPlusCtrl.getSettingsStorage().isProductEnabledForSteam(subscription.tier) if self._steamCompletionCtrl.isSteamAccount is True else True
