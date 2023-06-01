# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dict2model/validate.py
from __future__ import absolute_import
import typing
import re
from soft_exception import SoftException
from dict2model.exceptions import ValidationError, ValidationErrorMessage
if typing.TYPE_CHECKING:
    from dict2model.types import ValidatorType, ValidatorsType

def prepareValidators(validators):
    prepared = []
    if isinstance(validators, (list, tuple)):
        prepared += list(validators)
    elif validators is not None:
        prepared.append(validators)
    errors = None
    for validator in prepared:
        if not callable(validator):
            error = ValidationErrorMessage('Unsupported validator type: {}.'.format(type(validator)))
            errors = errors + error if errors else error

    if errors:
        raise SoftException(str(errors))
    return prepared


def runValidators(validations, toValidate):
    errors = None
    for validation in validations:
        try:
            validation(toValidate)
        except ValidationError as ve:
            errors = errors + ve.error if errors else ve.error

    if errors:
        raise ValidationError(errors)
    return


class Validator(object):
    __slots__ = ()

    def __call__(self, incoming):
        pass

    def __repr__(self):
        return '<{}({})>'.format(self.__class__.__name__, self._reprArgs() or '')

    def _reprArgs(self):
        pass


class Range(Validator):
    _messageMin = 'Must be at least {min}.'
    _messageMax = 'Must be at most {max}.'
    _messageAll = 'Must be between {min} and {max}.'
    __slots__ = ('_min', '_max')

    def __init__(self, minValue=None, maxValue=None):
        self._min = minValue
        self._max = maxValue

    def __call__(self, incoming):
        if self._min is not None and incoming < self._min:
            message = self._messageMin if self._max is None else self._messageAll
            raise ValidationError(self._formatError(message))
        if self._max is not None and incoming > self._max:
            message = self._messageMax if self._min is None else self._messageAll
            raise ValidationError(self._formatError(message))
        return

    def _reprArgs(self):
        return 'min={}, max={}'.format(self._min, self._max)

    def _formatError(self, message):
        return message.format(min=self._min, max=self._max)


class Length(Range):
    _messageMin = 'Shorter than minimum length {min}.'
    _messageMax = 'Longer than maximum length {max}.'
    _messageAll = 'Length must be between {min} and {max}.'
    _messageEqual = 'Length must be {equal}.'
    __slots__ = ('_equal',)

    def __init__(self, minValue=None, maxValue=None, equalValue=None):
        if equalValue is not None and any([minValue, maxValue]):
            raise SoftException('The `equal` parameter was provided, `max` or `min` parameter must not be provided.')
        super(Length, self).__init__(minValue, maxValue)
        self._equal = equalValue
        return

    def __call__(self, incoming):
        length = len(incoming)
        if self._equal is not None:
            if length != self._equal:
                raise ValidationError(self._formatError(self._messageEqual))
            return
        else:
            super(Length, self).__call__(length)
            return

    def _reprArgs(self):
        return 'min={}, max={}, equal={}'.format(self._min, self._max, self._equal)

    def _formatError(self, message):
        return message.format(min=self._min, max=self._max, equal=self._equal)


class URL(Validator):

    class RegexMemoizer(object):
        __slots__ = ('_memoized',)

        def __init__(self):
            self._memoized = {}

        def __call__(self, relative, requireTld):
            key = (relative, requireTld)
            if key not in self._memoized:
                self._memoized[key] = self._regexGenerator(relative, requireTld)
            return self._memoized[key]

        @staticmethod
        def _regexGenerator(relative, requireTld):
            return re.compile(''.join(('^',
             '(' if relative else '',
             '(?:[a-z0-9\\.\\-\\+]*)://',
             '(?:[^:@]+?(:[^:@]*?)?@|)',
             '(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\\.)+',
             '(?:[A-Z]{2,6}\\.?|[A-Z0-9-]{2,}\\.?)|',
             'localhost|',
             '(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\\.?)|' if not requireTld else '',
             '\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}|',
             '\\[?[A-F0-9]*:[A-F0-9:]+\\]?)',
             '(?::\\d+)?',
             ')?' if relative else '',
             '(?:/?|[/?]\\S+)\\Z')), re.IGNORECASE)

    _regex = RegexMemoizer()
    _message = 'Not a valid URL.'
    _schemes = {'http',
     'https',
     'ftp',
     'ftps'}
    __slots__ = ('relative', 'requireTld')

    def __init__(self, relative=False, requireTld=True):
        self.relative = relative
        self.requireTld = requireTld

    def __call__(self, incoming):
        if not incoming:
            raise ValidationError(self._message)
        if '://' in incoming:
            scheme = incoming.split('://')[0].lower()
            if scheme not in self._schemes:
                raise ValidationError(self._message)
        regex = self._regex(self.relative, self.requireTld)
        if not regex.search(incoming):
            raise ValidationError(self._message)

    def _reprArgs(self):
        return 'relative={}'.format(self.relative)
