# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/products_fetcher/user_subscriptions/controller.py
import logging
from functools import partial
import typing
from future.utils import listvalues
from BWUtil import AsyncReturn
import wg_async
from adisp import adisp_process
from gui.platform.products_fetcher.fetch_result import FetchResult
from gui.platform.products_fetcher.user_subscriptions.fetch_result import UserSubscriptionFetchResult
from gui.platform.products_fetcher.user_subscriptions.user_subscription import UserSubscription, SubscriptionStatus
from gui.wgcg.utils.contexts import PlatformGetUserSubscriptionsCtx
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.platform.product_fetch_controller import IUserSubscriptionsFetchController
from skeletons.gui.web import IWebController
from skeletons.gui.game_control import IWotPlusController
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from gui.wgcg.web_controller import WebController
__doc__ = '\nModule takes care of player subscriptions from platform.\n\nUsers can buy two types types of subscriptions. One from Steam, one from platform.\n\nOur workflow with this subscriptions is:\n1. if player has payed wot+, we will download from platform list of his subscriptions.\n2. we will create a list of his subscriptions as list of UserSubscriptions\n   in UserSubscriptionsFetchController._fetchResult.products.\n2. we will set the state of subscription - active, cancelled.\n\nSubscriptions are updated during lobby/hangar load. Cache is set to 5 minutes.\n'

class PlatformGetUserSubscriptionsParams(object):

    def __init__(self):
        self.status = [SubscriptionStatus.ACTIVE.value, SubscriptionStatus.INACTIVE.value]

    def __str__(self):
        return 'status: {status}'.format(status=self.status)


class UserSubscriptionsFetchController(IUserSubscriptionsFetchController):
    _webCtrl = dependency.descriptor(IWebController)
    _connectionMgr = dependency.descriptor(IConnectionManager)
    _wotPlusCtrl = dependency.descriptor(IWotPlusController)
    platformFetchCtx = PlatformGetUserSubscriptionsCtx

    def __init__(self):
        super(UserSubscriptionsFetchController, self).__init__()
        self._fetchResult = UserSubscriptionFetchResult()

    def init(self):
        self._connectionMgr.onDisconnected += self._fetchResult.stop

    def fini(self):
        self._connectionMgr.onDisconnected -= self._fetchResult.stop

    @wg_async.wg_async
    def getSubscriptions(self, clearCache=False):
        _logger.debug('Trying to fetch subscriptions')
        if self._fetchResult.isProcessed and not clearCache:
            _logger.debug('Return subscriptions from cache')
            raise AsyncReturn(self._fetchResult)
        self._fetchResult.reset()
        subscriptionParams = PlatformGetUserSubscriptionsParams()
        requestSuccess, subscriptionsData = yield wg_async.await_callback(partial(self._requestSubscriptions, subscriptionParams))()
        subscriptionProductCodes = self._wotPlusCtrl.getSettingsStorage().getAllProductCodes()
        if requestSuccess and subscriptionsData:
            _logger.debug('Subscriptions request from %s has been successfully processed.', str(subscriptionParams))
            subsLookup = {}
            for subscriptionData in subscriptionsData:
                productCode = subscriptionData.get('product_code')
                if productCode not in subscriptionProductCodes:
                    continue
                userSubscription = UserSubscription(subscriptionData)
                if productCode not in subsLookup:
                    subsLookup[productCode] = userSubscription
                if userSubscription.nextBillingTime > subsLookup[productCode].nextBillingTime:
                    subsLookup[productCode] = userSubscription

            self._fetchResult.products = listvalues(subsLookup)
        if requestSuccess:
            self._fetchResult.setProcessed()
        else:
            self._fetchResult.setFailed()
        raise AsyncReturn(self._fetchResult)

    @adisp_process
    def _requestSubscriptions(self, params, callback):
        ctx = PlatformGetUserSubscriptionsCtx(params)
        _logger.debug('Request subscriptions for params %s', params)
        response = yield self._webCtrl.sendRequest(ctx=ctx)
        data = response.getData()
        items = data.get('subscriptions') if data else None
        callback((response.isSuccess(), items))
        return

    def reset(self):
        self._fetchResult.reset()
