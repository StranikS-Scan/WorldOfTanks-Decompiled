# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/formatters/numbers.py
import BigWorld

def formatInt(value, negativeOrZero=None):
    """
    Returns the passed 'negativeOrZero' string for values <= 0 (except None value),
    otherwise a value converted to string.
    :param value: value to convert
    :param negativeOrZero: string to return in case value <=0
    :return: the passed 'negativeOrZero' string or converted value
    """
    if value <= 0 and negativeOrZero is not None:
        result = negativeOrZero
    else:
        result = BigWorld.wg_getIntegralFormat(value)
    return result


def makeStringWithThousandSymbol(value, digitLimit=4):
    """
    Make a string from number and replace zeroes with 'K' symbol.
    The string will not contain fractional part.
    For example: 1000 == '1k', 2500 =='2k', etc.
    :param value: value to convert
    :param digitLimit: specify limit of digits to display,
           example: val=9800, for limit=3 - result='9k'; for limit=4 result=='9800'
    :return: string with result, for zero and negative values it will return '-'
    """
    limitValue = 10 ** digitLimit - 1
    if value > limitValue:
        result = BigWorld.wg_getIntegralFormat(int(value * 0.001)) + 'K'
    else:
        result = formatInt(value, '-')
    return result
