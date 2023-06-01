# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dict2model/utils.py
from __future__ import absolute_import
import re
import typing
import copy
import datetime
import functools
from future.utils import string_types, binary_type
from soft_exception import SoftException
binaryType = binary_type
baseStringTypes = string_types + (binaryType,)
_ISO8601_RE = re.compile('(?P<year>\\d{4})-(?P<month>\\d{1,2})-(?P<day>\\d{1,2})[T ](?P<hour>\\d{1,2}):(?P<minute>\\d{1,2})(?::(?P<second>\\d{1,2})(?:\\.(?P<microsecond>\\d{1,6})\\d{0,6})?)?(?P<tzinfo>Z|[+-]\\d{2}(?::?\\d{2})?)?$')
ZERO = datetime.timedelta(0)
HOUR = datetime.timedelta(hours=1)

class UTC(datetime.tzinfo):
    zone = 'UTC'
    _utcoffset = ZERO
    _dst = ZERO
    _tzname = zone

    def fromutc(self, dt):
        return self.localize(dt) if dt.tzinfo is None else super(UTC, self).fromutc(dt)

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        pass

    def dst(self, dt):
        return ZERO

    def localize(self, dt, is_dst=False):
        if dt.tzinfo is not None:
            raise SoftException('Not naive datetime (tzinfo is already set)')
        return dt.replace(tzinfo=self)

    def normalize(self, dt, is_dst=False):
        if dt.tzinfo is self:
            return dt
        else:
            if dt.tzinfo is None:
                raise SoftException('Naive time - no tzinfo set')
            return dt.astimezone(self)

    def __repr__(self):
        pass

    def __str__(self):
        pass


utc = UTC()

def isoFormat(dt, localtime=False):
    if localtime and dt.tzinfo is not None:
        localized = dt
    elif dt.tzinfo is None:
        localized = utc.localize(dt)
    else:
        localized = dt.astimezone(utc)
    return localized.isoformat()


def fromIso(dateString):
    if not _ISO8601_RE.match(dateString):
        raise SoftException('Not a valid ISO8601-formatted string.')
    if '.' in dateString:
        dtNomsTz, mstz = dateString.split('.')
        msNoTz = mstz[:len(mstz) - len(mstz.lstrip('0123456789'))]
        datestring = '.'.join((dtNomsTz, msNoTz))
        return datetime.datetime.strptime(datestring[:26], '%Y-%m-%dT%H:%M:%S.%f')
    return datetime.datetime.strptime(dateString[:19], '%Y-%m-%dT%H:%M:%S')


def _mergeDicts(destination, source, deep=True):
    _copy = copy.deepcopy if deep else copy.copy
    for key in source:
        if key in destination:
            dstValue, srcValue = destination[key], source[key]
            if isinstance(dstValue, dict) and isinstance(srcValue, dict):
                _mergeDicts(dstValue, srcValue)
            elif dstValue is srcValue:
                pass
            else:
                srcValueCopy = _copy(srcValue)
                if isinstance(dstValue, list) and isinstance(srcValue, list):
                    dstValue.extend(srcValueCopy)
                elif isinstance(dstValue, set) and isinstance(srcValue, set):
                    dstValue.update(srcValueCopy)
                elif isinstance(dstValue, tuple) and isinstance(srcValue, tuple):
                    destination[key] = dstValue + srcValueCopy
                else:
                    listTypes = (list, set, tuple)
                    destination[key] = list(dstValue) if isinstance(dstValue, listTypes) else [dstValue]
                    destination[key] += list(srcValueCopy) if isinstance(srcValue, listTypes) else [srcValueCopy]
        destination[key] = _copy(source[key])

    return destination


def mergeDicts(destination, first, second=None, deep=True):
    sources = (first,) if second is None else (first, second)
    return functools.reduce(functools.partial(_mergeDicts, deep=deep), sources, destination)
