# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/formatters/currency.py
import BigWorld
from debug_utils import LOG_WARNING
from gui.shared.money import Currency
_CURRENCY_TO_BW_FORMATTER = {Currency.CREDITS: BigWorld.wg_getIntegralFormat,
 Currency.GOLD: BigWorld.wg_getGoldFormat}

def getBWFormatter(currency):
    if currency in _CURRENCY_TO_BW_FORMATTER:
        return _CURRENCY_TO_BW_FORMATTER[currency]
    LOG_WARNING('BW formatter is not set for the following currency: ', currency)
    return lambda v: v
