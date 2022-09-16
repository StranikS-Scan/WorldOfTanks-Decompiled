# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/player_subscriptions/player_subscriptions_view.py
import logging
import typing
from frameworks.wulf import ViewFlags, ViewSettings
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.player_subscriptions.player_subscriptions_model import PlayerSubscriptionsModel
from gui.impl.gen.view_models.views.lobby.player_subscriptions.subscription import Subscription
from gui.impl.pub import ViewImpl
from gui.shared.event_dispatcher import showOfferGiftsWindow, showBrowserOverlayView
from helpers import dependency
from skeletons.gui.game_control import IExternalLinksController, ISteamCompletionController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.platform.product_fetch_controller import ISubscriptionsFetchController
from skeletons.gui.platform.wgnp_controllers import IWGNPSteamAccRequestController
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from gui.platform.products_fetcher.subscriptions.subscriptions_descriptor import SubscriptionDescriptor
_PLAYER_SUBSCRIPTIONS_URL = 'playerSubscriptionsURL'

class PlayerSubscriptionsView(ViewImpl):
    _playerSubscriptionsController = dependency.descriptor(ISubscriptionsFetchController)
    _externalBrowser = dependency.descriptor(IExternalLinksController)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _wgnpSteamAccCtrl = dependency.descriptor(IWGNPSteamAccRequestController)
    _steamRegistrationCtrl = dependency.descriptor(ISteamCompletionController)
    __slots__ = ('__subscriptionsFetchResult', '__incompleteSteamAccount')

    def __init__(self, layoutID=R.views.lobby.player_subscriptions.PlayerSubscriptions(), ctx=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = PlayerSubscriptionsModel()
        self.__subscriptionsFetchResult = ctx.get('fetchResult')
        self.__incompleteSteamAccount = ctx.get('incompleteSteamAccount')
        super(PlayerSubscriptionsView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(PlayerSubscriptionsView, self)._onLoading(*args, **kwargs)
        self.__updateViewModel()

    def _getEvents(self):
        return ((self.viewModel.onBack, self.__onBackClick),
         (self.viewModel.onCardClick, self.__onCardClick),
         (self.viewModel.onButtonClick, self.__onButtonClick),
         (self._lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChange))

    def __updateViewModel(self):
        with self.viewModel.transaction() as model:
            if self.__incompleteSteamAccount:
                model.setWarningTitle(R.strings.player_subscriptions.confirmationNeeded())
                return
            subscriptions = model.getSubscriptions()
            if self.__subscriptionsFetchResult.isProcessed and self.__subscriptionsFetchResult.products:
                subscriptions.clear()
                subscriptions.reserve(len(self.__subscriptionsFetchResult.products))
                for subscriptionDescr in self.__subscriptionsFetchResult.products:
                    subscriptionModel = Subscription()
                    subscriptionModel.setId(subscriptionDescr.productID)
                    subscriptionModel.setName(subscriptionDescr.name)
                    subscriptionModel.setDescription(subscriptionDescr.description)
                    subscriptionModel.setImageUriLarge(subscriptionDescr.largeImageURL)
                    subscriptionModel.setImageUriMedium(subscriptionDescr.mediumImageURL)
                    subscriptionModel.setImageUriSmall(subscriptionDescr.smallImageURL)
                    subscriptionModel.setHas3rdPartyRewardsToClaim(not subscriptionDescr.isRewardsClaimed())
                    subscriptionModel.setHasDepotRewardsToClaim(subscriptionDescr.hasDepotRewards())
                    subscriptionModel.setRefreshTime(subscriptionDescr.expirationTime)
                    subscriptions.addViewModel(subscriptionModel)

            else:
                model.setWarningTitle(R.strings.player_subscriptions.noSubscriptions())

    def __onBackClick(self):
        self.destroyWindow()

    def __onCardClick(self, args):
        url = GUI_SETTINGS.playerSubscriptionsURL
        showBrowserOverlayView(url, VIEW_ALIAS.BROWSER_OVERLAY)

    def __onButtonClick(self, args):
        id_ = args['subscriptionId']
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
