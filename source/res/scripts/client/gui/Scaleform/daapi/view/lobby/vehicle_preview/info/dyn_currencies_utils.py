# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/info/dyn_currencies_utils.py
import typing
from battle_pass_common import CurrencyBP
from gui.game_control.seniority_awards_controller import WDR_CURRENCY
from gui.shared.money import Currency, Money
from gui.shared import event_dispatcher
from gui.shop import showBuyProductOverlay
from helpers import dependency
from shared_utils import first
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from typing import Dict, Iterable, Callable, Optional, Union
_BUY_PRODUCT_USING_DYN = {CurrencyBP.BIT.value: showBuyProductOverlay,
 WDR_CURRENCY: showBuyProductOverlay}
_DYN_CURRENCIES = tuple(_BUY_PRODUCT_USING_DYN.keys())

class DynMoney(object):

    def __init__(self, values):
        self._values = values

    def get(self, currency, default=None):
        return self._values.get(currency, default)

    def getCurrency(self):
        value = first(self._values.iterkeys())
        return value or ''

    def isDefined(self):
        return any(self._values)


def isCurrency(currency):
    return currency in Currency.ALL


def isDynCurrency(currency):
    return currency in _DYN_CURRENCIES


def isMoney(money):
    return isCurrency(money.getCurrency())


def isDynMoney(money):
    return isDynCurrency(money.getCurrency())


def getMoney(price, dynPrice):
    return DynMoney(dynPrice) if dynPrice else Money(**price)


def getBuyProductMethod(money):
    currency = money.getCurrency()
    if not currency:
        raise SoftException('Dyn money is empty')
    return _BUY_PRODUCT_USING_DYN.get(currency)


def separatePrice(price):
    return ({c:v for c, v in price.iteritems() if isCurrency(c)}, {c:v for c, v in price.iteritems() if isDynCurrency(c)})


def mayObtainForMoney(money):
    if isMoney(money):
        return event_dispatcher.mayObtainForMoney(money)
    if isDynMoney(money):
        return _mayObtainForDynCurrency(money)
    raise SoftException('Unsupported currency: {}'.format(money.getCurrency()))


def mayObtainWithMoneyExchange(money):
    if isMoney(money):
        return event_dispatcher.mayObtainWithMoneyExchange(money)
    if isDynMoney(money):
        return False
    raise SoftException('Unsupported currency: {}'.format(money.getCurrency()))


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getUserMoney(currency, itemsCache=None):
    if currency in Currency.ALL:
        return _getUserMoney(currency, itemsCache=itemsCache)
    if currency in _DYN_CURRENCIES:
        return _getUserDynCurrency(currency, itemsCache=itemsCache)
    raise SoftException('Unsupported currency: {}'.format(currency))


def _mayObtainForDynCurrency(money):
    currency = money.getCurrency()
    return money.get(currency) <= _getUserDynCurrency(currency)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _getUserDynCurrency(currency, itemsCache=None):
    return itemsCache.items.stats.dynamicCurrencies.get(currency, 0)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _getUserMoney(currency, itemsCache=None):
    return int(itemsCache.items.stats.money.get(currency, 0))
