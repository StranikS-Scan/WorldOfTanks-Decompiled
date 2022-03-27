# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/trade_in_common/constants_types.py
from collections import namedtuple
CONFIG_NAME = 'trade_in_config'
ConversionRule = namedtuple('ConversionRule', ['freeExchange',
 'sellPriceFactor',
 'accessToken',
 'checkVehicleAscendingLevels',
 'visibleToEveryone',
 'allowToBuyNotInShopVehicles'])
TradeInInfo = namedtuple('TradeInInfo', ['sellGroupId', 'buyGroupId', 'conversionRule'])
