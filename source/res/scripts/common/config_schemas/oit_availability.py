# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/config_schemas/oit_availability.py
from __future__ import absolute_import
from game_params_common.schema import GameParamsSchema
from dict2model import fields, models

class OitAvailabilityModel(models.Model):
    __slots__ = ('min', 'low', 'medium', 'high', 'ultra')

    def __init__(self, min, low, medium, high, ultra):
        super(OitAvailabilityModel, self).__init__()
        self.min = min
        self.low = low
        self.medium = medium
        self.high = high
        self.ultra = ultra


oitAvailabilitySchema = GameParamsSchema[OitAvailabilityModel](gameParamsKey='oit_availability_config', modelClass=OitAvailabilityModel, fields={'min': fields.Boolean(required=False, default=False),
 'low': fields.Boolean(required=False, default=False),
 'medium': fields.Boolean(required=False, default=False),
 'high': fields.Boolean(required=False, default=False),
 'ultra': fields.Boolean(required=False, default=False)})
