# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/products_fetcher/user_subscriptions/descriptor.py
import time
import calendar

class UserSubscriptionDescriptor(object):

    def __init__(self, data):
        self._params = data

    @property
    def productCode(self):
        return self._params.get('product_code')

    @property
    def status(self):
        return self._params.get('status')

    @property
    def nextBilling(self):
        return int(calendar.timegm(time.strptime(self._params.get('next_billing_time'), '%Y-%m-%dT%H:%M:%SZ')))
