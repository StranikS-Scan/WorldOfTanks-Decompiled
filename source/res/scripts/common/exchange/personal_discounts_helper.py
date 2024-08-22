# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/exchange/personal_discounts_helper.py
import logging
import math
import typing
from exchange.personal_discounts_constants import ExchangeDiscountInfo, ExchangeDiscountType, ExchangeRate, ExchangeRateShowFormat
if typing.TYPE_CHECKING:
    from typing import Tuple, List, Optional, Dict
_logger = logging.getLogger(__name__)

def sortExchangeRatesDiscountsRule(discount1, discount2):

    def _getComparisonKeys(discount):
        return (float(discount.resourceRateValue) / discount.goldRateValue,
         not discount.isPersonal,
         discount.discountType == ExchangeDiscountType.UNLIMITED,
         discount.amountOfDiscount,
         -discount.discountLifetime)

    return cmp(_getComparisonKeys(discount1), _getComparisonKeys(discount2))


def isExchangeRateDiscountAvailable(discount, currentTime):
    if discount is None:
        return False
    else:
        isUnlimited = discount.discountType == ExchangeDiscountType.UNLIMITED
        isNotUsedUp = discount.amountOfDiscount >= 1 or isUnlimited
        isValidValues = discount.resourceRateValue >= 1 and discount.goldRateValue == 1
        isUpToDate = bool(discount.discountLifetime > currentTime or not discount.isPersonal)
        return bool(isUpToDate and isNotUsedUp and isValidValues)


def getDiscountsRequiredForExchange(discounts, goldExchangeAmount, currentTime):
    discountWillBeUsed = {}
    if not discounts:
        return discountWillBeUsed
    leftAmount = goldExchangeAmount
    for discount in discounts:
        if not isExchangeRateDiscountAvailable(discount, currentTime):
            continue
        if discount.amountOfDiscount >= leftAmount or discount.discountType == ExchangeDiscountType.UNLIMITED:
            discountWillBeUsed[discount] = leftAmount
            break
        leftAmount -= discount.amountOfDiscount
        discountWillBeUsed[discount] = discount.amountOfDiscount

    return discountWillBeUsed


def sortExchangeRatesDiscounts(discountsInfo):
    return sorted(discountsInfo, cmp=sortExchangeRatesDiscountsRule, reverse=True)


def createCommonDiscount(exchangeType, exchangeRate):
    return ExchangeDiscountInfo(isPersonal=False, exchangeType=exchangeType, discountType=ExchangeDiscountType.UNLIMITED, showFormat=ExchangeRateShowFormat.COEFFICIENT, goldRateValue=exchangeRate.goldRateValue, resourceRateValue=exchangeRate.resourceRateValue, amountOfDiscount=0, discountLifetime=0, tokenName='')


def getPersonalDiscountsAndCommonDiscount(discounts):
    for index, i in enumerate(discounts):
        if not i.isPersonal or i.discountType == ExchangeDiscountType.UNLIMITED:
            return (discounts[:index] or None, i)

    return (discounts or None, None)


def calculateGoldExchange(discount, goldExchangeAmount):
    if discount.amountOfDiscount >= goldExchangeAmount or discount.discountType == ExchangeDiscountType.UNLIMITED:
        return (goldExchangeAmount, goldExchangeAmount * discount.resourceRateValue)
    resourceWithDiscount = discount.amountOfDiscount * discount.resourceRateValue
    return (discount.amountOfDiscount, resourceWithDiscount)


def calculateRequiredGoldFromSelectedResource(discount, resourceAmount):
    isUnlimited = discount.discountType == ExchangeDiscountType.UNLIMITED
    if discount.amountOfDiscount * discount.resourceRateValue >= resourceAmount or isUnlimited:
        goldAmount = int(math.ceil(float(resourceAmount) / discount.resourceRateValue))
        return (goldAmount, goldAmount * discount.resourceRateValue)
    resourceWithDiscount = discount.amountOfDiscount * discount.resourceRateValue
    return (discount.amountOfDiscount, resourceWithDiscount)


def calculateGoldExchangeWithDiscounts(discounts, goldExchangeAmount, defaultRate, currentTime):
    if goldExchangeAmount < 0 or defaultRate.resourceRateValue < 1:
        _logger.error('Exchange rate is lower then 1, resourceRateValue=%d or incorrect exchange amount=%d', defaultRate.resourceRateValue, goldExchangeAmount)
        return 0
    defaultDiscount = createCommonDiscount('default', defaultRate)
    discounts = discounts or []
    discounts.append(defaultDiscount)
    leftGoldToExchange = goldExchangeAmount
    receivedResource = 0
    for exchangeDiscount in discounts:
        if isExchangeRateDiscountAvailable(exchangeDiscount, currentTime):
            exchangedGold, received = calculateGoldExchange(exchangeDiscount, leftGoldToExchange)
            leftGoldToExchange -= exchangedGold
            receivedResource += received
        if leftGoldToExchange == 0:
            return receivedResource

    _logger.error('Error calculating gold exchange, left amount=%d, defaultRate=%d ', leftGoldToExchange, defaultRate.resourceRateValue)


def calculateResourceExchangeWithDiscounts(discounts, resourceAmount, defaultRate, currentTime):
    if resourceAmount < 0 or defaultRate.resourceRateValue < 1:
        _logger.error('Exchange rate is lower then 1, resourceRateValue=%d or incorrect exchange amount=%d', defaultRate.resourceRateValue, resourceAmount)
        return (0, 0)
    defaultDiscount = createCommonDiscount('default', defaultRate)
    discounts = discounts or []
    discounts.append(defaultDiscount)
    leftResourceAmount = resourceAmount
    requiredGold = 0
    for exchangeDiscount in discounts:
        if isExchangeRateDiscountAvailable(exchangeDiscount, currentTime):
            exchangedGold, received = calculateRequiredGoldFromSelectedResource(exchangeDiscount, leftResourceAmount)
            leftResourceAmount -= received
            requiredGold += exchangedGold
        if leftResourceAmount <= 0:
            return (requiredGold, -leftResourceAmount + resourceAmount)

    _logger.error('Error calculating resource exchange, left amount=%d, defaultRate=%d ', leftResourceAmount, defaultRate.resourceRateValue)
