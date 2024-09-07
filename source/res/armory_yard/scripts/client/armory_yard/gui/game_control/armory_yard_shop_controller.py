# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/game_control/armory_yard_shop_controller.py
from constants import Configs
from Event import Event, EventManager
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.prb_control.entities.listener import IGlobalListener
from helpers import dependency
from skeletons.gui.game_control import IArmoryYardShopController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from armory_yard_constants import ARMORY_YARD_COIN_NAME, SHOP_PDATA_KEY, PDATA_KEY_ARMORY_YARD, SHOP_PRODUCT_LIMITS
CONFIG_SECTION_NAME = 'shop'

class ArmoryYardShopController(IArmoryYardShopController, IGlobalListener):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __guiLoader = dependency.descriptor(IGuiLoader)

    def __init__(self):
        self.__eventManager = EventManager()
        self.__products = {}
        self.onProductsUpdate = Event(self.__eventManager)
        self.onAYCoinsUpdate = Event(self.__eventManager)
        self.onSettingsUpdate = Event(self.__eventManager)
        self.onPurchaseComplete = Event(self.__eventManager)
        self.onPurchaseError = Event(self.__eventManager)
        super(ArmoryYardShopController, self).__init__()

    @property
    def __settings(self):
        return getattr(self.__lobbyContext.getServerSettings().armoryYard, CONFIG_SECTION_NAME, {})

    @property
    def ayCoins(self):
        return self.__itemsCache.items.stats.dynamicCurrencies.get(ARMORY_YARD_COIN_NAME, 0)

    @property
    def conversionPrices(self):
        return self.__settings.get('conversionPrices', {})

    @property
    def products(self):
        return self.__products

    @property
    def isSeasonCompleted(self):
        return self.__itemsCache.items.armoryYard.shopLastSeasonCompleted

    @property
    def isEnabled(self):
        return self.__settings.get('isEnabled', False)

    def __onServerSettingsChanged(self, diff):
        if CONFIG_SECTION_NAME in diff.get(Configs.ARMORY_YARD_CONFIG.value, {}):
            self.onSettingsUpdate()
            self.__productUpdate(self.__itemsCache.items.armoryYard.shopProductLimits)

    def __isCoinUpdate(self, diff):
        if ARMORY_YARD_COIN_NAME in diff.get('dynamicCurrencies', {}):
            self.onAYCoinsUpdate()

    def __limitsUpdate(self, diff=None):
        newLimits = diff.get(SHOP_PDATA_KEY, {}).get(SHOP_PRODUCT_LIMITS, None)
        if newLimits is None:
            return
        elif not newLimits:
            self.__productUpdate({})
            return
        else:
            for productId, pdataLimit in newLimits.iteritems():
                product = self.__products.get(productId, None)
                if product is not None:
                    if 'limit' in product and pdataLimit >= product['limit']:
                        del self.__products[productId]
                    else:
                        self.__products[productId]['currCount'] = pdataLimit

            self.onProductsUpdate()
            return

    def __productUpdate(self, limits):
        self.__products = {}
        for productId, productParams in self.__settings.get('products', {}).iteritems():
            limit = limits.get(productId, 0)
            if 'limit' in productParams and limit >= productParams['limit']:
                continue
            self.__products[productId] = productParams
            self.__products[productId]['currCount'] = limit

        self.onProductsUpdate()

    def __subscribe(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        g_clientUpdateManager.addCallbacks({'cache': self.__isCoinUpdate,
         PDATA_KEY_ARMORY_YARD: self.__limitsUpdate})

    def __unsubscribe(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged

    def isBundle(self, productId):
        productInfo = self.products.get(productId)
        return productInfo and 'exclusiveVehicle' in productInfo

    def fini(self):
        self.__unsubscribe()

    def onLobbyInited(self, event):
        self.__subscribe()
        self.__productUpdate(self.__itemsCache.items.armoryYard.shopProductLimits)

    def onAccountBecomeNonPlayer(self):
        self.__unsubscribe()
