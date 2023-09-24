# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/products_fetcher/user_subscriptions/controller.py
import logging
from functools import partial
from BWUtil import AsyncReturn
from enum import Enum
import wg_async
from gui.Scaleform.Waiting import Waiting
from gui.platform.products_fetcher.controller import ProductsFetchController
from gui.platform.products_fetcher.fetch_result import FetchResult
from gui.platform.products_fetcher.user_subscriptions.descriptor import UserSubscriptionDescriptor
from gui.platform.products_fetcher.user_subscriptions.fetch_result import UserSubscriptionFetchResult
from gui.wgcg.utils.contexts import PlatformGetUserSubscriptionsCtx
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.platform.product_fetch_controller import IUserSubscriptionsFetchController
_logger = logging.getLogger(__name__)

class SubscriptionStatus(Enum):
    NEW = 'NEW'
    WAITING_FOR_PURCHASE = 'WAITING_FOR_PURCHASE'
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'
    GDPR_SUSPENDED = 'GDPR_SUSPENDED'
    NEXT_PAYMENT_UNAVAILABLE = 'NEXT_PAYMENT_UNAVAILABLE'


class SubscriptionRequestPlatform(Enum):
    WG_PLATFORM = 'wg_platform'
    STEAM = 'steam'


class PlatformGetUserSubscriptionsParams(object):
    _lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        serverSettings = self._lobbyContext.getServerSettings()
        self.status = [SubscriptionStatus.ACTIVE.value]
        self.productCode = serverSettings.getWotPlusProductCode()
        self.platform = SubscriptionRequestPlatform.WG_PLATFORM.value

    def __repr__(self):
        return 'product_code: {product_code} status: {status}, platform: {platform}'.format(product_code=self.productCode, status=self.status, platform=self.platform)


class SteamGetUserSubscriptionsParams(PlatformGetUserSubscriptionsParams):

    def __init__(self):
        super(SteamGetUserSubscriptionsParams, self).__init__()
        self.platform = SubscriptionRequestPlatform.STEAM.value


class UserSubscriptionsFetchController(ProductsFetchController, IUserSubscriptionsFetchController):
    requestParamsList = [PlatformGetUserSubscriptionsParams, SteamGetUserSubscriptionsParams]
    platformFetchCtx = PlatformGetUserSubscriptionsCtx
    defaultProductDescriptor = UserSubscriptionDescriptor
    dataGetKey = 'subscriptions'

    def init(self):
        self._fetchResult = UserSubscriptionFetchResult()
        self._connectionMgr.onDisconnected += self._onDisconnect

    def fini(self):
        self._fetchResult.stop()
        self._connectionMgr.onDisconnected -= self._onDisconnect

    @wg_async.wg_async
    def getProducts(self, showWaiting=True):
        _logger.debug('Trying to fetch products')
        if self._fetchResult.isProductsReady:
            _logger.debug('Return products from cache')
            raise AsyncReturn(self._fetchResult)
        if showWaiting:
            Waiting.show('loadingData')
        self._fetchResult.reset()
        processed = False
        for paramObj in self.requestParamsList:
            params = paramObj()
            requestSuccess, productsData = yield wg_async.await_callback(partial(self._requestProducts, params))()
            if requestSuccess and productsData:
                _logger.debug('Products request from %s has been successfully processed.', params.platform)
                self._createDescriptors(productsData)
                processed = True

        if processed:
            self._fetchResult.setProcessed()
        else:
            self._fetchResult.setFailed()
        if showWaiting:
            Waiting.hide('loadingData')
        raise AsyncReturn(self._fetchResult)
