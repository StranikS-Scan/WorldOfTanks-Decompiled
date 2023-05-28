# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dict2model/fields.py
from __future__ import absolute_import
import typing
import enum
from datetime import datetime
from soft_exception import SoftException
from dict2model import utils
from dict2model import validate
from dict2model.exceptions import ValidationError, ValidationErrorMessage
if typing.TYPE_CHECKING:
    from dict2model.types import ValidatorsType, SchemaModelTypes
    from dict2model.schemas import Schema

class Field(object):
    __slots__ = ('required', 'default', '_serializedValidators', '_deserializedValidators')

    def __init__(self, required=True, default=None, serializedValidators=None, deserializedValidators=None):
        self.required = required
        self.default = default
        self._serializedValidators = validate.prepareValidators(serializedValidators)
        self._deserializedValidators = validate.prepareValidators(deserializedValidators)

    def serialize(self, incoming, **kwargs):
        result = self._serialize(incoming)
        validate.runValidators(self._serializedValidators, result)
        return result

    def deserialize(self, incoming, **kwargs):
        result = self._deserialize(incoming)
        validate.runValidators(self._deserializedValidators, result)
        return result

    def _serialize(self, incoming):
        return incoming

    def _deserialize(self, incoming):
        return incoming


class Boolean(Field):
    _trueValues = {'t',
     'T',
     'true',
     'True',
     'TRUE',
     '1',
     1,
     True}
    _falseValues = {'f',
     'F',
     'false',
     'False',
     'FALSE',
     '0',
     0,
     0.0,
     False,
     None}
    __slots__ = ()

    def _serialize(self, incoming):
        return self._convert(incoming)

    def _deserialize(self, incoming):
        return self._convert(incoming)

    def _convert(self, incoming):
        try:
            if incoming in self._trueValues:
                return True
            if incoming in self._falseValues:
                return False
        except TypeError:
            pass

        raise ValidationError('Unsupported boolean.')


class String(Field):
    __slots__ = ()

    def _serialize(self, incoming):
        return self._convert(incoming)

    def _deserialize(self, incoming):
        return self._convert(incoming)

    @staticmethod
    def _convert(incoming):
        if not isinstance(incoming, utils.baseStringTypes):
            raise ValidationError('Unsupported string type.')
        try:
            if isinstance(incoming, utils.binaryType):
                incoming = incoming.decode('utf-8')
            return str(incoming)
        except UnicodeError:
            raise ValidationError('Invalid string.')


class Number(Field):
    numberType = float
    __slots__ = ('_serializeAsString',)

    def __init__(self, required=True, default=None, serializedValidators=None, deserializedValidators=None, serializeAsString=False):
        super(Number, self).__init__(required=required, default=default, serializedValidators=serializedValidators, deserializedValidators=deserializedValidators)
        self._serializeAsString = serializeAsString

    def serialize(self, incoming, **kwargs):
        result = super(Number, self).serialize(incoming)
        return self._toString(result) if self._serializeAsString else result

    def _serialize(self, incoming):
        return self._convert(incoming)

    def _deserialize(self, incoming):
        return self._convert(incoming)

    def _convert(self, incoming):
        try:
            return self._formatNumber(incoming)
        except (TypeError, ValueError):
            raise ValidationError('Not a valid number.')
        except OverflowError:
            raise ValidationError('Number too large.')

    def _formatNumber(self, value):
        return self.numberType(value)

    @staticmethod
    def _toString(value):
        return str(value)


class Integer(Number):
    numberType = int
    __slots__ = ()


class Float(Number):
    numberType = float
    __slots__ = ()


class DateTime(Field):
    __slots__ = ('_localtime',)

    def __init__(self, required=True, default=None, serializedValidators=None, deserializedValidators=None, localtime=False):
        super(DateTime, self).__init__(required=required, default=default, serializedValidators=serializedValidators, deserializedValidators=deserializedValidators)
        self._localtime = localtime

    def _serialize(self, incoming):
        try:
            return utils.isoFormat(incoming, localtime=self._localtime)
        except (TypeError,
         AttributeError,
         ValueError,
         SoftException):
            raise ValidationError('Not a valid datetime.')

    def _deserialize(self, incoming):
        try:
            return utils.fromIso(incoming)
        except (TypeError,
         AttributeError,
         ValueError,
         SoftException):
            raise ValidationError('Cannot be formatted as a datetime.')


class Url(String):
    __slots__ = ('_relative',)

    def __init__(self, required=True, default=None, serializedValidators=None, deserializedValidators=None, relative=False):
        super(Url, self).__init__(required=required, default=default, serializedValidators=serializedValidators, deserializedValidators=deserializedValidators)
        self._relative = relative
        self._serializedValidators = [validate.URL(relative=self._relative)] + list(self._serializedValidators)
        self._deserializedValidators = [validate.URL(relative=self._relative)] + list(self._deserializedValidators)


class Enum(Field):
    __slots__ = ('_enumClass',)

    def __init__(self, enumClass, required=True, default=None, serializedValidators=None, deserializedValidators=None):
        super(Enum, self).__init__(required=required, default=default, serializedValidators=serializedValidators, deserializedValidators=deserializedValidators)
        self._enumClass = enumClass

    def _serialize(self, incoming):
        if not isinstance(incoming, self._enumClass):
            raise ValidationError('Not a enum: {} class.'.format(self._enumClass))
        return incoming.value

    def _deserialize(self, incoming):
        try:
            return self._enumClass(incoming)
        except ValueError:
            enumValues = [ obj.value for obj in self._enumClass.__members__.values() ]
            raise ValidationError('Value: {} must be one of: {}.'.format(incoming, enumValues))


class Nested(Field):
    __slots__ = ('_schema',)

    def __init__(self, schema, required=True, default=None, serializedValidators=None, deserializedValidators=None):
        super(Nested, self).__init__(required=required, default=default, serializedValidators=serializedValidators, deserializedValidators=deserializedValidators)
        self._schema = schema

    def _serialize(self, incoming):
        return self._schema.serialize(incoming, silent=False)

    def _deserialize(self, incoming):
        return self._schema.deserialize(incoming, silent=False)


class List(Field):
    __slots__ = ('_fieldOrSchema',)

    def __init__(self, fieldOrSchema, required=True, default=None, serializedValidators=None, deserializedValidators=None):
        super(List, self).__init__(required=required, default=default, serializedValidators=serializedValidators, deserializedValidators=deserializedValidators)
        self._fieldOrSchema = fieldOrSchema

    def _serialize(self, incoming):
        return self._convert(incoming, method='serialize')

    def _deserialize(self, incoming):
        return self._convert(incoming, method='deserialize')

    def _convert(self, incoming, method):
        if not isinstance(incoming, (list, tuple)):
            raise ValidationError('Not a list type.')
        converted, errors = [], None
        for index, value in enumerate(incoming):
            try:
                converter = getattr(self._fieldOrSchema, method, None)
                if converter is None:
                    raise ValidationError('{} method {} not found.'.format(self._fieldOrSchema, method))
                converted.append(converter(value, silent=False))
            except ValidationError as ve:
                error = ValidationErrorMessage(ve.error.data, title='List[{}]'.format(index))
                errors = errors + error if errors else error

        if errors:
            raise ValidationError(errors)
        return converted
