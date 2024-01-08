# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/products_fetcher/wot_shop/fetch_result.py
from collections import namedtuple
from gui.platform.products_fetcher.fetch_result import FetchResult, ResponseStatus
ResponseData = namedtuple('ResponseData', ('status', 'products', 'accountLimits', 'categories'))
ResponseData.__new__.__defaults__ = (ResponseStatus.UNDEFINED,
 None,
 None,
 None)

class WotShopFetchResult(FetchResult):

    def __init__(self, status=ResponseStatus.UNDEFINED):
        super(WotShopFetchResult, self).__init__(status)
        self.__accountLimits = []
        self.__categories = []

    def getAccountLimits(self):
        return self.__accountLimits

    def setAccountLimits(self, accountLimits):
        self.__accountLimits = accountLimits

    def getCategories(self):
        return self.__categories

    def setCategories(self, categories):
        self.__categories = categories

    def getData(self):
        return ResponseData(status=self.status, products=self.getProducts(), accountLimits=self.getAccountLimits(), categories=self.getCategories()) if self.isProcessed else ResponseData(status=self.status)

    def stop(self):
        super(WotShopFetchResult, self).stop()
        for accountLimit in self.__accountLimits:
            accountLimit.destroy()

        for category in self.__categories:
            category.destroy()

        self.__accountLimits = []
        self.__categories = []
