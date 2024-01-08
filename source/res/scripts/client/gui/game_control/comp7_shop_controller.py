# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/comp7_shop_controller.py
import logging
from collections import namedtuple
import typing
from BWUtil import AsyncReturn
from enum import Enum
from shared_utils import findFirst
import Event
from gui.SystemMessages import SM_TYPE, pushMessage
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.comp7.base_product_model import Rank
from gui.impl.lobby.comp7 import comp7_shared
from gui.platform.products_fetcher.wot_shop.fetch_result import ResponseData, ResponseStatus
from gui.wgcg.wot_shop.controller import IWotShopController
from helpers import dependency
from skeletons.gui.game_control import IComp7ShopController, IComp7Controller
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.platform.product_purchase_controller import WotShopPrice
from wg_async import wg_await, wg_async
if typing.TYPE_CHECKING:
    from typing import List, Dict, Optional
    from gui.platform.products_fetcher.wot_shop.descriptors.product_descriptor import ProductDescriptor
    from gui.platform.products_fetcher.wot_shop.descriptors.account_limits_descriptor import AccountLimitsDescriptor
    from gui.platform.products_fetcher.wot_shop.descriptors.categories_descriptor import CategoriesDescriptor
    from helpers.server_settings import Comp7RanksConfig
_logger = logging.getLogger(__name__)
ShopPageProductInfo = namedtuple('_ShopPageProductInfo', ('code', 'description', 'rank', 'category', 'purchasable', 'entitlements', 'currencyName', 'originalPrice', 'discountPrice', 'limitedQuantity', 'limitsPurchaseAllowed', 'discounts'))

class ShopControllerStatus(Enum):
    IDLE = 'idle'
    PENDING = 'pending'
    DATA_READY = 'data_ready'
    ERROR = 'error'


