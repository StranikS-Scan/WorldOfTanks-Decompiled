# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/platform/product_fetch_controller.py
from typing import TYPE_CHECKING
from skeletons.gui.platform.controller import IPlatformRequestController
if TYPE_CHECKING:
    from gui.platform.products_fetcher.fetch_result import FetchResult

class IProductFetchController(IPlatformRequestController):

    def getProducts(self, showWaiting=True):
        raise NotImplementedError


class ISubscriptionProductsFetchController(IProductFetchController):
    pass


class IUserSubscriptionsFetchController(IPlatformRequestController):
    pass
