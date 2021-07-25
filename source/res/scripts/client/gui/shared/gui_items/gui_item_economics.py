# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/gui_item_economics.py
import typing
from collections import namedtuple
from gui.shared.money import Money, Currency, MONEY_UNDEFINED, ZERO_MONEY
from gui.shared.economics import getActionPrc
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.gui_items import Vehicle

class ActualPrice(object):
    RESTORE_PRICE = 1
    RENT_PRICE = 2
    BUY_PRICE = 3


_DisplayPrice = namedtuple('PriceTuple', ('type', 'cost'))

def cmpByCurrencyWeight(p1, p2):
    price1 = p1.price
    price2 = p2.price
    for c in Currency.BY_WEIGHT:
        v1 = price1.get(c)
        v2 = price2.get(c)
        if v1 is not None:
            v2 = price2.get(c)
            if v2 is None:
                return v1
            if v1 != v2:
                return v1 - v2
        if v2 is not None:
            return -v2

    return 0


def isItemBuyPriceAvailable(item, itemPrice, shop):
    currency = itemPrice.getCurrency(byWeight=True)
    originalCurrency = item.buyPrices.itemPrice.getCurrency()
    if currency == originalCurrency:
        return True
    if item.itemTypeID == GUI_ITEM_TYPE.SHELL:
        if originalCurrency == Currency.GOLD and currency == Currency.CREDITS and shop.isEnabledBuyingGoldShellsForCredits:
            return True
    elif item.itemTypeID == GUI_ITEM_TYPE.EQUIPMENT and originalCurrency == Currency.GOLD and currency == Currency.CREDITS:
        if shop.isEnabledBuyingGoldEqsForCredits:
            return True
    return False


def getItemBuyPrice(item, currency, shop):
    itemPrice = item.buyPrices.getMinItemPriceByCurrency(currency)
    return itemPrice if itemPrice is not None and isItemBuyPriceAvailable(item, itemPrice, shop) else None


def getPriceTypeAndValue(item, money, exchangeRate):
    mayRent, _ = item.mayRent(money)
    if item.isRestorePossible() and (item.isRestorePossible() and item.mayRestoreWithExchange(money, exchangeRate) or not mayRent):
        return _DisplayPrice(ActualPrice.RESTORE_PRICE, item.restorePrice)
    if item.hasRestoreCooldown() and not item.minRentPrice:
        return _DisplayPrice(ActualPrice.RESTORE_PRICE, item.restorePrice)
    minRentItemPrice = getMinRentItemPrice(item)
    return _DisplayPrice(ActualPrice.RENT_PRICE, minRentItemPrice) if minRentItemPrice else _DisplayPrice(ActualPrice.BUY_PRICE, item.getBuyPrice(preferred=False))


def getMinRentItemPrice(item):
    minRentPricePackage = item.getRentPackage()
    if minRentPricePackage:
        minRentPriceValue = minRentPricePackage['rentPrice']
        minRentDefPriceValue = minRentPricePackage['defaultRentPrice']
        return ItemPrice(price=minRentPriceValue, defPrice=minRentDefPriceValue)
    else:
        return None


def getVehicleConsumablesLayoutPrice(vehicle):
    return sum([ item.getBuyPrice() for item in vehicle.consumables.layout.getItems() if not item.isInInventory and item not in vehicle.consumables.installed ], ITEM_PRICE_ZERO)


def getVehicleBattleBoostersLayoutPrice(vehicle):
    return sum([ item.getBuyPrice() for item in vehicle.battleBoosters.layout.getItems() if not item.isInInventory and item not in vehicle.battleBoosters.installed ], ITEM_PRICE_ZERO)


def getVehicleOptionalDevicesLayoutPrice(vehicle):
    return sum([ item.getBuyPrice() for item in vehicle.optDevices.layout.getItems() if not item.isInInventory and item not in vehicle.optDevices.installed ], ITEM_PRICE_ZERO)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getVehicleShellsLayoutPrice(vehicle, itemsCache=None):
    price = ITEM_PRICE_ZERO
    installedShells = {shell.intCD:shell.count for shell in vehicle.shells.installed.getItems()}
    newShells = {shell.intCD:shell.count for shell in vehicle.shells.layout.getItems()}
    for shell in vehicle.shells.layout.getItems():
        installCount = installedShells.get(shell.intCD, 0)
        newCount = newShells[shell.intCD]
        if newCount > installCount:
            shellInInvenory = itemsCache.items.getItemByCD(shell.intCD)
            inventoryCount = shellInInvenory.inventoryCount
            price += shell.getBuyPrice() * max(0, newCount - installCount - inventoryCount)

    return price


