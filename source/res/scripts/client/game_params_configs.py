# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/game_params_configs.py
import typing
from commendations_schema import commendationsConfigSchema
from params_schemas.veh_playlists_schema import vehPlaylistsConfigSchema
import armor_flashlight_common.server_config
from config_schemas.umg import umgMissionsConfigSchema, umgEventsConfigSchema
from config_schemas.umg_config import umgConfigSchema
from player_satisfaction_schema import playerSatisfactionSchema
from schema_manager import getSchemaManager
import armor_inspector_common.schemas
import hints_common.prebattle.newbie.schemas
import hints_common.prebattle.schemas
import hints_common.battle.schemas.newbie
from weekly_quests_common.weekly_quests_schema import weeklyQuestsSchema
if typing.TYPE_CHECKING:
    from schema_manager import SchemaManager

def init():
    schemaManager = getSchemaManager()
    _registerSchemas(schemaManager)


def _registerSchemas(schemaManager):
    schemaManager.registerClientServerSchema(hints_common.prebattle.newbie.schemas.configSchema)
    schemaManager.registerClientServerSchema(hints_common.prebattle.schemas.configSchema)
    schemaManager.registerClientServerSchema(hints_common.battle.schemas.newbie.configSchema)
    schemaManager.registerClientServerSchema(playerSatisfactionSchema)
    schemaManager.registerClientServerSchema(commendationsConfigSchema)
    schemaManager.registerClientServerSchema(vehPlaylistsConfigSchema)
    schemaManager.registerClientServerSchema(armor_flashlight_common.server_config.serverConfigSchema)
    schemaManager.registerClientServerSchema(umgMissionsConfigSchema)
    schemaManager.registerClientServerSchema(umgEventsConfigSchema)
    schemaManager.registerClientServerSchema(umgConfigSchema)
    schemaManager.registerClientServerSchema(weeklyQuestsSchema)
    schemaManager.registerClientServerSchema(armor_inspector_common.schemas.armorInspectorConfigSchema)
