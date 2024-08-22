# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/exchange/personal_discounts_validator.py
from abc import ABCMeta
from exchange.personal_discounts_constants import ExchangeDiscountType, EXCHANGE_RATE_GOLD_NAME, MAX_DISCOUNT_COEFFICIENT, MAX_TIMESTAMP_VALUE, MAX_DISCOUNT_VALUE, ExchangeDiscountInfo, ExchangeRate, ExchangeRateShowFormat

def isDiscountValuesCorrect(discount, defaultGoldRateValue, defaultResourceRateValue):
    defaultCourse = ExchangeRate(goldRateValue=defaultGoldRateValue, resourceRateValue=defaultResourceRateValue)
    if discount.exchangeType == EXCHANGE_RATE_GOLD_NAME:
        return GoldExchangeValidator(discount, defaultCourse).isValid()
    else:
        return XpExchangeValidator(discount, defaultCourse).isValid()


class BaseExchangeValidator(object):
    __metaclass__ = ABCMeta
    _maxRateMultiplier = MAX_DISCOUNT_COEFFICIENT
    _maxDiscountValue = MAX_DISCOUNT_VALUE
    _maxLifetime = MAX_TIMESTAMP_VALUE
    _minDiscountRate = 1

    def __init__(self, discount, defaultCourse):
        self.discount = discount
        self.defaultCourse = defaultCourse

    def isValid(self):
        return self.isValidDiscountAmount and self.isValidDiscountRates and self.isValidDiscountLifetime and self.isValidShowFormat

    @property
    def isValidDiscountLifetime(self):
        return self.discount.discountLifetime < self._maxLifetime

    @property
    def isValidDiscountAmount(self):
        return self._isUnLimited or self._isDiscountAmountCorrect

    @property
    def isValidDiscountRates(self):
        return self._isDynamicCoefficientCorrect and self._isStaticCoefficientCorrect

    @property
    def _isDynamicCoefficientCorrect(self):
        isMinRateCorrect = float(self.dynamicCoefficient) / self.defaultDynamicCoefficient >= self._minDiscountRate
        maxRate = self.defaultDynamicCoefficient * self._maxRateMultiplier
        return isMinRateCorrect and maxRate >= self.dynamicCoefficient > self.defaultDynamicCoefficient

    @property
    def _isStaticCoefficientCorrect(self):
        return self.staticCoefficient == self.defaultStaticCoefficient

    @property
    def _isUnLimited(self):
        return self.discount.discountType == ExchangeDiscountType.UNLIMITED

    @property
    def _isDiscountAmountCorrect(self):
        return self.discount.amountOfDiscount <= self.maxDiscountVal

    @property
    def dynamicCoefficient(self):
        return self.discount.resourceRateValue

    @property
    def staticCoefficient(self):
        return self.discount.goldRateValue

    @property
    def defaultDynamicCoefficient(self):
        return self.defaultCourse.resourceRateValue

    @property
    def defaultStaticCoefficient(self):
        return self.defaultCourse.goldRateValue

    @property
    def maxDiscountVal(self):
        return self._maxDiscountValue // self.dynamicCoefficient

    @property
    def isValidShowFormat(self):
        return False if self.discount.discountType == ExchangeDiscountType.UNLIMITED and self.discount.showFormat == ExchangeRateShowFormat.LIMITED else True


class GoldExchangeValidator(BaseExchangeValidator):
    _minDiscountRate = 1.01


class XpExchangeValidator(BaseExchangeValidator):
    _minDiscountRate = 2.0
