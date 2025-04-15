# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/feature/constants.py
import logging
from enum import Enum
_logger = logging.getLogger(__name__)
UNAVAILABLE_REWARD_ERROR = 'UNAVAILABLE_REWARD_ERROR'
CHANNEL_NAME_PREFIX = 'suv_'
DEFAULT_SEASON_NUMBER = 0

class PurchaseMode(Enum):
    ONE_SERIAL_PRODUCT = 'ONE_SERIAL_PRODUCT'
    SEQUENTIAL_PRODUCT = 'SEQUENTIAL_PRODUCT'
    TWO_PARALLEL_PRODUCTS = 'TWO_PARALLEL_PRODUCTS'


class ResourceType(Enum):
    BLUEPRINTS = 'blueprints'
    CURRENCY = 'currency'

    @classmethod
    def getMember(cls, value):
        if value in cls._value2member_map_:
            return cls(value)
        else:
            _logger.error('%s does not exist in ResourceType values', value)
            return None