class ItemPrice(object):
    __slots__ = ('__price', '__defPrice')

    def __init__(self, price, defPrice):
        super(ItemPrice, self).__init__()
        self.__price = price
        self.__defPrice = defPrice

    def __nonzero__(self):
        return self.__price.isDefined()

    def __eq__(self, other):
        return self.price == other.price and self.defPrice == other.defPrice

    def __ne__(self, other):
        return self.price != other.price or self.defPrice != other.defPrice

    def __repr__(self):
        return 'ItemPrice(price: {}, defPrice: {})'.format(self.price, self.defPrice)

    def __add__(self, other):
        return ItemPrice(self.price + other.price, self.defPrice + other.defPrice)

    def __iadd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return ItemPrice(self.price - other.price, self.defPrice - other.defPrice)

    def __isub__(self, other):
        return self.__sub__(other)

    def __mul__(self, n):
        return ItemPrice(self.price * n, self.defPrice * n)

    def __rmul__(self, n):
        return self.__mul__(n)

    def __div__(self, n):
        return ItemPrice(self.price / n, self.defPrice / n)

    def __rdiv__(self, n):
        return self.__div__(n)

    @property
    def price(self):
        return self.__price

    @property
    def defPrice(self):
        return self.__defPrice

    def getCurrency(self, byWeight=True):
        return self.__price.getCurrency(byWeight=byWeight)

    def isDefined(self):
        return self.__price.isDefined()

    def isActionPrice(self):
        return self.__price != self.__defPrice

    def getActionPrc(self):
        return getActionPrc(self.__price, self.__defPrice) if self.isActionPrice() else 0

    def getActionPrcAsMoney(self):
        actionPrc = MONEY_UNDEFINED
        if self.isActionPrice():
            for currency in Currency.ALL:
                prc = getActionPrc(self.__price.get(currency), self.__defPrice.get(currency))
                actionPrc += Money.makeFrom(currency, prc if prc else None)

        return actionPrc


ITEM_PRICE_EMPTY = ItemPrice(price=MONEY_UNDEFINED, defPrice=MONEY_UNDEFINED)
ITEM_PRICE_ZERO = ItemPrice(price=ZERO_MONEY, defPrice=ZERO_MONEY)

class ItemPrices(object):
    __slots__ = ('__itemPrice', '__itemAltPrice')

    def __init__(self, itemPrice, itemAltPrice=ITEM_PRICE_EMPTY):
        super(ItemPrices, self).__init__()
        self.__itemPrice = itemPrice
        self.__itemAltPrice = itemAltPrice

    def __iter__(self):
        return self.iteritems(directOrder=True)

    def __nonzero__(self):
        return True if self.__itemPrice else False

    @property
    def itemPrice(self):
        return self.__itemPrice

    @property
    def itemAltPrice(self):
        return self.__itemAltPrice

    def hasAltPrice(self):
        return self.__itemAltPrice.isDefined()

    def iteritems(self, directOrder=True):
        if directOrder:
            yield self.__itemPrice
            if self.hasAltPrice():
                yield self.__itemAltPrice
        else:
            if self.hasAltPrice():
                yield self.__itemAltPrice
            yield self.__itemPrice

    def getSum(self):
        price = MONEY_UNDEFINED
        defPrice = MONEY_UNDEFINED
        for itemPrice in self:
            price += itemPrice.price
            defPrice += itemPrice.defPrice

        return ItemPrice(price=price, defPrice=defPrice)

    def getMaxValuesAsMoney(self):
        return Money(**{c:max(self._priceValueGenerator(c)) for c in Currency.ALL})

    def hasPriceIn(self, currency):
        for itemPrice in self:
            if itemPrice.price.getCurrency(byWeight=True) == currency:
                return True

        return False

    def getMinItemPriceByCurrency(self, currency):
        minValue = None
        result = None
        for itemPrice in self:
            money = itemPrice.price
            if money.getCurrency(byWeight=True) == currency:
                value = money.get(currency)
                if minValue is None or value < minValue:
                    result = itemPrice
                    minValue = value

        return result

    def _priceValueGenerator(self, currency):
        for itemPrice in self.iteritems(directOrder=True):
            yield itemPrice.price.get(currency)


ITEM_PRICES_EMPTY = ItemPrices(itemPrice=ITEM_PRICE_EMPTY, itemAltPrice=ITEM_PRICE_EMPTY)
