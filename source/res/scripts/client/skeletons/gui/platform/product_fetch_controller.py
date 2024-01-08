# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/platform/product_fetch_controller.py
import typing
from skeletons.gui.platform.controller import IPlatformRequestController
if typing.TYPE_CHECKING:
    from gui.platform.products_fetcher.fetch_result import FetchResult

class IProductFetchController(IPlatformRequestController):

    def reset(self):
        raise NotImplementedError

    def getProducts(self, showWaiting=True, **kwargs):
        raise NotImplementedError


class ISubscriptionProductsFetchController(IProductFetchController):
    pass


class IUserSubscriptionsFetchController(IPlatformRequestController):
    pass


class IWotShopFetchController(IProductFetchController):

    def getProducts(self, showWaiting=True, **kwargs):
        raise NotImplementedError
