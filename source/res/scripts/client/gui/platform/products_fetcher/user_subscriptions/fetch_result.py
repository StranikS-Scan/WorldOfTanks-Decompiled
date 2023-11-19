# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/products_fetcher/user_subscriptions/fetch_result.py
from gui.platform.products_fetcher.fetch_result import FetchResult, ResponseStatus

class UserSubscriptionFetchResult(FetchResult):
    _CACHE_TTL = 600

    def stop(self):
        self._clearTimeoutBwCbId()
        self.status = ResponseStatus.UNDEFINED
        self.products = []
