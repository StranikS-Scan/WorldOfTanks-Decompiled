# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/formatters/currency.py
import BigWorld
from debug_utils import LOG_WARNING
from gui.shared.formatters import text_styles
from gui.shared.money import Currency
_CURRENCY_TO_BW_FORMATTER = {Currency.CREDITS: BigWorld.wg_getIntegralFormat,
 Currency.GOLD: BigWorld.wg_getGoldFormat,
 Currency.CRYSTAL: BigWorld.wg_getIntegralFormat}
_CURRENCY_TO_TEXT_STYLE = {Currency.CREDITS: text_styles.credits,
 Currency.GOLD: text_styles.gold,
 Currency.CRYSTAL: text_styles.crystal}

def getBWFormatter(currency):
    if currency in _CURRENCY_TO_BW_FORMATTER:
        return _CURRENCY_TO_BW_FORMATTER[currency]
    LOG_WARNING('BW formatter is not set for the following currency: ', currency)
    return BigWorld.wg_getIntegralFormat


def getStyle(currency):
    if currency in _CURRENCY_TO_TEXT_STYLE:
        return _CURRENCY_TO_TEXT_STYLE[currency]
    LOG_WARNING('Text style is not set for the following currency: ', currency)
    return str


def applyAll(currency, value):
    style = getStyle(currency)
    return style(getBWFormatter(currency)(value))
