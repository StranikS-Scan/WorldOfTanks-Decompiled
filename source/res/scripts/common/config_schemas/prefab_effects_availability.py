# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/config_schemas/prefab_effects_availability.py
from __future__ import absolute_import
from game_params_common.schema import GameParamsSchema
from dict2model import fields, models

class PrefabEffectsAvailabilityModel(models.Model):
    __slots__ = ('enabled', 'switchEnabled')

    def __init__(self, enabled, switchEnabled):
        super(PrefabEffectsAvailabilityModel, self).__init__()
        self.enabled = enabled
        self.switchEnabled = switchEnabled


prefabEffectsAvailabilitySchema = GameParamsSchema[PrefabEffectsAvailabilityModel](gameParamsKey='prefab_effects_availability_config', modelClass=PrefabEffectsAvailabilityModel, fields={'enabled': fields.Boolean(required=False, default=True),
 'switchEnabled': fields.Boolean(required=False, default=False)}, usedInReplay=True)
