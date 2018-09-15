# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/gui_item_economics.py
from gui.shared.money import Money, Currency, MONEY_UNDEFINED
from gui.shared.economics import getActionPrc
from gui.shared.gui_items import GUI_ITEM_TYPE

def cmpByCurrencyWeight(p1, p2):
    """
    Compares prices by currency weight and value (see Currency enum description). Comparator that takes two ItemPrice
    and returns int according to the following rules: -1 if p1 < p2, 0 if p1 == p2, 1 if p1 > p2.
    
    :param p1: ItemPrice
    :param p2: ItemPrice
    :return: int
    """
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
    """
    Determines if the given buy price is allowed on the server for the given item type ID.
    
    :param item: item to be bought
    :param itemPrice: ItemPrice to be checked
    :param shop: ref to shop stats, see IShopCommonStats
    :return: bool, True if the price is allowed, False - otherwise
    """
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
    """
    Determines price to buy the given item taking into account available prices for buying and server settings
    (switches). If the item can be bought for the given (desired) currency,
     the method returns a price in this currency.
    Otherwise the original currency is used to determine the price.
    
    The price is calculated based on the item alternative and original prices. If an alternative price is defined,
    it is used to obtain the cost in the desired (or original) currency. Otherwise, the original (default) price
    is used.
    
    :param item: item to be bought
    :param currency: preferred currency for buying, see Currency enum
    :param shop: ref to shop stats, see IShopCommonStats
    
    :return: an instance of ItemPrice or None if no price or buying for the given currency is disabled on the server.
    """
    itemPrice = item.buyPrices.getMinItemPriceByCurrency(currency)
    return itemPrice if itemPrice is not None and isItemBuyPriceAvailable(item, itemPrice, shop) else None


class ItemPrice(object):
    """
    Represents a price of a fitting item. Includes two price components: the current price and default price.
    Note that ItemPrice - immutable!
    """
    __slots__ = ('__price', '__defPrice')

    def __init__(self, price, defPrice):
        """
        Ctr
        :param price: current price represented by Money
        :param defPrice: default price represented by Money
        """
        super(ItemPrice, self).__init__()
        self.__price = price
        self.__defPrice = defPrice

    def __nonzero__(self):
        """
        Returns True if the price is defined (for details please see Money class description), otherwise - False.
        :return: bool
        """
        return self.__price.isDefined()

    def __eq__(self, other):
        """
        Implements the equal operation ==
        
        :param other: An instance of ItemPrice class
        :return: True if both components (price and defPrice) are equal
        """
        return self.price == other.price and self.defPrice == other.defPrice

    def __ne__(self, other):
        """
        Implements non equal operation !=
        
        :param other: An instance of ItemPrice class
        :return: True if at least one component (price or defPrice) is not equal to other ItemPrice
        """
        return self.price != other.price or self.defPrice != other.defPrice

    def __repr__(self):
        return 'ItemPrice(price: {}, defPrice: {})'.format(self.price, self.defPrice)

    def __add__(self, other):
        """
        Implements the arithmetic operation +
        :param other: Summing represented by ItemPrice class.
        :return: A new ItemPrice object.
        """
        return ItemPrice(self.price + other.price, self.defPrice + other.defPrice)

    def __iadd__(self, other):
        """
        Implements the arithmetic operation +=
        :param other: Summing represented by ItemPrice class.
        :return: A new ItemPrice object.
        """
        return self.__add__(other)

    def __sub__(self, other):
        """
        Implements the arithmetic operation -
        :param other: Deduction represented by ItemPrice class.
        :return: A new ItemPrice object.
        """
        return ItemPrice(self.price - other.price, self.defPrice - other.defPrice)

    def __isub__(self, other):
        """
        Implements the arithmetic operation -=
        :param other: Deduction represented by ItemPrice class.
        :return: A new ItemPrice object.
        """
        return self.__sub__(other)

    def __mul__(self, n):
        """
        Implements the arithmetic operation *
        :param n: Multiplier represented by a number (not an ItemPrice).
        :return: A new ItemPrice object.
        """
        return ItemPrice(self.price * n, self.defPrice * n)

    def __rmul__(self, n):
        """
        Implements the arithmetic operation *=
        :param n: Multiplier represented by a number (not an ItemPrice).
        :return: A new ItemPrice object.
        """
        return self.__mul__(n)

    def __div__(self, n):
        """
        Implements the arithmetic operation /
        :param n: Denominator represented by a number (not an ItemPrice).
        :return: A new ItemPrice object.
        """
        return ItemPrice(self.price / n, self.defPrice / n)

    def __rdiv__(self, n):
        """
        Implements the arithmetic operation /=
        :param n: Denominator represented by a number (not an ItemPrice).
        :return: A new ItemPrice object.
        """
        return self.__div__(n)

    @property
    def price(self):
        """
        Returns the default price as Money. Cannot be None.
        :return: Money
        """
        return self.__price

    @property
    def defPrice(self):
        """
        Returns the default price as Money. Cannot be None.
        :return: Money
        """
        return self.__defPrice

    def getCurrency(self, byWeight=True):
        """
        Returns currency of the current price (see Currency enum). For details please see Money.getCurrency
        description.
        :param byWeight: bool
        :return: str
        """
        return self.__price.getCurrency(byWeight=byWeight)

    def isDefined(self):
        """
        Returns True if the price is defined (the current price is defined). Otherwise returns False. For details
        please see Money class description.
        :return: bool
        """
        return self.__price.isDefined()

    def isActionPrice(self):
        """
        Returns True if the current price != default price (an item can be bought with discount or penalty). Otherwise
        returns False.
        :return: bool
        """
        return self.__price != self.__defPrice

    def getActionPrc(self):
        """
        Returns discount/penalty percent as int. 0 - if no action.
        :return: int
        """
        return getActionPrc(self.__price, self.__defPrice) if self.isActionPrice() else 0

    def getActionPrcAsMoney(self):
        """
        Returns discount/penalty percent as Money. MONEY_UNDEFINED - if no action.
        :return: Money, where each element - percent value for a currency.
        """
        actionPrc = MONEY_UNDEFINED
        if self.isActionPrice():
            for currency in Currency.ALL:
                prc = getActionPrc(self.__price.get(currency), self.__defPrice.get(currency))
                actionPrc += Money.makeFrom(currency, prc if prc else None)

        return actionPrc


