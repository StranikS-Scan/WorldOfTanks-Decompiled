# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/products_fetcher/user_subscriptions/controller.py
import logging
import typing
from functools import partial
from BWUtil import AsyncReturn
import wg_async
from adisp import adisp_process
from gui.Scaleform.Waiting import Waiting
from gui.platform.products_fetcher.controller import ProductsFetchController
from gui.platform.products_fetcher.fetch_result import FetchResult
from gui.platform.products_fetcher.user_subscriptions.descriptor import UserSubscriptionDescriptor
from gui.platform.products_fetcher.user_subscriptions.fetch_result import UserSubscriptionFetchResult
from gui.wgcg.utils.contexts import PlatformGetUserSubscriptionsCtx
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.platform.product_fetch_controller import IUserSubscriptionsFetchController
if typing.TYPE_CHECKING:
    from typing import List, Dict
_logger = logging.getLogger(__name__)

class SubscriptionStatus(object):
    NEW = 'NEW'
    WAITING_FOR_PURCHASE = 'WAITING_FOR_PURCHASE'
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'
    GDPR_SUSPENDED = 'GDPR_SUSPENDED'
    NEXT_PAYMENT_UNAVAILABLE = 'NEXT_PAYMENT_UNAVAILABLE'


class PlatformGetUserSubscriptionsParams(object):
    _lobbyContext = dependency.descriptor(ILobbyContext)
    status = []
    productCode = ''

    def setFields(self):
        serverSettings = self._lobbyContext.getServerSettings()
        self.status = [SubscriptionStatus.ACTIVE]
        self.productCode = serverSettings.getWotPlusProductCode()

    def __repr__(self):
        return 'product_code: {product_code} status: {status}, '.format(product_code=self.productCode, status=self.status)


class UserSubscriptionsFetchController(ProductsFetchController, IUserSubscriptionsFetchController):
    platformParams = PlatformGetUserSubscriptionsParams
    platformFetchCtx = PlatformGetUserSubscriptionsCtx
    subscriptionDescriptor = UserSubscriptionDescriptor

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
        params = self.platformParams()
        params.setFields()
        requestSuccess, productsData = yield wg_async.await_callback(partial(self._requestProducts, params))()
        if requestSuccess and productsData:
            _logger.debug('Products request has been successfully processed.')
            self._createDescriptors(productsData)
            self._fetchResult.setProcessed()
        else:
            self._fetchResult.setFailed()
        if showWaiting:
            Waiting.hide('loadingData')
        raise AsyncReturn(self._fetchResult)

    def _createDescriptors(self, productsData):
        for product in productsData:
            self._fetchResult.products.append(self.subscriptionDescriptor(product))

    @adisp_process
    def _requestProducts(self, params, callback):
        ctx = self.platformFetchCtx(params)
        _logger.debug('Request products for params %s', params)
        response = yield self._webCtrl.sendRequest(ctx=ctx)
        data = response.getData()
        items = data.get('subscriptions') if data else None
        callback((response.isSuccess(), items))
        return
