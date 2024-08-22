# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/exchange/personal_discounts_constants.py
from collections import namedtuple
from enum import Enum
EXCHANGE_RATE_GOLD_NAME = 'gold_exchange'
EXCHANGE_RATE_FREE_XP_NAME = 'experience_translation'
EXCHANGE_RATE_TYPES = (EXCHANGE_RATE_GOLD_NAME, EXCHANGE_RATE_FREE_XP_NAME)
MAX_DISCOUNT_VALUE = 2147483647L
MAX_TIMESTAMP_VALUE = 9007199254740991L
MAX_DISCOUNT_COEFFICIENT = 10
DIGITAL_TEMPLATE = '([1-9]\\d*(\\.\\d+)?)'
EXCHANGE_NAME_TO_GAME_PARAM_NAME = {EXCHANGE_RATE_GOLD_NAME: 'exchangeRate',
 EXCHANGE_RATE_FREE_XP_NAME: 'freeXPConversion'}
ExchangeRate = namedtuple('ExchangeRate', ['goldRateValue', 'resourceRateValue'])

class ExchangeDiscountType(Enum):
    LIMITED = 'limited'
    UNLIMITED = 'unlimited'


class ExchangeRateShowFormat(Enum):
    COEFFICIENT = 'coefficient'
    INTEGER = 'integer'
    TEMPORARY = 'temporary'
    LIMITED = 'limited'


class ExchangeRateCoefficientType(Enum):
    AMOUNT = 'increase'
    MULTIPLY = 'mul'


ExchangeDiscountInfo = namedtuple('ExchangeDiscountInfo', ('isPersonal', 'exchangeType', 'discountType', 'goldRateValue', 'resourceRateValue', 'showFormat', 'amountOfDiscount', 'discountLifetime', 'tokenName'))

class ExchangeRateDiscountToken(Enum):
    LIMIT_TYPE = 'limit_type'
    SHOW_FORMAT = 'show_format'
    RATE_TYPE = 'rate_type'
    RATE_VALUE = 'change_on'
