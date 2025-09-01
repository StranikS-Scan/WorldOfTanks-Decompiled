# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/armor_flashlight_common/server_config.py
from base_schema_manager import GameParamsSchema
from dict2model import models, fields

class ServerConfigModel(models.Model):
    __slots__ = ('enabled',)

    def __init__(self, enabled):
        super(ServerConfigModel, self).__init__()
        self.enabled = enabled

    def _reprArgs(self):
        return 'enabled={}'.format(self.enabled)


serverConfigSchema = GameParamsSchema[ServerConfigModel](gameParamsKey='armor_flashlight_config', fields={'enabled': fields.Boolean(required=True)}, modelClass=ServerConfigModel)
