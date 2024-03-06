# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dict2model/types.py
from __future__ import absolute_import
import typing
from dict2model.models import Model
from dict2model.validate import Validator
_ModelClassType = typing.TypeVar('_ModelClassType', bound=typing.Type[Model])
SchemaModelClassesType = typing.Union[_ModelClassType, typing.Type[typing.Dict]]
ValidatorType = typing.Union[Validator, typing.Callable[[typing.Any], typing.Any]]
ValidatorsType = typing.Optional[typing.Union[ValidatorType, typing.List[ValidatorType]]]
