# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/clans/data_wrapper/utils.py
from debug_utils import LOG_ERROR
from gui.clans import formatters as clans_fmts
from helpers import time_utils
from messenger.ext import passCensor

def getTimestamp(datetimeValue):
    return time_utils.getTimestampFromUTC(datetimeValue.timetuple())


def toPercents(value):
    return 100 * value if value else value


def getEfficiency(dividend, delimiter):
    return float(dividend) / delimiter


def formatField(getter, dummy=None, formatter=None):
    return str(getter(doFmt=True, dummy=dummy, formatter=formatter))


def isValueAvailable(getter):
    return getter(checkAvailability=True)


class FieldsCheckerMixin(object):

    def __init__(self, *args, **kwargs):
        super(FieldsCheckerMixin, self).__init__()
        self.__class = self.__class__
        if hasattr(self, '_fields'):
            self._invalidFields = set((arg for arg in self._fields if arg not in kwargs))
        else:
            self._invalidFields = set()

    def isFieldValid(self, fieldName):
        return fieldName not in self._invalidFields

    def isValid(self):
        return not set(self._getCriticalFields()) & self._invalidFields

    def update(self, *args, **kwargs):
        obj = self._replace(**kwargs)
        obj._invalidFields = self._invalidFields
        return obj

    def _getCriticalFields(self):
        LOG_ERROR('Method must be override!', '_getCriticalFields', self.__class__)
        return tuple()


def fmtUnavailableValue(fields=tuple(), dummy=clans_fmts.DUMMY_UNAVAILABLE_DATA):

    def decorator(func):

        def wrapper(self, *args, **kwargs):

            def _isAvailable(fields):
                for field in fields:
                    if not self.isFieldValid(field):
                        return False

                return True

            checkAvailability = kwargs.pop('checkAvailability', False)
            if checkAvailability:
                return _isAvailable(fields)
            doFmt = kwargs.get('doFmt', False)
            placeholder = kwargs.get('dummy', dummy) or dummy
            f = kwargs.get('formatter', None)
            if doFmt and not _isAvailable(fields):
                return placeholder
            try:
                value = func(self)
            except ValueError:
                value = None

            if value is None:
                return placeholder
            else:
                return f(value) if f is not None else value

        return wrapper

    return decorator


def fmtNullValue(nullValue=0, dummy=clans_fmts.DUMMY_NULL_DATA):

    def decorator(func):

        def wrapper(*args, **kwargs):
            checkAvailability = kwargs.get('checkAvailability', False)
            doFmt = kwargs.get('doFmt', False)
            value = func(*args, **kwargs)
            if not checkAvailability and doFmt and value == nullValue:
                value = dummy
            return value

        return wrapper

    return decorator


def fmtZeroDivisionValue(defValue=0, dummy=clans_fmts.DUMMY_NULL_DATA):

    def decorator(func):

        def wrapper(*args, **kwargs):
            try:
                value = func(*args, **kwargs)
            except ZeroDivisionError:
                if kwargs.get('doFmt', False):
                    return kwargs.get('dummy', dummy) or dummy
                return defValue

            return value

        return wrapper

    return decorator


def formatString(value):
    return clans_fmts.DUMMY_UNAVAILABLE_DATA if not value else passCensor(value)


def fmtDelegat(path, dummy=clans_fmts.DUMMY_UNAVAILABLE_DATA):

    def decorator(func):

        def wrapper(self, *args, **kwargs):

            def _getGetter(path):
                return reduce(getattr, path.split('.'), self)

            checkAvailability = kwargs.pop('checkAvailability', False)
            doFmt = kwargs.pop('doFmt', False)
            placeholder = kwargs.pop('dummy', dummy) or dummy
            f = kwargs.pop('formatter', None)
            if checkAvailability:
                return _getGetter(path)(checkAvailability=checkAvailability)
            else:
                return _getGetter(path)(doFmt=doFmt, dummy=placeholder, formatter=f) if doFmt else func(self, *args, **kwargs)

        return wrapper

    return decorator


def conditionFormatter(formatter=None):

    def decorator(func):

        def wrapper(self, *args, **kwargs):
            doFmt = kwargs.get('doFmt', False)
            fmt = kwargs.get('formatter', None) or formatter
            value = func(self)
            if doFmt and fmt:
                value = fmt(value)
            return value

        return wrapper

    return decorator


def simpleFormatter(formatter=None):

    def decorator(func):

        def wrapper(self):
            value = func(self)
            if formatter and value is not None:
                value = formatter(value)
            return value

        return wrapper

    return decorator
