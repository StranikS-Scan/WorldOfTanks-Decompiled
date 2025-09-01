# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/config_schemas/umg_config.py
from base_schema_manager import GameParamsSchema
from dict2model import fields, models

class ConfigModel(models.Model):
    __slots__ = ('enableAllDaily', 'enableAllWeekly', 'enableDailyWeeklyUI', 'enablePM3Banner')

    def __init__(self, enableAllDaily, enableAllWeekly, enableDailyWeeklyUI, enablePM3Banner):
        super(ConfigModel, self).__init__()
        self.enableAllDaily = enableAllDaily
        self.enableAllWeekly = enableAllWeekly
        self.enableDailyWeeklyUI = enableDailyWeeklyUI
        self.enablePM3Banner = enablePM3Banner

    def _reprArgs(self):
        return 'enableAllDaily=%s, enableAllWeekly=%s, enableDailyWeeklyUI=%s, enablePM3Banner=%s' % (self.enableAllDaily,
         self.enableAllWeekly,
         self.enableDailyWeeklyUI,
         self.enablePM3Banner)


umgConfigSchema = GameParamsSchema[ConfigModel](gameParamsKey='umgConfig', modelClass=ConfigModel, fields={'enableAllDaily': fields.Integer(),
 'enableAllWeekly': fields.Integer(),
 'enableDailyWeeklyUI': fields.Integer(),
 'enablePM3Banner': fields.Integer()})
