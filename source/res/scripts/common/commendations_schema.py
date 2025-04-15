# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/commendations_schema.py
from base_schema_manager import GameParamsSchema
from constants import Configs
from dict2model import models, fields as d2mfields

class CommendationsConfigModel(models.Model):
    __slots__ = ('isLiveTagsEnabled', 'isCommendationsEnabled')

    def __init__(self, isLiveTagsEnabled, isCommendationsEnabled):
        super(CommendationsConfigModel, self).__init__()
        self.isCommendationsEnabled = isCommendationsEnabled
        self.isLiveTagsEnabled = isLiveTagsEnabled


commendationsConfigSchema = GameParamsSchema[CommendationsConfigModel](gameParamsKey=Configs.COMMENDATIONS_CONFIG.value, fields={'isLiveTagsEnabled': d2mfields.Boolean(),
 'isCommendationsEnabled': d2mfields.Boolean()}, modelClass=CommendationsConfigModel, checkUnknown=True)
