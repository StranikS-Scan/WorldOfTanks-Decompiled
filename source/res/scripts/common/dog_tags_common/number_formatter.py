# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dog_tags_common/number_formatter.py
import re
from collections import defaultdict
from math import floor
import typing
from dog_tags_common.config.common import ComponentNumberType

def formatComponentValue(locale, value, numberType, specialReplacements=True):
    if numberType == ComponentNumberType.PERCENTAGE:
        raw_value = formatPercentage(value)
    else:
        raw_value = formatNumber(locale, value, regionalPrefix=specialReplacements)
    return raw_value if not specialReplacements else ''.join((_replacements.get(c, c) for c in raw_value))


def formatPercentage(value):
    rounded = customRound(value, 2)
    formatted = '{:.2f}'.format(rounded)
    formattedNoZeroes = _TRAILING_ZEROES_RE.sub('', formatted)
    return '{}%'.format(formattedNoZeroes)


def formatNumber(locale, value, regionalPrefix=True):
    suffix = '{}_'.format(locale) if regionalPrefix else ''
    suffix = suffix + '{}'
    if regionalPrefix:
        suffix = '[{}]'.format(suffix)
    if value < 100000:
        formatted = '{:,.2f}'.format(customRound(value, 2))
        formatted = _TRAILING_ZEROES_RE.sub('', formatted)
    elif value < 999500:
        formatted = '{} {}'.format(_formatThousands(value), suffix.format('k'))
    elif value < 1000000:
        formatted = '{} {}'.format(_formatThousands(value, floor), suffix.format('k'))
    else:
        formatted = '{} {}'.format(_formatMillions(locale, value), suffix.format('m'))
    return formatted.replace(',', ' ')


def customRound(value, ndecimals=0):
    fact = 10 ** (ndecimals + 1)
    norm_value = float(value) * fact
    last = norm_value % 10
    if last >= 5:
        norm_value += 10
    return (norm_value - last) / fact


def _formatThousands(value, roundStrategy=customRound):
    shortValue = float(value) / 1000
    return '{:,d}'.format(int(roundStrategy(shortValue)))


def _formatMillions(locale, value):
    shortValue = float(value) / _millionDivider[locale]
    return '{:,.1f}'.format(customRound(shortValue, 1)).replace('.0', '')


_TRAILING_ZEROES_RE = re.compile('\\.?0+$')
_millionDivider = defaultdict(lambda : 1000000)
_TEN_THOUSAND_DIVIDER = 10000
_millionDivider['ja'] = _TEN_THOUSAND_DIVIDER
_millionDivider['zh_cn'] = _TEN_THOUSAND_DIVIDER
_replacements = {'%': '[percentage]',
 '.': '[dot]'}
