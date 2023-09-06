# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/schema_manager.py
import logging
from base_schema_manager import BaseSchemaManager, GameParamsSchema
_logger = logging.getLogger(__name__)

class SchemaManager(BaseSchemaManager):

    def __init__(self):
        super(SchemaManager, self).__init__()
        self._models = {}

    def registerClientServerSchema(self, schema):
        self._addSchema(schema)

    def set(self, serverSettings):
        for schema in self.getSchemas():
            if schema.gpKey in serverSettings:
                rawConfig = serverSettings[schema.gpKey]
                self._models[schema.gpKey] = schema.deserialize(rawConfig, onlyPublic=True)
                from PlayerEvents import g_playerEvents
                g_playerEvents.onConfigModelUpdated(schema.gpKey)

    def update(self, serverSettingsDiff):
        for schema in self.getSchemas():
            if schema.gpKey in serverSettingsDiff:
                if schema.gpKey not in self._models:
                    _logger.error('Update is called before set. schema=%s', schema.gpKey)
                    continue
                rawConfig = serverSettingsDiff[schema.gpKey]
                self._models[schema.gpKey] = schema.deserialize(rawConfig, onlyPublic=True)
                from PlayerEvents import g_playerEvents
                g_playerEvents.onConfigModelUpdated(schema.gpKey)

    def get(self, schema):
        model = self._models.get(schema.gpKey)
        if model is None:
            _logger.error('No such schema: %s.', schema.gpKey)
        return model

    def clear(self):
        self._models.clear()


g_SchemaManager = None

def getSchemaManager():
    global g_SchemaManager
    if g_SchemaManager is None:
        g_SchemaManager = SchemaManager()
    return g_SchemaManager
