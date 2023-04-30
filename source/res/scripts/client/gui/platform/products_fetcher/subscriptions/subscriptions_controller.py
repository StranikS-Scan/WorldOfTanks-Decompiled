# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/products_fetcher/subscriptions/subscriptions_controller.py
import logging
import typing
from BWUtil import AsyncReturn
from constants import SUBSCRIPTION_ENTITLEMENT
from skeletons.gui.game_control import IWotPlusController
from skeletons.gui.lobby_context import ILobbyContext
from wg_async import wg_async, wg_await
from gui.platform.base.statuses.constants import StatusTypes
from gui.platform.products_fetcher.controller import ProductsFetchController, _PlatformProductListParams
from gui.platform.products_fetcher.subscriptions.subscriptions_descriptor import PrimeGamingDescriptor, SubscriptionDescriptor, WotPlusDescriptor
from helpers import dependency, getClientLanguage
from skeletons.gui.platform.product_fetch_controller import ISubscriptionsFetchController
from skeletons.gui.platform.wgnp_controllers import IWGNPGeneralRequestController
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from gui.platform.wgnp.general.statuses import GeneralAccountCountryStatus

class PlatformSubscriptionsParams(_PlatformProductListParams):
    storefront = 'player_subscriptions'
    language = getClientLanguage()
    __wgnpCountryController = dependency.descriptor(IWGNPGeneralRequestController)

    @wg_async
    def setCountry(self):
        status = yield wg_await(self.__wgnpCountryController.getAccountCountry())
        if status.typeIs(StatusTypes.ADDED):
            self.country = status.country
        raise AsyncReturn(None)
        return


class SubscriptionFetcherController(ProductsFetchController, ISubscriptionsFetchController):
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _wotPlusCtrl = dependency.descriptor(IWotPlusController)
    platformParams = PlatformSubscriptionsParams
    defaultProductDescriptor = SubscriptionDescriptor
    productIDToDescriptor = {'prime_subscription': PrimeGamingDescriptor,
     SUBSCRIPTION_ENTITLEMENT: WotPlusDescriptor}

    def init(self):
        super(SubscriptionFetcherController, self).init()
        self._wotPlusCtrl.onDataChanged += self.__onWotPlusChanged

    def fini(self):
        super(SubscriptionFetcherController, self).fini()
        self._wotPlusCtrl.onDataChanged -= self.__onWotPlusChanged

    @wg_async
    def getProducts(self, showWaiting=True):
        wasReady = self.isProductsReady
        yield wg_await(super(SubscriptionFetcherController, self).getProducts(showWaiting))
        if not wasReady:
            if self._wotPlusCtrl.isWotPlusEnabled():
                self._createDescriptors([{'product_code': SUBSCRIPTION_ENTITLEMENT}])
                self._fetchResult.products.insert(0, self._fetchResult.products.pop())
                self._fetchResult.setProcessed()
        raise AsyncReturn(self._fetchResult)

    def __onWotPlusChanged(self, diff):
        if 'isEnabled' in diff:
            self._fetchResult.reset()
