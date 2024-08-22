# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/client_web_api/exchange/__init__.py
from exchange.personal_discounts_constants import EXCHANGE_RATE_TYPES
from helpers import dependency
from skeletons.gui.game_control import IExchangeRatesWithDiscountsProvider
from web.client_web_api.api import C2WHandler, c2w

class PersonalExchangeRatesDiscountsEventHandler(C2WHandler):
    __exchangeRatesProvider = dependency.descriptor(IExchangeRatesWithDiscountsProvider)

    def init(self):
        super(PersonalExchangeRatesDiscountsEventHandler, self).init()
        for exchangeType in EXCHANGE_RATE_TYPES:
            self.__exchangeRatesProvider.get(exchangeType).onUpdated += self.__sendNotify

    def fini(self):
        for exchangeType in EXCHANGE_RATE_TYPES:
            self.__exchangeRatesProvider.get(exchangeType).onUpdated -= self.__sendNotify

        super(PersonalExchangeRatesDiscountsEventHandler, self).fini()

    @c2w(name='personal_exchange_rates_discounts_changed')
    def __sendNotify(self):
        return None
