# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dict2model/exceptions.py
from __future__ import absolute_import
import typing
import pprint
from soft_exception import SoftException
from dict2model import utils

class ValidationErrorMessage(object):
    _indicator = '>>>'
    __slots__ = ('_data', '_str')

    def __init__(self, data, title=None):
        if isinstance(data, (list, tuple, set)):
            self._data = {title or self._indicator: list(data)}
        elif isinstance(data, dict):
            if title is None:
                self._data = dict(data)
            else:
                self._data = {title: dict(data)}
        else:
            self._data = {title or self._indicator: str(data)}
        self._str = None
        return

    def __str__(self):
        if self._str is None:
            try:
                self._str = pprint.pformat(self._data, width=200, depth=50)
            except Exception:
                self._str = str(self._data)

        return self._str

    def __add__(self, other):
        if not isinstance(other, ValidationErrorMessage):
            raise SoftException('Unsupported error message type: {}'.format(type(other)))
        return ValidationErrorMessage(utils.mergeDicts({}, self.data, other.data, deep=False))

    @property
    def data(self):
        return self._data


class ValidationError(SoftException):

    def __init__(self, error):
        if not isinstance(error, ValidationErrorMessage):
            error = ValidationErrorMessage(error)
        self.error = error
        super(ValidationError, self).__init__(self.error)


class AccessToFieldDeniedError(SoftException):

    def __init__(self, message):
        errorMsg = 'Field is not public and can`t be used. Method: %s.' % message
        super(AccessToFieldDeniedError, self).__init__(errorMsg)
