# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/products_fetcher/controller.py
import typing
import json
import logging
from functools import partial
import BigWorld
import wg_async
from BWUtil import AsyncReturn
from adisp import adisp_process
from gui.Scaleform.Waiting import Waiting
from gui.platform.products_fetcher.fetch_result import FetchResult
from gui.platform.products_fetcher.product_descriptor import ProductDescriptor
from gui.wgcg.utils.contexts import PlatformFetchProductListCtx
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.platform.product_fetch_controller import IProductFetchController
from skeletons.gui.web import IWebController
from web.cache.web_downloader import WebDownloader
if typing.TYPE_CHECKING:
    from typing import List
_logger = logging.getLogger(__name__)

class _PlatformProductListParams(object):
    storefront = ''
    wgid = ''
    language = ''
    additional_data = ''
    country = ''
    response_fields = {'items': True}
    response_fields_profile = ''
    product_codes = []
    category = ''

    @wg_async.wg_async
    def setFields(self):
        yield wg_async.wg_await(self.setCountry())
        raise AsyncReturn(None)
        return

    @wg_async.wg_async
    def setCountry(self):
        self.country = ''
        raise AsyncReturn(None)
        return

    def __repr__(self):
        return 'storefront: {storefront} country: {country}, language: {language}'.format(storefront=self.storefront, country=self.country, language=self.language)


class ProductsDownloader(object):
    _DOWNLOAD_WORKERS_LIMIT = 2
    _TIMEOUT = 30

    def __init__(self):
        self.__downloader = None
        self.__downloadQueue = {}
        self.__onFinishCallback = None
        self.__timeoutTimer = None
        return

    def download(self, products, callback):
        self.__onFinishCallback = callback
        self.__downloadQueue.clear()
        self.__downloader = WebDownloader(self._DOWNLOAD_WORKERS_LIMIT)
        self.__timeoutTimer = BigWorld.callback(self._TIMEOUT, self.__onTimeoutTimer)
        for product in products:
            _logger.debug('Download product with url %s', product.productUrl)
            self.__downloadQueue[product.productUrl] = product
            self.__downloader.download(product.productUrl, self._onProductDownloaded)

    def stop(self):
        self.__destroyTimer()
        self.__downloadQueue.clear()
        if self.__downloader:
            self.__downloader.close()

    def _onProductDownloaded(self, url, productData):
        _logger.debug('Product with url=%s downloaded', url)
        product = self.__downloadQueue.pop(url, None)
        if product:
            descrData = json.loads(productData)
            product.extendData(descrData)
        else:
            _logger.warning('Product with url=%s has been downloaded but not found in queue', url)
        if self.__isDownloadQueueEmpty:
            _logger.debug('Download queue is over')
            self.stop()
            if self.__onFinishCallback and callable(self.__onFinishCallback):
                self.__onFinishCallback(True)
            else:
                _logger.warning('Download queue is over but callback is None or not callable')
        return

    @property
    def __isDownloadQueueEmpty(self):
        return len(self.__downloadQueue) == 0

    def __destroyTimer(self):
        if self.__timeoutTimer is not None:
            BigWorld.cancelCallback(self.__timeoutTimer)
        self.__timeoutTimer = None
        return

    def __onTimeoutTimer(self):
        self.__destroyTimer()
        if not self.__isDownloadQueueEmpty:
            if self.__onFinishCallback and callable(self.__onFinishCallback):
                self.__onFinishCallback(False)


class ProductsFetchController(IProductFetchController):
    _webCtrl = dependency.descriptor(IWebController)
    _connectionMgr = dependency.descriptor(IConnectionManager)
    platformParams = _PlatformProductListParams
    platformFetchCtx = PlatformFetchProductListCtx
    defaultProductDescriptor = ProductDescriptor
    productIDToDescriptor = {}
    dataGetKey = 'items'

    def __init__(self):
        self.__downloader = None
        self._fetchResult = None
        return

    def init(self):
        self.__downloader = ProductsDownloader()
        self._fetchResult = FetchResult()
        self._connectionMgr.onDisconnected += self._onDisconnect

    def fini(self):
        self.__downloader.stop()
        self._fetchResult.stop()
        self._connectionMgr.onDisconnected -= self._onDisconnect

    @property
    def isProductsReady(self):
        return self._fetchResult.isProductsReady

    @wg_async.wg_async
    def getProducts(self, showWaiting=True):
        _logger.debug('Trying to fetch products')
        if self._fetchResult.isProductsReady:
            _logger.debug('Return products from cache')
            raise AsyncReturn(self._fetchResult)
        if showWaiting:
            Waiting.show('loadingData')
        self._fetchResult.reset()
        params = self.platformParams()
        yield wg_async.wg_await(params.setFields())
        requestSuccess, productsData = yield wg_async.await_callback(partial(self._requestProducts, params))()
        if requestSuccess and productsData:
            _logger.debug('Products request has been successfully processed. Downloading additional data')
            self._createDescriptors(productsData)
            yield wg_async.await_callback(partial(self.__downloader.download, self._fetchResult.products))()
            self._fetchResult.setProcessed()
        else:
            self._fetchResult.setFailed()
        if showWaiting:
            Waiting.hide('loadingData')
        raise AsyncReturn(self._fetchResult)

    @adisp_process
    def _requestProducts(self, params, callback):
        ctx = self.platformFetchCtx(params)
        _logger.debug('Request products for params %s', params)
        response = yield self._webCtrl.sendRequest(ctx=ctx)
        data = response.getData()
        items = data.get(self.dataGetKey) if data else None
        callback((response.isSuccess(), items))
        return

    def _createDescriptors(self, productsData):
        for data in productsData:
            productCode = data.get('product_code', '')
            descriptor = next((v for k, v in self.productIDToDescriptor.items() if productCode.startswith(k)), self.defaultProductDescriptor)
            self._fetchResult.products.append(descriptor(data))

    def _onDisconnect(self):
        if self.__downloader:
            self.__downloader.stop()
        self._fetchResult.stop()
