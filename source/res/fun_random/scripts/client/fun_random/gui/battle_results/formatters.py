# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/battle_results/formatters.py
from gui.battle_results.components.style import getIntegralFormatIfNoEmpty
from gui.shared.formatters.numbers import makeStringWithThousandSymbol

def formatter(value):
    return '{:,}'.format(value).replace(',', ' ')


def formatOneValue(value, digitLimit=9):
    return makeStringWithThousandSymbol(value, digitLimit, formatter, getIntegralFormatIfNoEmpty)


def formatTwoValues(values, digitLimit=5):
    result = []
    for value in values:
        if value > 0:
            result.append(makeStringWithThousandSymbol(value, digitLimit, formatter=str))
        result.append(value)

    return result
