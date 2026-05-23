# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/summer_sale_controller.py
import logging
from copy import deepcopy
from json import loads
from enum import IntEnum
from typing import TYPE_CHECKING
from adisp import adisp_async, adisp_process
from gui.clientgw.shop.contexts import ShopBuyStorefrontProductCtx, ShopStorefrontProductsCtx
from gui.game_control.events_notifications import EventNotification
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getShopURL
from helpers import dependency
from helpers.time_utils import ONE_DAY, getDateTimeInLocal, getServerUTCTime, getTimestampByStrDate, getTimestampFromLocal
from skeletons.gui.game_control import IEventsNotificationsController, ISummerSaleController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.web import IWebController
import Event
if TYPE_CHECKING:
    from typing import Any, Callable, Dict, Generator, Tuple
_logger = logging.getLogger(__name__)
EVENT_TYPE_NAME = 'SummerSale'
SUMMER_SALE_STOREFRONT_SHOP = 'summersale_store'
_ENDING_TIME_OFFSET = ONE_DAY * 1
SUMMER_SALE_EVENT_STATE = {'Active': 'Active',
 'Disabled': 'Disabled'}

class ProductsStates(IntEnum):
    EMPTY = 0
    CACHED = 1
    ACTUAL = 2


class RequestStates(IntEnum):
    INIT = 0
    FETCHING = 1


def eventActionsFilter(action):
    return action.eventType == EVENT_TYPE_NAME