class Comp7ShopController(IComp7ShopController):
    __shopController = dependency.descriptor(IWotShopController)
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __lobbyCtx = dependency.descriptor(ILobbyContext)
    __PRODUCTS_STOREFRONT = 'comp7_shop'

    def __init__(self):
        super(Comp7ShopController, self).__init__()
        self.__products = None
        self.__categoriesDiscounts = None
        self.__ranksDiscounts = None
        self.__categoriesToRanks = None
        self.__ranksToCategories = None
        self.__notifiedRanks = None
        self.__status = None
        self.__isShopEnabled = None
        self.__eventsManager = Event.EventManager()
        self.onDataUpdated = Event.Event(self.__eventsManager)
        self.onShopStateChanged = Event.Event(self.__eventsManager)
        return

    @property
    def isShopEnabled(self):
        return self.__isShopEnabled

    def init(self):
        super(Comp7ShopController, self).init()
        self.__products = {}
        self.__categoriesDiscounts = {}
        self.__ranksDiscounts = {}
        self.__categoriesToRanks = {}
        self.__ranksToCategories = {}
        self.__notifiedRanks = []
        self.__status = ShopControllerStatus.IDLE
        self.__isShopEnabled = False

    def fini(self):
        super(Comp7ShopController, self).fini()
        self.__products = None
        self.__categoriesDiscounts = None
        self.__ranksDiscounts = None
        self.__categoriesToRanks = None
        self.__ranksToCategories = None
        self.__notifiedRanks = None
        self.__status = None
        self.__isShopEnabled = None
        return

    def onConnected(self):
        self.__comp7Controller.onHighestRankAchieved += self.__onHighestRankAchieved
        self.__comp7Controller.onComp7ConfigChanged += self.__onConfigChanged

    def onDisconnected(self):
        self.__comp7Controller.onHighestRankAchieved -= self.__onHighestRankAchieved
        self.__comp7Controller.onComp7ConfigChanged -= self.__onConfigChanged
        self.__status = None
        self.__products.clear()
        self.__ranksToCategories.clear()
        self.__categoriesToRanks.clear()
        self.__categoriesDiscounts.clear()
        self.__ranksDiscounts.clear()
        self.__notifiedRanks = []
        self.__isShopEnabled = None
        return

    @wg_async
    def __requestProducts(self, force=False):
        if not self.isShopEnabled:
            return
        if self.__status in (ShopControllerStatus.PENDING, ShopControllerStatus.DATA_READY) and not force:
            return
        self.__setStatus(ShopControllerStatus.PENDING)
        response = yield wg_await(self.__shopController.fetchProducts(self.__PRODUCTS_STOREFRONT, force))
        if not self.__isResponseReadyToProcess(response):
            self.__resetCache()
            self.__setStatus(ShopControllerStatus.ERROR)
            return
        try:
            self.__processShopResponse(response)
            self.__setStatus(ShopControllerStatus.DATA_READY)
        except Exception as e:
            logging.error('An exception has occurred while processing shop response: %s', e)
            self.__setStatus(ShopControllerStatus.ERROR)

    def getProducts(self):
        if not self.__products:
            forceFetch = self.__status == ShopControllerStatus.DATA_READY
            self.__requestProducts(forceFetch)
        return self.__products

    @wg_async
    def buyProduct(self, productCode):
        product = self.__products.get(productCode)
        if not product:
            raise AsyncReturn(False)
        expectedPrice = product.discountPrice or product.originalPrice
        result = yield self.__shopController.buyProduct(self.__PRODUCTS_STOREFRONT, productCode, expectedPrice=WotShopPrice(product.currencyName, expectedPrice))
        if result:
            self.__requestProducts(force=True)
        else:
            self.__sendPurchaseErrorSystemMessage()
        raise AsyncReturn(result)

    def hasNewProducts(self, rank):
        if not self.__products:
            return False
        categoryCode = self.__ranksToCategories[rank]
        for product in self.__products.values():
            if product.category == categoryCode and product.purchasable:
                return True

        return False

    def hasNewDiscounts(self, newRank):
        config = self.__lobbyCtx.getServerSettings().comp7RanksConfig
        prevRankDiscounts = {}
        currentRankDiscounts = {}
        for rankId in config.ranksOrder:
            rank = comp7_shared.getRankById(rankId)
            discounts = self.__ranksDiscounts.get(rank, {})
            if rank != newRank:
                prevRankDiscounts = discounts
            currentRankDiscounts = discounts
            break

        prevRankDiscounts = {k:v for k, v in prevRankDiscounts.iteritems() if v > 0}
        currentRankDiscounts = {k:v for k, v in currentRankDiscounts.iteritems() if v > 0}
        return prevRankDiscounts != currentRankDiscounts

    @wg_async
    def __onHighestRankAchieved(self, *_, **__):
        if not self.isShopEnabled:
            return
        rank = comp7_shared.getRankEnumValue(comp7_shared.getPlayerDivision())
        if rank in self.__notifiedRanks:
            return
        self.__notifiedRanks.append(rank)
        yield self.__requestProducts(force=True)
        if self.hasNewProducts(rank):
            self.__sendNewProductsForRankMessage()
        if self.hasNewDiscounts(rank):
            self.__sendNewDiscountsForRankMessage()

    def __onConfigChanged(self):
        config = self.__comp7Controller.getModeSettings()
        isShopEnabled = config is not None and config.isShopEnabled
        if self.__isShopEnabled != isShopEnabled:
            self.__isShopEnabled = isShopEnabled
            self.onShopStateChanged()
            if not self.__isShopEnabled:
                self.__resetCache()
        return

    def __resetCache(self):
        self.__products.clear()
        self.__ranksToCategories.clear()
        self.__categoriesToRanks.clear()
        self.__categoriesDiscounts.clear()
        self.__ranksDiscounts.clear()

    def __setStatus(self, status):
        self.__status = status
        self.onDataUpdated(status)

    def __processShopResponse(self, response):
        products = response.products
        accountLimits = response.accountLimits
        categories = response.categories
        self.__convertCategoriesToRanks(categories)
        self.__processDiscounts(categories)
        self.__convertProducts(products, accountLimits)

    def __convertCategoriesToRanks(self, categories):
        self.__categoriesToRanks.clear()
        self.__ranksToCategories.clear()
        config = self.__lobbyCtx.getServerSettings().comp7RanksConfig
        for idx, category in enumerate(categories):
            rankId = config.ranksOrder[idx]
            rank = comp7_shared.getRankById(rankId)
            self.__categoriesToRanks[category.code] = rank
            self.__ranksToCategories[rank] = category.code

    def __processDiscounts(self, categories):
        self.__categoriesDiscounts.clear()
        self.__ranksDiscounts.clear()
        for category in categories:
            discounts = category.metadata.get('rank_discounts', {})
            rank = self.__categoriesToRanks[category.code]
            self.__categoriesDiscounts[rank] = discounts
            for rankName, rankDiscount in discounts.iteritems():
                rank = comp7_shared.getRankByName(rankName)
                rankDiscounts = self.__ranksDiscounts.setdefault(rank, {})
                rankDiscounts[category.code] = rankDiscount

    def __convertProducts(self, products, accountLimits):
        self.__products.clear()
        for product in products:
            productCode = product.productCode
            productRank = self.__categoriesToRanks.get(product.category)
            if not productRank:
                _logger.warning('No rank for category %s at product %s', product.category, productCode)
                continue
            limitsData = findFirst(lambda limit, code=productCode: limit.productCode == code, accountLimits)
            if not limitsData:
                _logger.warning('No limits data for product %s', productCode)
                continue
            entitlements = {}
            for entitlement in product.entitlements:
                cd = entitlement.get('cd', 0)
                if not cd:
                    continue
                entitlements[int(cd)] = entitlement['type']

            self.__products[productCode] = ShopPageProductInfo(code=productCode, description=product.description, rank=productRank, category=product.category, purchasable=product.purchasable, entitlements=entitlements, currencyName=product.currencyName, originalPrice=product.originalPrice, discountPrice=product.discountPrice, limitedQuantity=limitsData.personalLimit - limitsData.personalCount, limitsPurchaseAllowed=limitsData.purchaseAllowed, discounts=self.__categoriesDiscounts[productRank])

    def __isResponseReadyToProcess(self, response):
        return False if response.status != ResponseStatus.PROCESSED else response.products and response.categories and response.accountLimits

    def __sendPurchaseErrorSystemMessage(self):
        pushMessage(type=SM_TYPE.ErrorSimple, text=backport.text(R.strings.comp7.system_messages.shop.purchase.error()))

    def __sendNewProductsForRankMessage(self):
        pushMessage(type=SM_TYPE.Comp7ShopItemsAvailableForRank, text=backport.text(R.strings.comp7.system_messages.shop.offer.newItems.body()), messageData={'header': backport.text(R.strings.comp7.system_messages.shop.offer.newItems.title())})

    def __sendNewDiscountsForRankMessage(self):
        pushMessage(type=SM_TYPE.Comp7ShopItemsAvailableForRank, text=backport.text(R.strings.comp7.system_messages.shop.offer.newDiscounts.body()), messageData={'header': backport.text(R.strings.comp7.system_messages.shop.offer.newDiscounts.title())})
