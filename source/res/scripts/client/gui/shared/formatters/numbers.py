# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/formatters/numbers.py
from gui.impl import backport

def formatInt(value, negativeOrZero=None, formatter=backport.getIntegralFormat):
    if value <= 0 and negativeOrZero is not None:
        result = negativeOrZero
    else:
        result = formatter(value)
    return result


def makeStringWithThousandSymbol(value, digitLimit=4, formatter=backport.getIntegralFormat, defNegativeOrZero='-'):
    limitValue = 10 ** digitLimit - 1
    if value > limitValue:
        result = formatter(int(value * 0.001)) + 'K'
    else:
        result = formatInt(value, defNegativeOrZero, formatter)
    return result
