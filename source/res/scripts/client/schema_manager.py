# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/schema_manager.py
import typing
import logging
from game_params_common.base_manager import BaseSchemaManager, SchemaInfo
from game_params_common.scope import clientFilter
if typing.TYPE_CHECKING:
    from dict2model.schemas import SchemaModelType
    from game_params_common.schema import GameParamsSchema
_logger = logging.getLogger(__name__)

class ClientSchemaInfo(SchemaInfo):
    __slots__ = ('skipValidation',)

    def __init__(self, schema, skipValidation):
        super(ClientSchemaInfo, self).__init__(schema)
        self.skipValidation = skipValidation


class SchemaManager(BaseSchemaManager[ClientSchemaInfo]):

    def __init__(self):
        super(SchemaManager, self).__init__()
        self._models = {}

    def registerSchema(self, schema, skipValidation=True):
        self._addSchema(ClientSchemaInfo(schema, skipValidation))

    def set(self, serverSettings):
        for schemaInfo in self.getSchemasInfo():
            schema = schemaInfo.schema
            if schema.gpKey in serverSettings:
                rawConfig = serverSettings[schema.gpKey]
                self._models[schema.gpKey] = schema.deserialize(rawConfig, filter_=clientFilter, skipValidation=schemaInfo.skipValidation)
                from PlayerEvents import g_playerEvents
                g_playerEvents.onConfigModelUpdated(schema.gpKey)

    def update(self, serverSettingsDiff):
        for schemaInfo in self.getSchemasInfo():
            schema = schemaInfo.schema
            if schema.gpKey in serverSettingsDiff:
                if schema.gpKey not in self._models:
                    _logger.error('Update is called before set. schema=%s', schema.gpKey)
                    continue
                rawConfig = serverSettingsDiff[schema.gpKey]
                self._models[schema.gpKey] = schema.deserialize(rawConfig, filter_=clientFilter, skipValidation=schemaInfo.skipValidation)
                from PlayerEvents import g_playerEvents
                g_playerEvents.onConfigModelUpdated(schema.gpKey)

    def getModel(self, schema, **kwargs):
        model = self._models.get(schema.gpKey)
        if model is None:
            _logger.debug('No such schema: %s.', schema.gpKey)
        return model

    def updateSettings(self, serverSettings, diff):
        diffCopy = dict(diff)
        for key in diff:
            if key in self._models:
                serverSettings[key] = diffCopy.pop(key)

        return diffCopy

    def clear(self):
        self._models.clear()


g_SchemaManager = None

def getSchemaManager():
    global g_SchemaManager
    if g_SchemaManager is None:
        g_SchemaManager = SchemaManager()
    return g_SchemaManager
