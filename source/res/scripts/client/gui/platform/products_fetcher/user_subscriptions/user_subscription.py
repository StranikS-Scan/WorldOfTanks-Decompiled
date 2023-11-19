# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/products_fetcher/user_subscriptions/user_subscription.py
import logging
from enum import Enum
from typing import Dict
from helpers.time_utils import getTimestampFromISO

class SubscriptionStatus(Enum):
    NEW = 'NEW'
    WAITING_FOR_PURCHASE = 'WAITING_FOR_PURCHASE'
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'
    GDPR_SUSPENDED = 'GDPR_SUSPENDED'
    NEXT_PAYMENT_UNAVAILABLE = 'NEXT_PAYMENT_UNAVAILABLE'


SUBSCRIPTION_CANCEL_STATUSES = [SubscriptionStatus.INACTIVE, SubscriptionStatus.GDPR_SUSPENDED, SubscriptionStatus.NEXT_PAYMENT_UNAVAILABLE]
_logger = logging.getLogger(__name__)

class SubscriptionRequestPlatform(Enum):
    WG_PLATFORM = 'wg_platform'
    STEAM = 'steam'
    UNKNOWN = 'unknown'


class UserSubscription(object):
    __slots__ = ('subscriptionId', 'productCode', 'status', 'nextBillingTime', 'platform')

    def __init__(self, subscriptionData):
        self.subscriptionId = None
        self.productCode = None
        self.status = None
        self.nextBillingTime = None
        self.platform = SubscriptionRequestPlatform.UNKNOWN
        self.loadFromData(subscriptionData)
        return

    def loadFromData(self, subscriptionData):
        self.subscriptionId = subscriptionData.get('subscription_id')
        self.productCode = subscriptionData.get('product_code')
        self.status = SubscriptionStatus(subscriptionData.get('status'))
        try:
            self.nextBillingTime = int(getTimestampFromISO(subscriptionData.get('next_billing_time')))
        except ValueError:
            _logger.warning('Unknown billing time in subscription: %s', subscriptionData.get('next_billing_time'))

        try:
            self.platform = SubscriptionRequestPlatform(subscriptionData.get('platform'))
        except ValueError:
            _logger.warning('Unknown subscription type in subscription: %s', subscriptionData.get('platform'))

    def __str__(self):
        return 'subscriptionId: {}, productCode: {}, status: {}, nextBillingTime: {}, platform: {}'.format(self.subscriptionId, self.productCode, self.status, self.nextBillingTime, self.platform)
