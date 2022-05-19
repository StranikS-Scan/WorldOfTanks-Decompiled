# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/formatters/currency.py
import logging
from gui.impl import backport
from gui.shared.formatters import text_styles
from gui.shared.money import Currency
_logger = logging.getLogger(__name__)
_CURRENCY_TO_BW_FORMATTER = {Currency.CREDITS: backport.getIntegralFormat,
 Currency.GOLD: backport.getGoldFormat,
 Currency.CRYSTAL: backport.getIntegralFormat,
 Currency.EVENT_COIN: backport.getIntegralFormat,
 Currency.BPCOIN: backport.getIntegralFormat,
 Currency.BRCOIN: backport.getIntegralFormat}
_CURRENCY_TO_TEXT_STYLE = {Currency.CREDITS: text_styles.credits,
 Currency.GOLD: text_styles.gold,
 Currency.CRYSTAL: text_styles.crystal,
 Currency.EVENT_COIN: text_styles.eventCoin,
 Currency.BPCOIN: text_styles.bpcoin,
 Currency.BRCOIN: text_styles.brcoin}

def getBWFormatter(currency):
    if currency in _CURRENCY_TO_BW_FORMATTER:
        return _CURRENCY_TO_BW_FORMATTER[currency]
    _logger.info('BW formatter is not set for the following currency: %r', currency)
    return backport.getIntegralFormat


def getStyle(currency):
    if currency in _CURRENCY_TO_TEXT_STYLE:
        return _CURRENCY_TO_TEXT_STYLE[currency]
    _logger.info('Text style is not set for the following currency: %r', currency)
    return str


def applyAll(currency, value):
    style = getStyle(currency)
    return style(getBWFormatter(currency)(value))
