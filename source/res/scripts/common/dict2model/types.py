# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dict2model/types.py
from __future__ import absolute_import
import typing
from dict2model.models import Model
from dict2model.schemas import Schema
from dict2model.validate import Validator
ModelType = typing.TypeVar('ModelType', bound=Model)
SchemaType = typing.TypeVar('SchemaType', bound=Schema)
SchemaModelTypes = typing.Union[ModelType, typing.Dict]
SchemaModelClassesType = typing.Union[typing.Type[ModelType], typing.Type[typing.Dict]]
ValidatorType = typing.Union[Validator, typing.Callable[[typing.Any], typing.Any]]
ValidatorsType = typing.Optional[typing.Union[ValidatorType, typing.List[ValidatorType]]]
