# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/products_fetcher/subscriptions/subscriptions_controller.py
import logging
import typing
from BWUtil import AsyncReturn
from constants import WOT_PLUS_SUBSCRIPTION_PRODUCT, PRIME_GAMING_SUBSCRIPTION_PRODUCT
from gui.platform.base.statuses.constants import StatusTypes
from gui.platform.products_fetcher.controller import ProductsFetchController, _PlatformProductListParams
from gui.platform.products_fetcher.subscriptions.subscription_descriptors import PrimeGamingDescriptor, SubscriptionDescriptor, WotPlusDescriptor
from helpers import dependency, getClientLanguage
from skeletons.gui.game_control import IWotPlusController
from skeletons.gui.platform.wgnp_controllers import IWGNPGeneralRequestController
from wg_async import wg_async, wg_await
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from gui.platform.wgnp.general.statuses import GeneralAccountCountryStatus
__doc__ = '\nModule takes care of subscription products on platform.\n\nTo receive product from platform usually we do 2 steps.\n\n1. receive list of products from platform storefront named "player_subscriptions"\n2. obtain detailed information per product, link on product detail is stored by product from first request.\n\nFor now we support two types of subscriptions Prime Gaming subscription or Wot Plus subscription.\nThis subscription products are defined with PrimeGamingDescriptor or WotPlusDescriptor.\nDescriptors are stored in SubscriptionProductsFetchController._fetchResult.products.\nDescriptors have 24 hours cache.\n'

class PlatformSubscriptionsParams(_PlatformProductListParams):
    storefront = 'subscriptions_general'
    language = getClientLanguage()
    __wgnpCountryController = dependency.descriptor(IWGNPGeneralRequestController)

    @wg_async
    def setCountry(self):
        status = yield wg_await(self.__wgnpCountryController.getAccountCountry())
        if status.typeIs(StatusTypes.ADDED):
            self.country = status.country
        raise AsyncReturn(None)
        return


class SubscriptionProductsFetchController(ProductsFetchController):
    _wotPlusCtrl = dependency.descriptor(IWotPlusController)
    platformParams = PlatformSubscriptionsParams
    defaultProductDescriptor = SubscriptionDescriptor
    productIDToDescriptor = {PRIME_GAMING_SUBSCRIPTION_PRODUCT: PrimeGamingDescriptor,
     WOT_PLUS_SUBSCRIPTION_PRODUCT: WotPlusDescriptor}

    def init(self):
        super(SubscriptionProductsFetchController, self).init()
        self._wotPlusCtrl.onDataChanged += self.__onWotPlusChanged

    def fini(self):
        super(SubscriptionProductsFetchController, self).fini()
        self._wotPlusCtrl.onDataChanged -= self.__onWotPlusChanged

    def __onWotPlusChanged(self, diff):
        if 'isEnabled' in diff:
            self._fetchResult.reset()
