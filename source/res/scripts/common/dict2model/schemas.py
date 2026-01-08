# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dict2model/schemas.py
from __future__ import absolute_import
import logging
import traceback
import typing
from future.utils import viewitems
from dict2model import validate
from dict2model.exceptions import ValidationError, ValidationErrorMessage
from dict2model.fields import AccessDeniedField
from dict2model.models import Model
from py2to3 import patched_typing
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from dict2model.fields import Field
    from dict2model.types import ValidatorsType, SchemaModelClassesType, TFilter
    TRawData = typing.Dict[str, typing.Any]
_logger = logging.getLogger(__name__)
SchemaModelType = typing.TypeVar('SchemaModelType', bound=typing.Union[Model, typing.Dict])
accessDeniedField = AccessDeniedField()

class Schema(patched_typing.Generic[SchemaModelType]):
    __slots__ = ('_modelClass', '_checkUnknown', '_fields', '_serializedValidators', '_deserializedValidators')

    def __init__(self, fields, modelClass=dict, checkUnknown=True, serializedValidators=None, deserializedValidators=None):
        if not issubclass(modelClass, (Model, dict)):
            raise SoftException('ClassModel is not Model or dict.')
        self._fields = dict(fields)
        self._modelClass = modelClass
        self._checkUnknown = checkUnknown
        self._serializedValidators = validate.prepareValidators(serializedValidators)
        self._deserializedValidators = validate.prepareValidators(deserializedValidators)

    def serialize(self, incoming, filter_=None, silent=False, logError=True, skipValidation=False, **kwargs):
        try:
            if not isinstance(incoming, self._modelClass):
                raise ValidationError('Data not a {} type.'.format(self._modelClass))
            modelAsDict = incoming.toDict() if isinstance(incoming, Model) else incoming
            result = self._serialize(modelAsDict, filter_=filter_, skipValidation=skipValidation, **kwargs)
            if not skipValidation:
                validate.runValidators(self._serializedValidators, result)
            return result
        except Exception as errors:
            if not silent:
                raise
            if logError:
                _logger.error('Serialized validation errors: %s.', errors)

        return None

    def deserialize(self, incoming, filter_=None, silent=False, logError=True, skipValidation=False, **kwargs):
        try:
            if not skipValidation:
                if not isinstance(incoming, dict):
                    raise ValidationError('Data not a dict type.')
                if self._checkUnknown:
                    unknown = set(incoming) - set(self._fields)
                    if unknown:
                        raise ValidationError('Unexpected attributes: {}.'.format(unknown))
            result = self._deserialize(incoming, filter_=filter_, skipValidation=skipValidation, **kwargs)
            if not skipValidation:
                validate.runValidators(self._deserializedValidators, result)
            return result
        except Exception as errors:
            if not silent:
                raise
            if logError:
                _logger.error('Deserialized validation errors: %s.', errors)

        return None

    def _serialize(self, incoming, filter_=None, skipValidation=False, **kwargs):
        serialized, errors = {}, None
        for name, field in viewitems(self._fields):
            try:
                if filter_ and field.filterParams is not None and not filter_(field.filterParams):
                    continue
                if name not in incoming:
                    if field.required:
                        raise ValidationError('Required attribute: {} missing.'.format(name))
                else:
                    if not field.required:
                        default = field.default() if callable(field.default) else field.default
                        if incoming[name] == default:
                            continue
                    serialized[name] = field.serialize(incoming[name], skipValidation=skipValidation, filter_=filter_, **kwargs)
            except ValidationError as ve:
                error = ValidationErrorMessage(ve.error.data, title='Field({})'.format(name))
                errors = errors + error if errors else error

        if errors:
            raise ValidationError(errors)
        return serialized

    def _deserialize(self, incoming, filter_=None, skipValidation=False, **kwargs):
        deserialized, errors = {}, None
        for name, field in viewitems(self._fields):
            try:
                if filter_ and field.filterParams is not None and not filter_(field.filterParams):
                    deserialized[name] = accessDeniedField
                elif name not in incoming:
                    if field.required:
                        raise ValidationError('Required attribute: {} missing.'.format(name))
                    default = field.default() if callable(field.default) else field.default
                    deserialized[name] = default
                else:
                    deserialized[name] = field.deserialize(incoming[name], skipValidation=skipValidation, filter_=filter_, **kwargs)
            except ValidationError as ve:
                error = ValidationErrorMessage(ve.error.data, title='Field({})'.format(name))
                errors = errors + error if errors else error

        if errors:
            raise ValidationError(errors)
        try:
            return self._modelClass(**deserialized)
        except Exception as error:
            raise ValidationError('Model: {}, error: {}, traceback: {}'.format(self._modelClass, error, traceback.format_exc()))

        return
