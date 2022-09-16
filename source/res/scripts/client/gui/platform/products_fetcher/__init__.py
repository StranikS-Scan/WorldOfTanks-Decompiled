# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/products_fetcher/__init__.py
import typing
from gui.platform.products_fetcher.subscriptions.subscriptions_controller import SubscriptionFetcherController
from skeletons.gui.platform.product_fetch_controller import ISubscriptionsFetchController
if typing.TYPE_CHECKING:
    from helpers.dependency import DependencyManager
__all__ = ('getProductFetchControllers',)

def getProductFetchControllers(manager):
    subscriptionsFetchController = SubscriptionFetcherController()
    subscriptionsFetchController.init()
    manager.addInstance(ISubscriptionsFetchController, subscriptionsFetchController, finalizer='fini')