ITEM_PRICE_EMPTY = ItemPrice(price=MONEY_UNDEFINED, defPrice=MONEY_UNDEFINED)

class ItemPrices(object):
    """
    Represents a container of a fitting item prices.
    Note that ItemPrices - immutable!
    """
    __slots__ = ('__itemPrice', '__itemAltPrice')

    def __init__(self, itemPrice, itemAltPrice=ITEM_PRICE_EMPTY):
        """
        Ctr
        :param itemPrice: current item price represented by ItemPrice
        :param itemAltPrice: an alternative item price represented by ItemPrice or None
        """
        super(ItemPrices, self).__init__()
        self.__itemPrice = itemPrice
        self.__itemAltPrice = itemAltPrice

    def __iter__(self):
        """
        Returns an iterator object. The object is required to support the iterator protocol. Iterable values are
        represented by ItemPrice in order: original price, alt price1, ... , altPriceN.
        """
        return self.iteritems(directOrder=True)

    def __nonzero__(self):
        """
        Returns True current item price is defined (for details please see Money class description), otherwise - False.
        :return: bool
        """
        return True if self.__itemPrice else False

    @property
    def itemPrice(self):
        """
        Returns the current item price.
        :return: ItemPrice
        """
        return self.__itemPrice

    @property
    def itemAltPrice(self):
        """
        Returns the alternative item price. Returns ITEM_PRICE_EMPTY if an item has no an alternative price.
        :return: ItemPrice or ITEM_PRICE_EMPTY
        """
        return self.__itemAltPrice

    def hasAltPrice(self):
        """
        Returns True if the item has an alternative price (alt price is defined). Otherwise - False.
        :return: bool
        """
        return self.__itemAltPrice.isDefined()

    def iteritems(self, directOrder=True):
        """
        Returns an iterator object.
        :param directOrder: if True - the order will be: 'original price, alt price1, ... , altPriceN.'
                            if False - the order will be: 'alt price1, ... , altPriceN, .... original price'
        :return:
        """
        if directOrder:
            yield self.__itemPrice
            if self.hasAltPrice():
                yield self.__itemAltPrice
        else:
            if self.hasAltPrice():
                yield self.__itemAltPrice
            yield self.__itemPrice

    def getSum(self):
        """
        Returns the sum of all prices.
        :return: ItemPrice
        """
        price = MONEY_UNDEFINED
        defPrice = MONEY_UNDEFINED
        for itemPrice in self:
            price += itemPrice.price
            defPrice += itemPrice.defPrice

        return ItemPrice(price=price, defPrice=defPrice)

    def getMaxValuesAsMoney(self):
        """
        Returns money where all currencies correspond to the max values in all prices.
        :return: Money
        """
        return Money(**{c:max(self._priceValueGenerator(c)) for c in Currency.ALL})

    def hasPriceIn(self, currency):
        """
        Returns True, if there is defined price in the given currency.
        :param currency: str, see Currency enum.
        :return: bool
        """
        for itemPrice in self:
            if itemPrice.price.getCurrency(byWeight=True) == currency:
                return True

        return False

    def getMinItemPriceByCurrency(self, currency):
        """
        Finds the min item price with the given currency.
        :param currency: str, see Currency enum.
        :return: ItemPrice or None if there is no price with the given currency.
        """
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
        """
        Returns an iterator to go through values of all prices. Iterable values are represented by float (see Money
        class description) in order: original price value, alt price1 value, ... , altPriceN value.
        :param currency: str, see Currency enum.
        :return: iterator to float
        """
        for itemPrice in self.iteritems(directOrder=True):
            yield itemPrice.price.get(currency)


ITEM_PRICES_EMPTY = ItemPrices(itemPrice=ITEM_PRICE_EMPTY, itemAltPrice=ITEM_PRICE_EMPTY)
