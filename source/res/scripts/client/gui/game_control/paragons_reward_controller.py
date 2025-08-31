# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/paragons_reward_controller.py
import copy
from enum import Enum
import logging
import typing
import Event
import adisp
from gui.impl.lobby.paragons.paragons_helpers.entitlements_helpers import ParagonsEntitlementsContext
from gui.clientgw.shop import contexts as shop_contexts
from gui.clientgw.web_controller import WebController
from helpers import dependency
from paragons_common import PARAGONS_STOREFRONT_SHOP
from skeletons.gui.game_control import IParagonsRewardsShopController
from skeletons.gui.web import IWebController
_logger = logging.getLogger(__name__)

class ProductsStates(Enum):
    EMPTY = 0
    CACHED = 1
    ACTUAL = 2


class RequestStates(Enum):
    INIT = 0
    FETCHING = 1


class ParagonsRewardsShopController(IParagonsRewardsShopController):
    __webCtrl = dependency.descriptor(IWebController)

    def __init__(self):
        super(ParagonsRewardsShopController, self).__init__()
        self.__entitlementsContext = ParagonsEntitlementsContext()
        self.__products = {}
        self.__productsState = ProductsStates.EMPTY
        self.__requestState = RequestStates.INIT
        self.__callbacks = []
        self.onSelectableRewardReceived = Event.Event()

    @property
    def entitlements(self):
        return self.__entitlementsContext.state

    @adisp.adisp_async
    @adisp.adisp_process
    def getProducts(self, callback=lambda x: x):
        if not self.__products:
            requestStatus, result = yield self.__getProducts(action='Load')
            if requestStatus:
                result = copy.deepcopy(result)
            callback((self.__productsState, result))
        else:
            self.__productsState = ProductsStates.CACHED
            _logger.info('Load done: products state: %s', self.__productsState.name)
            callback((self.__productsState, copy.deepcopy(self.__products)))

    @adisp.adisp_async
    @adisp.adisp_process
    def fetchProducts(self, callback=lambda x: x):
        if not self.__products:
            yield self.__getProducts(action='Prefetch')
        else:
            self.__productsState = ProductsStates.CACHED
            _logger.info('Prefetch done: products state: %s', self.__productsState.name)
        callback((self.__productsState, self.__products))

    @adisp.adisp_async
    @adisp.adisp_process
    def buyProduct(self, productCode, callback=lambda x: x):
        res = yield self.__buyProduct(productCode)
        callback(res)

    def onAccountBecomePlayer(self):
        self.entitlements.init()

    def onAccountBecomeNonPlayer(self):
        self.entitlements.fin()

    def onDisconnected(self):
        self.__products = {}
        self.__productsState = ProductsStates.EMPTY
        self.__releaseCallbacks(False)

    def selectableRewardReceived(self, data):
        self.onSelectableRewardReceived(data)

    @adisp.adisp_async
    @adisp.adisp_process
    def __getProducts(self, action, callback):
        _logger.info('%s available selectable rewards products', action)
        isSuccess = False
        if not self.__webCtrl.isEnabled() and self.__webCtrl.isAvailable() and self.__webCtrl.isStarted:
            callback((isSuccess, self.__products))
            return
        if self.__requestState == RequestStates.FETCHING:
            _logger.info('%s already in progress!', action)
            self.__callbacks.append(callback)
            return
        self.__requestState = RequestStates.FETCHING
        self.__callbacks.append(callback)
        ctx = shop_contexts.ShopStorefrontProductsCtx(storefront=PARAGONS_STOREFRONT_SHOP, userCountry='ru')
        result = yield self.__webCtrl.sendRequest(ctx)
        if result.isSuccess():
            isSuccess = True
            self.__productsState = ProductsStates.ACTUAL
            data = ctx.getDataObj(result.data).get('data', [])
            for product in data:
                self.__parseProductData(product)

            if not self.__products:
                self.__productsState = ProductsStates.EMPTY
        else:
            self.__productsState = ProductsStates.EMPTY
        _logger.info('%s %s: Products state: %s', action, 'done' if isSuccess else 'failed', self.__productsState.name)
        self.__requestState = RequestStates.INIT
        self.__releaseCallbacks((isSuccess, self.__products))

    @adisp.adisp_async
    @adisp.adisp_process
    def __buyProduct(self, productCode, callback=lambda x: x):
        _logger.info('Attempting purchase product %s', productCode)
        isSuccess = False
        if not self.__webCtrl.isEnabled() and self.__webCtrl.isAvailable() and self.__webCtrl.isStarted:
            callback((isSuccess, productCode))
            return
        product = self.__products[productCode]
        entCode = product['price']['currency']
        price = product['price']['amount']
        if not self.__isEnoughToBuy(entCode, price):
            _logger.info('Attempting purchase product %s: FAILED - not enough Ent balance', productCode)
            callback((isSuccess, productCode))
            return
        ctx = shop_contexts.ShopBuyStorefrontProductCtx(storefront=PARAGONS_STOREFRONT_SHOP, productCode=productCode, userCountry='ru', prices=[{'code': entCode,
          'amount': price,
          'item_type': 'entitlement'}])
        result = yield self.__webCtrl.sendRequest(ctx)
        if result.isSuccess():
            isSuccess = True
            self.__products.pop(productCode)
            self.entitlements.update()
            self.entitlements.consumeGranted(entCode)
        _logger.info('Attempting purchase product %s: %s', productCode, 'Success' if isSuccess else 'Failed')
        callback((isSuccess, productCode))

    def __parseProductData(self, data):
        parsedData = {}
        price = {'currency': data['price']['currency'],
         'amount': data['price']['value']}
        parsedData['price'] = price
        for item in data['entitlements']:
            if item['type'].startswith('vehicle/'):
                parsedData['vehicleCD'] = int(item['cd'])
                continue
            if item['type'].startswith('token/'):
                parsedData['token'] = {'cd': item['cd'],
                 'amount': item['amount']}
                continue

        productCode = data['code']
        self.__products[productCode] = parsedData

    def __isEnoughToBuy(self, currency, price):
        return self.entitlements.getEntitlementsByID(currency) >= price

    def __releaseCallbacks(self, ctx=True):
        for callback in self.__callbacks:
            callback(ctx)

        self.__callbacks = []
