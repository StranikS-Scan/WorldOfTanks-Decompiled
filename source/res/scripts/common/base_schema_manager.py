# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/base_schema_manager.py
import logging
import typing
from constants import IS_CLIENT, IS_BASEAPP
from dict2model.schemas import Schema, SchemaModelType
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from dict2model.fields import Field
    from dict2model.types import SchemaModelClassesType, ValidatorsType
    from section2dict import TReaders
_logger = logging.getLogger(__name__)

class GameParamsSchema(Schema[SchemaModelType]):
    __slots__ = ('readers', '_gameParamsKey')

    def __init__(self, gameParamsKey, fields, modelClass=dict, checkUnknown=True, serializedValidators=None, deserializedValidators=None, readers=None):
        super(GameParamsSchema, self).__init__(fields=fields, modelClass=modelClass, checkUnknown=checkUnknown, serializedValidators=serializedValidators, deserializedValidators=deserializedValidators)
        self.readers = readers
        self._gameParamsKey = gameParamsKey

    @property
    def gpKey(self):
        return self._gameParamsKey

    def getModel(self):
        if not IS_CLIENT and not IS_BASEAPP:
            raise NotImplementedError
        from schema_manager import getSchemaManager
        return getSchemaManager().getModel(self)


class BaseSchemaManager(object):
    __slots__ = ('_schemas', '_configs')

    def __init__(self):
        self._schemas = {}

    def registerClientServerSchema(self, *args, **kwargs):
        raise NotImplementedError

    def getModel(self, schema):
        raise NotImplementedError

    def getSchemas(self):
        return self._schemas.values()

    def _addSchema(self, schema):
        if not isinstance(schema, GameParamsSchema):
            raise SoftException('Registered root schema must be instance of GameParamsSchema. schema=%s', schema)
        if schema.gpKey in self._schemas:
            raise SoftException('Schema gameParamsKey duplication. Schema "%s" is already registered.' % schema.gpKey)
        self._schemas[schema.gpKey] = schema
