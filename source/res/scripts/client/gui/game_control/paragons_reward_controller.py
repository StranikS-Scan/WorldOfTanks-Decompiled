# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/paragons_reward_controller.py
import copy
from enum import Enum
import logging
import th_async
import typing
import Event
import adisp
from BWUtil import AsyncReturn
from gui.impl.lobby.paragons.paragons_helpers.entitlements_helpers import ParagonsEntitlementsContext
from gui.clientgw.shop import contexts as shop_contexts
from gui.clientgw.web_controller import WebController
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared.gui_items.processors.paragons import MarkSelectedRewardsProcessor
from helpers import dependency
from paragons_common import PARAGONS_STOREFRONT_SHOP, PARAGONS_ENTITLEMENT_TO_NUMBER_CODES, FRIEND_ENT_CODES, getSelectedRewardTokenTemplate
from shared_utils import findFirst
from skeletons.gui.game_control import IParagonsRewardsShopController
from skeletons.gui.web import IWebController
from skeletons.gui.shared import IItemsCache
from paragons_common import PARAGONS_SELECTED_REWARD_TOKEN_PREFIX
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
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(ParagonsRewardsShopController, self).__init__()
        self.__entitlementsContext = ParagonsEntitlementsContext()
        self.__products = {}
        self.__productsState = ProductsStates.EMPTY
        self.__requestState = RequestStates.INIT
        self.__asyncScope = th_async.AsyncScope()
        self.__asyncEvent = th_async.AsyncEvent(scope=self.__asyncScope)
        self.__callbacks = []
        self.__selectedTokenIsWaited = False
        self.onSelectableRewardReceived = Event.Event()

    def fini(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__asyncScope.destroy()

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

    @adisp.adisp_process
    def buyProduct(self, productCode, callback=lambda x: x):
        res = yield self.__buyProduct(productCode)
        callback(res)

    def findSelectedRewardToken(self, entCode):
        for friendCode in FRIEND_ENT_CODES.get(entCode, (entCode,)):
            tokenTemplate = getSelectedRewardTokenTemplate(friendCode)
            token = findFirst(lambda t: t.startswith(tokenTemplate), self.__itemsCache.items.tokens.getTokens(), None)
            if token:
                return token

        return

    def tryMarkSelectedReward(self, chapterID, levelID, entitlementID):
        if not self.entitlements.isCached():
            return
        elif self.entitlements.getEntitlementsByID(entitlementID) > 0:
            return
        elif self.__selectedTokenIsWaited:
            return
        else:
            entCode = PARAGONS_ENTITLEMENT_TO_NUMBER_CODES.get(entitlementID)
            selectedRewardToken = self.findSelectedRewardToken(entCode)
            if selectedRewardToken is not None:
                _logger.info('[Paragons]: tryMarkSelectedReward %s %s %s %s', chapterID, levelID, entitlementID, selectedRewardToken)
                self.__markReward(chapterID, levelID, entitlementID, selectedRewardToken)
            return

    @adisp.adisp_process
    def __markReward(self, chapterID, levelID, entitlementID, tokenId):
        res = yield MarkSelectedRewardsProcessor(chapterID, levelID, entitlementID, tokenId).request()
        if not res.success:
            _logger.error('[Paragons]: markReward failed %s', res)
        _logger.info('[Paragons]: rewardMarked %s', res)

    @th_async.th_async
    def buyProductAndMarkReward(self, productCode, chapterID, levelID, entitlementID):
        self.__asyncEvent.clear()
        self.__selectedTokenIsWaited = True
        try:
            res = yield th_async.await_callback(self.buyProduct)(productCode)
            isSuccess, _ = res
            if isSuccess:
                if not self.__asyncEvent.is_set():

                    def _markReward(diff):
                        tokenID = findFirst(lambda t: t.startswith(PARAGONS_SELECTED_REWARD_TOKEN_PREFIX), diff)
                        if tokenID is not None and diff[tokenID] > 0:
                            self.__markReward(chapterID, levelID, entitlementID, tokenID)
                            self.__asyncEvent.set()
                        return

                    g_clientUpdateManager.addCallback('tokens', _markReward)
                    yield th_async.th_await(self.__asyncEvent.wait(), timeout=10)
                    g_clientUpdateManager.removeCallback('tokens', _markReward)
        finally:
            self.__selectedTokenIsWaited = False

        raise AsyncReturn(res)

    def onAccountBecomePlayer(self):
        self.__selectedTokenIsWaited = False
        self.entitlements.init()

    def onAccountBecomeNonPlayer(self):
        self.entitlements.fin()

    def onDisconnected(self):
        self.__products = {}
        self.__productsState = ProductsStates.EMPTY
        self.__releaseCallbacks(False)
        self.__selectedTokenIsWaited = False

    def selectableRewardReceived(self, data):
        self.onSelectableRewardReceived(data)

    def isValidProduct(self, product, entitlementID):
        currency = product.get('price', {}).get('currency')
        return entitlementID == currency

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
        return self.entitlements.getEntitlementsByID(currency) >= price

    def __releaseCallbacks(self, ctx=True):
        for callback in self.__callbacks:
            callback(ctx)

        self.__callbacks = []
