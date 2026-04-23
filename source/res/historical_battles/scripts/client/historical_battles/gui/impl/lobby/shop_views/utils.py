# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/shop_views/utils.py
import typing
from historical_battles_common.hb_constants import EventShop
from helpers.dependency import replace_none_kwargs
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from historical_battles_common.helpers_common import EventShopBundlePrice
    from typing import Iterable

@replace_none_kwargs(gameEventController=IGameEventController)
def getCurrentCurrencyCount(price, gameEventController=None, itemsCache=None):
    if price.currencyType == EventShop.CurrencyType.VIRTUAL:
        currencyType, count = gameEventController.coins.getNameAndCount(price.currency)
    else:
        currencyType = price.currency.value
        count = itemsCache.items.stats.money.get(currencyType, 0)
    return (currencyType, count)


def hasEnoughMoney(prices):
    for price in prices:
        _, currentCount = getCurrentCurrencyCount(price)
        if currentCount < price.amount:
            return False

    return True


@replace_none_kwargs(gameEventController=IGameEventController)
def getSortedPriceList(prices, gameEventController=None):
    sortedCurrencies = [ front.getCoinsName() for front in gameEventController.frontController.getOrderedFrontsList() ]
    sortedCurrenciesLen = len(sortedCurrencies)

    def sortingKey(price):
        if price.currencyType == EventShop.CurrencyType.VIRTUAL:
            currencyType = gameEventController.coins.getName(price.currency)
            if currencyType in sortedCurrencies:
                return sortedCurrencies.index(currencyType)
        return sortedCurrenciesLen

    return sorted(prices, key=sortingKey)
