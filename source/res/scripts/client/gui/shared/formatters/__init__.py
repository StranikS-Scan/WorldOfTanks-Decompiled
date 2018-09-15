# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/formatters/__init__.py
import BigWorld
from debug_utils import LOG_ERROR
from gui.shared.formatters import icons
from gui.shared.formatters import text_styles
from gui.shared.formatters import time_formatters
from gui.shared.formatters.currency import getBWFormatter
from gui.shared.money import Money, Currency
from helpers.i18n import makeString
__all__ = ('icons', 'text_styles', 'time_formatters')

def formatPrice(price, reverse=False, defaultCurrency=Currency.CREDITS):
    outPrice = []
    currencies = price.getSetCurrencies(byWeight=False)
    if not currencies:
        currencies = [defaultCurrency]
    for currency in currencies:
        formatter = getBWFormatter(currency)
        cname = makeString('#menu:price/{}'.format(currency)) + ': '
        value = price.get(currency, 0)
        cformatted = formatter(value) if formatter else value
        outPrice.append(''.join((cformatted, ' ', cname) if reverse else (cname, ' ', cformatted)))

    return ', '.join(outPrice)


def formatPriceForCurrency(money, currencyName):
    return formatPrice(Money(money.get(currencyName)))


def formatGoldPrice(gold, reverse=False):
    return formatPrice(Money(gold=gold), reverse, defaultCurrency=Currency.GOLD)


def getGlobalRatingFmt(globalRating):
    return BigWorld.wg_getIntegralFormat(globalRating) if globalRating >= 0 else '--'


def moneyWithIcon(money, currType=None):
    if currType is None:
        currType = money.getCurrency()
    style = getattr(text_styles, currType)
    icon = getattr(icons, currType)
    value = money.get(currType)
    formatter = getBWFormatter(currType)
    if style is not None and icon is not None and value is not None:
        return style(formatter(value)) + icon()
    else:
        LOG_ERROR('Unsupported currency for displaying with icon:', currType)
        return formatter(value)
        return


def getMoneyVO(moneyObj):
    """
    Converts money to tuple that includes only set currencies.
    AS3 expects money in this format.
    :param moneyObj: Money instance
    :return: tuple (MoneyVO)
    """
    return tuple(((c, v) for c, v in moneyObj.iteritems()))


def getItemPricesVO(*itemPrices):
    """
    Builds ItemPricesVO, it is a list of dicts (for each price). The dict can be in two forms:
    1) Full - includes 'price', 'defPrice' and 'action' fields, if an action is available
    2) Short - no action, only one field 'price' will be packed.
    Example (let it be two price, for original - an action is available, for alternative price - no action):
    [ {'price': MoneyVO, 'defPrice': MoneyVO, 'action': MoneyVO}, {'price': MoneyVO} ]
    
    NOTE: MoneyVO is constructed in getMoneyVO function, see above
    
    For more information, see: tests/client/gui/shared/formatters/test_price_formatters.py
    :param itemPrices: ItemPrice instances
    :return: tuple of itemPrice VO
    """
    resultVO = []
    for itemPrice in itemPrices:
        action = itemPrice.getActionPrcAsMoney()
        if action.isDefined():
            vo = {'price': getMoneyVO(itemPrice.price),
             'defPrice': getMoneyVO(itemPrice.defPrice),
             'action': getMoneyVO(action)}
            resultVO.append(vo)
        resultVO.append({'price': getMoneyVO(itemPrice.price)})

    return resultVO
