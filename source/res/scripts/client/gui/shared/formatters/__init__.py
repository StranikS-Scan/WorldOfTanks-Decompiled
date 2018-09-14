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
        cformatted = formatter(price.get(currency)) if formatter else price.get(currency)
        outPrice.append(''.join((cformatted, ' ', cname) if reverse else (cname, ' ', cformatted)))

    return ', '.join(outPrice)


def formatPriceForCurrency(money, currencyName):
    return formatPrice(Money(money.get(currencyName)))


def formatGoldPrice(gold, reverse=False):
    return formatPrice(Money(gold=gold), reverse, defaultCurrency=Currency.GOLD)


def getGlobalRatingFmt(globalRating):
    return BigWorld.wg_getIntegralFormat(globalRating) if globalRating >= 0 else '--'


def moneyWithIcon(money, currType=Currency.CREDITS):
    style = getattr(text_styles, currType)
    icon = getattr(icons, currType)
    value = money.get(currType)
    formatter = currency.getBWFormatter(currType)
    if style is not None and icon is not None and value is not None:
        return style(formatter(value)) + icon()
    else:
        LOG_ERROR('Unsupported currency for displaying with icon:', currType)
        return formatter(value)
        return
