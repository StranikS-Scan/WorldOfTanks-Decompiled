# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/products_fetcher/user_subscriptions/descriptor.py


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
    def platform(self):
        return self._params.get('platform')
