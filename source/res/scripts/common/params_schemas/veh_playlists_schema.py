# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/params_schemas/veh_playlists_schema.py
from base_schema_manager import GameParamsSchema
from constants import Configs
from dict2model import models, fields as d2mfields

class VehPlaylistsConfigModel(models.Model):
    __slots__ = ('isVehPlaylistsEnabled',)

    def __init__(self, isVehPlaylistsEnabled):
        super(VehPlaylistsConfigModel, self).__init__()
        self.isVehPlaylistsEnabled = isVehPlaylistsEnabled


vehPlaylistsConfigSchema = GameParamsSchema[VehPlaylistsConfigModel](gameParamsKey=Configs.VEH_PLAYLISTS_CONFIG.value, fields={'isVehPlaylistsEnabled': d2mfields.Boolean()}, modelClass=VehPlaylistsConfigModel, checkUnknown=True)
