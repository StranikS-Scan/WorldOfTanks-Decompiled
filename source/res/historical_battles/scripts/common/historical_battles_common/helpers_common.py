# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/common/historical_battles_common/helpers_common.py
import BigWorld
import re
import logging
from soft_exception import SoftException
from copy import deepcopy
from hb_constants import EventShop
from hb_constants_extension import INVALID_FRONTMAN_ROLE_ID
_logger = logging.getLogger(__name__)

def getFrontCouponModifier(frontCouponID):
    pattern = re.compile('_x(?P<multiplier>[0-9]*)')
    group = 'multiplier'
    match = re.search(pattern, frontCouponID)
    return None if match is None else int(match.group(group))


def getVehicleBonus(bonuses):
    for bonus in bonuses:
        if bonus.getName() == 'vehicles':
            for vehicle, _ in bonus.getVehicles():
                return vehicle

    return None


def getFrontmanRoleID(vehicleID):
    vehicle = BigWorld.entity(vehicleID)
    if vehicle:
        dynamicRoleComponent = vehicle.dynamicComponents.get('roleComponent', None)
        if dynamicRoleComponent:
            return dynamicRoleComponent.frontmanRoleID
    return INVALID_FRONTMAN_ROLE_ID


class EventShopBundlePrice(object):

    class SinglePrice(object):
        __slots__ = ('type', 'currencyType', 'currency', 'amount')

        def __init__(self, *args):
            self.type = EventShop.PriceType.SINGLE
            if isinstance(args[0], self.__class__):
                self.currencyType, self.currency, self.amount = args[0].currencyType, args[0].currency, args[0].amount
            elif isinstance(args[0], tuple):
                price = args[0]
                self.currencyType, self.currency, self.amount = EventShop.CurrencyType(price[0]), price[1], price[2]
            else:
                self.currencyType, self.currency, self.amount = EventShop.CurrencyType(args[0]), args[1], args[2]

        def __add__(self, other):
            return self.__class__(self.currencyType, self.currency, self.amount + other.amount) if isinstance(other, EventShopBundlePrice.SinglePrice) and self.isSamePriceCurrency(other) else EventShopBundlePrice.MultiPrice([self]) + other

        def __sub__(self, other):
            if isinstance(other, EventShopBundlePrice.SinglePrice) and self.isSamePriceCurrency(other):
                return self.__class__(self.currencyType, self.currency, max(self.amount - other.amount, 0))
            raise SoftException('Cant SUB different prices:: Price1={0}, Price2={1}'.format(self, other))

        def __repr__(self):
            return 'PriceType={0}, CurrencyType={1}, currency={2}, amount={3}'.format(self.type, self.currencyType, self.currency, self.amount)

        def getDiscountedPrice(self, discount):
            return None if not (isinstance(discount, Discount) and self.isSamePriceCurrency(discount.discountAmountPrice)) else self - discount.discountAmountPrice

        def isSamePriceCurrency(self, other):
            return True if isinstance(other, self.__class__) and self.currencyType == other.currencyType and self.currency == other.currency else False

    class MultiPrice(object):
        __slots__ = ('type', 'subPrices')

        def __init__(self, prices):
            super(EventShopBundlePrice.MultiPrice, self).__init__()
            self.type = EventShop.PriceType.MULTI
            self.subPrices = tuple((EventShopBundlePrice.SinglePrice(subPrice) for subPrice in prices))

        def getDiscountedPrice(self, discount):
            return None

        def __add__(self, other):
            if isinstance(other, EventShopBundlePrice.SinglePrice):
                other = self.__class__([other])
            elif not isinstance(other, self.__class__):
                _logger.error('Cant ADD different priceTypes: Price1=' + str(self) + ', Price2=' + str(other))
                return self
            resultPricesData = {(p.currencyType, p.currency):p.amount for p in self.subPrices}
            for subPrice in other.subPrices:
                key = (subPrice.currencyType, subPrice.currency)
                if key in resultPricesData:
                    resultPricesData[key] += subPrice.amount
                resultPricesData[key] = subPrice.amount

            resultPrices = [ k + (v,) for k, v in resultPricesData.iteritems() ]
            return self.__class__(resultPrices)

        def __repr__(self):
            subPricesStr = ''
            for i, subprice in enumerate(self.subPrices):
                subPricesStr += 'Price{0}: [{1}]\n'.format(i, subprice)

            return 'PriceType={0}, subPrices:\n{1}'.format(self.type, subPricesStr)

    @classmethod
    def makePrice(cls, priceTuple):
        if priceTuple[0] == EventShop.PriceType.SINGLE.value:
            return cls.SinglePrice(priceTuple[1], priceTuple[2], priceTuple[3])
        else:
            return cls.MultiPrice(priceTuple[1]) if priceTuple[0] == EventShop.PriceType.MULTI.value else None


class Discount(object):
    __slots__ = ('discountAmountPrice', 'tokensToDraw', 'getDiscountPercent')

    def __init__(self, discountData, tokenGetterFn):
        super(Discount, self).__init__()
        self.tokensToDraw = {}
        self.discountAmountPrice = self._getDiscountAmountPrice(discountData, tokenGetterFn)

    @classmethod
    def getDiscountPercent(cls, discountedPrice, originalPrice):
        if originalPrice is None:
            return {}
        else:

            def priceToDict(price):
                return {subPrice.currency:subPrice.amount for subPrice in price.subPrices} if price.type == EventShop.PriceType.MULTI else {price.currency: price.amount}

            def calcPercent(oldPrice, currentPrice):
                return int(float(oldPrice - currentPrice) / float(oldPrice) * 100.0)

            pricesMap = priceToDict(discountedPrice)
            oldPricesMap = priceToDict(originalPrice)
            return {k:calcPercent(oldPricesMap.get(k, v), v) for k, v in pricesMap.iteritems()}

    @staticmethod
    def parseDiscountConfig(discountConfig):
        return {(token, limit):EventShopBundlePrice.makePrice(price) for (token, limit), price in discountConfig.items()}

    def _getDiscountAmountPrice(self, discountData, tokenGetterFn):
        discountAmountPrice = None
        for (tokenName, limit), price in discountData.items():
            if tokenGetterFn(tokenName) >= limit:
                self.tokensToDraw.update({tokenName: limit})
                discountAmountPrice = discountAmountPrice + price if discountAmountPrice else deepcopy(price)

        return discountAmountPrice
