# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/products_fetcher/fetch_result.py
from enum import Enum
import BigWorld
from constants import SECONDS_IN_DAY

class ResponseStatus(Enum):
    UNDEFINED = 0
    PROCESSED = 1
    FAILED = 2
    FAILED_BY_TIMEOUT = 3


class FetchResult(object):
    _CACHE_TTL = SECONDS_IN_DAY

    def __init__(self, status=ResponseStatus.UNDEFINED):
        self.status = status
        self.products = []
        self.__timerTTL = None
        return

    @property
    def isUndefined(self):
        return self._isStatus(ResponseStatus.UNDEFINED)

    @property
    def isProcessed(self):
        return self._isStatus(ResponseStatus.PROCESSED)

    @property
    def isFailed(self):
        return self._isStatus(ResponseStatus.FAILED)

    @property
    def isFailedByTimeout(self):
        return self._isStatus(ResponseStatus.FAILED_BY_TIMEOUT)

    @property
    def isProductsReady(self):
        return self.isProcessed and self.products

    def getProducts(self):
        return self.products

    def setProducts(self, products):
        self.products = products

    def reset(self):
        self.stop()

    def stop(self):
        self._clearTimeoutBwCbId()
        self.status = ResponseStatus.UNDEFINED
        for product in self.products:
            product.destroy()

        self.products = []

    def setProcessed(self):
        self.status = ResponseStatus.PROCESSED
        self.__timerTTL = BigWorld.callback(self._CACHE_TTL, self.__onTTLTimer)

    def setFailed(self):
        self.status = ResponseStatus.FAILED

    def setFailedByTimeout(self):
        self.status = ResponseStatus.FAILED_BY_TIMEOUT

    def getProductByID(self, productID):
        return next((product for product in self.products if product.productID == productID), None)

    def _isStatus(self, status):
        return self.status == status

    def __onTTLTimer(self):
        self.__timerTTL = None
        self.reset()
        return

    def _clearTimeoutBwCbId(self):
        if self.__timerTTL is not None:
            BigWorld.cancelCallback(self.__timerTTL)
        self.__timerTTL = None
        return
