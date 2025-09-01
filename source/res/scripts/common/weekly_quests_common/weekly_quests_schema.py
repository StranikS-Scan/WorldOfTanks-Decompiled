# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/weekly_quests_common/weekly_quests_schema.py
from base_schema_manager import GameParamsSchema
from constants import Configs
from dict2model import fields, models, validate

class WeeklyQuestsConfigModel(models.Model):
    __slots__ = ('enabled', 'rerollTimeout')

    def __init__(self, enabled, rerollTimeout):
        super(WeeklyQuestsConfigModel, self).__init__()
        self.enabled = enabled
        self.rerollTimeout = rerollTimeout

    def _reprArgs(self):
        return 'enabled={}, rerollTimeout={}'.format(self.enabled, self.rerollTimeout)


weeklyQuestsSchema = GameParamsSchema[WeeklyQuestsConfigModel](gameParamsKey=Configs.WEEKLY_QUESTS_CONFIG.value, fields={'enabled': fields.Boolean(required=True),
 'rerollTimeout': fields.Integer(required=True, deserializedValidators=validate.Range(minValue=1))}, modelClass=WeeklyQuestsConfigModel, checkUnknown=True)