class SummerSaleController(ISummerSaleController):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __notificationsCtrl = dependency.descriptor(IEventsNotificationsController)
    __webCtrl = dependency.descriptor(IWebController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(SummerSaleController, self).__init__()
        self.__eManager = Event.EventManager()
        self.onEventSettingsUpdated = Event.Event(self.__eManager)
        self.__endDate = None
        self.__startDate = None
        self.__questGroupId = None
        self.__shopPageUrl = None
        self.__productTag = None
        self.__randomVehicleObtainedToken = None
        self.__eventState = None
        self.__productsState = ProductsStates.EMPTY
        self.__requestState = RequestStates.INIT
        self.__summerSaleSetInfo = {}
        self.__summerSaleVehiclesSetInfo = {}
        self.__productsOrder = {}
        self.__products = {}
        self.__callbacks = []
        return

    def onDisconnected(self):
        self.__products = {}
        self.__productsState = ProductsStates.EMPTY
        self.__releaseCallbacks(False)
        self.__eManager.clear()

    def getStartTime(self):
        return self.__startDate

    def getExpiryTime(self):
        return self.__endDate

    def getQuestGroupId(self):
        return self.__questGroupId

    def getProductTag(self):
        return self.__productTag

    def isEnabled(self):
        currentTime = getServerUTCTime()
        return self.__eventState == SUMMER_SALE_EVENT_STATE['Active'] and self.__startDate <= currentTime < self.__endDate

    def isRandomVehicleObtained(self):
        return self.__itemsCache.items.tokens.getToken(self.__randomVehicleObtainedToken) is not None

    def isFinished(self):
        currentTime = getServerUTCTime()
        return currentTime >= self.__endDate

    def isEnding(self):
        currentTime = getServerUTCTime()
        return self.isEnabled() and currentTime >= self.__endDate - _ENDING_TIME_OFFSET

    def getShopPageUrl(self):
        return self.__shopPageUrl

    def getSummerSaleSetType(self):
        return self.__summerSaleSetInfo['type']

    def getSummerSaleSetProductCode(self):
        return self.__summerSaleSetInfo['productCode']

    def getSummerSaleSetCategory(self):
        return self.__summerSaleSetInfo['category']

    def getSummerSaleVehiclesSetType(self):
        return self.__summerSaleVehiclesSetInfo['type']

    def getSummerSaleVehicleSetProductCode(self):
        return self.__summerSaleVehiclesSetInfo['productCode']

    def getSummerSaleVehicleSetCategory(self):
        return self.__summerSaleVehiclesSetInfo['category']

    def getProductsOrder(self):
        return deepcopy(self.__productsOrder)

    def getBalance(self, currency):
        return self.__itemsCache.items.stats.dynamicCurrencies.get(currency, 0)

    def onLobbyInited(self, event):
        self.__processAction()
        self.__notificationsCtrl.onEventNotificationsChanged += self.__processAction

    def onAccountBecomeNonPlayer(self):
        self.__notificationsCtrl.onEventNotificationsChanged -= self.__processAction

    def onAvatarBecomePlayer(self):
        self.__eManager.clear()

    def getLocalEndDate(self):
        return getTimestampFromLocal(getDateTimeInLocal(self.getExpiryTime()).timetuple())

    @adisp_async
    @adisp_process
    def fetchProducts(self, callback=lambda x: x):
        if not self.__products:
            yield self.__getProducts(action='Fetch')
        else:
            self.__productsState = ProductsStates.CACHED
            _logger.info('Prefetch done: products state: %s', self.__productsState.name)
        callback((self.__productsState, self.__products))

    @adisp_async
    @adisp_process
    def buyProduct(self, productCode, count=1, callback=lambda x: x):
        res = yield self.__buyProduct(productCode, count)
        callback(res)

    def __processAction(self, *args, **kwargs):
        actionData = self.__notificationsCtrl.getEventsNotifications(filterFunc=eventActionsFilter)
        if actionData:
            action = loads(actionData[0].data)
            state = action['eventState'] if action['eventState'] in SUMMER_SALE_EVENT_STATE else SUMMER_SALE_EVENT_STATE['Disabled']
            self.__eventState = state
            if getTimestampByStrDate(action['startDate']) > getTimestampByStrDate(action['endDate']):
                _logger.error('Wrong SummerSale time date range')
            else:
                self.__startDate = getTimestampByStrDate(action['startDate'])
                self.__endDate = getTimestampByStrDate(action['endDate'])
            self.__questGroupId = action['questGroupId']
            self.__productTag = action['productTag']
            self.__randomVehicleObtainedToken = action['randomVehicleObtainedToken']
            self.__shopPageUrl = '/'.join((getShopURL(), action['shopPage']))
            self.__summerSaleSetInfo = action['summerSaleSet']
            self.__summerSaleVehiclesSetInfo = action['summerSaleVehiclesSet']
            self.__productsOrder = {productCode:order for order, productCode in enumerate(action['productsOrder'])}
        else:
            self.__eventState = SUMMER_SALE_EVENT_STATE['Disabled']
        self.onEventSettingsUpdated()

    @adisp_async
    @adisp_process
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
        ctx = ShopStorefrontProductsCtx(storefront=SUMMER_SALE_STOREFRONT_SHOP, userCountry='ru')
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

    @adisp_async
    @adisp_process
    def __buyProduct(self, productCode, count, callback=lambda x: x):
        isSuccess = False
        if not self.__webCtrl.isEnabled() and self.__webCtrl.isAvailable() and self.__webCtrl.isStarted:
            callback((isSuccess, productCode))
            return
        product = self.__products.get(productCode)
        if not product:
            _logger.warning('Product %s not found', productCode)
            callback((False, productCode))
            return
        priceInfo = product.get('price', {})
        currencyCode = priceInfo.get('currency')
        price = priceInfo.get('amount', 0) * count
        if not self.__isEnoughToBuy(currencyCode, price):
            _logger.info('Attempting purchase product %s: FAILED - not enough balance', productCode)
            callback((isSuccess, productCode))
            return
        ctx = ShopBuyStorefrontProductCtx(storefront=SUMMER_SALE_STOREFRONT_SHOP, productCode=productCode, userCountry='ru', amount=count, prices=[{'code': currencyCode,
          'amount': price,
          'item_type': 'currency'}])
        result = yield self.__webCtrl.sendRequest(ctx)
        isSuccess = result.isSuccess()
        _logger.info('Attempting purchase product %s: %s', productCode, 'Success' if isSuccess else 'Failed')
        callback((isSuccess, productCode))

    def __parseProductData(self, data):
        parsedData = {}
        price = {'currency': data['price']['currency'],
         'amount': data['price']['value']}
        parsedData['price'] = price
        parsedData['tags'] = data['tags']
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
        return self.getBalance(currency) >= price

    def __releaseCallbacks(self, ctx=True):
        for callback in self.__callbacks:
            callback(ctx)

        self.__callbacks = []
