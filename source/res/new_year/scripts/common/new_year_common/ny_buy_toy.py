# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/common/new_year_common/ny_buy_toy.py
from new_year_common.settings import NyBuyToyConsts

class BuyToyConfig(object):
    __slots__ = ('_config',)

    def __init__(self, config):
        self._config = config

    def getToyCountForOnePurchase(self):
        return self._config.get(NyBuyToyConsts.TOY_COUNT_FOR_ONE_PURCHASE)
