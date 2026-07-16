# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/game_params_common/base_manager.py
from __future__ import absolute_import
import logging
import typing
from future.utils import listvalues
from game_params_common.schema import GameParamsSchema
from py2to3 import patched_typing
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from dict2model.schemas import SchemaModelType
_logger = logging.getLogger(__name__)

class SchemaInfo(object):
    __slots__ = ('schema',)

    def __init__(self, schema):
        self.schema = schema


TSchemaInfo = typing.TypeVar('TSchemaInfo', bound=SchemaInfo)

class BaseSchemaManager(patched_typing.Generic[TSchemaInfo]):
    __slots__ = ('_schemas', '_usedInReplaySchemaKeys')

    def __init__(self):
        self._schemas = {}
        self._usedInReplaySchemaKeys = set()

    def registerSchema(self, *args, **kwargs):
        raise NotImplementedError

    def getModel(self, schema, **kwargs):
        raise NotImplementedError

    def getSchemasInfo(self):
        return listvalues(self._schemas)

    def getSchemaInfo(self, schema):
        return self._schemas.get(schema.gpKey)

    def getUsedInReplayKeys(self):
        return self._usedInReplaySchemaKeys

    def _addSchema(self, schemaInfo):
        if not isinstance(schemaInfo.schema, GameParamsSchema):
            raise SoftException('Registered root schema must be instance of GameParamsSchema. schema={}'.format(schemaInfo.schema))
        if schemaInfo.schema.gpKey in self._schemas:
            raise SoftException('Schema gameParamsKey duplication. Schema "{}" is already registered.'.format(schemaInfo.schema.gpKey))
        self._schemas[schemaInfo.schema.gpKey] = schemaInfo
        if schemaInfo.schema.usedInReplay:
            self._usedInReplaySchemaKeys.add(schemaInfo.schema.gpKey)
