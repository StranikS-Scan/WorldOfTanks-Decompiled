# Embedded file name: scripts/client/gui/wgnc/xml/format_by_tags.py
import BigWorld
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_WARNING
import re
_RE_FLAGS = re.M | re.U

class _TagFormatter(object):
    __slots__ = ('_compiled',)

    def __init__(self, name):
        super(_TagFormatter, self).__init__()
        self._compiled = self._makePattern(name)

    def format(self, text):
        try:
            all = re.findall(self._compiled, text)
        except re.error:
            return text

        for tag, formatted in self._prepare(all):
            text = text.replace(tag, formatted)

        return text

    def _prepare(self, all):
        raise NotImplementedError

    def _makePattern(self, name):
        raise NotImplementedError


class _ValueFormatter(_TagFormatter):

    def _prepare(self, all):
        for found in all:
            if len(found) != 2:
                continue
            tag, value = found
            if not value:
                LOG_WARNING('Value of tag is empty. It is ignored', tag)
                continue
            try:
                formatted = self._getValue(value)
            except (TypeError, ValueError):
                formatted = value
                LOG_CURRENT_EXCEPTION()

            yield (tag, formatted)

    def _getValue(self, value):
        raise NotImplementedError

    def _makePattern(self, name):
        return re.compile('(<{0}.*?>(.+?)</{0}>)'.format(name), _RE_FLAGS)


class _GoldFormatter(_ValueFormatter):

    def __init__(self):
        super(_GoldFormatter, self).__init__('gold')

    def _getValue(self, value):
        return BigWorld.wg_getGoldFormat(long(value))


class _IntegerFormatter(_ValueFormatter):

    def __init__(self):
        super(_IntegerFormatter, self).__init__('integer')

    def _getValue(self, value):
        return BigWorld.wg_getIntegralFormat(long(value))


class _FloatFormatter(_ValueFormatter):

    def __init__(self):
        super(_FloatFormatter, self).__init__('float')

    def _getValue(self, value):
        return BigWorld.wg_getFractionalFormat(float(value))


class _NiceNumberFormatter(_ValueFormatter):

    def __init__(self):
        super(_NiceNumberFormatter, self).__init__('nicenumber')

    def _getValue(self, value):
        return BigWorld.wg_getNiceNumberFormat(float(value))


class _TimeFormatter(_ValueFormatter):

    def _getLocalTime(self, value):
        return float(value)


class _ShortTimeFormatter(_TimeFormatter):

    def __init__(self):
        super(_ShortTimeFormatter, self).__init__('shorttime')

    def _getValue(self, value):
        return BigWorld.wg_getShortTimeFormat(self._getLocalTime(value))


class _LongTimeFormatter(_TimeFormatter):

    def __init__(self):
        super(_LongTimeFormatter, self).__init__('longtime')

    def _getValue(self, value):
        return BigWorld.wg_getLongTimeFormat(self._getLocalTime(value))


class _ShortDateFormatter(_TimeFormatter):

    def __init__(self):
        super(_ShortDateFormatter, self).__init__('shortdate')

    def _getValue(self, value):
        return BigWorld.wg_getShortDateFormat(self._getLocalTime(value))


class _LongDateFormatter(_TimeFormatter):

    def __init__(self):
        super(_LongDateFormatter, self).__init__('longdate')

    def _getValue(self, value):
        return BigWorld.wg_getLongDateFormat(self._getLocalTime(value))


class _DateTimeFormatter(_TimeFormatter):

    def __init__(self):
        super(_DateTimeFormatter, self).__init__('datetime')

    def _getValue(self, value):
        value = self._getLocalTime(value)
        return '{0:>s} {1:>s}'.format(BigWorld.wg_getShortDateFormat(value), BigWorld.wg_getLongTimeFormat(value))


_LINK_HTML = '<a href="event:{0}">{1}</a>'

class _LinkFormatter(_TagFormatter):

    def __init__(self):
        super(_LinkFormatter, self).__init__('link')

    def _prepare(self, all):
        for found in all:
            if len(found) != 4:
                continue
            tag, _, actions, label = found
            label = label.strip()
            if not label:
                LOG_WARNING('Label is empty. It is ignored', tag)
                continue
            if not actions:
                LOG_WARNING('Actions are empty. It is removed', tag)
                yield (tag, '')
            else:
                yield (tag, _LINK_HTML.format(actions, label))

    def _makePattern(self, name):
        return re.compile('(<{0} actions=(["|\\\']+?)(.+?)\\2>(.+?)</{0}>)'.format(name), _RE_FLAGS)


_formatters = (_GoldFormatter(),
 _IntegerFormatter(),
 _FloatFormatter(),
 _NiceNumberFormatter(),
 _ShortTimeFormatter(),
 _LongTimeFormatter(),
 _ShortDateFormatter(),
 _LongDateFormatter(),
 _DateTimeFormatter(),
 _LinkFormatter())

def formatText(text):
    for formatter in _formatters:
        text = formatter.format(text)

    return text
