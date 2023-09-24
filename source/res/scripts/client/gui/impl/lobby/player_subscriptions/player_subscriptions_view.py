# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/player_subscriptions/player_subscriptions_view.py
import logging
import typing
from frameworks.wulf import ViewFlags, ViewSettings
from gui import GUI_SETTINGS
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getWotPlusShopUrl
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.player_subscriptions.external_subscription_model import ExternalSubscriptionModel
from gui.impl.gen.view_models.views.lobby.player_subscriptions.player_subscriptions_model import PlayerSubscriptionsModel
from gui.impl.gen.view_models.views.lobby.player_subscriptions.subscription_model import SubscriptionTypeEnum
from gui.impl.gen.view_models.views.lobby.player_subscriptions.wot_subscription_model import WotSubscriptionModel
from gui.impl.pub import ViewImpl
from gui.platform.base.statuses.constants import StatusTypes
from gui.platform.products_fetcher.fetch_result import FetchResult
from gui.shared.event_dispatcher import showOfferGiftsWindow, showBrowserOverlayView, showShop, showWotPlusInfoPage, showWotPlusProductPage, showWotPlusSteamSubscriptionManagementPage
from helpers import dependency
from skeletons.gui.game_control import IExternalLinksController, ISteamCompletionController, IWotPlusController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.platform.product_fetch_controller import ISubscriptionsFetchController
from skeletons.gui.platform.wgnp_controllers import IWGNPSteamAccRequestController
from uilogging.wot_plus.loggers import WotPlusSubscriptionViewLogger
from uilogging.wot_plus.logging_constants import WotPlusInfoPageSource, SubscriptionPageKeys
from wg_async import wg_await, wg_async
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from typing import Optional, Dict, Any
    from gui.platform.products_fetcher.subscriptions.subscriptions_descriptor import SubscriptionDescriptor, WotPlusDescriptor
    from gui.platform.wgnp.steam_account.statuses import SteamAccEmailStatus
    from gui.impl.gen.view_models.views.lobby.player_subscriptions.subscription_model import SubscriptionModel
_PLAYER_SUBSCRIPTIONS_URL = 'playerSubscriptionsURL'

def __makeWotPlusSubscriptionModel(subscriptionDescr):
    subscriptionModel = WotSubscriptionModel()
    subscriptionModel.setSubscriptionType(subscriptionDescr.type)
    subscriptionModel.setId(subscriptionDescr.productID)
    subscriptionModel.setName(subscriptionDescr.name)
    subscriptionModel.setDescription(subscriptionDescr.description)
    subscriptionModel.setImageUriLarge(subscriptionDescr.largeImageURL)
    subscriptionModel.setImageUriMedium(subscriptionDescr.mediumImageURL)
    subscriptionModel.setRefreshTime(subscriptionDescr.expirationTime)
    subscriptionModel.setWotSubscriptionState(subscriptionDescr.state)
    return subscriptionModel


def __makeExternalSubscriptionModel(subscriptionDescr):
    subscriptionModel = ExternalSubscriptionModel()
    subscriptionModel.setSubscriptionType(subscriptionDescr.type)
    subscriptionModel.setId(subscriptionDescr.productID)
    subscriptionModel.setName(subscriptionDescr.name)
    subscriptionModel.setDescription(subscriptionDescr.description)
    subscriptionModel.setImageUriLarge(subscriptionDescr.largeImageURL)
    subscriptionModel.setImageUriMedium(subscriptionDescr.mediumImageURL)
    subscriptionModel.setImageUriSmall(subscriptionDescr.smallImageURL)
    subscriptionModel.setHas3rdPartyRewardsToClaim(not subscriptionDescr.isRewardsClaimed())
    subscriptionModel.setHasDepotRewardsToClaim(subscriptionDescr.hasDepotRewards())
    subscriptionModel.setRefreshTime(subscriptionDescr.expirationTime)
    return subscriptionModel


_SUBSCRIPTION_TYPE_FACTORIES = {SubscriptionTypeEnum.EXTERNALSUBSCRIPTION: __makeExternalSubscriptionModel,
 SubscriptionTypeEnum.WOTSUBSCRIPTION: __makeWotPlusSubscriptionModel}

class PlayerSubscriptionsView(ViewImpl):
    _playerSubscriptionsController = dependency.descriptor(ISubscriptionsFetchController)
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
                    fetchResult = yield wg_await(self._playerSubscriptionsController.getProducts())
            else:
                fetchResult = yield wg_await(self._playerSubscriptionsController.getProducts())
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
        if 'isEnabled' in args:
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
                for subscriptionDescr in self.__subscriptionsFetchResult.products:
                    subsModel = _SUBSCRIPTION_TYPE_FACTORIES[subscriptionDescr.type](subscriptionDescr)
                    subscriptions.addViewModel(subsModel)
                    self.__subscriptions[subscriptionDescr.productID] = subscriptionDescr.type

            else:
                model.setWarningTitle(R.strings.player_subscriptions.noSubscriptions())
            subscriptions.invalidate()

    def __onBackClick(self):
        self._wotPlusUILogger.logCloseEvent()
        self.destroyWindow()

    def __onCardClick(self, args):
        id_ = args['subscriptionId']
        if self.__subscriptions[id_] == SubscriptionTypeEnum.WOTSUBSCRIPTION:
            showWotPlusInfoPage(WotPlusInfoPageSource.SUBSCRIPTION_PAGE, includeSubscriptionInfo=True)
            return
        if self.__subscriptions[id_] == SubscriptionTypeEnum.EXTERNALSUBSCRIPTION:
            url = GUI_SETTINGS.playerSubscriptionsURL
            showBrowserOverlayView(url, VIEW_ALIAS.BROWSER_OVERLAY)

    def __onButtonClick(self, args):
        id_ = args['subscriptionId']
        if self.__subscriptions[id_] == SubscriptionTypeEnum.WOTSUBSCRIPTION:
            self._wotPlusUILogger.logClickEvent(SubscriptionPageKeys.CTA_BUTTON)
            if self._wotPlusCtrl.isEnabled():
                if self._wotPlusCtrl.hasSteamSubscription():
                    showWotPlusSteamSubscriptionManagementPage()
                else:
                    showWotPlusProductPage()
            else:
                showShop(getWotPlusShopUrl())
            return
        subcriptionDescriptor = self.__subscriptionsFetchResult.getProductByID(id_)
        if not subcriptionDescriptor:
            _logger.warning('Subscription descriptor with id=%s was not found', id_)
            return
        if not subcriptionDescriptor.isRewardsClaimed():
            self._externalBrowser.open(subcriptionDescriptor.claimURL)
        elif subcriptionDescriptor.hasDepotRewards():
            showOfferGiftsWindow(subcriptionDescriptor.getOfferID())

    def __onServerSettingsChange(self, *args, **kwargs):
        if not self._lobbyContext.getServerSettings().isPlayerSubscriptionsEnabled():
            self.destroyWindow()
