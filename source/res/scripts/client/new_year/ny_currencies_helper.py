# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_currencies_helper.py
import typing
from gui.ClientUpdateManager import g_clientUpdateManager
from Event import Event, EventManager
from gui.shared.money import DynamicMoney
from helpers import dependency
from new_year.gift_machine_helper import getCoinType, getCoinToken
from new_year.ny_helper import getNYGeneralConfig
from skeletons.gui.shared import IItemsCache
from items.components.ny_constants import NyCurrency
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.loot_box import LootBox

class NyCurrenciesHelper(object):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        self.__balance = DynamicMoney()
        self._eManager = EventManager()
        self.onBalanceUpdated = Event(self._eManager)
        self.onNyCoinsUpdate = Event(self._eManager)
        self.__coinsCount = None
        return

    def onLobbyInited(self):
        self.__initBalanceCurrencies()
        self.__updateCoinsCount()
        self.__addEventHandlers()

    def clear(self):
        self.__removeEventHandlers()

    def __addEventHandlers(self):
        g_clientUpdateManager.addCallbacks({'cache.dynamicCurrencies': self.__updateDynamicCurrencies,
         'tokens': self.__onTokensChanged})

    def getResourceConverterCoefficients(self):
        generalConfig = getNYGeneralConfig()
        return generalConfig.getResourceConverterCoefficients()

    def calculateInitialValueByReceived(self, value):
        generalConfig = getNYGeneralConfig()
        return generalConfig.calculateInitialValueByReceived(value)

    def __removeEventHandlers(self):
        g_clientUpdateManager.removeObjectCallbacks(self)

    def getResourcesBalance(self):
        return {currency:self.getResouceBalance(currency) for currency in NyCurrency.ALL}

    def getResouceBalance(self, currencyCode, default=0):
        return int(self.__balance.get(currencyCode, default))

    def getCoins(self):
        for lootBox in self.__itemsCache.items.tokens.getLootBoxes().values():
            if lootBox.getType() == getCoinType():
                return lootBox

        return None

    def getCoinsCount(self):
        return self.__coinsCount

    def __initBalanceCurrencies(self):
        self.__updateBalanceCurrencies()
        self.onBalanceUpdated()

    def __updateBalanceCurrencies(self):
        self.__balance = self.__itemsCache.items.stats.getDynamicMoney()

    def __updateDynamicCurrencies(self, currencies):
        changed = [ currency for currency in currencies.keys() if currency in NyCurrency.ALL ]
        if not changed:
            return
        for currency in changed:
            if self.getResouceBalance(currency) != currencies.get(currency, 0):
                self.__updateBalanceCurrencies()
                self.onBalanceUpdated()
                return

    def __onTokensChanged(self, tokens):
        coinToken = getCoinToken()
        if any((token for token in tokens if token == coinToken)):
            self.__updateCoinsCount()
            self.onNyCoinsUpdate()

    def __updateCoinsCount(self):
        coins = self.getCoins()
        self.__coinsCount = coins.getInventoryCount() if coins else 0
