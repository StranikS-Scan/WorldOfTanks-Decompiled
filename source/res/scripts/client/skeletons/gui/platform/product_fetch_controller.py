# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/platform/product_fetch_controller.py
from skeletons.gui.platform.controller import IPlatformRequestController

class IProductFetchController(IPlatformRequestController):

    def getProducts(self, showWaiting=True):
        raise NotImplementedError


class ISubscriptionsFetchController(IProductFetchController):

    def getProducts(self, showWaiting=True):
        raise NotImplementedError


class IUserSubscriptionsFetchController(IProductFetchController):

    def getProducts(self, showWaiting=True):
        raise NotImplementedError

    def resetFetch(self):
        raise NotImplementedError
